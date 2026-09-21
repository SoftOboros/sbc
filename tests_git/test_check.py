import unittest
from contextlib import nullcontext
import io
import json
from unittest.mock import patch

import test_admission as fixtures
from test_provenance_inputs import commit_files
from sbc_tools.provenance import ReferenceUnavailableError
from sbc_tools.cli_results import execute_check
from sbc_tools.cli import CommittedCheckHost, main


class CommittedCheckTests(unittest.TestCase):
    def setUp(self):
        fixtures.AdmissionTests.setUp(self)
        self.routing = dict(document_families={'docs/todo/spec.md':'example'}, archive_families={})
        self.generated = self.verifier.generate_source(**self.routing)

    def select(self, bundle):
        files = dict(self.source_files, **{'projection/'+p:b for p,b in bundle.items()})
        commit = commit_files(self.source_repo,files)
        fixtures.checkout(self.source_repo,self.source_root,commit)
        return commit

    def test_equal_reference_keeps_candidate_identity_and_writes_nothing(self):
        commit = self.select(self.generated.files)
        before = {p.relative_to(self.source_root).as_posix():p.read_bytes()
                  for p in self.source_root.rglob('*') if p.is_file()}
        result = self.verifier.check_source(**self.routing)
        self.assertEqual('equal',result.comparison)
        self.assertEqual(commit,result.projection_commit)
        self.assertEqual(self.generated.snapshot_id,result.candidate.snapshot_id)
        self.assertEqual((),result.differing_paths)
        after = {p.relative_to(self.source_root).as_posix():p.read_bytes()
                 for p in self.source_root.rglob('*') if p.is_file()}
        self.assertEqual(before,after)
        # Equality must retain diagnostics from the deliberately unidentified source.
        self.assertIn(b'document_id_missing',result.candidate.files['diagnostics/example.json'])
        envelope = execute_check(self.verifier,**self.routing)
        self.assertEqual((1,'equal'),(envelope['exit_code'],envelope['result']['comparison']))
        self.assertEqual(result.candidate.snapshot_id,envelope['selection']['snapshot_id'])

    def test_complete_other_bundle_is_drift_over_full_path_union(self):
        commit = self.select(self.bundle)
        result = self.verifier.check_source(**self.routing)
        expected = tuple(sorted(p for p in set(self.bundle)|set(self.generated.files)
                                if self.bundle.get(p) != self.generated.files.get(p)))
        self.assertEqual('different',result.comparison)
        self.assertEqual(expected,result.differing_paths)
        self.assertEqual(commit,result.projection_commit)
        self.assertEqual(self.generated.snapshot_id,result.candidate.snapshot_id)
        self.assertNotEqual(self.bundle,result.candidate.files)

    def test_missing_reference_is_unavailable_with_candidate_preserved(self):
        with self.assertRaises(ReferenceUnavailableError) as caught:
            self.verifier.check_source(**self.routing)
        self.assertEqual(self.generated.files,caught.exception.candidate.files)
        self.assertEqual('Committed projection reference is unavailable.',str(caught.exception))
        envelope = execute_check(self.verifier,**self.routing)
        self.assertEqual(3,envelope['exit_code'])
        self.assertTrue(envelope['findings'])
        self.assertIsNone(envelope['result'])

    def test_corrupt_reference_is_unavailable_not_drift(self):
        files = dict(self.generated.files)
        files['index/_manifest.json'] = b'private malformed content'
        self.select(files)
        with self.assertRaises(ReferenceUnavailableError) as caught:
            self.verifier.check_source(**self.routing)
        self.assertNotIn('private',str(caught.exception))

    def test_incomplete_reference_is_unavailable_not_missing_file_drift(self):
        files = dict(self.generated.files)
        del files['diagnostics/example.json']
        self.select(files)
        with self.assertRaises(ReferenceUnavailableError):
            self.verifier.check_source(**self.routing)

    def test_reference_uses_selected_commit_despite_ref_change(self):
        selected = self.select(self.generated.files)
        original = self.verifier.generate_source
        def generate_and_move(**kwargs):
            candidate = original(**kwargs)
            other = commit_files(self.source_repo,{'unrelated':b'other'})
            self.source_repo.refs[b'refs/heads/main'] = other.encode()
            return candidate
        with patch.object(self.verifier,'generate_source',side_effect=generate_and_move):
            result = self.verifier.check_source(**self.routing)
        self.assertEqual(selected,result.projection_commit)
        self.assertEqual('equal',result.comparison)

    def test_cli_dispatch_over_real_committed_comparison(self):
        self.select(self.generated.files)
        host = CommittedCheckHost(self.verifier,self.routing['document_families'],{})
        output = io.BytesIO()
        def loader(path):
            self.assertEqual('sbc.toml',path)
            return nullcontext(host)
        code = main(['check','--config','sbc.toml','--format=json'],load_host=loader,stdout=output)
        result = json.loads(output.getvalue())
        self.assertEqual(1,code)
        self.assertEqual('equal',result['result']['comparison'])
        self.assertEqual(self.generated.snapshot_id,result['selection']['snapshot_id'])


if __name__ == '__main__': unittest.main()
