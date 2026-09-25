from dataclasses import replace
import json
import unittest
from unittest.mock import patch

from dulwich.repo import Repo
from sbc_tools.git_reader import GitCommitReader
from sbc_tools.mounted_working_tree import generate_mounted_working_tree, AggregateObservationUnavailable
from sbc_tools.observations import check_observation
from sbc_tools.provenance import AuthorityValidationError
from sbc_tools.validation import BundleValidator
from sbc_tools.working_tree import _RejectCommittedProof
import test_host as fixtures
from test_admission import checkout
from test_provenance_inputs import commit_files


class MountedWorkingGenerationTests(unittest.TestCase):
    def setUp(self):
        fixtures.HostLoaderTests.setUp(self)
        self.child_root = self.source_root / 'docs/todo/child'
        self.child_root.mkdir()
        self.child_repo = Repo.init(str(self.child_root))
        self.addCleanup(self.child_repo.close)
        self.child_reader = GitCommitReader(str(self.child_root))
        self.addCleanup(self.child_reader.close)
        child = commit_files(self.child_repo, {'note.md': b'# Child document\n'})
        checkout(self.child_repo, self.child_root, child)
        config = self.registration.config_bytes.replace(b'mode = "committed"', b'mode = "working-tree"')
        config = config.replace(b'submodules = []',
            b'submodules = [{path = "docs/todo/child", repository_id = "child"}]')
        files = dict(self.source_files, **{'sbc.toml': config})
        source = commit_files(self.source_repo, files, {'docs/todo/child': child})
        checkout(self.source_repo, self.source_root, source)
        self.registration = replace(self.registration, config_bytes=config,
            source_repositories={'source': self.source_root, 'child': self.child_root},
            document_families=dict(self.registration.document_families,
                                  **{'docs/todo/child/note.md': 'child'}))

    def generate(self, **overrides):
        args = dict(source_readers={'source': self.reader, 'child': self.child_reader},
                    authority_readers={'fixture': self.authority_reader})
        args.update(overrides)
        return generate_mounted_working_tree(self.registration, **args)

    def test_dirty_child_generates_v2_comparison_without_commit_claims_or_publication(self):
        (self.child_root / 'note.md').write_bytes(b'# Observed child\n')
        result = self.generate()
        self.assertEqual(b'# Observed child\n', result.corpus.files['docs/todo/child/note.md'])
        self.assertIn('child', {r.repository_id for r in result.corpus.records})
        validator = BundleValidator(source_roots=('docs/todo',),
            profile_sha256=self.registration.profile_sha256, provenance_verifier=_RejectCommittedProof())
        checked = check_observation(repository_id='source', corpus_records=result.corpus.records,
            authority_sha256=result.authority_sha256, candidate_files=result.files,
            reference_files=result.files, validator=validator,
            observation_set=json.loads(result.corpus.observation))
        self.assertEqual(2, checked['schema_version'])
        self.assertEqual('equal', checked['result']['comparison'])
        self.assertIsNone(checked['selection']['source_commit'])
        self.assertIsNone(checked['selection']['projection_commit'])
        self.assertEqual([], checked['selection']['dependencies'])
        self.assertFalse((self.source_root / 'projection').exists())
        self.assertFalse(hasattr(result, 'admission'))

    def test_wrong_authority_pin_prevents_producer(self):
        self.registration = replace(self.registration, approved_authority_sha256='0' * 64)
        with patch('sbc_tools.projections.build_configured_projection', side_effect=AssertionError('Producer ran')):
            with self.assertRaises(AuthorityValidationError): self.generate()

    def test_changed_config_profile_and_patch_prevent_producer(self):
        for name in ('sbc.toml', 'profile.json', 'support.patch'):
            path = self.source_root / name
            original = path.read_bytes()
            try:
                path.write_bytes(original + b'changed')
                with self.subTest(name=name), patch('sbc_tools.projections.build_configured_projection',
                        side_effect=AssertionError('Producer ran')):
                    with self.assertRaises(ValueError): self.generate()
            finally:
                path.write_bytes(original)

    def test_unavailable_child_prevents_producer(self):
        with patch('sbc_tools.projections.build_configured_projection', side_effect=AssertionError('Producer ran')):
            with self.assertRaises(AggregateObservationUnavailable):
                self.generate(source_readers={'source': self.reader})

    def test_registered_mount_location_cannot_be_replaced_by_reader(self):
        self.registration = replace(self.registration,
            source_repositories={'source': self.source_root, 'child': self.authority_reader.checkout_path})
        with self.assertRaisesRegex(ValueError, 'Registered child location'):
            self.generate()
