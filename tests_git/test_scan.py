from contextlib import nullcontext
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import test_admission as fixtures
from test_provenance_inputs import commit_files
from test_provenance_integration import publication_identity, sha
from sbc_tools.cli import CommittedCheckHost, main
from sbc_tools.cli_results import execute_scan
from sbc_tools.provenance import ReferenceUnavailableError
from sbc_tools.store import SQLiteSnapshotStore
from sbc_tools.validation import ValidatedBundle


class ScanTests(unittest.TestCase):
    def setUp(self):
        fixtures.AdmissionTests.setUp(self)
        self.routing = dict(document_families={'docs/todo/spec.md':'example'},archive_families={})

    def commit_output(self):
        files = dict(self.source_files)
        files.update({p.relative_to(self.source_root).as_posix():p.read_bytes()
                      for p in (self.source_root/'projection').rglob('*') if p.is_file()})
        commit = commit_files(self.source_repo,files)
        fixtures.checkout(self.source_repo,self.source_root,commit)
        return commit,files

    def test_scan_commit_check_and_sqlite_validation(self):
        host = CommittedCheckHost(self.verifier,self.routing['document_families'],{})
        out = io.BytesIO()
        code = main(['scan','--config','sbc.toml','--format=json'],
                    load_host=lambda path:nullcontext(host),stdout=out)
        envelope = json.loads(out.getvalue())
        self.assertEqual(1,code)  # Fixture intentionally has source findings.
        self.assertEqual('published',envelope['result']['publication'])
        self.assertIsNone(envelope['selection']['projection_commit'])
        commit,_ = self.commit_output()
        checked = self.verifier.check_source(**self.routing)
        self.assertEqual('equal',checked.comparison)
        self.assertEqual(envelope['selection']['snapshot_id'],checked.candidate.snapshot_id)
        publication = publication_identity(dict(self.publication,source_commit=commit,
            projection_commit=commit,snapshot_id=checked.candidate.snapshot_id))
        validated = self.validator.validate(publication,checked.candidate.files,sha(self.profile))
        self.assertIsInstance(validated,ValidatedBundle)
        with tempfile.TemporaryDirectory() as temp:
            store = SQLiteSnapshotStore(Path(temp)/'store.db',self.validator)
            self.assertEqual(1,store.publish(validated,0,'selected')['generation'])

    def test_failed_switch_preserves_committed_prior_and_reports_findings(self):
        self.verifier.scan_source(**self.routing)
        self.commit_output()
        pointer = self.source_root/'projection/current.json'
        before = pointer.read_bytes()
        with patch('sbc_tools.directory_store.os.replace',side_effect=PermissionError('private path')):
            result = execute_scan(self.verifier,**self.routing)
        self.assertEqual(3,result['exit_code'])
        self.assertTrue(result['findings'])
        self.assertIsNone(result['result'])
        self.assertEqual(before,pointer.read_bytes())

    def test_corrupt_selected_pointer_never_falls_back_to_retained_bundle(self):
        self.verifier.scan_source(**self.routing)
        (self.source_root/'projection/current.json').write_bytes(b'{}\n')
        self.commit_output()
        with self.assertRaises(ReferenceUnavailableError): self.verifier.check_source(**self.routing)

    def test_mixed_layout_rejected_by_check_and_scan(self):
        self.verifier.scan_source(**self.routing)
        flat = self.source_root/'projection/index/_manifest.json'
        flat.parent.mkdir()
        flat.write_bytes(self.bundle['index/_manifest.json'])
        self.commit_output()
        with self.assertRaises(ReferenceUnavailableError): self.verifier.check_source(**self.routing)
        pointer = (self.source_root/'projection/current.json').read_bytes()
        result = execute_scan(self.verifier,**self.routing)
        self.assertEqual(4,result['exit_code'])
        self.assertEqual(pointer,(self.source_root/'projection/current.json').read_bytes())

    def test_retained_bundles_do_not_change_selected_snapshot(self):
        first = self.verifier.scan_source(**self.routing)
        self.commit_output()
        second = self.verifier.scan_source(**self.routing)
        self.commit_output()
        self.assertEqual(first.snapshot_id,second.snapshot_id)
        self.assertEqual(2,len(list((self.source_root/'projection').glob('bundle-*'))))
        self.assertEqual('equal',self.verifier.check_source(**self.routing).comparison)


if __name__ == '__main__': unittest.main()
