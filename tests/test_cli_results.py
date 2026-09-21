import hashlib
from dataclasses import replace
import json
from types import SimpleNamespace
import unittest

from sbc_tools.cli_results import (CommandFailure, check_envelope, scan_envelope, execute_check,
                                   failure_envelope, render_envelope)
from sbc_tools.git_reader import GitUnavailableError
from sbc_tools.projections import build_projection_files
from sbc_tools.provenance import AdmittedSource, CheckedProjection, GeneratedProjection, ReferenceUnavailableError
from sbc_tools.validation import VerifiedProvenance
from sbc_tools.mounts import PinnedMount


def candidate(findings=False):
    sources = [('specs/EX-00.md','example',b'# Missing ID\n')] if findings else []
    files, diagnostics = build_projection_files(sources, registered_prefixes=[], archives={},archive_families={})
    admission = AdmittedSource('fixture','1'*40,'2'*64,VerifiedProvenance('3'*64,'4'*64),
                               SimpleNamespace(pins=()))
    return GeneratedProjection(admission,'5'*64,files,json.dumps(diagnostics).encode())


def sample_envelopes():
    quiet, noisy = candidate(), candidate(True)
    return [check_envelope(CheckedProjection(quiet,'6'*40,())),
            check_envelope(CheckedProjection(quiet,'6'*40,('index/example.json',))),
            check_envelope(CheckedProjection(noisy,'6'*40,())),
            failure_envelope('evidence_unavailable',command='check',mode='committed',candidate=noisy),
            *[failure_envelope(code) for code in ('invalid_invocation','invalid_configuration',
                'invalid_authority','evidence_unavailable','io_failure','internal_failure')],
            scan_envelope(quiet), scan_envelope(noisy)]


class CLIResultTests(unittest.TestCase):
    def test_success_drift_and_findings_have_distinct_results(self):
        ok, drift, findings = sample_envelopes()[:3]
        self.assertEqual((0,'ok','equal'),(ok['exit_code'],ok['status'],ok['result']['comparison']))
        self.assertEqual((1,'different',[]),(drift['exit_code'],drift['result']['comparison'],drift['findings']))
        self.assertEqual((1,'equal'),(findings['exit_code'],findings['result']['comparison']))
        self.assertTrue(findings['findings'])

    def test_candidate_hashes_and_reference_commit_not_confused(self):
        value = candidate(True)
        envelope = check_envelope(CheckedProjection(value,'6'*40,('locations/other.json',)))
        self.assertEqual('6'*40,envelope['selection']['projection_commit'])
        self.assertEqual(value.snapshot_id,envelope['selection']['snapshot_id'])
        self.assertEqual([{'path':p,'sha256':hashlib.sha256(b).hexdigest()}
                          for p,b in sorted(value.files.items())],envelope['result']['files'])
        self.assertEqual('not_written',envelope['result']['publication'])

    def test_unavailable_overrides_findings_and_preserves_them(self):
        value = candidate(True)
        def fail(**kwargs): raise ReferenceUnavailableError(value)
        envelope = execute_check(SimpleNamespace(check_source=fail),document_families={},archive_families={})
        self.assertEqual((3,'error'),(envelope['exit_code'],envelope['status']))
        self.assertTrue(envelope['findings'])
        self.assertIsNone(envelope['result'])
        self.assertIsNone(envelope['selection']['projection_commit'])

    def test_failures_use_safe_closed_messages_and_exit_codes(self):
        errors = [(OSError('secret path'),3,'io_failure'),
                  (GitUnavailableError('secret ref'),3,'evidence_unavailable'),
                  (RuntimeError('secret token'),4,'internal_failure'),
                  (CommandFailure('invalid_authority'),2,'invalid_authority')]
        for error, code, kind in errors:
            def fail(**kwargs): raise error
            result = execute_check(SimpleNamespace(check_source=fail),document_families={},archive_families={})
            self.assertEqual(code,result['exit_code'])
            self.assertEqual(kind,result['error']['code'])
            self.assertNotIn(b'secret',render_envelope(result,format='json'))

    def test_json_is_one_utf8_object_with_final_newline(self):
        for envelope in sample_envelopes():
            raw = render_envelope(envelope,format='json')
            self.assertTrue(raw.endswith(b'\n'))
            self.assertEqual(1,raw.count(b'\n'))
            self.assertEqual(envelope,json.loads(raw))
            self.assertTrue(render_envelope(envelope).endswith(b'\n'))

    def test_invocation_error_has_no_selected_context(self):
        result = failure_envelope('invalid_invocation')
        self.assertEqual(2,result['exit_code'])
        for key in ('command','mode','selection','result'): self.assertIsNone(result[key])
        with self.assertRaises(ValueError): CommandFailure('new_code')
        with self.assertRaises(ValueError): render_envelope(result,format='yaml')

    def test_findings_are_fresh_and_committed_mode_is_enforced(self):
        value = candidate(True)
        checked = CheckedProjection(value,'6'*40,())
        first = check_envelope(checked)
        first['findings'].clear()
        self.assertTrue(check_envelope(checked)['findings'])
        with self.assertRaises(ValueError):
            failure_envelope('io_failure',mode='working-tree',candidate=value)

    def test_nested_dependency_uses_immediate_parent_coordinates(self):
        value = candidate()
        pin = PinnedMount('vendor/inner','leaf','child','7'*40,'inner','8'*40)
        value = replace(value,admission=replace(value.admission,checkout=SimpleNamespace(pins=(pin,))))
        result = check_envelope(CheckedProjection(value,'6'*40,()))
        self.assertEqual([{'parent_repository_id':'child','parent_commit':'7'*40,
                           'path':'inner','repository_id':'leaf','child_commit':'8'*40}],
                         result['selection']['dependencies'])


if __name__ == '__main__': unittest.main()
