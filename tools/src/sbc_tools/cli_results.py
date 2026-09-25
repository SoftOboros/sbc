"""SBCT-01 command envelopes; no executable or host configuration discovery."""
import hashlib
import json

from .canonical import canonical_json
from .git_reader import GitUnavailableError
from .provenance import ReferenceUnavailableError, ScanPublicationError, AuthorityValidationError


_ERRORS = {
    'invalid_invocation': (2, 'Invalid command invocation.'),
    'invalid_configuration': (2, 'Invalid repository configuration.'),
    'invalid_authority': (2, 'Invalid authority manifest.'),
    'evidence_unavailable': (3, 'Required evidence is unavailable.'),
    'io_failure': (3, 'Required input or output could not be accessed.'),
    'internal_failure': (4, 'The operation could not produce a valid result.'),
}


class CommandFailure(Exception):
    """A host classifies its failure without disclosing exception text."""
    def __init__(self, code, *, mounted_observation=False):
        if code not in _ERRORS:
            raise ValueError('Unknown command error code')
        self.code = code
        self.mounted_observation = mounted_observation
        super().__init__(_ERRORS[code][1])


def _findings(candidate):
    if candidate is None:
        return []
    findings = []
    for path, raw in sorted(candidate.files.items()):
        if path.startswith('diagnostics/') and path != 'diagnostics/_manifest.json':
            findings.extend(json.loads(raw)['records'])
    findings.extend(json.loads(candidate.location_diagnostics))
    return findings


def _selection(candidate, projection_commit):
    if candidate is None:
        return None
    admitted = candidate.admission
    return {
        'repository_id': admitted.repository_id,
        'source_commit': admitted.source_commit,
        'projection_commit': projection_commit,
        'corpus_sha256': admitted.provenance.corpus_sha256,
        'authority_manifest_sha256': admitted.provenance.authority_manifest_sha256,
        'snapshot_id': candidate.snapshot_id,
        'dependencies': sorted([
            {'parent_repository_id':p.parent_repository_id, 'parent_commit':p.parent_commit,
             'path':p.parent_relative_path, 'repository_id':p.repository_id, 'child_commit':p.child_commit}
            for p in admitted.checkout.pins], key=lambda p:(p['parent_repository_id'],p['path'])),
    }


def failure_envelope(code, *, command=None, mode=None, candidate=None):
    """Return a safe closed error envelope, preserving available source findings."""
    if command not in (None,'check','scan') or mode not in (None,'committed','working-tree'):
        raise ValueError('Invalid command context')
    if candidate is not None and mode != 'committed':
        raise ValueError('Committed candidate requires committed mode')
    exit_code, message = _ERRORS[code]
    return {'schema_version':1, 'command':command, 'mode':mode, 'status':'error',
            'exit_code':exit_code, 'selection':_selection(candidate,None),
            'findings':_findings(candidate), 'error':{'code':code,'message':message}, 'result':None}


def check_envelope(checked):
    """Complete check result: candidate identities never describe the reference."""
    candidate = checked.candidate
    findings = _findings(candidate)
    exit_code = int(bool(findings or checked.differing_paths))
    return {'schema_version':1, 'command':'check', 'mode':'committed',
            'status':'findings' if exit_code else 'ok', 'exit_code':exit_code,
            'selection':_selection(candidate,checked.projection_commit), 'findings':findings,
            'error':None, 'result':{'publication':'not_written','comparison':checked.comparison,
                'files':[{'path':p,'sha256':hashlib.sha256(b).hexdigest()}
                         for p,b in sorted(candidate.files.items())]}}


def scan_envelope(candidate):
    findings = _findings(candidate)
    return {'schema_version':1, 'command':'scan', 'mode':'committed',
            'status':'findings' if findings else 'ok', 'exit_code':int(bool(findings)),
            'selection':_selection(candidate,None), 'findings':findings, 'error':None,
            'result':{'publication':'published','comparison':'not_applicable',
                'files':[{'path':p,'sha256':hashlib.sha256(b).hexdigest()}
                         for p,b in sorted(candidate.files.items())]}}


def execute_check(verifier, **routing):
    return _execute(verifier,'check',routing)


def execute_scan(verifier, **routing):
    return _execute(verifier,'scan',routing)


def _execute(verifier, command, routing):
    try:
        if command == 'scan':
            return scan_envelope(verifier.scan_source(**routing))
        return check_envelope(verifier.check_source(**routing))
    except ScanPublicationError as exc:
        return failure_envelope(exc.code,command=command,mode='committed',candidate=exc.candidate)
    except ReferenceUnavailableError as exc:
        return failure_envelope('evidence_unavailable',command=command,mode='committed',candidate=exc.candidate)
    except CommandFailure as exc:
        return failure_envelope(exc.code,command=command,mode='committed')
    except AuthorityValidationError:
        return failure_envelope('invalid_authority',command=command,mode='committed')
    except GitUnavailableError:
        return failure_envelope('evidence_unavailable',command=command,mode='committed')
    except OSError:
        return failure_envelope('io_failure',command=command,mode='committed')
    except Exception:
        return failure_envelope('internal_failure',command=command,mode='committed')


def render_envelope(envelope, *, format='text'):
    """Return output bytes; the process wrapper owns stdout/stderr and exit."""
    if format == 'json':
        return canonical_json(envelope)
    if format != 'text':
        raise ValueError('Unsupported output format')
    error = envelope['error']
    detail = error['message'] if error else (
        f"Comparison: {envelope['result']['comparison']}; source findings: {len(envelope['findings'])}.")
    return f"{envelope['command'] or 'command'}: {envelope['status']} (exit {envelope['exit_code']}). {detail}\n".encode('utf-8')
