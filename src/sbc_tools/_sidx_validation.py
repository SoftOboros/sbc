"""Extracted SIDX validators; no ORM, settings or publication writes.
Approved source Git blob: d77b462102367d143a4d1d204df3df7dd586d193.
Mechanical changes: instance-qualified helpers and explicit corpus roots.
Reproduce with tools/extract_validation.py.
"""
from __future__ import annotations
import collections
import hashlib
import json
import pathlib
import re
import unicodedata
import urllib.parse
SUPPORTED_SCHEMA_VERSIONS = {2, 3}
SUPPORTED_LOCATION_SCHEMA_VERSIONS = {1}
SUPPORTED_DIAGNOSTIC_SCHEMA_VERSIONS = {1, 2, 3}
CURRENT_INGEST_PROFILE = (3, 1, 3)
MANIFEST = '_manifest.json'
_COMMIT = re.compile('[0-9a-f]{40}')
_LOCATION_COMMIT = re.compile('[0-9a-f]{7,40}')
_SHA256 = re.compile('[0-9a-f]{64}')
_MALFORMED_TOKEN = re.compile('(?:PCDN|EOQ)-[A-Z0-9][A-Z0-9-]{0,95}', re.ASCII)
_MAX_LINE = 2 ** 31 - 1
_MAX_DIAGNOSTIC_RECORDS = 100000
_MAX_DIAGNOSTIC_LOCATORS = 10000
_MAX_DIAGNOSTIC_MANIFEST_BYTES = 1024 * 1024
_MAX_DIAGNOSTIC_FAMILY_BYTES = 16 * 1024 * 1024
_MAX_DIAGNOSTIC_PROJECTION_BYTES = 64 * 1024 * 1024
DIAGNOSTIC_V1_CODES = ('document_id_missing', 'invalid_document_lifecycle', 'open_question_definition_duplicate', 'malformed_open_question_handle', 'errata_missing_index_row', 'errata_index_without_body', 'errata_duplicate_index_row', 'errata_duplicate_body', 'errata_unsupported_status', 'errata_status_disagreement')
DIAGNOSTIC_C6_CODES = DIAGNOSTIC_V1_CODES + ('dependency_source_unresolved', 'dependency_target_unresolved', 'dependency_kind_unresolved', 'change_kind_unresolved', 'touches_unresolved', 'retirement_supersedes_missing')
DIAGNOSTIC_V2_CODES = DIAGNOSTIC_C6_CODES
DIAGNOSTIC_V3_CODES = DIAGNOSTIC_C6_CODES
ERRATA_DIAGNOSTIC_CODES = DIAGNOSTIC_V1_CODES[4:]
ERRATA_STATUSES = {'resolved', 'diagnosed', 'open', 'deviation-pending-ratification'}
DOCUMENT_LIFECYCLE_STATES = {'draft', 'ratified', 'executing', 'execution_complete', 'handoff_eligible', 'handed_off', 'superseded', 'abandoned', 'unknown'}
PROVENANCE_VALUES = {'declared', 'inferred'}
OBJECT_KINDS = {'document', 'section', 'invariant', 'term', 'gate', 'nongoal', 'enum_value', 'authority_row', 'errata', 'open_question', 'amendment', 'rationale'}
RETIRED_DEPENDENCY_EDGE_TYPES = {'cites', 'refines', 'verifies', 'evidences', 'blocks', 'same-as'}
RETIRED_DEPENDENCY_CHANGE_KINDS = {'semantic', 'scope', 'retirement'}
CHANGE_KINDS = {'editorial', 'clarification', 'semantic', 'scope', 'retirement'}
TOUCHES_REQUIRED_CHANGE_KINDS = {'clarification', 'semantic', 'scope', 'retirement'}
LOCATION_KINDS = {'repository', 'archive', 'memalpha', 'pointer'}
LOCATION_COVERAGE_FIELDS = {'active_documents_seen', 'active_documents_identified', 'active_documents_missing_id', 'duplicate_document_ids', 'declaration_errors', 'archives_scanned', 'archive_markdown_members', 'archive_members_identified', 'archive_members_missing_id'}
_LOCATION_URI = re.compile('[A-Za-z][A-Za-z0-9+.-]*://', re.ASCII)
_LOCATION_ABSOLUTE = re.compile('(?:/|[A-Za-z]:[\\\\/]|\\\\\\\\)', re.ASCII)
_LOCATION_SIGNED_QUERY = re.compile('[?&](?:x-amz-[^=]*signature|x-goog-[^=]*signature|signature|sig|token|access_token)=', re.IGNORECASE)
_LOCATION_CREDENTIAL = re.compile('(?:(?:^|[^A-Za-z0-9])(?:(?:x[-_])?(?:authorization|proxy[-_]?authorization|cookie|set[-_]?cookie|api(?:[-_]?key)?|token|access(?:[-_]?(?:token|key(?:[-_]?id)?))?|refresh(?:[-_]?token)?|session(?:[-_]?(?:token|id))?|auth(?:[-_]?token)?|credential(?:s)?|secret|password|passwd|private(?:[-_]?(?:key|token|handle))?|upload|signature|sig)|aws[-_]?access[-_]?key[-_]?id|aws[-_]?secret[-_]?access[-_]?key)\\s*[=:]|(?:^|[^A-Za-z0-9])bearer(?:\\s+|[=:])|\\b(?:AKIA|ASIA)[0-9A-Z]{16}\\b)', re.IGNORECASE)
_LOCATION_PRIVATE_HANDLE = re.compile('(?:private[-_ ]?(?:upload[-_ ]?)?handle|upload[-_ ]?handle)\\s*[:=]', re.IGNORECASE)
_LOCATION_PRIVATE_KEY = re.compile('-----begin (?:[a-z0-9][a-z0-9 -]* )?private key-----', re.IGNORECASE)
_LOCATION_ENVIRONMENT = re.compile('(?:\\$(?:[A-Za-z_][A-Za-z0-9_]*|\\{[A-Za-z_][A-Za-z0-9_]*\\})|%[A-Za-z_][A-Za-z0-9_]*%)', re.ASCII)
_LOCATION_HOME = re.compile('~(?:[A-Za-z0-9._-]+)?(?:[\\\\/]|$)', re.ASCII)
_DOCUMENT_ID = re.compile('[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+', re.ASCII)
_INVARIANT_ID = re.compile('INV-([A-Z]{2,8})-([1-9][0-9]*)', re.ASCII)
_PCDN_ID = re.compile('PCDN-(?:[A-Z0-9]+-)+[0-9]{3}', re.ASCII)
_FAMILY_KEY = '[A-Za-z][A-Za-z0-9-]{0,63}'
_EOQ_ID = re.compile(f'({_FAMILY_KEY}):EOQ-[0-9]{{3}}-ERRATA-[0-9]{{3}}', re.ASCII)
_ERRATA_ID = re.compile(f'({_FAMILY_KEY}):ERRATA-[0-9]{{3}}', re.ASCII)
_TERM_ID = re.compile(f'({_FAMILY_KEY}):TERM-(?:00[1-9]|0[1-9][0-9]|[1-9][0-9]{{2}})', re.ASCII)
_GATE_ID = re.compile(f'({_FAMILY_KEY}):GATE-(?:00[1-9]|0[1-9][0-9]|[1-9][0-9]{{2}})', re.ASCII)
_NONGOAL_ID = re.compile(f'({_FAMILY_KEY}):NONGOAL-(?:00[1-9]|0[1-9][0-9]|[1-9][0-9]{{2}})', re.ASCII)
_SECTION_ID = re.compile(f'({_FAMILY_KEY}):SECTION-(?:00[1-9]|0[1-9][0-9]|[1-9][0-9]{{2}})', re.ASCII)
_SEMVER = '(?:0|[1-9][0-9]*)\\.(?:0|[1-9][0-9]*)\\.(?:0|[1-9][0-9]*)'
_AMENDMENT_ID = re.compile(f'([A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+)#amendment:({_SEMVER})', re.ASCII)
_RATIONALE_ID = re.compile(f'([A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+)#amendment:({_SEMVER})#rationale', re.ASCII)
SEMANTIC_FINGERPRINT_VERSION = 1
SEMANTIC_FINGERPRINT_DESCRIPTOR = {'base_fields': ['kind', 'text'], 'excluded_kinds': ['amendment', 'rationale'], 'per_kind': {'authority_row': [], 'document': ['lifecycle_state'], 'enum_value': [], 'errata': [], 'gate': ['checked'], 'invariant': ['title'], 'nongoal': [], 'open_question': ['resolution'], 'term': ['term', 'relationship']}, 'semantic_attrs_common': ['normative', 'status'], 'version': 1}
REGISTERED_EDGE_TYPES = {'defines', 'cites', 'refines', 'verifies', 'evidences', 'amends', 'supersedes', 'blocks', 'motivates', 'same-as', 'homonym-of'}

class IngestError(RuntimeError):
    """A committed projection cannot be loaded without guessing."""

def _validate_nfc(value, label: str) -> None:
    """Reject implicit Unicode repair and values JCS cannot serialize safely."""
    if isinstance(value, str):
        try:
            value.encode('utf-8')
        except UnicodeEncodeError as exc:
            raise IngestError(f'{label} contains a lone surrogate') from exc
        if unicodedata.normalize('NFC', value) != value:
            raise IngestError(f'{label} contains a non-NFC string')
    elif isinstance(value, list):
        for member in value:
            _validate_nfc(member, label)
    elif isinstance(value, dict):
        for key, member in value.items():
            _validate_nfc(key, label)
            _validate_nfc(member, label)

def _canonical_json(value) -> bytes:
    _validate_nfc(value, 'canonical JSON')
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('utf-8')
SEMANTIC_FINGERPRINT_EXTRACTOR_SHA256 = hashlib.sha256(_canonical_json(SEMANTIC_FINGERPRINT_DESCRIPTOR)).hexdigest()
if SEMANTIC_FINGERPRINT_EXTRACTOR_SHA256 != 'eadb11f7d275ed90b1455de18d2c9cae00297881e107542e564ca37a23a01a12':
    raise RuntimeError('semantic-fingerprint descriptor identity drifted')

class ProjectionSemantics:

    def __init__(self, corpus_roots):
        if isinstance(corpus_roots, (str, bytes)):
            raise ValueError('Corpus roots must be a sequence of paths')
        roots = tuple(corpus_roots)
        if not roots or not all((isinstance(root, str) and root for root in roots)):
            raise ValueError('Explicit corpus roots are required')
        for root in roots:
            self._safe_document(root, 'corpus root')
        self.corpus_roots = roots

    def validate_triple(self, index_dir, location_dir, diagnostic_dir):
        object_manifest, object_families, object_manifest_sha256, validated_edges = self._load_object_index(index_dir)
        location_manifest, location_families, location_manifest_sha256, location_rows = self._load_location_index(location_dir)
        diagnostic_manifest, diagnostic_families, diagnostic_manifest_sha256, diagnostic_records, diagnostic_payload = self._load_diagnostic_index(diagnostic_dir)
        profile = (object_manifest['schema_version'], location_manifest['schema_version'], diagnostic_manifest['schema_version'])
        if profile != CURRENT_INGEST_PROFILE:
            raise IngestError(f'snapshot profile {profile} is ineligible for new ingestion; required {CURRENT_INGEST_PROFILE}')
        self._validate_projection_agreement(object_families, location_rows, location_families)
        self._validate_diagnostic_agreement(object_manifest, object_families, validated_edges, location_manifest, location_families, diagnostic_manifest, diagnostic_families, diagnostic_records)

    def _duplicate_member_pairs(self, pairs):
        value = {}
        for key, member in pairs:
            if key in value:
                raise IngestError(f'duplicate JSON member {key!r}')
            value[key] = member
        return value

    def _decode_json(self, raw: bytes, label: str):
        """Decode committed JSON without accepting duplicate keys or non-finite values."""
        try:
            text = raw.decode('utf-8')
            if text.startswith('\ufeff'):
                raise IngestError(f'{label} must not contain a UTF-8 BOM')
            return json.loads(text, object_pairs_hook=self._duplicate_member_pairs, parse_constant=lambda value: (_ for _ in ()).throw(IngestError(f'{label} contains non-finite number {value}')))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise IngestError(f'invalid {label}') from exc

    def _require_exact_keys(self, value: dict, expected: set[str], label: str) -> None:
        if set(value) != expected:
            missing = sorted(expected - set(value))
            extra = sorted(set(value) - expected)
            raise IngestError(f'{label} has invalid members (missing={missing}, extra={extra})')

    def _nonnegative_int(self, value, label: str) -> int:
        if type(value) is not int or value < 0:
            raise IngestError(f'{label} must be a non-negative integer')
        return value

    def _count_map(self, value, label: str) -> dict[str, int]:
        if not isinstance(value, dict):
            raise IngestError(f'{label} must be an object')
        out: dict[str, int] = {}
        for key, count in value.items():
            if not isinstance(key, str) or not key:
                raise IngestError(f'{label} contains an invalid key')
            out[key] = self._nonnegative_int(count, f'{label}.{key}')
        return out

    def _location_coverage_counts(self, value, label: str) -> dict[str, int]:
        counts = self._count_map(value, label)
        self._require_exact_keys(counts, LOCATION_COVERAGE_FIELDS, label)
        if counts['active_documents_seen'] != counts['active_documents_identified'] + counts['active_documents_missing_id']:
            raise IngestError(f'{label} active-document arithmetic mismatch')
        if counts['archive_markdown_members'] != counts['archive_members_identified'] + counts['archive_members_missing_id']:
            raise IngestError(f'{label} archive-member arithmetic mismatch')
        return counts

    def _positive_line(self, value, label: str) -> int:
        if type(value) is not int or not 1 <= value <= _MAX_LINE:
            raise IngestError(f'{label} must be a positive 32-bit integer')
        return value

    def _safe_document(self, value, label: str) -> str:
        if not isinstance(value, str) or not value:
            raise IngestError(f'{label} must be a non-empty repository-relative path')
        _validate_nfc(value, label)
        if len(value.encode('utf-8')) > 1024:
            raise IngestError(f'{label} exceeds 1,024 UTF-8 bytes')
        pure = pathlib.PurePosixPath(value)
        if pure.is_absolute() or '\\' in value or value != pure.as_posix() or any((part in {'', '.', '..'} for part in pure.parts)):
            raise IngestError(f'{label} is not a safe normalized relative path')
        return value

    def _safe_corpus_document(self, value, label: str) -> str:
        document = self._safe_document(value, label)
        if not any((document == root or document.startswith(f'{root}/') for root in self.corpus_roots)):
            raise IngestError(f'{label} is outside the scanned corpus')
        return document

    def _safe_global_object_id(self, value, label: str, *, kind: str | None=None) -> str:
        """Validate the closed GlobalObjectIdV1 common and kind grammar."""
        if not isinstance(value, str) or not value:
            raise IngestError(f'{label} must be a non-empty GlobalObjectIdV1 string')
        _validate_nfc(value, label)
        if len(value.encode('utf-8')) > 512:
            raise IngestError(f'{label} exceeds 512 UTF-8 bytes')
        if value != value.strip():
            raise IngestError(f'{label} has leading or trailing whitespace')
        if any((unicodedata.category(character) == 'Cc' for character in value)):
            raise IngestError(f'{label} contains a control character')
        if any((character in value for character in ('`', '/', '\\'))):
            raise IngestError(f'{label} contains a forbidden character')
        invariant_match = _INVARIANT_ID.fullmatch(value)
        if invariant_match and invariant_match.group(1) in {'FOO', 'BAR', 'BAZ', 'EXAMPLE'}:
            raise IngestError(f'{label} uses a reserved illustrative invariant prefix')

        def matches(candidate_kind: str) -> bool:
            if candidate_kind == 'document':
                return len(value.encode('utf-8')) <= 128 and _DOCUMENT_ID.fullmatch(value) is not None
            if candidate_kind == 'invariant':
                return invariant_match is not None
            if candidate_kind == 'open_question':
                return bool(len(value.encode('utf-8')) <= 128 and _PCDN_ID.fullmatch(value) or _EOQ_ID.fullmatch(value))
            if candidate_kind == 'errata':
                return _ERRATA_ID.fullmatch(value) is not None
            if candidate_kind == 'term':
                return _TERM_ID.fullmatch(value) is not None
            if candidate_kind == 'gate':
                return _GATE_ID.fullmatch(value) is not None
            if candidate_kind == 'nongoal':
                return _NONGOAL_ID.fullmatch(value) is not None
            if candidate_kind == 'section':
                return _SECTION_ID.fullmatch(value) is not None
            if candidate_kind == 'amendment':
                match = _AMENDMENT_ID.fullmatch(value)
                return bool(match and self._safe_document_id_component(match.group(1)))
            if candidate_kind == 'rationale':
                match = _RATIONALE_ID.fullmatch(value)
                return bool(match and self._safe_document_id_component(match.group(1)))
            return False
        if kind is not None:
            if not matches(kind):
                raise IngestError(f'{label} is not eligible for object kind {kind!r}')
        elif not any((matches(candidate_kind) for candidate_kind in ('document', 'invariant', 'open_question', 'errata', 'term', 'gate', 'nongoal', 'section', 'amendment', 'rationale'))):
            raise IngestError(f'{label} is not GlobalObjectIdV1 eligible')
        return value

    def _safe_retained_v2_subject(self, value, label: str, *, amendment: bool=False) -> str:
        """Validate immutable diagnostic-v2 subjects without applying v3 identity.

    Diagnostic schema v2 predates ``GlobalObjectIdV1`` and used the then-current
    path/revision amendment identity. Reading those bytes is compatibility, not
    permission to emit or ingest another v2 snapshot.
    """
        if not isinstance(value, str) or not value:
            raise IngestError(f'{label} must be a non-empty retained-v2 token')
        _validate_nfc(value, label)
        if len(value.encode('utf-8')) > 2048:
            raise IngestError(f'{label} exceeds the retained-v2 token limit')
        if value != value.strip():
            raise IngestError(f'{label} has leading or trailing whitespace')
        if any((unicodedata.category(character) == 'Cc' for character in value)):
            raise IngestError(f'{label} contains a control character')
        if '`' in value or '\\' in value:
            raise IngestError(f'{label} contains a forbidden character')
        if amendment:
            if _AMENDMENT_ID.fullmatch(value):
                return value
            base, separator, revision = value.rpartition('#')
            if not separator or re.fullmatch(_SEMVER, revision) is None:
                raise IngestError(f'{label} is not a retained-v2 amendment identity')
            if self._safe_document_id_component(base):
                return value
            try:
                self._safe_corpus_document(base, f'{label} document')
            except IngestError as exc:
                raise IngestError(f'{label} is not a retained-v2 amendment identity') from exc
            return value
        if '/' in value:
            base = value.split('#', 1)[0]
            self._safe_corpus_document(base, f'{label} document')
        return value

    def _safe_document_id_component(self, value: str) -> bool:
        return bool(len(value.encode('utf-8')) <= 128 and _DOCUMENT_ID.fullmatch(value))

    def _validate_retired_dependencies(self, obj: dict, label: str, document_owners: dict[str, list[dict]]) -> None:
        """Validate the exact object-carried retirement declaration, not DAG proof."""
        attrs = obj['attrs']
        provenance = attrs.get('attr_provenance')
        if provenance is None:
            provenance = {}
        if not isinstance(provenance, dict):
            raise IngestError(f'{label}.attrs.attr_provenance must be an object')
        has_records = 'retired_dependencies' in attrs
        has_provenance = 'retired_dependencies' in provenance
        if not has_records:
            if has_provenance:
                raise IngestError(f'{label} has retired_dependencies provenance without the attribute')
            return
        if obj['kind'] != 'amendment':
            raise IngestError(f'{label}.retired_dependencies is amendment-only')
        self._safe_global_object_id(obj['obj_id'], f'{label}.obj_id', kind='amendment')
        if attrs.get('shape') not in {'block', 'compact'}:
            raise IngestError(f'{label}.retired_dependencies requires a stable amendment')
        amendment_match = _AMENDMENT_ID.fullmatch(obj['obj_id'])
        owners = document_owners.get(obj['doc'], [])
        if len(owners) != 1 or owners[0]['obj_id'] != amendment_match.group(1):
            raise IngestError(f'{label}.retired_dependencies has wrong document authority')
        if attrs.get('rev') != amendment_match.group(2):
            raise IngestError(f'{label}.retired_dependencies has wrong amendment revision')
        records = attrs['retired_dependencies']
        if not isinstance(records, list) or not records:
            raise IngestError(f'{label}.retired_dependencies must be a non-empty array')
        if provenance.get('retired_dependencies') != 'declared':
            raise IngestError(f'{label}.retired_dependencies requires declared array provenance')
        if attrs.get('change_kind') not in RETIRED_DEPENDENCY_CHANGE_KINDS:
            raise IngestError(f'{label}.retired_dependencies requires an eligible change_kind')
        touches = attrs.get('touches')
        if not isinstance(touches, list) or not touches:
            raise IngestError(f'{label}.retired_dependencies requires non-empty touches')
        if not all((isinstance(target, str) for target in touches)):
            raise IngestError(f'{label}.attrs.touches must contain strings')
        observed: list[tuple[bytes, bytes, bytes]] = []
        seen: set[tuple[str, str, str]] = set()
        for ordinal, record in enumerate(records, start=1):
            member_label = f'{label}.retired_dependencies[{ordinal}]'
            if not isinstance(record, dict):
                raise IngestError(f'{member_label} must be an object')
            self._require_exact_keys(record, {'upstream_object_id', 'dependent_object_id', 'edge_type'}, member_label)
            upstream = self._safe_global_object_id(record['upstream_object_id'], f'{member_label}.upstream_object_id')
            dependent = self._safe_global_object_id(record['dependent_object_id'], f'{member_label}.dependent_object_id')
            edge_type = record['edge_type']
            if edge_type not in RETIRED_DEPENDENCY_EDGE_TYPES:
                raise IngestError(f'{member_label}.edge_type is unsupported')
            key = (upstream, dependent, edge_type)
            if key in seen:
                raise IngestError(f'{label}.retired_dependencies contains a duplicate')
            seen.add(key)
            observed.append(tuple((part.encode('utf-8') for part in key)))
            if edge_type == 'same-as':
                if upstream.encode('utf-8') > dependent.encode('utf-8'):
                    raise IngestError(f'{member_label} same-as ids are not ordered')
                if upstream not in touches or dependent not in touches:
                    raise IngestError(f'{member_label} same-as ids must both be in touches')
            elif dependent not in touches:
                raise IngestError(f'{member_label} dependent id must be in touches')
        if observed != sorted(observed):
            raise IngestError(f'{label}.retired_dependencies is not canonically sorted')

    def _read_projection(self, index_dir: pathlib.Path, *, label: str, supported_versions: set[int]) -> tuple[dict, dict[str, dict], str]:
        """Return one validated manifest envelope, family payloads, and byte hash."""
        manifest_path = index_dir / MANIFEST
        if not manifest_path.exists():
            raise IngestError(f'no {MANIFEST} in {index_dir} — is the {label} index committed?')
        try:
            manifest_bytes = manifest_path.read_bytes()
            manifest = self._decode_json(manifest_bytes, f'{label} manifest')
        except OSError as exc:
            raise IngestError(f'invalid {label} manifest') from exc
        if not isinstance(manifest, dict):
            raise IngestError(f'{label} manifest must be a JSON object')
        version = manifest.get('schema_version')
        if type(version) is not int or version not in supported_versions:
            raise IngestError(f'{label} schema_version {version} unsupported (this build understands {sorted(supported_versions)})')
        family_names = manifest.get('families')
        if not isinstance(family_names, list) or not all((isinstance(name, str) and name for name in family_names)):
            raise IngestError(f'{label} manifest families must be a list of names')
        if family_names != sorted(set(family_names)):
            raise IngestError(f'{label} manifest families must be sorted and unique')
        families: dict[str, dict] = {}
        for name in family_names:
            if pathlib.PurePosixPath(name).name != name or '\\' in name:
                raise IngestError(f'{label} manifest contains an unsafe family name')
            path = index_dir / f'{name}.json'
            if not path.exists():
                raise IngestError(f'{label} manifest lists {name} but {path.name} is missing')
            try:
                payload = self._decode_json(path.read_bytes(), f'{label} family {name}')
            except OSError as exc:
                raise IngestError(f'invalid {label} family payload for {name}') from exc
            if not isinstance(payload, dict):
                raise IngestError(f'{label} family payload for {name} must be an object')
            if payload.get('schema_version') != version:
                raise IngestError(f'{label} family {name} has a mismatched schema_version')
            if payload.get('family') != name:
                raise IngestError(f'{label} family {name} has a mismatched family envelope')
            families[name] = payload
        digest = hashlib.sha256(manifest_bytes).hexdigest()
        return (manifest, families, digest)

    def _validate_v3_endpoint(self, endpoint, *, label: str, object_candidates: dict[str, list[dict]], document_owners: dict[str, list[dict]]) -> dict:
        if not isinstance(endpoint, dict):
            raise IngestError(f'{label} must be an object')
        self._require_exact_keys(endpoint, {'family', 'object_id', 'definition'}, label)
        family = endpoint['family']
        object_id = endpoint['object_id']
        definition = endpoint['definition']
        if not isinstance(family, str) or not family:
            raise IngestError(f'{label}.family must be a non-empty string')
        if not isinstance(object_id, str) or not object_id:
            raise IngestError(f'{label}.object_id must be a non-empty string')
        if not isinstance(definition, dict):
            raise IngestError(f'{label}.definition must be an object')
        self._require_exact_keys(definition, {'document', 'line'}, f'{label}.definition')
        document = self._safe_corpus_document(definition['document'], f'{label}.definition.document')
        line = self._positive_line(definition['line'], f'{label}.definition.line')
        candidates = object_candidates.get(object_id, [])
        if len(candidates) != 1:
            raise IngestError(f'{label}.object_id {object_id} resolves to {len(candidates)} objects')
        candidate = candidates[0]
        self._safe_global_object_id(object_id, f'{label}.object_id', kind=candidate['kind'])
        if candidate['kind'] == 'open_question':
            eoq_match = _EOQ_ID.fullmatch(object_id)
            if eoq_match and eoq_match.group(1) != candidate['family']:
                raise IngestError(f'{label}.object_id has the wrong EOQ family')
        elif candidate['kind'] == 'errata':
            errata_match = _ERRATA_ID.fullmatch(object_id)
            if errata_match and errata_match.group(1) != candidate['family']:
                raise IngestError(f'{label}.object_id has the wrong ERRATA family')
        elif candidate['kind'] == 'term':
            term_match = _TERM_ID.fullmatch(object_id)
            if term_match and term_match.group(1) != candidate['family']:
                raise IngestError(f'{label}.object_id has the wrong term family')
        elif candidate['kind'] == 'gate':
            gate_match = _GATE_ID.fullmatch(object_id)
            if gate_match and gate_match.group(1) != candidate['family']:
                raise IngestError(f'{label}.object_id has the wrong gate family')
        elif candidate['kind'] == 'nongoal':
            nongoal_match = _NONGOAL_ID.fullmatch(object_id)
            if nongoal_match and nongoal_match.group(1) != candidate['family']:
                raise IngestError(f'{label}.object_id has the wrong non-goal family')
        elif candidate['kind'] == 'section':
            section_match = _SECTION_ID.fullmatch(object_id)
            if section_match and section_match.group(1) != candidate['family']:
                raise IngestError(f'{label}.object_id has the wrong section family')
        elif candidate['kind'] in {'amendment', 'rationale'}:
            match = _AMENDMENT_ID.fullmatch(object_id) if candidate['kind'] == 'amendment' else _RATIONALE_ID.fullmatch(object_id)
            owners = document_owners.get(candidate['doc'], [])
            if len(owners) != 1 or owners[0]['obj_id'] != match.group(1):
                raise IngestError(f'{label}.object_id has the wrong document authority')
            if candidate['kind'] == 'amendment':
                if candidate['attrs'].get('shape') not in {'block', 'compact'}:
                    raise IngestError(f'{label}.object_id is not a stable amendment shape')
                if candidate['attrs'].get('rev') != match.group(2):
                    raise IngestError(f'{label}.object_id has the wrong amendment revision')
            else:
                amendment_id = object_id.removesuffix('#rationale')
                amendments = object_candidates.get(amendment_id, [])
                if len(amendments) != 1 or amendments[0]['kind'] != 'amendment' or amendments[0]['family'] != candidate['family'] or (amendments[0]['doc'] != candidate['doc']):
                    raise IngestError(f'{label}.object_id has no linked amendment')
        if candidate['family'] != family or candidate['doc'] != document or candidate['line'] != line:
            raise IngestError(f'{label} definition evidence does not match its object')
        return candidate

    def _validate_v3_edge(self, family: str, edge, object_candidates: dict[str, list[dict]], document_owners: dict[str, list[dict]], definition_owners: dict[tuple[str, int], list[dict]]) -> dict:
        label = f'object family {family} edge'
        if not isinstance(edge, dict):
            raise IngestError(f'{label} must be an object')
        self._require_exact_keys(edge, {'edge_type', 'source', 'target', 'locator', 'kind_provenance'}, label)
        edge_type = edge['edge_type']
        if edge_type not in REGISTERED_EDGE_TYPES:
            raise IngestError(f'{label} has unsupported edge_type {edge_type!r}')
        provenance = edge['kind_provenance']
        if provenance not in {'declared', 'inferred'}:
            raise IngestError(f'{label} has invalid kind_provenance')
        if provenance == 'declared' and edge_type == 'defines':
            raise IngestError(f'{label} defines cannot be authored')
        if provenance == 'inferred' and edge_type not in {'defines', 'cites', 'amends', 'motivates'}:
            raise IngestError(f'{label} edge type is outside the inference registry')
        if edge_type == 'verifies':
            raise IngestError(f'{label} verifies has no registered checking source kind')
        source_object = self._validate_v3_endpoint(edge['source'], label=f'{label}.source', object_candidates=object_candidates, document_owners=document_owners)
        target_object = self._validate_v3_endpoint(edge['target'], label=f'{label}.target', object_candidates=object_candidates, document_owners=document_owners)
        locator = edge['locator']
        if not isinstance(locator, dict):
            raise IngestError(f'{label}.locator must be an object')
        self._require_exact_keys(locator, {'document', 'line'}, f'{label}.locator')
        citation_document = self._safe_corpus_document(locator['document'], f'{label}.locator.document')
        citation_line = self._positive_line(locator['line'], f'{label}.locator.line')
        source_id = edge['source']['object_id']
        target_id = edge['target']['object_id']
        if source_id == target_id:
            raise IngestError(f'{label} must not be a self-edge')
        if edge_type == 'same-as' and source_id.encode('utf-8') > target_id.encode('utf-8'):
            raise IngestError(f'{label} same-as endpoints are not canonically ordered')
        owners = document_owners.get(citation_document, [])
        if owners and (len(owners) != 1 or owners[0]['family'] != family):
            raise IngestError(f'{label} does not agree with its citation-envelope family')
        if provenance == 'inferred' and edge_type == 'defines':
            if source_object['kind'] != 'document' or source_object['doc'] != target_object['doc'] or citation_document != target_object['doc'] or (citation_line != target_object['line']):
                raise IngestError(f'{label} has invalid structural ownership evidence')
        elif provenance == 'inferred' and edge_type == 'cites':
            line_owners = definition_owners.get((citation_document, citation_line), [])
            if len(line_owners) == 1:
                valid_owner = line_owners[0] is source_object
            elif not line_owners:
                valid_owner = len(owners) == 1 and owners[0] is source_object and (source_object['kind'] == 'document') and (source_object['doc'] == citation_document)
            else:
                valid_owner = False
            if not valid_owner:
                raise IngestError(f'{label} has invalid inferred citation ownership')
            if source_object['family'] != family:
                raise IngestError(f'{label} does not agree with its citation-envelope family')
        elif provenance == 'inferred' and edge_type == 'amends':
            touches = source_object['attrs'].get('touches')
            attribute_provenance = source_object['attrs'].get('attr_provenance', {})
            if source_object['kind'] != 'amendment' or not isinstance(touches, list) or target_id not in touches or (attribute_provenance.get('touches') != 'declared') or (source_object['doc'] != citation_document) or (source_object['family'] != family):
                raise IngestError(f'{label} does not agree with amendment Touches')
        elif provenance == 'inferred' and edge_type == 'motivates':
            amendment_id = source_id.removesuffix('#rationale')
            amendments = object_candidates.get(amendment_id, [])
            amendment_provenance = amendments[0]['attrs'].get('attr_provenance', {}) if len(amendments) == 1 else {}
            if source_object['kind'] != 'rationale' or not source_id.endswith('#rationale') or len(amendments) != 1 or (not isinstance(amendments[0]['attrs'].get('touches'), list)) or (target_id not in amendments[0]['attrs']['touches']) or (amendment_provenance.get('touches') != 'declared') or (source_object['doc'] != citation_document) or (source_object['family'] != family):
                raise IngestError(f'{label} does not agree with rationale Touches')
        edge_key_input = {'edge_type': edge_type, 'kind_provenance': provenance, 'locator': {'document': citation_document, 'line': citation_line}, 'source_object_id': source_id, 'target_object_id': target_id}
        return {'edge_type': edge_type, 'source': source_id, 'target': target_id, 'source_definition': (source_object['obj_id'], source_object['doc'], source_object['line']), 'target_definition': (target_object['obj_id'], target_object['doc'], target_object['line']), 'family': family, 'citation_document': citation_document, 'line': citation_line, 'kind_provenance': provenance, 'canonical_edge_key': hashlib.sha256(_canonical_json(edge_key_input)).hexdigest()}

    def _validate_object_index(self, manifest: dict, families: dict[str, dict]) -> list[dict]:
        total_objects = 0
        total_edges = 0
        family_counts: dict[str, int] = {}
        object_sites: set[tuple[str, str, int]] = set()
        object_candidates: dict[str, list[dict]] = collections.defaultdict(list)
        document_owners: dict[str, list[dict]] = collections.defaultdict(list)
        definition_owners: dict[tuple[str, int], list[dict]] = collections.defaultdict(list)
        validated_edges: list[dict] = []
        version = manifest['schema_version']
        base_manifest_keys = {'schema_version', 'families', 'family_counts', 'total_objects', 'total_edges'}
        if version == 3:
            self._require_exact_keys(manifest, base_manifest_keys | {'semantic_fingerprint_version', 'semantic_fingerprint_extractor_sha256'}, 'object manifest')
            if manifest['semantic_fingerprint_version'] != SEMANTIC_FINGERPRINT_VERSION:
                raise IngestError('object manifest semantic_fingerprint_version unsupported')
            if manifest['semantic_fingerprint_extractor_sha256'] != SEMANTIC_FINGERPRINT_EXTRACTOR_SHA256:
                raise IngestError('object manifest semantic_fingerprint_extractor_sha256 unsupported')
        else:
            self._require_exact_keys(manifest, base_manifest_keys, 'object manifest')
        for family, payload in sorted(families.items()):
            objects = payload.get('objects')
            edges = payload.get('edges')
            if not isinstance(objects, list) or not isinstance(edges, list):
                raise IngestError(f'object family {family} must carry object and edge arrays')
            self._require_exact_keys(payload, {'schema_version', 'family', 'object_count', 'edge_count', 'kind_counts', 'objects', 'edges'}, f'object family {family}')
            if self._nonnegative_int(payload.get('object_count'), f'{family}.object_count') != len(objects):
                raise IngestError(f'object family {family} object_count does not match its rows')
            if self._nonnegative_int(payload.get('edge_count'), f'{family}.edge_count') != len(edges):
                raise IngestError(f'object family {family} edge_count does not match its rows')
            for obj in objects:
                if not isinstance(obj, dict):
                    raise IngestError(f'object family {family} contains a non-object row')
                if not all((isinstance(obj.get(key), str) and obj[key] for key in ('obj_id', 'kind', 'doc'))):
                    raise IngestError(f'object family {family} contains an incomplete object row')
                line = self._nonnegative_int(obj.get('line'), f'{family} object line')
                if version == 3:
                    self._require_exact_keys(obj, {'obj_id', 'kind', 'family', 'doc', 'line', 'text', 'attrs'}, f'object family {family} object')
                    if obj['kind'] not in OBJECT_KINDS:
                        raise IngestError(f'object family {family} contains unsupported ObjectKind')
                    line = self._positive_line(obj['line'], f'{family} object line')
                    self._safe_corpus_document(obj['doc'], f'{family} object document')
                attrs = obj.get('attrs', {})
                if not isinstance(attrs, dict):
                    raise IngestError(f'object family {family} contains non-object attrs')
                attr_provenance = attrs.get('attr_provenance', {})
                if not isinstance(attr_provenance, dict) or any((value not in PROVENANCE_VALUES for value in attr_provenance.values())):
                    raise IngestError(f'object family {family} contains invalid attribute provenance')
                object_family = obj.get('family', family)
                if not isinstance(object_family, str) or not object_family:
                    raise IngestError(f'object family {family} contains an invalid family attribute')
                if version == 3 and object_family != family:
                    raise IngestError(f'object family {family} object has a mismatched family')
                text = obj.get('text', '')
                if not isinstance(text, str):
                    raise IngestError(f'object family {family} contains non-string text')
                _validate_nfc(obj, f'object family {family} object')
                site = (obj['obj_id'], obj['doc'], line)
                if site in object_sites:
                    raise IngestError('object index contains a duplicate definition-site row')
                object_sites.add(site)
                object_candidates[obj['obj_id']].append(obj)
                definition_owners[obj['doc'], line].append(obj)
                if obj['kind'] == 'document':
                    document_owners[obj['doc']].append(obj)
                if version == 3:
                    if obj['kind'] == 'amendment':
                        for attribute in ('change_kind', 'touches'):
                            if attrs.get(attribute) is not None and attr_provenance.get(attribute) != 'declared':
                                raise IngestError(f'object amendment {attribute} requires declared provenance')
                    if obj['kind'] == 'document' and (attrs.get('lifecycle_state') not in DOCUMENT_LIFECYCLE_STATES or attr_provenance.get('lifecycle_state') not in PROVENANCE_VALUES):
                        raise IngestError(f"object document {obj['obj_id']} has invalid lifecycle provenance")
                    if obj['kind'] == 'gate' and (type(attrs.get('checked')) is not bool or attr_provenance.get('checked') != 'declared'):
                        raise IngestError(f"object gate {obj['obj_id']} has invalid checked provenance")
                    if obj['kind'] == 'invariant' and (type(attrs.get('has_verification')) is not bool or attr_provenance.get('has_verification') != 'inferred'):
                        raise IngestError(f"object invariant {obj['obj_id']} has invalid verification provenance")
            observed_kind_counts = dict(sorted(collections.Counter((obj['kind'] for obj in objects)).items()))
            if self._count_map(payload.get('kind_counts'), f'{family}.kind_counts') != observed_kind_counts:
                raise IngestError(f'object family {family} kind_counts does not match its rows')
            family_counts[family] = len(objects)
            total_objects += len(objects)
            total_edges += len(edges)
        if version == 3:
            for family, payload in sorted(families.items()):
                for obj in payload['objects']:
                    self._validate_retired_dependencies(obj, f"object family {family} object {obj['obj_id']}", document_owners)
        seen_v3_keys: set[str] = set()
        for family, payload in sorted(families.items()):
            for edge in payload['edges']:
                if version == 3:
                    validated = self._validate_v3_edge(family, edge, object_candidates, document_owners, definition_owners)
                    edge_key = validated['canonical_edge_key']
                    if edge_key in seen_v3_keys:
                        raise IngestError('object index contains a duplicate canonical edge')
                    seen_v3_keys.add(edge_key)
                    validated_edges.append(validated)
                else:
                    if not isinstance(edge, dict) or not all((isinstance(edge.get(key), str) and edge[key] for key in ('edge_type', 'source', 'target'))):
                        raise IngestError(f'object family {family} contains an incomplete edge row')
                    self._nonnegative_int(edge.get('line', 0), f'{family} edge line')
        if self._nonnegative_int(manifest.get('total_objects'), 'object total_objects') != total_objects:
            raise IngestError('object manifest total_objects does not match its family rows')
        if self._nonnegative_int(manifest.get('total_edges'), 'object total_edges') != total_edges:
            raise IngestError('object manifest total_edges does not match its family rows')
        if 'family_counts' in manifest and self._count_map(manifest['family_counts'], 'object family_counts') != family_counts:
            raise IngestError('object manifest family_counts does not match its family rows')
        return validated_edges

    def _canonical_location_record(self, document_id: str, record: dict) -> bytes:
        """Canonical bytes for the internal, document-scoped location identity."""
        return _canonical_json({'document_id': document_id, 'location': record})

    def location_record_key(self, document_id: str, record: dict) -> str:
        """Return the stable internal digest used to detect duplicate cache rows."""
        return hashlib.sha256(self._canonical_location_record(document_id, record)).hexdigest()

    def _fixed_point_percent_decode(self, value: str, label: str) -> str:
        """Return the final percent-decoded safety view without exposing it."""
        decoded = value
        for _iteration in range(len(value) + 1):
            try:
                candidate = urllib.parse.unquote(decoded, encoding='utf-8', errors='strict')
            except (UnicodeDecodeError, ValueError) as exc:
                raise IngestError(f'{label} contains an unsafe location value') from exc
            if candidate == decoded:
                return decoded
            decoded = candidate
        raise IngestError(f'{label} contains an unsafe location value')

    def _safe_location_string(self, value, label: str) -> str:
        """Reject unstable, secret-bearing, or payload-like locator material."""
        if not isinstance(value, str) or not value:
            raise IngestError(f'{label} must be a non-empty string')
        _validate_nfc(value, label)
        if len(value.encode('utf-8')) > 4096:
            raise IngestError(f'{label} contains an unsafe location payload')
        decoded = self._fixed_point_percent_decode(value, label)
        for safety_view in {value, decoded}:
            lower = safety_view.lower()
            compact = re.sub('\\s+', '', safety_view)
            if _LOCATION_URI.match(safety_view) or _LOCATION_ABSOLUTE.match(safety_view) or _LOCATION_SIGNED_QUERY.search(safety_view) or _LOCATION_CREDENTIAL.search(safety_view) or _LOCATION_PRIVATE_HANDLE.search(safety_view) or _LOCATION_PRIVATE_KEY.search(safety_view) or _LOCATION_ENVIRONMENT.search(safety_view) or _LOCATION_HOME.match(safety_view) or lower.startswith('data:') or (len(compact) > 512 and re.fullmatch('[A-Za-z0-9+/=]+', compact)) or ('"model"' in lower and ('"messages"' in lower or '"prompt"' in lower)) or any((unicodedata.category(character) == 'Cc' for character in safety_view)):
                raise IngestError(f'{label} contains an unsafe location value')
        return value

    def _safe_location_path(self, value, label: str) -> str:
        value = self._safe_location_string(value, label)
        try:
            return self._safe_document(value, label)
        except IngestError as exc:
            raise IngestError(f'{label} is not a safe normalized relative path') from exc

    def _validate_location_provenance(self, record: dict, document_id: str) -> None:
        kind = record['location_kind']
        provenance = record['attr_provenance']
        label = f'location document {document_id}'
        declared_locator = kind in {'memalpha', 'pointer'} or provenance['location_kind'] == 'declared'
        locator_value = 'declared' if declared_locator else 'inferred'
        expected = {'location_kind': locator_value, 'target': locator_value, 'baseline': 'declared' if record['baseline'] is not None else 'inferred', 'integrity': 'declared' if kind == 'archive' and declared_locator else 'inferred', 'retired_at': 'declared' if record['retired_at'] is not None else 'inferred'}
        if not declared_locator and (record['baseline'] is not None or record['retired_at'] is not None):
            raise IngestError(f'{label} inferred locator carries declared-only history')
        if provenance != expected:
            raise IngestError(f'{label} attribute provenance disagrees with its values')

    def _validate_location_record_shape(self, record: dict, document_id: str) -> None:
        """Validate one closed ADDENDUM-C §4.4 location-kind envelope."""
        label = f'location document {document_id}'
        kind = record['location_kind']
        if kind not in LOCATION_KINDS:
            raise IngestError(f'{label} has an unsupported location kind')
        target = record['target']
        if not isinstance(target, dict):
            raise IngestError(f'{label} target must be an object')
        expected_target_keys = {'repository': {'path'}, 'archive': {'path', 'member'}, 'memalpha': {'corpus', 'notebook', 'object_type', 'opaque_id'}, 'pointer': {'path', 'replacement_authority'}}[kind]
        self._require_exact_keys(target, expected_target_keys, f'{label} target')
        if kind in {'repository', 'archive', 'pointer'}:
            self._safe_location_path(target['path'], f'{label} target.path')
        if kind == 'archive':
            self._safe_location_path(target['member'], f'{label} target.member')
        elif kind == 'memalpha':
            for member in ('corpus', 'notebook', 'object_type', 'opaque_id'):
                self._safe_location_string(target[member], f'{label} target.{member}')
        elif kind == 'pointer':
            self._safe_location_string(target['replacement_authority'], f'{label} target.replacement_authority')
        baseline = record['baseline']
        if baseline is not None:
            self._safe_location_string(baseline, f'{label} baseline')
        if kind == 'memalpha' and baseline is None:
            raise IngestError(f'{label} memalpha locator requires a baseline')
        integrity = record['integrity']
        if kind == 'archive':
            if not isinstance(integrity, dict):
                raise IngestError(f'{label} archive integrity must be an object')
            self._require_exact_keys(integrity, {'archive_sha256', 'member_sha256'}, f'{label} integrity')
            for member in ('archive_sha256', 'member_sha256'):
                if not isinstance(integrity[member], str) or not _SHA256.fullmatch(integrity[member]):
                    raise IngestError(f'{label} integrity must use lowercase SHA-256')
        elif integrity is not None:
            raise IngestError(f'{label} {kind} integrity must be null')
        retired_at = record['retired_at']
        if retired_at is not None and (not isinstance(retired_at, str) or not _LOCATION_COMMIT.fullmatch(retired_at)):
            raise IngestError(f'{label} retired_at must be a lowercase 7-40 hex commit')
        self._validate_location_provenance(record, document_id)

    def validate_location_projection(self, manifest: dict, families: dict[str, dict]) -> list[tuple[str, dict, dict, str]]:
        """Validate schema-v1 payloads and return flattened location rows.

    Both database ingestion and the Git-backed history provider consume this
    committed wire. Keeping one public validator prevents historical reads
    from silently developing a second location-projection grammar.
    """
        self._require_exact_keys(manifest, {'schema_version', 'families', 'family_document_counts', 'family_record_counts', 'total_documents', 'total_records', 'kind_counts', 'coverage_counts'}, 'location manifest')
        flattened: list[tuple[str, dict, dict, str]] = []
        seen_documents: set[str] = set()
        seen_record_keys: set[str] = set()
        family_document_counts: dict[str, int] = {}
        family_record_counts: dict[str, int] = {}
        all_kind_counts: collections.Counter[str] = collections.Counter()
        for family, payload in sorted(families.items()):
            self._require_exact_keys(payload, {'schema_version', 'family', 'document_count', 'record_count', 'kind_counts', 'documents'}, f'location family {family}')
            documents = payload.get('documents')
            if not isinstance(documents, list):
                raise IngestError(f'location family {family} must carry a documents array')
            document_count = self._nonnegative_int(payload.get('document_count'), f'{family}.document_count')
            record_count = self._nonnegative_int(payload.get('record_count'), f'{family}.record_count')
            if document_count != len(documents):
                raise IngestError(f'location family {family} document_count does not match its rows')
            family_kind_counts: collections.Counter[str] = collections.Counter()
            observed_records = 0
            for document in documents:
                if not isinstance(document, dict):
                    raise IngestError(f'location family {family} contains a non-object document')
                self._require_exact_keys(document, {'document_id', 'lifecycle_state', 'attr_provenance', 'locations'}, f'location family {family} document')
                document_id = document.get('document_id')
                lifecycle = document.get('lifecycle_state')
                provenance = document.get('attr_provenance')
                records = document.get('locations')
                if not isinstance(document_id, str) or not document_id:
                    raise IngestError(f'location family {family} contains a missing document id')
                if document_id in seen_documents:
                    raise IngestError(f'location index contains duplicate document id {document_id}')
                seen_documents.add(document_id)
                if not isinstance(lifecycle, str) or not lifecycle:
                    raise IngestError(f'location document {document_id} has no lifecycle state')
                if lifecycle not in DOCUMENT_LIFECYCLE_STATES:
                    raise IngestError(f'location document {document_id} has invalid lifecycle state')
                if not isinstance(provenance, dict) or not isinstance(provenance.get('lifecycle_state'), str):
                    raise IngestError(f'location document {document_id} has no lifecycle provenance')
                if provenance != {'lifecycle_state': provenance['lifecycle_state']} or provenance['lifecycle_state'] not in PROVENANCE_VALUES:
                    raise IngestError(f'location document {document_id} has invalid lifecycle provenance')
                if not isinstance(records, list):
                    raise IngestError(f'location document {document_id} has no locations array')
                for record in records:
                    if not isinstance(record, dict):
                        raise IngestError(f'location document {document_id} contains a non-object row')
                    required = {'location_kind', 'target', 'baseline', 'integrity', 'retired_at', 'attr_provenance'}
                    if not required.issubset(record):
                        raise IngestError(f'location document {document_id} contains an incomplete row')
                    if set(record) != required:
                        raise IngestError(f'location document {document_id} contains extra row members')
                    if not isinstance(record['attr_provenance'], dict):
                        raise IngestError(f'location document {document_id} has invalid provenance')
                    if set(record['attr_provenance']) != {'location_kind', 'target', 'baseline', 'integrity', 'retired_at'} or any((value not in PROVENANCE_VALUES for value in record['attr_provenance'].values())):
                        raise IngestError(f'location document {document_id} has invalid attribute provenance')
                    self._validate_location_record_shape(record, document_id)
                    _validate_nfc(record, f'location document {document_id} record')
                    key = self.location_record_key(document_id, record)
                    if key in seen_record_keys:
                        raise IngestError('location index contains a duplicate canonical record')
                    seen_record_keys.add(key)
                    flattened.append((family, document, record, key))
                    family_kind_counts[record['location_kind']] += 1
                    observed_records += 1
            if record_count != observed_records:
                raise IngestError(f'location family {family} record_count does not match its rows')
            if self._count_map(payload.get('kind_counts'), f'{family}.kind_counts') != dict(sorted(family_kind_counts.items())):
                raise IngestError(f'location family {family} kind_counts does not match its rows')
            family_document_counts[family] = document_count
            family_record_counts[family] = record_count
            all_kind_counts.update(family_kind_counts)
        total_documents = sum(family_document_counts.values())
        total_records = sum(family_record_counts.values())
        if self._nonnegative_int(manifest.get('total_documents'), 'location total_documents') != total_documents:
            raise IngestError('location manifest total_documents does not match its family rows')
        if self._nonnegative_int(manifest.get('total_records'), 'location total_records') != total_records:
            raise IngestError('location manifest total_records does not match its family rows')
        if self._count_map(manifest.get('family_document_counts'), 'location family_document_counts') != family_document_counts:
            raise IngestError('location manifest family_document_counts does not match its rows')
        if self._count_map(manifest.get('family_record_counts'), 'location family_record_counts') != family_record_counts:
            raise IngestError('location manifest family_record_counts does not match its rows')
        if self._count_map(manifest.get('kind_counts'), 'location kind_counts') != dict(sorted(all_kind_counts.items())):
            raise IngestError('location manifest kind_counts does not match its rows')
        self._location_coverage_counts(manifest.get('coverage_counts'), 'location coverage_counts')
        return flattened

    def _read_canonical_diagnostic_json(self, path: pathlib.Path, *, label: str, byte_limit: int) -> tuple[dict, bytes]:
        try:
            raw = path.read_bytes()
        except OSError as exc:
            raise IngestError(f'cannot read {label}') from exc
        if len(raw) > byte_limit:
            raise IngestError(f'{label} exceeds its byte limit')
        value = self._decode_json(raw, label)
        if not isinstance(value, dict):
            raise IngestError(f'{label} must be a JSON object')
        if raw != _canonical_json(value) + b'\n':
            raise IngestError(f'{label} is not canonical UTF-8 JSON plus one final LF')
        return (value, raw)

    def _validate_locator(self, value, label: str) -> dict:
        if not isinstance(value, dict):
            raise IngestError(f'{label} must be an object')
        self._require_exact_keys(value, {'document', 'line'}, label)
        return {'document': self._safe_corpus_document(value['document'], f'{label}.document'), 'line': self._positive_line(value['line'], f'{label}.line')}

    def _required_int_fact(self, facts: dict, key: str, label: str, *, minimum: int=0) -> int:
        value = facts[key]
        if type(value) is not int or value < minimum:
            raise IngestError(f'{label}.{key} must be an integer >= {minimum}')
        return value

    def _require_subject(self, subject, label: str, *, mode: str) -> None:
        if mode == 'null':
            if subject is not None:
                raise IngestError(f'{label}.subject_token must be null')
            return
        if subject is None:
            if mode.endswith('-or-null'):
                return
            raise IngestError(f'{label}.subject_token must be present')
        if not isinstance(subject, str):
            raise IngestError(f'{label}.subject_token must be a string or null')
        if mode.startswith('document'):
            self._safe_global_object_id(subject, f'{label}.subject_token', kind='document')
        elif mode.startswith('open-question'):
            self._safe_global_object_id(subject, f'{label}.subject_token', kind='open_question')
        elif mode.startswith('errata'):
            self._safe_global_object_id(subject, f'{label}.subject_token', kind='errata')
        elif mode.startswith('amendment'):
            self._safe_global_object_id(subject, f'{label}.subject_token', kind='amendment')
        else:
            self._safe_global_object_id(subject, f'{label}.subject_token')

    def _require_retained_v2_subject(self, subject, label: str, *, mode: str) -> None:
        if subject is None:
            if mode.endswith('-or-null'):
                return
            raise IngestError(f'{label}.subject_token must be present')
        self._safe_retained_v2_subject(subject, f'{label}.subject_token', amendment=mode.startswith('amendment'))

    def _validate_v1_diagnostic_record(self, code: str, subject, locators: list[dict], facts: dict, label: str) -> None:
        if code == 'document_id_missing':
            self._require_subject(subject, label, mode='null')
            self._require_exact_keys(facts, set(), f'{label}.facts')
            if len(locators) != 1 or locators[0]['line'] != 1:
                raise IngestError(f'{label} requires one document line-1 locator')
        elif code == 'invalid_document_lifecycle':
            self._require_subject(subject, label, mode='document-or-null')
            self._require_exact_keys(facts, set(), f'{label}.facts')
            if len(locators) != 1:
                raise IngestError(f'{label} requires one declaration locator')
        elif code == 'open_question_definition_duplicate':
            self._require_subject(subject, label, mode='open-question')
            self._require_exact_keys(facts, {'definition_count'}, f'{label}.facts')
            count = self._required_int_fact(facts, 'definition_count', f'{label}.facts', minimum=2)
            if count != len(locators):
                raise IngestError(f'{label}.definition_count must equal locator count')
        elif code == 'malformed_open_question_handle':
            self._require_subject(subject, label, mode='null')
            if set(facts) not in (set(), {'observed_token'}):
                raise IngestError(f'{label}.facts has an invalid allowlist')
            if 'observed_token' in facts and (not isinstance(facts['observed_token'], str) or _MALFORMED_TOKEN.fullmatch(facts['observed_token']) is None):
                raise IngestError(f'{label}.facts.observed_token is not allowlisted')
            if len(locators) != 1:
                raise IngestError(f'{label} requires one candidate locator')
        elif code in {'errata_missing_index_row', 'errata_index_without_body'}:
            self._require_subject(subject, label, mode='errata')
            self._require_exact_keys(facts, set(), f'{label}.facts')
            if len(locators) != 1:
                raise IngestError(f'{label} requires one locator')
        elif code in {'errata_duplicate_index_row', 'errata_duplicate_body'}:
            self._require_subject(subject, label, mode='errata')
            self._require_exact_keys(facts, {'occurrence_count'}, f'{label}.facts')
            count = self._required_int_fact(facts, 'occurrence_count', f'{label}.facts', minimum=2)
            if count != len(locators):
                raise IngestError(f'{label}.occurrence_count must equal locator count')
        elif code == 'errata_unsupported_status':
            self._require_subject(subject, label, mode='errata')
            self._require_exact_keys(facts, {'source'}, f'{label}.facts')
            if facts['source'] not in {'index', 'body'}:
                raise IngestError(f'{label}.facts.source is invalid')
            if len(locators) != 1:
                raise IngestError(f'{label} requires one status locator')
        elif code == 'errata_status_disagreement':
            self._require_subject(subject, label, mode='errata')
            self._require_exact_keys(facts, {'index_status', 'body_status'}, f'{label}.facts')
            if facts['index_status'] not in ERRATA_STATUSES or facts['body_status'] not in ERRATA_STATUSES:
                raise IngestError(f'{label}.facts contains an invalid ErrataStatus')
            if len(locators) != 2:
                raise IngestError(f'{label} requires two status locators')
        else:
            raise IngestError(f'{label} has unsupported diagnostic code')

    def _validate_v2_c6_record(self, code: str, subject, locators: list[dict], facts: dict, label: str) -> None:
        if code == 'dependency_source_unresolved':
            reasons = {'missing_document', 'ambiguous_definition_line', 'ambiguous_document', 'global_identity_ambiguous'}
            expected = {'edge_candidate_key', 'reason'}
            if facts.get('reason') == 'global_identity_ambiguous':
                expected.add('definition_count')
            self._require_retained_v2_subject(subject, label, mode='global-or-null')
        elif code == 'dependency_target_unresolved':
            reasons = {'missing', 'ambiguous'}
            expected = {'edge_candidate_key', 'reason'}
            if facts.get('reason') == 'ambiguous' and 'definition_count' in facts:
                expected.add('definition_count')
            self._require_retained_v2_subject(subject, label, mode='global-or-null')
        elif code == 'dependency_kind_unresolved':
            reasons = {'missing', 'unsupported', 'ambiguous'}
            expected = {'edge_candidate_key', 'reason'}
            self._require_retained_v2_subject(subject, label, mode='global-or-null')
        elif code == 'change_kind_unresolved':
            reasons = {'missing', 'unsupported'}
            expected = {'reason'}
            self._require_retained_v2_subject(subject, label, mode='amendment')
        elif code == 'touches_unresolved':
            reasons = {'missing', 'unknown', 'ambiguous'}
            expected = {'reason'}
            if facts.get('reason') == 'ambiguous' and 'definition_count' in facts:
                expected.add('definition_count')
            self._require_retained_v2_subject(subject, label, mode='amendment')
        else:
            reasons = set()
            expected = set()
            self._require_retained_v2_subject(subject, label, mode='amendment')
        self._require_exact_keys(facts, expected, f'{label}.facts')
        if code == 'retirement_supersedes_missing':
            return
        if facts['reason'] not in reasons:
            raise IngestError(f'{label}.facts.reason is invalid')
        if 'edge_candidate_key' in facts and (not isinstance(facts['edge_candidate_key'], str) or _SHA256.fullmatch(facts['edge_candidate_key']) is None):
            raise IngestError(f'{label}.facts.edge_candidate_key must be SHA-256')
        if 'definition_count' in facts:
            self._required_int_fact(facts, 'definition_count', f'{label}.facts', minimum=2)
        if not locators:
            raise IngestError(f'{label} requires at least one locator')

    def _validate_v3_c6_record(self, code: str, subject, locators: list[dict], facts: dict, label: str) -> None:
        reason = facts.get('reason')
        if code == 'dependency_source_unresolved':
            reasons = {'missing_document', 'ambiguous_definition_line', 'ambiguous_document', 'missing', 'invalid', 'global_identity_ambiguous'}
            if reason not in reasons:
                raise IngestError(f'{label}.facts.reason is invalid')
            ambiguous = reason in {'ambiguous_definition_line', 'ambiguous_document', 'global_identity_ambiguous'}
            expected = {'edge_candidate_key', 'reason'} | ({'definition_count'} if ambiguous else set())
            subject_mode = 'null' if reason in {'missing_document', 'ambiguous_definition_line', 'ambiguous_document'} else 'global-or-null' if reason in {'missing', 'invalid'} else 'global'
            self._require_subject(subject, label, mode=subject_mode)
            if reason in {'missing_document', 'missing', 'invalid'} and len(locators) != 1:
                raise IngestError(f'{label} requires one candidate locator')
        elif code == 'dependency_target_unresolved':
            if reason not in {'missing', 'invalid', 'ambiguous'}:
                raise IngestError(f'{label}.facts.reason is invalid')
            expected = {'edge_candidate_key', 'reason'} | ({'definition_count'} if reason == 'ambiguous' else set())
            self._require_subject(subject, label, mode='global' if reason == 'ambiguous' else 'global-or-null')
            if reason in {'missing', 'invalid'} and len(locators) != 1:
                raise IngestError(f'{label} requires one candidate locator')
        elif code == 'dependency_kind_unresolved':
            if reason not in {'missing', 'unsupported', 'ambiguous'}:
                raise IngestError(f'{label}.facts.reason is invalid')
            expected = {'edge_candidate_key', 'reason'}
            self._require_subject(subject, label, mode='global-or-null')
            if len(locators) != 1:
                raise IngestError(f'{label} requires one candidate locator')
        elif code == 'change_kind_unresolved':
            if reason not in {'missing', 'unsupported'}:
                raise IngestError(f'{label}.facts.reason is invalid')
            expected = {'reason'}
            self._require_subject(subject, label, mode='amendment')
            if len(locators) != 1:
                raise IngestError(f'{label} requires one amendment locator')
        elif code == 'touches_unresolved':
            if reason not in {'missing', 'unknown', 'ambiguous'}:
                raise IngestError(f'{label}.facts.reason is invalid')
            expected = {'reason', 'touch_ordinal', 'target_token'} | ({'definition_count'} if reason == 'ambiguous' else set())
            self._require_subject(subject, label, mode='amendment')
            ordinal = facts.get('touch_ordinal')
            if type(ordinal) is not int or (ordinal != 0 if reason == 'missing' else ordinal < 1):
                raise IngestError(f'{label}.facts.touch_ordinal is invalid')
            target = facts.get('target_token')
            if reason == 'missing':
                if target is not None:
                    raise IngestError(f'{label}.facts.target_token must be null')
            elif target is not None:
                self._safe_global_object_id(target, f'{label}.facts.target_token')
            if reason == 'ambiguous' and target is None:
                raise IngestError(f'{label}.facts.target_token must be canonical')
            if reason != 'ambiguous' and len(locators) != 1:
                raise IngestError(f'{label} requires one field locator')
        else:
            if reason not in {'missing', 'ambiguous'}:
                raise IngestError(f'{label}.facts.reason is invalid')
            expected = {'retired_object_id', 'reason', 'successor_count'}
            self._require_subject(subject, label, mode='amendment')
            retired_id = facts.get('retired_object_id')
            self._safe_global_object_id(retired_id, f'{label}.facts.retired_object_id')
            successor_count = facts.get('successor_count')
            if type(successor_count) is not int or (successor_count != 0 if reason == 'missing' else successor_count <= 1):
                raise IngestError(f'{label}.facts.successor_count is invalid')
            if reason == 'missing' and len(locators) != 1:
                raise IngestError(f'{label} missing reason requires one Touches locator')
        self._require_exact_keys(facts, expected, f'{label}.facts')
        if 'edge_candidate_key' in facts and (not isinstance(facts['edge_candidate_key'], str) or _SHA256.fullmatch(facts['edge_candidate_key']) is None):
            raise IngestError(f'{label}.facts.edge_candidate_key must be SHA-256')
        if 'definition_count' in facts:
            self._required_int_fact(facts, 'definition_count', f'{label}.facts', minimum=2)
        if not locators:
            raise IngestError(f'{label} requires at least one locator')

    def _diagnostic_record_order(self, record: dict) -> tuple:
        subject = record['subject_token']
        locator_tuple = tuple(((locator['document'], locator['line']) for locator in record['locators']))
        return (record['code'], subject is None, '' if subject is None else subject, locator_tuple, record['record_key'])

    def _validate_diagnostic_record(self, record, *, version: int, family: str) -> dict:
        label = f'diagnostic family {family} record'
        if not isinstance(record, dict):
            raise IngestError(f'{label} must be an object')
        self._require_exact_keys(record, {'record_key', 'code', 'family', 'subject_token', 'locators', 'facts', 'provenance'}, label)
        if record['family'] != family:
            raise IngestError(f'{label} has a mismatched family')
        if record['provenance'] != 'inferred':
            raise IngestError(f'{label}.provenance must be inferred')
        if not isinstance(record['locators'], list) or not record['locators']:
            raise IngestError(f'{label}.locators must be a non-empty array')
        if len(record['locators']) > _MAX_DIAGNOSTIC_LOCATORS:
            raise IngestError(f'{label}.locators exceeds its resource limit')
        locators = [self._validate_locator(locator, f'{label}.locators[{ordinal}]') for ordinal, locator in enumerate(record['locators'], start=1)]
        locator_keys = [(item['document'], item['line']) for item in locators]
        if locator_keys != sorted(set(locator_keys)):
            raise IngestError(f'{label}.locators must be sorted and deduplicated')
        if not isinstance(record['facts'], dict):
            raise IngestError(f'{label}.facts must be an object')
        facts = record['facts']
        code = record['code']
        codes = DIAGNOSTIC_V1_CODES if version == 1 else DIAGNOSTIC_C6_CODES
        if code not in codes:
            raise IngestError(f'{label}.code is unsupported for schema {version}')
        if code in DIAGNOSTIC_V1_CODES:
            self._validate_v1_diagnostic_record(code, record['subject_token'], locators, facts, label)
        elif version == 2:
            self._validate_v2_c6_record(code, record['subject_token'], locators, facts, label)
        else:
            self._validate_v3_c6_record(code, record['subject_token'], locators, facts, label)
        key = record['record_key']
        if not isinstance(key, str) or _SHA256.fullmatch(key) is None:
            raise IngestError(f'{label}.record_key must be 64 lowercase hex')
        preimage = {member: value for member, value in record.items() if member != 'record_key'}
        if hashlib.sha256(_canonical_json(preimage)).hexdigest() != key:
            raise IngestError(f'{label}.record_key does not match its canonical preimage')
        return record

    def _validate_diagnostic_coverage(self, manifest: dict, records: list[dict]) -> None:
        coverage = manifest['coverage']
        if not isinstance(coverage, dict):
            raise IngestError('diagnostic coverage must be an object')
        self._require_exact_keys(coverage, {'f18', 'f19', 'f20'}, 'diagnostic coverage')
        f18 = coverage['f18']
        f19 = coverage['f19']
        f20 = coverage['f20']
        if not all((isinstance(bucket, dict) for bucket in (f18, f19, f20))):
            raise IngestError('diagnostic coverage buckets must be objects')
        self._require_exact_keys(f18, {'eligible_documents', 'identified_documents', 'missing_document_ids', 'invalid_document_lifecycle'}, 'diagnostic coverage.f18')
        f18_counts = {key: self._nonnegative_int(value, f'diagnostic coverage.f18.{key}') for key, value in f18.items()}
        if f18_counts['eligible_documents'] - f18_counts['identified_documents'] != f18_counts['missing_document_ids']:
            raise IngestError('diagnostic F18 missing count is not eligible minus identified')
        self._require_exact_keys(f19, {'emitted_definitions', 'unique_definition_ids', 'duplicate_definition_ids', 'malformed_handles', 'status_counts'}, 'diagnostic coverage.f19')
        for key in ('emitted_definitions', 'unique_definition_ids', 'duplicate_definition_ids', 'malformed_handles'):
            self._nonnegative_int(f19[key], f'diagnostic coverage.f19.{key}')
        status_counts = self._count_map(f19['status_counts'], 'diagnostic coverage.f19.status_counts')
        if set(status_counts) != {'open', 'pending_ratification', 'resolved', 'unknown'}:
            raise IngestError('diagnostic F19 status_counts has an invalid key set')
        if sum(status_counts.values()) != f19['emitted_definitions']:
            raise IngestError('diagnostic F19 status counts do not equal definitions')
        self._require_exact_keys(f20, {'diagnostic_records'}, 'diagnostic coverage.f20')
        self._nonnegative_int(f20['diagnostic_records'], 'diagnostic coverage.f20.diagnostic_records')
        code_counts = manifest['code_counts']
        if f18_counts['missing_document_ids'] != code_counts['document_id_missing']:
            raise IngestError('diagnostic F18 missing count disagrees with records')
        if f18_counts['invalid_document_lifecycle'] != code_counts['invalid_document_lifecycle']:
            raise IngestError('diagnostic F18 lifecycle count disagrees with records')
        if f19['duplicate_definition_ids'] != code_counts['open_question_definition_duplicate']:
            raise IngestError('diagnostic F19 duplicate count disagrees with records')
        if f19['malformed_handles'] != code_counts['malformed_open_question_handle']:
            raise IngestError('diagnostic F19 malformed count disagrees with records')
        if f20['diagnostic_records'] != sum((code_counts[code] for code in ERRATA_DIAGNOSTIC_CODES)):
            raise IngestError('diagnostic F20 count disagrees with records')

    def _load_diagnostic_index(self, index_dir: pathlib.Path) -> tuple[dict, dict[str, dict], str, list[dict], dict]:
        manifest_path = index_dir / MANIFEST
        if not manifest_path.exists():
            raise IngestError(f'no {MANIFEST} in {index_dir} — is the diagnostic index committed?')
        manifest, manifest_bytes = self._read_canonical_diagnostic_json(manifest_path, label='diagnostic manifest', byte_limit=_MAX_DIAGNOSTIC_MANIFEST_BYTES)
        self._require_exact_keys(manifest, {'schema_version', 'families', 'total_records', 'code_counts', 'coverage'}, 'diagnostic manifest')
        version = manifest['schema_version']
        if type(version) is not int or version not in SUPPORTED_DIAGNOSTIC_SCHEMA_VERSIONS:
            raise IngestError(f'diagnostic schema_version {version} unsupported (this build understands {sorted(SUPPORTED_DIAGNOSTIC_SCHEMA_VERSIONS)})')
        descriptors = manifest['families']
        if not isinstance(descriptors, list):
            raise IngestError('diagnostic manifest families must be an array')
        expected_codes = DIAGNOSTIC_V1_CODES if version == 1 else DIAGNOSTIC_C6_CODES
        code_counts = self._count_map(manifest['code_counts'], 'diagnostic code_counts')
        if set(code_counts) != set(expected_codes):
            raise IngestError('diagnostic code_counts keys are not the exact profile')
        families: dict[str, dict] = {}
        all_records: list[dict] = []
        total_bytes = len(manifest_bytes)
        descriptor_names: list[str] = []
        for ordinal, descriptor in enumerate(descriptors, start=1):
            label = f'diagnostic family descriptor {ordinal}'
            if not isinstance(descriptor, dict):
                raise IngestError(f'{label} must be an object')
            self._require_exact_keys(descriptor, {'family', 'filename', 'record_count', 'sha256'}, label)
            family = descriptor['family']
            if not isinstance(family, str) or not family or family in {'.', '..'} or (pathlib.PurePosixPath(family).name != family) or ('\\' in family):
                raise IngestError(f'{label}.family is unsafe')
            if descriptor['filename'] != f'{family}.json':
                raise IngestError(f'{label}.filename does not match its family')
            count = self._nonnegative_int(descriptor['record_count'], f'{label}.record_count')
            sha256 = descriptor['sha256']
            if not isinstance(sha256, str) or _SHA256.fullmatch(sha256) is None:
                raise IngestError(f'{label}.sha256 must be 64 lowercase hex')
            path = index_dir / descriptor['filename']
            payload, family_bytes = self._read_canonical_diagnostic_json(path, label=f'diagnostic family {family}', byte_limit=_MAX_DIAGNOSTIC_FAMILY_BYTES)
            total_bytes += len(family_bytes)
            if total_bytes > _MAX_DIAGNOSTIC_PROJECTION_BYTES:
                raise IngestError('diagnostic projection exceeds its byte limit')
            if hashlib.sha256(family_bytes).hexdigest() != sha256:
                raise IngestError(f'diagnostic family {family} SHA-256 mismatch')
            self._require_exact_keys(payload, {'schema_version', 'family', 'record_count', 'records'}, f'diagnostic family {family}')
            if payload['schema_version'] != version or payload['family'] != family:
                raise IngestError(f'diagnostic family {family} envelope mismatch')
            if not isinstance(payload['records'], list):
                raise IngestError(f'diagnostic family {family}.records must be an array')
            if count != len(payload['records']) or payload['record_count'] != count:
                raise IngestError(f'diagnostic family {family} record_count mismatch')
            records = [self._validate_diagnostic_record(record, version=version, family=family) for record in payload['records']]
            if records != sorted(records, key=self._diagnostic_record_order):
                raise IngestError(f'diagnostic family {family} records are not sorted')
            families[family] = payload
            all_records.extend(records)
            descriptor_names.append(family)
        if descriptor_names != sorted(set(descriptor_names)):
            raise IngestError('diagnostic family descriptors must be sorted and unique')
        if len(all_records) > _MAX_DIAGNOSTIC_RECORDS:
            raise IngestError('diagnostic projection exceeds its record limit')
        record_keys = [record['record_key'] for record in all_records]
        if len(record_keys) != len(set(record_keys)):
            raise IngestError('diagnostic projection contains a duplicate record')
        total_records = self._nonnegative_int(manifest['total_records'], 'diagnostic total_records')
        if total_records != len(all_records) or total_records != sum((descriptor['record_count'] for descriptor in descriptors)):
            raise IngestError('diagnostic manifest total_records mismatch')
        observed_code_counts = collections.Counter((record['code'] for record in all_records))
        if code_counts != {code: observed_code_counts.get(code, 0) for code in expected_codes}:
            raise IngestError('diagnostic manifest code_counts mismatch')
        self._validate_diagnostic_coverage(manifest, all_records)
        digest = hashlib.sha256(manifest_bytes).hexdigest()
        payload = {'manifest': manifest, 'records': all_records}
        return (manifest, families, digest, all_records, payload)

    def _validate_projection_agreement(self, object_families: dict[str, dict], location_rows: list[tuple[str, dict, dict, str]], location_families: dict[str, dict]) -> None:
        """Require one matching document/lifecycle fact across both projections."""
        object_documents: dict[str, tuple[str, str, str]] = {}
        for envelope_family, payload in sorted(object_families.items()):
            for obj in payload['objects']:
                if obj['kind'] != 'document':
                    continue
                document_id = obj['obj_id']
                if document_id in object_documents:
                    raise IngestError(f'object index contains duplicate document id {document_id}')
                attrs = obj.get('attrs') or {}
                provenance = attrs.get('attr_provenance') or {}
                lifecycle = attrs.get('lifecycle_state')
                lifecycle_provenance = provenance.get('lifecycle_state')
                if not isinstance(lifecycle, str) or not isinstance(lifecycle_provenance, str):
                    raise IngestError(f'object document {document_id} lacks lifecycle provenance')
                object_documents[document_id] = (obj.get('family', envelope_family), lifecycle, lifecycle_provenance)
        location_documents: dict[str, tuple[str, str, str]] = {}
        for family, payload in sorted(location_families.items()):
            for document in payload['documents']:
                location_documents[document['document_id']] = (family, document['lifecycle_state'], document['attr_provenance']['lifecycle_state'])
        object_ids = set(object_documents)
        location_ids = set(location_documents)
        if object_ids != location_ids:
            missing_locations = sorted(object_ids - location_ids)
            missing_objects = sorted(location_ids - object_ids)
            detail = []
            if missing_locations:
                detail.append(f"documents without locations: {', '.join(missing_locations)}")
            if missing_objects:
                detail.append(f"locations without documents: {', '.join(missing_objects)}")
            raise IngestError('object/location document identity mismatch (' + '; '.join(detail) + ')')
        for document_id in sorted(object_ids):
            if object_documents[document_id] != location_documents[document_id]:
                raise IngestError(f'object/location lifecycle or family mismatch for document {document_id}')
        expected_record_count = sum((len(document['locations']) for payload in location_families.values() for document in payload['documents']))
        if len(location_rows) != expected_record_count:
            raise IngestError('location rows were not fully validated')

    def _validate_diagnostic_agreement(self, object_manifest: dict, object_families: dict[str, dict], validated_edges: list[dict], location_manifest: dict, location_families: dict[str, dict], diagnostic_manifest: dict, diagnostic_families: dict[str, dict], diagnostic_records: list[dict]) -> None:
        """Bind diagnostic-v3 coverage and omission evidence to the same triple."""
        object_family_names = set(object_manifest['families'])
        location_family_names = set(location_manifest['families'])
        diagnostic_family_names = set(diagnostic_families)
        if set(object_families) != object_family_names or set(location_families) != location_family_names:
            raise IngestError('projection family payloads do not match their manifests')
        if not object_family_names.issubset(diagnostic_family_names):
            raise IngestError('diagnostic manifest omits an object-bearing family')
        if not location_family_names.issubset(object_family_names):
            raise IngestError('location manifest names a family absent from objects')
        objects = [obj for payload in object_families.values() for obj in payload['objects']]
        object_candidates: dict[str, list[dict]] = collections.defaultdict(list)
        document_owners: dict[str, list[dict]] = collections.defaultdict(list)
        definition_owners: dict[tuple[str, int], list[dict]] = collections.defaultdict(list)
        for obj in objects:
            object_candidates[obj['obj_id']].append(obj)
            definition_owners[obj['doc'], obj['line']].append(obj)
            if obj['kind'] == 'document':
                document_owners[obj['doc']].append(obj)
        documents = [obj for obj in objects if obj['kind'] == 'document']
        f18 = diagnostic_manifest['coverage']['f18']
        if f18['identified_documents'] != len(documents):
            raise IngestError('diagnostic F18 identified count disagrees with objects')
        if f18['identified_documents'] != location_manifest['total_documents']:
            raise IngestError('diagnostic F18 identified count disagrees with locations')
        open_questions = [obj for obj in objects if obj['kind'] == 'open_question']
        open_question_ids = collections.Counter((obj['obj_id'] for obj in open_questions))
        f19 = diagnostic_manifest['coverage']['f19']
        if f19['emitted_definitions'] != len(open_questions):
            raise IngestError('diagnostic F19 definition count disagrees with objects')
        if f19['unique_definition_ids'] != len(open_question_ids):
            raise IngestError('diagnostic F19 unique id count disagrees with objects')
        if f19['duplicate_definition_ids'] != sum((1 for count in open_question_ids.values() if count > 1)):
            raise IngestError('diagnostic F19 duplicate id count disagrees with objects')
        observed_statuses: collections.Counter[str] = collections.Counter()
        for obj in open_questions:
            status = obj['attrs'].get('status')
            if status not in {'open', 'pending_ratification', 'resolved', 'unknown'}:
                raise IngestError('object open-question status is outside the closed enum')
            observed_statuses[status] += 1
        if f19['status_counts'] != {status: observed_statuses.get(status, 0) for status in ('open', 'pending_ratification', 'resolved', 'unknown')}:
            raise IngestError('diagnostic F19 status counts disagree with objects')
        valid_candidate_keys = {hashlib.sha256(_canonical_json({'locator': {'document': edge['citation_document'], 'line': edge['line']}, 'target_token': edge['target']})).hexdigest() for edge in validated_edges}

        def locator_key(locator: dict) -> tuple[str, int]:
            return (locator['document'], locator['line'])

        def resolution_status(token: str) -> str:
            candidates = object_candidates.get(token, [])
            if not candidates:
                return 'missing'
            if len(candidates) > 1:
                return 'ambiguous'
            candidate = candidates[0]
            endpoint = {'family': candidate['family'], 'object_id': candidate['obj_id'], 'definition': {'document': candidate['doc'], 'line': candidate['line']}}
            try:
                self._validate_v3_endpoint(endpoint, label='diagnostic endpoint', object_candidates=object_candidates, document_owners=document_owners)
            except IngestError:
                return 'invalid'
            if candidate['kind'] == 'invariant':
                return 'registry_indeterminate'
            return 'resolved'

        def candidate_locator_for(record: dict, target_token: str | None) -> tuple[str, int]:
            expected_key = record['facts']['edge_candidate_key']
            matches = [locator_key(locator) for locator in record['locators'] if hashlib.sha256(_canonical_json({'locator': locator, 'target_token': target_token})).hexdigest() == expected_key]
            if len(matches) != 1:
                raise IngestError('diagnostic edge_candidate_key does not identify one candidate locator')
            return matches[0]
        candidate_evidence: dict[str, tuple[tuple[str, int], str | None]] = {}
        for record in diagnostic_records:
            if record['code'] != 'dependency_target_unresolved':
                continue
            evidence = (candidate_locator_for(record, record['subject_token']), record['subject_token'])
            key = record['facts']['edge_candidate_key']
            previous = candidate_evidence.get(key)
            if previous is not None and previous != evidence:
                raise IngestError('diagnostic candidate evidence disagrees across records')
            candidate_evidence[key] = evidence

        def require_candidate_only_agreement(record: dict) -> None:
            evidence = candidate_evidence.get(record['facts']['edge_candidate_key'])
            if evidence is not None and {locator_key(item) for item in record['locators']} != {evidence[0]}:
                raise IngestError('candidate-only diagnostic has the wrong locator')

        def require_definition_evidence(record: dict, object_id: str, *, label: str, candidate_locator: tuple[str, int] | None=None, context_document: str | None=None) -> None:
            definitions = object_candidates.get(object_id, [])
            definition_keys = {(candidate['doc'], candidate['line']) for candidate in definitions}
            record_keys = {locator_key(locator) for locator in record['locators']}
            if candidate_locator is not None:
                expected = definition_keys | {candidate_locator}
                if record_keys != expected:
                    raise IngestError(f'{label} locator set disagrees with definitions')
                return
            extras = record_keys - definition_keys
            if len(extras) > 1 or not definition_keys.issubset(record_keys):
                raise IngestError(f'{label} locator set disagrees with definitions')
            if context_document is not None:
                if not extras:
                    raise IngestError(f'{label} omits its field locator')
                if next(iter(extras))[0] != context_document:
                    raise IngestError(f'{label} field locator has the wrong document')
        inferred_edges: dict[tuple[str, str, str], list[dict]] = collections.defaultdict(list)
        touch_field_locators: dict[str, set[tuple[str, int]]] = collections.defaultdict(set)
        for edge in validated_edges:
            if edge['kind_provenance'] != 'inferred':
                continue
            inferred_edges[edge['edge_type'], edge['source'], edge['target']].append(edge)
            if edge['edge_type'] == 'amends':
                touch_field_locators[edge['source']].add((edge['citation_document'], edge['line']))

        def exact_touch_field_locator(amendment_id: str) -> tuple[str, int] | None:
            locators = touch_field_locators.get(amendment_id, set())
            if len(locators) > 1:
                raise IngestError('inferred amends edges disagree on the exact Touches field locator')
            return next(iter(locators), None)

        def is_exact_invalid_target_diagnostic(record: dict, target: dict, subject_token: str | None) -> bool:
            locator = {'document': target['doc'], 'line': target['line']}
            candidate_key = hashlib.sha256(_canonical_json({'locator': locator, 'target_token': subject_token})).hexdigest()
            return record['family'] == target['family'] and record['code'] == 'dependency_target_unresolved' and (record['subject_token'] == subject_token) and (record['locators'] == [locator]) and (record['facts'] == {'edge_candidate_key': candidate_key, 'reason': 'invalid'})

        def exact_invalid_target_diagnostics(target: dict, subject_token: str | None) -> list[dict]:
            return [record for record in diagnostic_records if is_exact_invalid_target_diagnostic(record, target, subject_token)]

        def is_deferred_invariant_defines_conflict(record: dict) -> bool:
            subject = record['subject_token']
            candidates = object_candidates.get(subject, [])
            if len(candidates) != 1 or candidates[0]['kind'] != 'invariant':
                return False
            target = candidates[0]
            owners = document_owners.get(target['doc'], [])
            if len(owners) != 1 or owners[0]['obj_id'] == target['obj_id']:
                return False
            defines = inferred_edges['defines', owners[0]['obj_id'], target['obj_id']]
            return bool(defines) and is_exact_invalid_target_diagnostic(record, target, target['obj_id'])
        for record in diagnostic_records:
            facts = record['facts']
            candidate_key = facts.get('edge_candidate_key')
            if candidate_key in valid_candidate_keys and (not is_deferred_invariant_defines_conflict(record)):
                raise IngestError('diagnostic record masks an otherwise valid edge')
            reason = facts.get('reason')
            subject = record['subject_token']
            record_locator_keys = {(locator['document'], locator['line']) for locator in record['locators']}
            if record['code'] == 'dependency_source_unresolved' and reason == 'global_identity_ambiguous':
                if facts['definition_count'] != len(object_candidates[subject]):
                    raise IngestError('source ambiguity count disagrees with objects')
                evidence = candidate_evidence.get(candidate_key)
                require_definition_evidence(record, subject, label='source ambiguity', candidate_locator=evidence[0] if evidence else None)
            elif record['code'] == 'dependency_source_unresolved' and reason == 'ambiguous_definition_line':
                if len(record_locator_keys) != 1 or len(definition_owners[next(iter(record_locator_keys))]) != facts['definition_count']:
                    raise IngestError('definition-line ambiguity count disagrees with objects')
            elif record['code'] == 'dependency_source_unresolved' and reason == 'ambiguous_document':
                matching_documents = set((document for document, _line in record_locator_keys))
                if len(matching_documents) != 1:
                    raise IngestError('document ambiguity count disagrees with objects')
                document = next(iter(matching_documents))
                definitions = document_owners.get(document, [])
                expected_definition_keys = {(obj['doc'], obj['line']) for obj in definitions}
                if len(definitions) != facts['definition_count'] or not expected_definition_keys.issubset(record_locator_keys) or len(record_locator_keys - expected_definition_keys) > 1:
                    raise IngestError('document ambiguity locator set disagrees with objects')
            elif record['code'] == 'dependency_source_unresolved' and reason in {'missing', 'invalid'}:
                require_candidate_only_agreement(record)
                observed = resolution_status(subject) if subject is not None else None
                if subject is not None and (not (observed == reason or (reason == 'invalid' and observed == 'registry_indeterminate'))):
                    raise IngestError(f'source {reason} diagnostic disagrees with objects')
            elif record['code'] == 'dependency_source_unresolved' and reason == 'missing_document':
                require_candidate_only_agreement(record)
                candidate_document = record['locators'][0]['document']
                if document_owners.get(candidate_document):
                    raise IngestError('missing-document diagnostic has a document owner')
            elif record['code'] == 'dependency_target_unresolved' and reason == 'ambiguous':
                if facts['definition_count'] != len(object_candidates[subject]):
                    raise IngestError('target ambiguity count disagrees with objects')
                candidate_locator = candidate_locator_for(record, subject)
                require_definition_evidence(record, subject, label='target ambiguity', candidate_locator=candidate_locator)
            elif record['code'] == 'dependency_target_unresolved' and reason in {'missing', 'invalid'}:
                candidate_locator_for(record, subject)
                if subject is not None:
                    observed = resolution_status(subject)
                    if reason == 'missing' and observed != 'missing':
                        raise IngestError('missing target exists in object projection')
                    if reason == 'invalid' and observed not in {'invalid', 'registry_indeterminate'}:
                        raise IngestError('invalid target diagnostic disagrees with objects')
            elif record['code'] == 'dependency_kind_unresolved':
                require_candidate_only_agreement(record)
            elif record['code'] == 'touches_unresolved' and reason == 'ambiguous':
                target = facts['target_token']
                if facts['definition_count'] != len(object_candidates[target]):
                    raise IngestError('Touches ambiguity count disagrees with objects')
            if record['code'] in {'change_kind_unresolved', 'touches_unresolved', 'retirement_supersedes_missing'}:
                candidates = object_candidates.get(subject, [])
                if len(candidates) != 1 or candidates[0]['kind'] != 'amendment' or candidates[0]['family'] != record['family']:
                    raise IngestError('amendment diagnostic does not resolve in its envelope family')
                amendments = candidates
                amendment = amendments[0]
                attrs = amendment['attrs']
                if record['code'] in {'change_kind_unresolved', 'touches_unresolved'} and reason == 'missing':
                    definition = {'document': amendments[0]['doc'], 'line': amendments[0]['line']}
                    if record['locators'] != [definition]:
                        raise IngestError('missing amendment-field diagnostic has wrong definition locator')
                if record['code'] == 'change_kind_unresolved':
                    change_kind = attrs.get('change_kind')
                    if reason == 'missing' and change_kind:
                        raise IngestError('change_kind is present despite missing diagnostic')
                    if reason == 'unsupported' and (not change_kind or change_kind in CHANGE_KINDS):
                        raise IngestError('unsupported change_kind diagnostic disagrees with attrs')
                    if record['locators'][0]['document'] != amendment['doc']:
                        raise IngestError('change_kind diagnostic has the wrong document')
                elif record['code'] == 'touches_unresolved':
                    touches = attrs.get('touches')
                    nonempty_touches = [member for member in touches if isinstance(member, str) and member] if isinstance(touches, list) else []
                    if reason == 'missing':
                        if attrs.get('change_kind') not in TOUCHES_REQUIRED_CHANGE_KINDS:
                            raise IngestError('Touches missing diagnostic has no required change kind')
                        if nonempty_touches:
                            raise IngestError('Touches contains a target despite missing diagnostic')
                    else:
                        if record['locators'][0]['document'] != amendment['doc'] and reason != 'ambiguous':
                            raise IngestError('Touches diagnostic has the wrong field document')
                        target = facts['target_token']
                        ordinal = facts['touch_ordinal']
                        if not isinstance(touches, list) or ordinal > len(touches):
                            raise IngestError('Touches diagnostic ordinal disagrees with attrs')
                        member = touches[ordinal - 1]
                        canonical_member = None
                        if isinstance(member, str) and member:
                            try:
                                canonical_member = self._safe_global_object_id(member, 'amendment Touches member')
                            except IngestError:
                                canonical_member = None
                        if target is None and canonical_member is not None:
                            raise IngestError('Touches diagnostic target disagrees with its ordinal member')
                        if target is not None:
                            if member != target:
                                raise IngestError('Touches diagnostic ordinal disagrees with attrs')
                            if target not in nonempty_touches:
                                raise IngestError('Touches diagnostic target is absent from attrs')
                            observed = resolution_status(target)
                            if reason == 'unknown':
                                if observed not in {'missing', 'invalid', 'registry_indeterminate'}:
                                    raise IngestError('Touches unknown diagnostic disagrees with objects')
                                if attrs.get('change_kind') == 'retirement' and observed == 'missing':
                                    raise IngestError('parent-resolved retirement target cannot be unknown')
                            elif observed != 'ambiguous':
                                raise IngestError('Touches ambiguity disagrees with objects')
                        if reason == 'ambiguous':
                            require_definition_evidence(record, target, label='Touches ambiguity', context_document=amendment['doc'])
                        expected_field_locator = exact_touch_field_locator(subject)
                        if expected_field_locator is not None:
                            if reason == 'ambiguous':
                                definition_keys = {(candidate['doc'], candidate['line']) for candidate in object_candidates.get(target, [])}
                                field_locators = record_locator_keys - definition_keys
                                actual_field_locator = next(iter(field_locators))
                            else:
                                actual_field_locator = next(iter(record_locator_keys))
                            if actual_field_locator != expected_field_locator:
                                raise IngestError('Touches diagnostic field locator disagrees with inferred edges')
                        if canonical_member is not None and inferred_edges['amends', subject, canonical_member]:
                            raise IngestError('Touches diagnostic contradicts an inferred amends edge')
            if record['code'] == 'retirement_supersedes_missing':
                retired_id = facts['retired_object_id']
                amendment = object_candidates[subject][0]
                if amendment['attrs'].get('change_kind') != 'retirement':
                    raise IngestError('retirement diagnostic requires ChangeKind retirement')
                touches = amendment['attrs'].get('touches')
                if not isinstance(touches, list) or retired_id not in touches:
                    raise IngestError('retirement diagnostic amendment must name the retired target')
                if resolution_status(retired_id) not in {'resolved', 'registry_indeterminate'}:
                    raise IngestError('retirement diagnostic target must resolve once in this snapshot')
                successors = {edge['source'] for edge in validated_edges if edge['edge_type'] == 'supersedes' and edge['kind_provenance'] == 'declared' and (edge['target'] == retired_id)}
                if facts['successor_count'] != len(successors):
                    raise IngestError('retirement diagnostic successor count disagrees with edges')
                if (reason == 'missing') != (not successors):
                    raise IngestError('retirement diagnostic reason disagrees with successors')
                touches_edges = [edge for edge in validated_edges if edge['edge_type'] == 'amends' and edge['kind_provenance'] == 'inferred' and (edge['source'] == subject) and (edge['target'] == retired_id)]
                if len(touches_edges) != 1:
                    raise IngestError('retirement diagnostic lacks one Touches edge')
                successor_locators = {(edge['citation_document'], edge['line']) for edge in validated_edges if edge['edge_type'] == 'supersedes' and edge['kind_provenance'] == 'declared' and (edge['target'] == retired_id)}
                diagnostic_locators = {(locator['document'], locator['line']) for locator in record['locators']}
                expected_locators = successor_locators | {(touches_edges[0]['citation_document'], touches_edges[0]['line'])}
                if diagnostic_locators != expected_locators:
                    raise IngestError('retirement diagnostic locator set disagrees with edge evidence')

        def matching_diagnostics(*, code: str, subject: str, reason: str, touch_ordinal: int | None=None, target_token: str | None=None, retired_object_id: str | None=None, successor_count: int | None=None) -> list[dict]:
            matches = []
            for record in diagnostic_records:
                if record['code'] != code or record['subject_token'] != subject or record['facts'].get('reason') != reason:
                    continue
                facts = record['facts']
                if touch_ordinal is not None and facts.get('touch_ordinal') != touch_ordinal:
                    continue
                if touch_ordinal is not None and facts.get('target_token') != target_token:
                    continue
                if retired_object_id is not None and facts.get('retired_object_id') != retired_object_id:
                    continue
                if successor_count is not None and facts.get('successor_count') != successor_count:
                    continue
                matches.append(record)
            return matches

        def require_one_diagnostic(message: str, **criteria) -> None:
            if len(matching_diagnostics(**criteria)) != 1:
                raise IngestError(message)

        def endpoint_is_mechanically_valid(obj: dict, label: str) -> bool:
            if len(object_candidates[obj['obj_id']]) != 1:
                return False
            endpoint = {'family': obj['family'], 'object_id': obj['obj_id'], 'definition': {'document': obj['doc'], 'line': obj['line']}}
            try:
                self._validate_v3_endpoint(endpoint, label=label, object_candidates=object_candidates, document_owners=document_owners)
            except IngestError:
                return False
            return True

        def require_linked_motivates(amendment: dict, target_id: str, amends_edge: dict) -> None:
            rationale_id = f"{amendment['obj_id']}#rationale"
            rationales = object_candidates.get(rationale_id, [])
            if len(rationales) != 1 or rationales[0]['kind'] != 'rationale':
                return
            rationale = rationales[0]
            if not endpoint_is_mechanically_valid(rationale, 'linked rationale coverage endpoint'):
                return
            motivates = inferred_edges['motivates', rationale_id, target_id]
            if len(motivates) != 1:
                raise IngestError('required inferred motivates edge is missing')
            if (motivates[0]['citation_document'], motivates[0]['line']) != (amends_edge['citation_document'], amends_edge['line']):
                raise IngestError('inferred motivates edge disagrees with the exact Touches field locator')
        for amendment in objects:
            if amendment['kind'] != 'amendment':
                continue
            if not endpoint_is_mechanically_valid(amendment, 'amendment coverage endpoint'):
                continue
            attrs = amendment['attrs']
            change_kind = attrs.get('change_kind')
            if not change_kind:
                require_one_diagnostic('required change_kind diagnostic is missing', code='change_kind_unresolved', subject=amendment['obj_id'], reason='missing')
                continue
            if not isinstance(change_kind, str) or change_kind not in CHANGE_KINDS:
                require_one_diagnostic('required change_kind diagnostic is missing', code='change_kind_unresolved', subject=amendment['obj_id'], reason='unsupported')
            touches = attrs.get('touches')
            nonempty_touches = [member for member in touches if isinstance(member, str) and member] if isinstance(touches, list) else []
            if change_kind in TOUCHES_REQUIRED_CHANGE_KINDS and (not nonempty_touches):
                require_one_diagnostic('required Touches diagnostic is missing', code='touches_unresolved', subject=amendment['obj_id'], reason='missing', touch_ordinal=0, target_token=None)
                continue
            if not isinstance(touches, list):
                continue
            current_retirement_targets: set[str] = set()
            for ordinal, target in enumerate(touches, start=1):
                canonical_target: str | None = None
                if isinstance(target, str) and target:
                    try:
                        canonical_target = self._safe_global_object_id(target, 'amendment Touches member')
                    except IngestError:
                        canonical_target = None
                if canonical_target is None:
                    require_one_diagnostic('required Touches diagnostic is missing', code='touches_unresolved', subject=amendment['obj_id'], reason='unknown', touch_ordinal=ordinal, target_token=None)
                    continue
                status = resolution_status(canonical_target)
                edges = inferred_edges['amends', amendment['obj_id'], canonical_target]
                if status == 'resolved':
                    if len(edges) != 1:
                        raise IngestError('required inferred amends edge is missing')
                    require_linked_motivates(amendment, canonical_target, edges[0])
                    if change_kind == 'retirement':
                        current_retirement_targets.add(canonical_target)
                    continue
                if status == 'registry_indeterminate' and len(edges) == 1:
                    require_linked_motivates(amendment, canonical_target, edges[0])
                    if change_kind == 'retirement':
                        current_retirement_targets.add(canonical_target)
                    continue
                if status == 'registry_indeterminate':
                    if len(matching_diagnostics(code='touches_unresolved', subject=amendment['obj_id'], reason='unknown', touch_ordinal=ordinal, target_token=canonical_target)) != 1:
                        raise IngestError('required inferred amends edge is missing')
                    continue
                if status == 'missing' and change_kind == 'retirement':
                    continue
                reason = 'ambiguous' if status == 'ambiguous' else 'unknown'
                require_one_diagnostic('required Touches diagnostic is missing', code='touches_unresolved', subject=amendment['obj_id'], reason=reason, touch_ordinal=ordinal, target_token=canonical_target)
            if change_kind != 'retirement':
                continue
            for retired_id in current_retirement_targets:
                successors = {edge['source'] for edge in validated_edges if edge['edge_type'] == 'supersedes' and edge['kind_provenance'] == 'declared' and (edge['target'] == retired_id)}
                if len(successors) == 1:
                    continue
                reason = 'missing' if not successors else 'ambiguous'
                require_one_diagnostic('required retirement diagnostic is missing', code='retirement_supersedes_missing', subject=amendment['obj_id'], reason=reason, retired_object_id=retired_id, successor_count=len(successors))
        for target in objects:
            if len(object_candidates[target['obj_id']]) != 1:
                continue
            owners = document_owners.get(target['doc'], [])
            if len(owners) != 1:
                continue
            owner = owners[0]
            if owner['obj_id'] == target['obj_id']:
                continue
            if not endpoint_is_mechanically_valid(owner, 'defines coverage source'):
                continue
            if not endpoint_is_mechanically_valid(target, 'defines coverage target'):
                if len(exact_invalid_target_diagnostics(target, None)) != 1:
                    raise IngestError('required invalid defines-target diagnostic is missing')
                continue
            defines = inferred_edges['defines', owner['obj_id'], target['obj_id']]
            status = resolution_status(target['obj_id'])
            if status == 'registry_indeterminate':
                diagnostics = exact_invalid_target_diagnostics(target, target['obj_id'])
                if defines and diagnostics:
                    raise IngestError('defines edge and target-invalid diagnostic are mutually exclusive')
                if len(defines) == 1 or (not defines and len(diagnostics) == 1):
                    continue
                raise IngestError('required inferred defines edge or invariant diagnostic is missing')
            if len(defines) != 1:
                raise IngestError('required inferred defines edge is missing')

    def _load_object_index(self, index_dir: pathlib.Path) -> tuple[dict, dict[str, dict], str, list[dict]]:
        manifest, families, digest = self._read_projection(index_dir, label='object', supported_versions=SUPPORTED_SCHEMA_VERSIONS)
        edges = self._validate_object_index(manifest, families)
        return (manifest, families, digest, edges)

    def _load_location_index(self, index_dir: pathlib.Path) -> tuple[dict, dict[str, dict], str, list[tuple[str, dict, dict, str]]]:
        manifest, families, digest = self._read_projection(index_dir, label='location', supported_versions=SUPPORTED_LOCATION_SCHEMA_VERSIONS)
        rows = self.validate_location_projection(manifest, families)
        return (manifest, families, digest, rows)

    def load_index(self, index_dir: pathlib.Path) -> tuple[dict, dict]:
        """Read and validate a retained-v2 or current-v3 object projection."""
        manifest, families, _digest, _edges = self._load_object_index(index_dir)
        return (manifest, families)

    def load_location_index(self, index_dir: pathlib.Path) -> tuple[dict, dict]:
        """Read and validate schema-v1 location family files."""
        manifest, families, _digest, _rows = self._load_location_index(index_dir)
        return (manifest, families)

    def load_diagnostic_index(self, index_dir: pathlib.Path) -> tuple[dict, dict]:
        """Read immutable diagnostic schema v1/v2 or current schema v3 bytes."""
        manifest, families, _digest, _records, _payload = self._load_diagnostic_index(pathlib.Path(index_dir))
        return (manifest, families)
