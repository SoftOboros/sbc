from dataclasses import replace
import unittest
from unittest.mock import patch

import test_console_host as fixtures
from test_provenance_integration import sha


class WorkingCLITests(unittest.TestCase):
    def setUp(self):
        fixtures.ConsoleHostTests.setUp(self)
        self.config = self.config.replace(b'mode = "committed"',b'mode = "working-tree"')
        self.registration = replace(self.registration,config_bytes=self.config)
        self.registration.configuration_file.write_bytes(self.config)
        self.source_files['sbc.toml'] = self.config
        self.binding['config_sha256'] = sha(self.config)
        self.write()

    write = fixtures.ConsoleHostTests.write
    invoke = fixtures.ConsoleHostTests.invoke
    commit_output = fixtures.ConsoleHostTests.commit_output
    observed_files = fixtures.ConsoleHostTests.observed_files

    def assert_observation(self,result):
        self.assertEqual('working-tree',result['mode'])
        self.assertIsNone(result['selection']['source_commit'])
        self.assertIsNone(result['selection']['projection_commit'])

    def test_scan_commit_check_and_dirty_drift_are_observations(self):
        before = self.observed_files()
        code,result = self.invoke('scan')
        self.assertIn(code,(0,1))
        self.assert_observation(result)
        self.assertEqual('published',result['result']['publication'])
        self.assertEqual(before,{p:b for p,b in self.observed_files().items() if not p.startswith('projection/')})
        self.commit_output()
        code,result = self.invoke()
        self.assertIn(code,(0,1))
        self.assertEqual('equal',result['result']['comparison'])
        self.assert_observation(result)
        (self.source_root/'docs/todo/spec.md').write_bytes(b'# Change\n\n**Document ID:** EX-00\n')
        before = self.observed_files()
        code,result = self.invoke()
        self.assertEqual((1,'different'),(code,result['result']['comparison']))
        self.assert_observation(result)
        self.assertEqual(before,self.observed_files())

    def test_missing_reference_retains_observation_findings(self):
        code,result = self.invoke()
        self.assertEqual((3,'evidence_unavailable'),(code,result['error']['code']))
        self.assert_observation(result)
        self.assertIsNone(result['result'])
        self.assertFalse((self.source_root/'projection').exists())

    def test_wrong_authority_pin_rejects_without_publication(self):
        self.binding['approved_authority_sha256'] = '0'*64
        self.write()
        code,result = self.invoke('scan')
        self.assertEqual((2,'invalid_authority'),(code,result['error']['code']))
        self.assertEqual('working-tree',result['mode'])
        self.assertFalse((self.source_root/'projection').exists())

    def test_failed_switch_preserves_previous_selection(self):
        self.assertIn(self.invoke('scan')[0],(0,1))
        pointer = self.source_root/'projection/current.json'
        before = pointer.read_bytes()
        with patch('sbc_tools.directory_store.os.replace',side_effect=OSError('private detail')):
            code,result = self.invoke('scan')
        self.assertEqual((3,'io_failure'),(code,result['error']['code']))
        self.assert_observation(result)
        self.assertEqual(before,pointer.read_bytes())
        self.assertNotIn('private detail',str(result))

    def test_scan_capability_is_enforced(self):
        self.config = self.config.replace(b'["scan", "check"]',b'["check"]')
        self.registration.configuration_file.write_bytes(self.config)
        self.binding['config_sha256'] = sha(self.config)
        self.write()
        code,result = self.invoke('scan')
        self.assertEqual((2,'invalid_configuration'),(code,result['error']['code']))
        self.assertFalse((self.source_root/'projection').exists())
