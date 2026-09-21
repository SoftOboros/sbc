from dataclasses import replace
import io
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import test_admission as fixtures
from test_provenance_inputs import commit_files
from test_provenance_integration import sha
from sbc_tools.cli import main
from sbc_tools.git_reader import GitCommitReader
from sbc_tools.host import HostRegistration, RegisteredHostLoader


class HostLoaderTests(unittest.TestCase):
    def setUp(self):
        fixtures.AdmissionTests.setUp(self)
        self.registration = HostRegistration(repository_id='source',
            source_repositories={'source':self.source_root},
            authority_repositories={'fixture':self.authority_reader.checkout_path},
            config_path='sbc.toml',config_bytes=self.config,tracked_branch='main',
            profile_path='profile.json',profile_sha256=sha(self.profile),patch_path='support.patch',
            approved_authority_sha256=sha(self.authority_bytes),
            approved_support_sha256={r:sha((r+' updated\n').encode()) for r in ('AGENTS.md','CLAUDE.md','README.md')},
            document_families={'docs/todo/spec.md':'example'})
        self.loader = RegisteredHostLoader([self.registration])

    def invoke(self, command='check', path=None, loader=None):
        out = io.BytesIO()
        code = main([command,'--config',str(path or self.registration.configuration_file),'--format=json'],
                    load_host=loader or self.loader,stdout=out)
        return code,json.loads(out.getvalue())

    def test_registered_scan_commit_check_and_reader_cleanup(self):
        closed = []
        close = GitCommitReader.close
        def closing(reader):
            closed.append(reader)
            close(reader)
        with patch.object(GitCommitReader,'close',closing):
            code,scan = self.invoke('scan')
        self.assertEqual(1,code)
        self.assertEqual('published',scan['result']['publication'])
        self.assertEqual(2,len(closed))
        files = dict(self.source_files)
        files.update({p.relative_to(self.source_root).as_posix():p.read_bytes()
                      for p in (self.source_root/'projection').rglob('*') if p.is_file()})
        commit = commit_files(self.source_repo,files)
        fixtures.checkout(self.source_repo,self.source_root,commit)
        code,checked = self.invoke()
        self.assertEqual((1,'equal'),(code,checked['result']['comparison']))
        self.assertEqual(scan['selection']['snapshot_id'],checked['selection']['snapshot_id'])

    def test_unregistered_path_not_read_or_opened(self):
        with (patch.object(Path,'read_bytes',side_effect=AssertionError('Unexpected read')),
              patch('sbc_tools.host.GitCommitReader',side_effect=AssertionError('Unexpected repository'))):
            code,result = self.invoke(path=self.source_root/'unregistered.toml')
        self.assertEqual(2,code)
        self.assertEqual('invalid_configuration',result['error']['code'])

    def test_changed_configuration_rejected_before_git_open(self):
        self.registration.configuration_file.write_bytes(self.config+b'# changed\n')
        with patch('sbc_tools.host.GitCommitReader',side_effect=AssertionError('Unexpected repository')):
            code,result = self.invoke()
        self.assertEqual(2,code)
        self.assertIsNone(result['selection'])

    def test_registration_copies_mutable_inputs_and_rejects_duplicates(self):
        families = {'docs/todo/spec.md':'example'}
        registration = replace(self.registration,document_families=families)
        families.clear()
        self.assertEqual({'docs/todo/spec.md':'example'},registration.document_families)
        with self.assertRaises(TypeError): registration.document_families['other'] = 'bad'
        with self.assertRaises(ValueError): RegisteredHostLoader([registration,registration])
        with self.assertRaises(ValueError): replace(registration,config_path='../outside')

    def test_partial_reader_open_failure_closes_opened_reader(self):
        opened,closed = [],[]
        close = GitCommitReader.close
        def opening(path):
            if opened: raise OSError('private unavailable repository')
            reader = GitCommitReader(path)
            opened.append(reader)
            return reader
        def closing(reader):
            closed.append(reader)
            close(reader)
        with patch('sbc_tools.host.GitCommitReader',side_effect=opening),patch.object(GitCommitReader,'close',closing):
            code,result = self.invoke()
        self.assertEqual(3,code)
        self.assertEqual(opened,closed)
        self.assertNotIn('private',json.dumps(result))

    def test_configuration_construction_failure_closes_all_readers(self):
        loader = RegisteredHostLoader([replace(self.registration,tracked_branch='other')])
        closed = []
        close = GitCommitReader.close
        def closing(reader):
            closed.append(reader)
            close(reader)
        with patch.object(GitCommitReader,'close',closing):
            code,_ = self.invoke(loader=loader)
        self.assertEqual(2,code)
        self.assertEqual(2,len(closed))


if __name__ == '__main__': unittest.main()
