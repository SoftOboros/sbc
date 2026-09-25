"""Data-only working-tree comparison; no committed provenance or publication.

A trusted host supplies captured corpus records, generated candidate bytes and
its semantic validator. This module neither captures a checkout nor approves an
authority digest. It is deliberately separate from committed admission objects.
"""
import hashlib
import json
import re
import unicodedata

from ._sidx_validation import IngestError
from .canonical import canonical_json
from .corpus import corpus_digest
from .identity import copy_files
from .cli_results import failure_envelope


def check_observation(*, repository_id, corpus_records, authority_sha256,
                      candidate_files, reference_files, validator,
                      location_diagnostics=(), observation_set=None):
    """Validate and compare supplied bytes with null committed identities.

    Mounted observations require a complete validated observation set whose
    per-participant corpus hashes match the supplied records. Without that set,
    only single-repository records are accepted. Hosts must enforce authority, complete
    capture and scope before calling; passing a digest never establishes approval.
    None or invalid reference bytes mean unavailable, never ordinary drift.
    Candidate validation failures propagate to the host for safe classification.
    """
    if (not isinstance(repository_id,str) or not repository_id
            or unicodedata.normalize('NFC',repository_id) != repository_id):
        raise ValueError('Invalid repository identity')
    if not isinstance(authority_sha256,str) or not re.fullmatch('[0-9a-f]{64}',authority_sha256):
        raise ValueError('Invalid authority digest')
    records = tuple(corpus_records)
    observation = None
    if observation_set is None:
        if any(r.repository_id != repository_id for r in records):
            raise ValueError('Single-repository observation required')
    else:
        from .observation_sets import observation_set_bytes
        observation = json.loads(observation_set_bytes(observation_set))
        if not observation['complete'] or observation['root_repository_id'] != repository_id:
            raise ValueError('Complete observation for the selected root required')
        participants = {p['repository_id']: p for p in observation['participants']}
        if any(r.repository_id not in participants for r in records):
            raise ValueError('Unobserved corpus owner')
        for owner, participant in participants.items():
            if corpus_digest(r for r in records if r.repository_id == owner) != participant['corpus_sha256']:
                raise ValueError('Participant corpus hash mismatch')

    def envelope(result):
        if observation is not None:
            result.update(schema_version=2, observation=observation)
        return result
    # Copy inputs before validation; no caller mutation can alter the result.
    files = validator.validate_files(copy_files(candidate_files))
    corpus = corpus_digest(records)
    hashes = [{'path':p,'sha256':hashlib.sha256(b).hexdigest()} for p,b in sorted(files.items())]
    snapshot = hashlib.sha256(canonical_json(dict(authority_manifest_sha256=authority_sha256,
                                                corpus_sha256=corpus,files=hashes))).hexdigest()
    findings = []
    for path,raw in sorted(files.items()):
        if path.startswith('diagnostics/') and path != 'diagnostics/_manifest.json':
            findings.extend(json.loads(raw)['records'])
    findings.extend(json.loads(canonical_json(list(location_diagnostics))))
    selection = dict(repository_id=repository_id,source_commit=None,projection_commit=None,
                     corpus_sha256=corpus,authority_manifest_sha256=authority_sha256,
                     snapshot_id=snapshot,dependencies=[])
    try:
        if reference_files is None:
            raise ValueError('Missing reference')
        reference = validator.validate_files(copy_files(reference_files))
    except (ValueError,KeyError,TypeError,IngestError):
        result = failure_envelope('evidence_unavailable',command='check',mode='working-tree')
        result.update(selection=selection,findings=findings)
        return envelope(result)
    different = dict(files) != dict(reference)
    code = int(bool(different or findings))
    return envelope(dict(schema_version=1,command='check',mode='working-tree',
                status='findings' if code else 'ok',exit_code=code,selection=selection,
                findings=findings,error=None,result=dict(publication='not_written',
                    comparison='different' if different else 'equal',files=hashes)))
