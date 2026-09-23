import unittest
from unittest.mock import patch
from pathlib import Path

from sbc_tools.observations import check_observation
from sbc_tools.projections import build_projection_files
from sbc_tools.validation import BundleValidator
from sbc_tools.corpus import CorpusInput
from test_validation import FixtureProvenance, PROFILE


def observation_samples():
    files, _ = build_projection_files([],registered_prefixes=[],archives={},archive_families={})
    proof = FixtureProvenance(files)
    validator = BundleValidator(source_roots=('specs',),profile_sha256=PROFILE,provenance_verifier=proof)
    args = dict(repository_id='fixture',corpus_records=(),authority_sha256='a'*64,
                candidate_files=files,reference_files=files,validator=validator)
    return args,proof


class ObservationTests(unittest.TestCase):
    def test_equal_is_observation_without_provenance_or_filesystem_calls(self):
        args,proof = observation_samples()
        with patch.object(Path,'read_bytes',side_effect=AssertionError('Filesystem read')):
            result = check_observation(**args)
        self.assertEqual(('working-tree',0,'equal','not_written'),
                         (result['mode'],result['exit_code'],result['result']['comparison'],result['result']['publication']))
        self.assertIsNone(result['selection']['source_commit'])
        self.assertIsNone(result['selection']['projection_commit'])
        self.assertEqual(0,proof.calls)

    def test_invalid_or_missing_reference_is_unavailable_with_findings(self):
        args,_ = observation_samples()
        for reference in (None,{}, {'index/_manifest.json':b'corrupt'}):
            result = check_observation(**dict(args,reference_files=reference,
                                             location_diagnostics=[{'code':'fixture'}]))
            self.assertEqual(3,result['exit_code'])
            self.assertEqual('evidence_unavailable',result['error']['code'])
            self.assertEqual([{'code':'fixture'}],result['findings'])
            self.assertIsNone(result['result'])
            self.assertIsNone(result['selection']['source_commit'])

    def test_drift_preserves_candidate_identity(self):
        args,_ = observation_samples()
        files,diag = build_projection_files([('specs/EX-00.md','example',b'# Changed\n')],
                                            registered_prefixes=[],archives={},archive_families={})
        result = check_observation(**dict(args,candidate_files=files,location_diagnostics=diag))
        self.assertEqual((1,'different'),(result['exit_code'],result['result']['comparison']))
        equal = check_observation(**dict(args,candidate_files=files,reference_files=files,location_diagnostics=diag))
        self.assertEqual(result['selection'],equal['selection'])

    def test_bad_candidate_does_not_produce_result(self):
        args,_ = observation_samples()
        with self.assertRaises(Exception): check_observation(**dict(args,candidate_files={}))

    def test_foreign_corpus_and_invalid_digest_reject(self):
        args,_ = observation_samples()
        for change in ({'authority_sha256':'bad'},
                       {'corpus_records':(CorpusInput('other','a.md','b'*64),)}):
            with self.assertRaises(ValueError): check_observation(**dict(args,**change))
