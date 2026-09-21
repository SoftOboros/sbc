import io
import json
import os
from pathlib import Path
import shutil
import tempfile
import stat
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import test_host as fixtures
import test_admission
from test_provenance_inputs import commit_files
from test_provenance_integration import sha
from sbc_tools.cli import main
from sbc_tools.host import load_console_host


class ConsoleHostTests(unittest.TestCase):
    def setUp(self):
        fixtures.HostLoaderTests.setUp(self)
        r = self.registration
        self.binding = {name:getattr(r,name) for name in r.__dataclass_fields__}
        self.binding.pop('config_bytes')
        self.binding.update(schema_version=1,config_sha256=sha(self.config),evidence_paths=[],archive_families=[])
        for key in ('source_repositories','authority_repositories'):
            self.binding[key] = {k:os.path.relpath(v,self.root) for k,v in self.binding[key].items()}
        for key in ('document_families','approved_support_sha256'):
            self.binding[key] = dict(self.binding[key])
        self.host_path = self.root/'host.json'
        self.write()

    def write(self):
        self.host_path.write_bytes(json.dumps(self.binding).encode())

    def invoke(self,command='check',config=None,**kwargs):
        out = io.BytesIO()
        code = main([command,'--config',str(config or self.registration.configuration_file),
                     '--host',str(self.host_path),'--format=json'],stdout=out,**kwargs)
        return code,json.loads(out.getvalue())

    def commit_output(self):
        files = dict(self.source_files)
        files.update({p.relative_to(self.source_root).as_posix():p.read_bytes()
                      for p in (self.source_root/'projection').rglob('*') if p.is_file()})
        commit = commit_files(self.source_repo,files)
        test_admission.checkout(self.source_repo,self.source_root,commit)

    def test_default_console_scan_commit_check_and_relocated_checkout(self):
        code,scan = self.invoke('scan')
        self.assertEqual((1,'published'),(code,scan['result']['publication']))
        self.commit_output()
        code,check = self.invoke()
        self.assertEqual((1,'equal'),(code,check['result']['comparison']))
        self.assertEqual(scan['selection']['snapshot_id'],check['selection']['snapshot_id'])
        with tempfile.TemporaryDirectory() as temp:
            relocated = Path(temp)/'copied'
            shutil.copytree(self.root,relocated)
            out = io.BytesIO()
            moved_config = relocated/self.registration.configuration_file.relative_to(self.root)
            code = main(['check','--config',str(moved_config),'--host',str(relocated/'host.json'),
                         '--format=json'],stdout=out)
            self.assertEqual(1,code)
            self.assertEqual(check['selection']['snapshot_id'],json.loads(out.getvalue())['selection']['snapshot_id'])

    def test_schema_and_config_hash_failures(self):
        original = dict(self.binding)
        for change in ({'extra':True},{'schema_version':2},{'config_sha256':'0'*64},
                       {'config_path':'../outside'},{'document_families':[]},
                       {'archive_families':[{'archive':'a.zip','member':'b.md','family':'x'}]*2}):
            self.binding = dict(original,**change)
            self.write()
            with self.subTest(change=change):
                code,result = self.invoke()
                self.assertEqual((2,'invalid_configuration'),(code,result['error']['code']))

    def test_duplicate_keys_and_nonfinite_values_reject(self):
        for raw in (b'{"schema_version":1,"schema_version":1}',b'{"value":NaN}'):
            self.host_path.write_bytes(raw)
            self.assertEqual(2,self.invoke()[0])

    def test_mismatched_config_not_read(self):
        from sbc_tools import host
        original = host._regular_input
        read = []
        def observed(path):
            read.append(path)
            return original(path)
        with patch.object(host,'_regular_input',side_effect=observed):
            self.assertEqual(2,self.invoke(config=self.root/'unknown.toml')[0])
        self.assertEqual([self.host_path],read)

    def test_injected_loader_conflicts_before_binding_read(self):
        with patch('sbc_tools.host.load_console_host',side_effect=AssertionError('Unexpected read')):
            code,result = self.invoke(load_host=self.loader)
        self.assertEqual((2,'invalid_invocation'),(code,result['error']['code']))

    def test_loaded_binding_does_not_change_with_file_edit(self):
        loader = load_console_host(self.host_path,self.registration.configuration_file)
        self.host_path.write_bytes(b'invalid replacement')
        with loader(self.registration.configuration_file) as host:
            self.assertTrue(host.verifier.supports('check'))
        self.assertEqual(2,self.invoke()[0])

    def test_wrong_authority_pin_is_not_inferred_or_repaired(self):
        self.binding['approved_authority_sha256'] = '0'*64
        self.write()
        code,result = self.invoke('scan')
        self.assertEqual((2,'invalid_authority'),(code,result['error']['code']))
        self.assertFalse((self.source_root/'projection').exists())

    def test_reparse_binding_rejected_before_read(self):
        original = Path.lstat
        def metadata(path,*args,**kwargs):
            if path == self.host_path:
                return SimpleNamespace(st_mode=stat.S_IFREG,st_file_attributes=0x400)
            return original(path,*args,**kwargs)
        with patch.object(Path,'lstat',metadata),patch.object(Path,'read_bytes',side_effect=AssertionError('Unexpected read')):
            self.assertEqual(2,self.invoke()[0])


if __name__ == '__main__': unittest.main()
