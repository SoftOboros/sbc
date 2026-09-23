from dataclasses import replace
import unittest
from unittest.mock import patch

import test_host as fixtures
from sbc_tools.working_tree import generate_working_tree, _RejectCommittedProof
from sbc_tools.provenance import AuthorityValidationError


class WorkingGenerationTests(unittest.TestCase):
    def setUp(self):
        fixtures.HostLoaderTests.setUp(self)
        config = self.registration.config_bytes.replace(b'mode = "committed"',b'mode = "working-tree"')
        self.registration = replace(self.registration,config_bytes=config)
        self.registration.configuration_file.write_bytes(config)

    def generate(self):
        return generate_working_tree(self.registration,authority_readers={'fixture':self.authority_reader})

    def test_dirty_source_generates_immutable_observation_without_commit_claim(self):
        note = self.source_root/'docs/todo/spec.md'
        note.write_bytes(b'# Observed dirty source\n')
        observed = self.generate()
        self.assertEqual(b'# Observed dirty source\n',observed.corpus.files['docs/todo/spec.md'])
        note.write_bytes(b'# Later change\n')
        self.assertEqual(b'# Observed dirty source\n',observed.corpus.files['docs/todo/spec.md'])
        self.assertNotEqual(observed.corpus.records,self.generate().corpus.records)
        self.assertFalse(hasattr(observed,'admission'))
        self.assertFalse(hasattr(observed.corpus,'source_commit'))
        self.assertFalse((self.source_root/'projection').exists())
        with self.assertRaises(TypeError): observed.files['x'] = b'x'

    def test_authority_pin_not_inferred_from_working_tree(self):
        self.registration = replace(self.registration,approved_authority_sha256='0'*64)
        with patch('sbc_tools.projections.build_configured_projection',side_effect=AssertionError('Producer ran')):
            with self.assertRaises(AuthorityValidationError): self.generate()

    def test_config_profile_and_patch_tampering_reject(self):
        for name in ('sbc.toml','profile.json','support.patch'):
            path = self.source_root/name
            original = path.read_bytes()
            try:
                path.write_bytes(original+b'changed')
                with self.subTest(name=name),self.assertRaises(ValueError): self.generate()
            finally: path.write_bytes(original)

    def test_observation_verifier_cannot_validate_committed_publication(self):
        with self.assertRaisesRegex(ValueError,'cannot verify committed'):
            _RejectCommittedProof().verify({}, {}, 'a'*64)
