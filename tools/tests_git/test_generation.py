import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import test_admission as fixtures
from test_provenance_inputs import commit_files
from test_provenance_integration import publication_identity, sha
from sbc_tools.store import SQLiteSnapshotStore
from sbc_tools.validation import ValidatedBundle
from sbc_tools.provenance import CommittedProvenanceVerifier


class GenerationTests(unittest.TestCase):
    def setUp(self):
        fixtures.AdmissionTests.setUp(self)

    def generate(self):
        return self.verifier.generate_source(document_families={'docs/todo/spec.md':'example'}, archive_families={})

    def test_generation_then_committed_validation_and_store_publication(self):
        result = self.generate()
        with self.assertRaises(TypeError): result.files['extra'] = b'bad'
        projected = dict(self.source_files, **{'projection/'+p:b for p,b in result.files.items()})
        commit = commit_files(self.source_repo, projected)
        publication = publication_identity(dict(self.publication,
            source_commit=result.admission.source_commit, projection_commit=commit, snapshot_id=result.snapshot_id))
        validated = self.validator.validate(publication,result.files,sha(self.profile))
        self.assertIsInstance(validated,ValidatedBundle)
        with tempfile.TemporaryDirectory() as temp:
            store = SQLiteSnapshotStore(Path(temp)/'store.db',self.validator)
            self.assertEqual(1,store.publish(validated,0,'generated')['generation'])
            self.assertEqual(result.files['locations/_manifest.json'],
                             store.open_view(publication).projection_bytes('locations/_manifest.json'))

    def test_incomplete_routing_and_dirty_admission_rejected(self):
        with self.assertRaises(ValueError):
            self.verifier.generate_source(document_families={},archive_families={})
        (self.source_root/'docs/todo/spec.md').write_bytes(b'dirty')
        with self.assertRaises(ValueError): self.generate()

    def test_changes_after_admission_do_not_change_selected_bytes(self):
        expected = self.generate()
        original = self.verifier.admit_source
        def admit_then_edit():
            admitted = original()
            (self.source_root/'docs/todo/spec.md').write_bytes(b'# Changed after admission\n')
            self.source_repo.refs[b'refs/heads/main'] = commit_files(self.source_repo,{'different':b'new'}).encode()
            return admitted
        with patch.object(self.verifier,'admit_source',side_effect=admit_then_edit):
            result = self.generate()
        self.assertEqual(expected.snapshot_id,result.snapshot_id)
        self.assertEqual(expected.files,result.files)

    def test_semantically_invalid_generated_files_never_become_result(self):
        with patch('sbc_tools.projections.build_projection_files',return_value=({'index/_manifest.json':b'{}'},[])):
            with self.assertRaises(Exception): self.generate()

    def test_prefixes_loaded_from_committed_registry_and_full_wire_matches(self):
        fixture_path = Path(__file__).resolve().parents[1]/'tests/fixtures'
        stable = next(c for c in json.loads((fixture_path/'producer-source-vectors.json').read_bytes())['cases']
                      if c['name'] == 'stable')
        config = self.config.replace(b'registry_paths = []',
                                     b'registry_paths = ["docs/spec-index/PREFIX-REGISTRY.md"]')
        files = {p:b for p,b in self.source_files.items() if p != 'docs/todo/spec.md'}
        files.update({p:t.encode() for p,t in stable['inputs'].items()})
        files['sbc.toml'] = config
        # Remove only the superseded fixture source before creating its clean checkout.
        (self.source_root/'docs/todo/spec.md').unlink()
        commit = commit_files(self.source_repo,files)
        fixtures.checkout(self.source_repo,self.source_root,commit)
        verifier = CommittedProvenanceVerifier(repository_id='source',reader=self.reader,
            config_path='sbc.toml',config_bytes=config,tracked_branch='main',profile_path='profile.json',
            profile_sha256=sha(self.profile),patch_path='support.patch',
            approved_authority_sha256=sha(self.authority_bytes),
            approved_support_sha256={r:sha((r+' updated\n').encode()) for r in ('AGENTS.md','CLAUDE.md','README.md')},
            authority_readers={'fixture':self.authority_reader})
        generated = verifier.generate_source(document_families={'docs/todo/vectors/VECT-00.md':'vectors'},
                                             archive_families={})
        expected = next(c['files'] for c in json.loads((fixture_path/'projection-wire-vectors.json').read_bytes())['cases']
                        if c['name'] == 'stable')
        self.assertEqual({p:t.encode() for p,t in expected.items()},generated.files)


class MountedGenerationTests(unittest.TestCase):
    def setUp(self):
        fixtures.MountedAdmissionTests.setUp(self)

    def test_child_documents_generated_from_parent_pinned_bytes(self):
        result = self.verifier.generate_source(document_families={
            'docs/todo/spec.md':'example','docs/todo/vendor/note.md':'child'},archive_families={})
        manifest = json.loads(result.files['locations/_manifest.json'])
        self.assertEqual(2,manifest['coverage_counts']['active_documents_seen'])
        self.assertEqual(self.child_commit,result.admission.checkout.pins[0].child_commit)
        with self.assertRaises(ValueError):
            self.verifier.generate_source(document_families={'docs/todo/spec.md':'example'},archive_families={})


if __name__ == '__main__': unittest.main()
