from dataclasses import replace
import hashlib
import io
import json
import os
import unittest
from unittest.mock import patch

from sbc_tools.cli import main
from test_admission import checkout
from test_provenance_inputs import commit_files
import test_mounted_working_generation as fixtures


class MountedWorkingCLITests(unittest.TestCase):
    def setUp(self):
        fixtures.MountedWorkingGenerationTests.setUp(self)
        self.host_path = self.root / 'mounted-host.json'
        self.write_binding()

    def write_binding(self):
        r = self.registration
        value = {name: getattr(r, name) for name in r.__dataclass_fields__}
        value.pop('config_bytes')
        value.update(schema_version=1, config_sha256=hashlib.sha256(r.config_bytes).hexdigest(),
                     evidence_paths=list(r.evidence_paths), archive_families=[])
        for key in ('source_repositories', 'authority_repositories'):
            value[key] = {k: os.path.relpath(v, self.root) for k, v in value[key].items()}
        for key in ('document_families', 'approved_support_sha256'):
            value[key] = dict(value[key])
        self.host_path.write_bytes(json.dumps(value).encode())

    def invoke(self, command='scan'):
        out = io.BytesIO()
        code = main([command, '--host', str(self.host_path), '--config',
                     str(self.registration.configuration_file), '--format=json'], stdout=out)
        return code, json.loads(out.getvalue())

    def test_scan_and_committed_reference_check_emit_v2(self):
        code, scan = self.invoke()
        self.assertIn(code, (0, 1))
        self.assertEqual((2, 'published'), (scan['schema_version'], scan['result']['publication']))
        self.assertTrue(scan['observation']['complete'])
        self.assertIsNone(scan['selection']['source_commit'])
        files = dict(self.source_files, **{'sbc.toml': self.registration.config_bytes})
        files.update({p.relative_to(self.source_root).as_posix(): p.read_bytes()
                      for p in (self.source_root / 'projection').rglob('*') if p.is_file()})
        child = self.child_reader.resolve_commit('HEAD')
        commit = commit_files(self.source_repo, files, {'docs/todo/child': child})
        checkout(self.source_repo, self.source_root, commit)
        code, checked = self.invoke('check')
        self.assertIn(code, (0, 1))
        self.assertEqual('equal', checked['result']['comparison'])
        self.assertEqual(scan['selection']['snapshot_id'], checked['selection']['snapshot_id'])
        self.assertEqual([], checked['selection']['dependencies'])

    def test_missing_reference_keeps_complete_observation(self):
        code, result = self.invoke('check')
        self.assertEqual((3, 2), (code, result['schema_version']))
        self.assertTrue(result['observation']['complete'])
        self.assertIsNotNone(result['selection'])
        self.assertFalse((self.source_root / 'projection').exists())

    def test_bad_mounted_configuration_is_v2_early_error(self):
        config = self.registration.config_bytes.replace(b'output_root = "projection"',
                                                        b'output_root = "docs/todo"')
        self.registration = replace(self.registration, config_bytes=config)
        self.registration.configuration_file.write_bytes(config)
        self.write_binding()
        code, result = self.invoke()
        self.assertEqual((2, 2), (code, result['schema_version']))
        self.assertIsNone(result['observation'])

    def test_in_read_change_is_unavailable_without_publication(self):
        from sbc_tools.working_tree import WorkingTreeChangedError
        with patch('sbc_tools.mounted_working_tree._read_regular',
                   side_effect=WorkingTreeChangedError('private detail')):
            code, result = self.invoke()
        self.assertEqual((3, 'evidence_unavailable'), (code, result['error']['code']))
        self.assertFalse(result['observation']['complete'])
        self.assertIsNone(result['selection'])
        self.assertFalse((self.source_root / 'projection').exists())

    def test_missing_child_returns_incomplete_without_publication(self):
        parked = self.root / 'parked-child'
        self.child_root.rename(parked)
        try:
            code, result = self.invoke()
        finally:
            parked.rename(self.child_root)
        self.assertEqual((3, 2), (code, result['schema_version']))
        self.assertIsNone(result['selection'])
        self.assertIsNone(result['result'])
        self.assertFalse(result['observation']['complete'])
        states = {p['repository_id']: p for p in result['observation']['participants']}
        self.assertEqual('missing_checkout', states['child']['availability'])
        self.assertEqual('available', states['source']['availability'])
        self.assertEqual('unknown', states['source']['checkout_state'])
        self.assertIsNone(states['source']['corpus_sha256'])
        self.assertFalse((self.source_root / 'projection').exists())

    def test_missing_child_blocks_registered_descendant(self):
        config = self.registration.config_bytes.replace(
            b'repository_id = "child"}]',
            b'repository_id = "child"}, {path = "docs/todo/child/nested", repository_id = "nested"}]')
        self.registration = replace(self.registration, config_bytes=config,
            source_repositories=dict(self.registration.source_repositories,
                                     nested=self.child_root / 'nested'))
        self.registration.configuration_file.write_bytes(config)
        self.write_binding()
        parked = self.root / 'parked-child'
        self.child_root.rename(parked)
        try:
            code, result = self.invoke()
        finally:
            parked.rename(self.child_root)
        self.assertEqual(3, code)
        states = {p['repository_id']: p['availability'] for p in result['observation']['participants']}
        self.assertEqual('blocked_by_ancestor', states['nested'])

    def test_unavailable_history_is_not_missing_checkout(self):
        self.child_repo.refs[b'HEAD'] = b'0' * 40
        code, result = self.invoke()
        self.assertEqual(3, code)
        self.assertEqual('unavailable_history', result['observation']['participants'][0]['availability'])
        self.assertIsNone(result['selection'])

    def test_bad_authority_is_v2_early_error(self):
        self.registration = replace(self.registration, approved_authority_sha256='0' * 64)
        self.write_binding()
        code, result = self.invoke()
        self.assertEqual((2, 2, 'invalid_authority'), (code, result['schema_version'], result['error']['code']))
        self.assertIsNone(result['observation'])
        self.assertFalse((self.source_root / 'projection').exists())

    def test_failed_switch_retains_previous_pointer_and_complete_observation(self):
        self.assertIn(self.invoke()[0], (0, 1))
        pointer = self.source_root / 'projection/current.json'
        original = pointer.read_bytes()
        with patch('sbc_tools.directory_store.os.replace', side_effect=OSError('private detail')):
            code, result = self.invoke()
        self.assertEqual(3, code)
        self.assertEqual(original, pointer.read_bytes())
        self.assertTrue(result['observation']['complete'])
        self.assertIsNotNone(result['selection'])
        self.assertNotIn('private detail', str(result))

    def test_missing_source_root_inside_child_is_evidence_failure(self):
        config = self.registration.config_bytes.replace(b'source_roots = ["docs/todo"]',
                                                        b'source_roots = ["docs/todo/child"]')
        self.registration = replace(self.registration, config_bytes=config)
        self.registration.configuration_file.write_bytes(config)
        self.write_binding()
        parked = self.root / 'parked-child'
        self.child_root.rename(parked)
        try:
            code, result = self.invoke()
        finally:
            parked.rename(self.child_root)
        self.assertEqual((3, 'evidence_unavailable'), (code, result['error']['code']))
        self.assertFalse(result['observation']['complete'])
