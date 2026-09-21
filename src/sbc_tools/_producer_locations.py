"""Pinned pure parser extraction. Reproduce with tools/extract_document_parser.py.
Source blob: 31217a012c99785cd0bda3cae3a3d9feb3cf33d5.
"""
from __future__ import annotations
import io
import collections
import dataclasses
import hashlib
import json
import pathlib
import re
import urllib.parse
import zipfile
RE_HEADER_ATTR = re.compile('^\\*\\*([A-Za-z][A-Za-z ]{2,40}):\\*\\*\\s*(.*)$')
RE_H1 = re.compile('^#\\s+(.+?)\\s*$')
RE_H2 = re.compile('^##(?:\\s|$)')
RE_HORIZONTAL_RULE = re.compile('^\\s*(?:---+|___+|\\*\\*\\*+)\\s*$')
DOCUMENT_LIFECYCLE_STATES = {'draft', 'ratified', 'executing', 'execution_complete', 'handoff_eligible', 'handed_off', 'superseded', 'abandoned', 'unknown'}
_STATUS_TO_LIFECYCLE = (('EXECUTION COMPLETE', 'execution_complete'), ('HANDOFF ELIGIBLE', 'handoff_eligible'), ('HANDED OFF', 'handed_off'), ('SUPERSEDED', 'superseded'), ('ABANDONED', 'abandoned'), ('EXECUTING', 'executing'), ('RATIFIED', 'ratified'), ('DRAFT', 'draft'))

def parse_markdown_header(lines: list[str]) -> tuple[dict, dict, str]:
    """Return ``(attributes, line_numbers, title)`` from the governed header.

    The normal authored form starts with one H1, followed by bold metadata.
    Blank lines are permitted. The header ends at a horizontal rule, an H2,
    or the first nonblank non-attribute line. Metadata-looking body prose is
    therefore never absorbed into authority state.
    """
    attributes: dict[str, str] = {}
    line_numbers: dict[str, int] = {}
    title = ''
    saw_h1 = False
    for lineno, line in enumerate(lines, start=1):
        if not saw_h1:
            if not line.strip():
                continue
            match = RE_H1.match(line)
            if not match:
                return (attributes, line_numbers, title)
            title = match.group(1).strip()
            saw_h1 = True
            continue
        if not line.strip():
            continue
        if RE_HORIZONTAL_RULE.match(line) or RE_H2.match(line):
            break
        match = RE_HEADER_ATTR.match(line)
        if not match:
            break
        key = match.group(1).strip().lower()
        attributes[key] = match.group(2).strip()
        line_numbers[key] = lineno
    return (attributes, line_numbers, title)

def _normalize_explicit_lifecycle(value: str) -> str:
    return re.sub('[\\s-]+', '_', value.strip().lower())

def resolve_lifecycle(header: dict) -> tuple[str, str, bool]:
    """Return lifecycle value, provenance, and declaration validity.

    Explicit ``Document lifecycle state`` wins. Otherwise only the closed,
    leading-token Status mapping ratified by PCDN-SIDX-06A-006 is used.
    ``bool`` is false only when an explicit declaration uses an unknown value.
    """
    explicit = header.get('document lifecycle state')
    if explicit is not None:
        normalized = _normalize_explicit_lifecycle(explicit)
        if normalized in DOCUMENT_LIFECYCLE_STATES:
            return (normalized, 'declared', True)
        return ('unknown', 'declared', False)
    raw_status = header.get('status', '')
    status = raw_status.strip().lstrip('*_`').upper()
    for token, lifecycle in _STATUS_TO_LIFECYCLE:
        if status == token or (status.startswith(token) and len(status) > len(token) and (not (status[len(token)].isalnum() or status[len(token)] == '_'))):
            return (lifecycle, 'inferred', True)
    return ('unknown', 'inferred', True)

def split_markdown_row(line: str) -> list[str] | None:
    """Split a simple Markdown table row used by the governed declarations."""
    if not line.lstrip().startswith('|'):
        return None
    return [cell.strip() for cell in line.strip().strip('|').split('|')]

def strip_cell_markup(value: str) -> str:
    """Remove presentation-only wrapping from an identity/status table cell."""
    out = value.strip()
    changed = True
    while changed and len(out) >= 2:
        changed = False
        for left, right in (('**', '**'), ('__', '__'), ('`', '`')):
            if out.startswith(left) and out.endswith(right):
                out = out[len(left):-len(right)].strip()
                changed = True
    return out

class LocationProjectionError(RuntimeError):
    """A location input is unsafe or cannot be represented without guessing."""

@dataclasses.dataclass
class CommonMarkFence:
    """Track one CommonMark fenced-code block without loose toggle semantics."""
    marker: str | None = None
    length: int = 0

    @property
    def active(self) -> bool:
        return self.marker is not None

    def consume(self, line: str) -> bool:
        """Consume a valid opener/closer and return whether ``line`` is a fence."""
        match = re.match('^ {0,3}(?P<fence>`{3,}|~{3,})(?P<tail>.*)$', line)
        if match is None:
            return False
        fence = match.group('fence')
        tail = match.group('tail')
        if self.marker is None:
            if fence[0] == '`' and '`' in tail:
                return False
            self.marker = fence[0]
            self.length = len(fence)
            return True
        if fence[0] == self.marker and len(fence) >= self.length and (not tail.strip(' \t')):
            self.marker = None
            self.length = 0
            return True
        return False

@dataclasses.dataclass(frozen=True)
class ArchiveLimits:
    max_members: int = 10000
    max_member_bytes: int = 10 * 1024 * 1024
    max_total_bytes: int = 100 * 1024 * 1024
    max_compression_ratio: float = 200.0

@dataclasses.dataclass
class DeclaredLocation:
    document_id: str
    family: str
    record: dict
    source_path: str
    line: int

@dataclasses.dataclass
class DeclaredLifecycle:
    document_id: str
    family: str
    state: str
    evidence: str
    source_path: str
    line: int

@dataclasses.dataclass
class ArchiveFact:
    archive_path: str
    member_path: str
    archive_sha256: str
    member_sha256: str
    document_id: str | None
    family: str
    lifecycle_state: str
    lifecycle_provenance: str
LOCATION_COLUMNS = ['Document ID', 'Kind', 'Path', 'Member', 'Corpus', 'Notebook', 'Object Type', 'Opaque ID', 'Replacement Authority', 'Baseline', 'Archive SHA-256', 'Member SHA-256', 'Retired At']
LIFECYCLE_COLUMNS = ['Document ID', 'State', 'Evidence']
LOCATION_KINDS = {'repository', 'archive', 'memalpha', 'pointer'}
_SHA256 = re.compile('[0-9a-fA-F]{64}')
_COMMIT_SHA = re.compile('[0-9a-fA-F]{7,40}')
_H2 = re.compile('^##\\s+(.+?)\\s*$')

def _cell_value(value: str) -> str | None:
    cleaned = strip_cell_markup(value).strip()
    if cleaned.lower() in {'', '—', '–', '-', 'n/a', 'none', 'null'}:
        return None
    return cleaned

def _unsafe_kind(value: str) -> str | None:
    """Classify unsafe committed locator content without returning the value."""
    if not isinstance(value, str):
        return 'non-string value'
    decoded = value
    for _round in range(4):
        try:
            next_value = urllib.parse.unquote(decoded, encoding='utf-8', errors='strict')
        except UnicodeDecodeError:
            return 'encoded value'
        if next_value == decoded:
            break
        decoded = next_value
    else:
        try:
            if urllib.parse.unquote(decoded, encoding='utf-8', errors='strict') != decoded:
                return 'encoded value'
        except UnicodeDecodeError:
            return 'encoded value'
    lower = decoded.lower()
    if re.search('[?&](?:x-amz-[^=]*signature|x-goog-[^=]*signature|signature|sig|token|access_token)=', lower):
        return 'signed URL'
    if decoded.startswith('/') or re.match('^(?:[a-z]:[\\\\/]|\\\\\\\\|//)', decoded, re.IGNORECASE) or lower.startswith('file:'):
        return 'absolute path'
    if re.match('^[a-z][a-z0-9+.-]*://', decoded, re.IGNORECASE):
        return 'URL'
    if decoded.startswith('~') or re.search('\\$(?:\\{[A-Za-z_][A-Za-z0-9_]*\\}|[A-Za-z_][A-Za-z0-9_]*)', decoded) or re.search('%[A-Za-z_][A-Za-z0-9_]*%', decoded):
        return 'home or environment path'
    credential_name = '(?:x[-_])?(?:authorization|proxy[-_]?authorization|cookie|set[-_]?cookie|api(?:[-_]?key)?|token|access(?:[-_]?token)?|refresh(?:[-_]?token)?|session(?:[-_]?token)?|auth(?:[-_]?token)?|credential|secret|password|private(?:[-_]?(?:key|token|handle))?|upload|signature)'
    if re.match('(?i)^\\s*bearer(?:\\s|$)', decoded) or re.search(f'(?i)(?:^\\s*|[?&;,]\\s*){credential_name}\\s*[:=]', decoded) or re.search('\\bAKIA[0-9A-Z]{16}\\b', decoded) or ('-----begin private key-----' in lower) or ('private-token' in lower):
        return 'credential'
    compact = re.sub('\\s+', '', decoded)
    if lower.startswith('data:') or len(decoded) > 4096 or (len(compact) > 512 and re.fullmatch('[A-Za-z0-9+/=]+', compact)) or ('"model"' in lower and ('"messages"' in lower or '"prompt"' in lower)):
        return 'payload'
    return None

def _check_safe(value: str, source_path: str, line: int, field: str) -> None:
    kind = _unsafe_kind(value)
    if kind:
        raise LocationProjectionError(f'unsafe {kind} in {source_path}:{line} field {field}')

def require_safe_value(value: str, *, label: str='declared value') -> str:
    """Return one safe value or fail without including caller-controlled bytes."""
    if _unsafe_kind(value) is not None:
        raise LocationProjectionError(f'unsafe {label}')
    return value

def normalize_relative_path(value: str, *, member: bool=False) -> str:
    """Return a canonical POSIX relative path or reject traversal/absolutes."""
    require_safe_value(value, label='relative path')
    if '\\' in value:
        raise LocationProjectionError('non-POSIX path separator in location declaration')
    path = pathlib.PurePosixPath(value)
    if path.is_absolute() or any((part == '..' for part in path.parts)):
        label = 'archive member path traversal' if member else 'repository path traversal'
        raise LocationProjectionError(label)
    normalized = path.as_posix()
    if normalized in {'', '.'} or normalized != value:
        raise LocationProjectionError('empty relative path in location declaration')
    return normalized

def _declaration_error(kind: str, source_path: str, line: int, **extra) -> dict:
    return {'kind': kind, 'source_path': source_path, 'line': line, **extra}

def parse_declarations(text, source_path, family) -> tuple[list[DeclaredLocation], list[DeclaredLifecycle], list[dict]]:
    """Parse the exact ratified Location Records and Document Lifecycle tables."""
    lines = text.splitlines()
    locations_out: list[DeclaredLocation] = []
    lifecycles_out: list[DeclaredLifecycle] = []
    diagnostics: list[dict] = []
    section = None
    header_seen = False
    fence = CommonMarkFence()
    for lineno, line in enumerate(lines, start=1):
        if fence.consume(line):
            continue
        if fence.active:
            continue
        heading = _H2.match(line)
        if heading:
            title = heading.group(1).strip().lower()
            section = title if title in {'location records', 'document lifecycle'} else None
            header_seen = False
            continue
        if section is None:
            continue
        cells = split_markdown_row(line)
        if cells is None:
            if line.strip():
                section = None
            continue
        cleaned = [strip_cell_markup(cell) for cell in cells]
        if cleaned and all((re.fullmatch(':?-{3,}:?', cell) for cell in cleaned)):
            continue
        expected = LOCATION_COLUMNS if section == 'location records' else LIFECYCLE_COLUMNS
        if not header_seen:
            if [cell.lower() for cell in cleaned] != [cell.lower() for cell in expected]:
                diagnostics.append(_declaration_error(f"{section.replace(' ', '_')}_header_mismatch", source_path, lineno))
                section = None
                continue
            header_seen = True
            continue
        if len(cells) != len(expected):
            diagnostics.append(_declaration_error(f"{section.replace(' ', '_')}_column_count", source_path, lineno))
            continue
        values = [_cell_value(cell) for cell in cells]
        for field, value in zip(expected, values):
            if value is not None:
                _check_safe(value, source_path, lineno, field)
        if section == 'document lifecycle':
            document_id, state, evidence = values
            if not document_id or not state:
                diagnostics.append(_declaration_error('lifecycle_missing_required_field', source_path, lineno))
                continue
            normalized_state = re.sub('[\\s-]+', '_', state.lower())
            if normalized_state not in DOCUMENT_LIFECYCLE_STATES:
                diagnostics.append(_declaration_error('invalid_document_lifecycle', source_path, lineno, document_id=document_id))
                continue
            lifecycles_out.append(DeclaredLifecycle(document_id=document_id, family=family, state=normalized_state, evidence=evidence or '', source_path=source_path, line=lineno))
            continue
        row = dict(zip(LOCATION_COLUMNS, values))
        document_id = row['Document ID']
        kind = (row['Kind'] or '').lower()
        if not document_id or kind not in LOCATION_KINDS:
            diagnostics.append(_declaration_error('location_invalid_identity_or_kind', source_path, lineno))
            continue
        required = {'repository': {'Path'}, 'archive': {'Path', 'Member', 'Archive SHA-256', 'Member SHA-256'}, 'memalpha': {'Corpus', 'Notebook', 'Object Type', 'Opaque ID', 'Baseline'}, 'pointer': {'Path', 'Replacement Authority'}}[kind]
        missing = sorted((field for field in required if not row[field]))
        allowed = required | {'Document ID', 'Kind', 'Baseline', 'Retired At'}
        incompatible = sorted((field for field in LOCATION_COLUMNS if field not in allowed and row[field] is not None))
        if missing or incompatible:
            diagnostics.append(_declaration_error('location_field_contract', source_path, lineno, document_id=document_id, missing=missing, incompatible=incompatible))
            continue
        retired_at = row['Retired At']
        if retired_at and (not _COMMIT_SHA.fullmatch(retired_at)):
            diagnostics.append(_declaration_error('invalid_retired_at', source_path, lineno, document_id=document_id))
            continue
        integrity = None
        if kind == 'repository':
            target = {'path': normalize_relative_path(row['Path'])}
        elif kind == 'archive':
            archive_sha = row['Archive SHA-256']
            member_sha = row['Member SHA-256']
            if not _SHA256.fullmatch(archive_sha) or not _SHA256.fullmatch(member_sha):
                diagnostics.append(_declaration_error('invalid_archive_integrity', source_path, lineno, document_id=document_id))
                continue
            target = {'path': normalize_relative_path(row['Path']), 'member': normalize_relative_path(row['Member'], member=True)}
            integrity = {'archive_sha256': archive_sha.lower(), 'member_sha256': member_sha.lower()}
        elif kind == 'memalpha':
            target = {'corpus': row['Corpus'], 'notebook': row['Notebook'], 'object_type': row['Object Type'], 'opaque_id': row['Opaque ID']}
        else:
            target = {'path': normalize_relative_path(row['Path']), 'replacement_authority': row['Replacement Authority']}
        record = {'location_kind': kind, 'target': target, 'baseline': row['Baseline'], 'integrity': integrity, 'retired_at': retired_at.lower() if retired_at else None, 'attr_provenance': {'location_kind': 'declared', 'target': 'declared', 'baseline': 'declared' if row['Baseline'] else 'inferred', 'integrity': 'declared' if integrity else 'inferred', 'retired_at': 'declared' if retired_at else 'inferred'}}
        locations_out.append(DeclaredLocation(document_id, family, record, source_path, lineno))
    return (locations_out, lifecycles_out, diagnostics)

def scan_archives(archive_sources, family_for_path, limits) -> tuple[list[ArchiveFact], list[dict], dict]:
    """Inspect every top-level archive safely and without workspace extraction."""
    facts: list[ArchiveFact] = []
    diagnostics: list[dict] = []
    coverage = {'archives_scanned': 0, 'archive_markdown_members': 0, 'archive_members_identified': 0, 'archive_members_missing_id': 0}
    for relative_archive, archive_bytes in sorted(archive_sources.items()):
        coverage['archives_scanned'] += 1
        archive_sha = hashlib.sha256(archive_bytes).hexdigest()
        try:
            zf = zipfile.ZipFile(io.BytesIO(archive_bytes))
        except (OSError, zipfile.BadZipFile) as exc:
            raise LocationProjectionError(f'invalid archive: {relative_archive}') from exc
        with zf:
            infos = zf.infolist()
            if len(infos) > limits.max_members:
                raise LocationProjectionError(f'archive member count limit exceeded: {relative_archive}')
            normalized_names: set[str] = set()
            total_size = 0
            for info in infos:
                if info.is_dir():
                    raw_directory = info.filename
                    if not raw_directory.endswith('/') or raw_directory.endswith('//'):
                        raise LocationProjectionError(f'archive member path traversal: {relative_archive}')
                    normalize_relative_path(raw_directory[:-1], member=True)
                    continue
                try:
                    member_path = normalize_relative_path(info.filename, member=True)
                except LocationProjectionError as exc:
                    if 'traversal' in str(exc).lower():
                        raise LocationProjectionError(f'archive member path traversal: {relative_archive}') from exc
                    raise
                if member_path in normalized_names:
                    raise LocationProjectionError(f'duplicate member in archive: {relative_archive}')
                normalized_names.add(member_path)
                if info.flag_bits & 1:
                    raise LocationProjectionError(f'encrypted archive member is unsupported: {relative_archive}')
                if info.file_size > limits.max_member_bytes:
                    raise LocationProjectionError(f'archive member size limit exceeded: {relative_archive}')
                total_size += info.file_size
                if total_size > limits.max_total_bytes:
                    raise LocationProjectionError(f'archive total size limit exceeded: {relative_archive}')
                ratio = info.file_size / max(1, info.compress_size)
                if ratio > limits.max_compression_ratio:
                    raise LocationProjectionError(f'archive compression ratio limit exceeded: {relative_archive}')
                if not member_path.lower().endswith('.md'):
                    continue
                coverage['archive_markdown_members'] += 1
                try:
                    member_bytes = zf.read(info)
                except (RuntimeError, zipfile.BadZipFile) as exc:
                    raise LocationProjectionError(f'archive member could not be read safely: {relative_archive}') from exc
                member_sha = hashlib.sha256(member_bytes).hexdigest()
                text = member_bytes.decode('utf-8', errors='replace')
                header, _header_lines, _title = parse_markdown_header(text.splitlines())
                for value in header.values():
                    _check_safe(value, relative_archive, 1, 'archive header')
                document_id = header.get('document id', '').strip() or None
                lifecycle_state, lifecycle_provenance, lifecycle_valid = resolve_lifecycle(header)
                if not lifecycle_valid:
                    diagnostics.append({'kind': 'invalid_archive_document_lifecycle', 'archive_path': relative_archive, 'member': member_path})
                if document_id:
                    coverage['archive_members_identified'] += 1
                else:
                    coverage['archive_members_missing_id'] += 1
                    diagnostics.append({'kind': 'archive_markdown_missing_document_id', 'archive_path': relative_archive, 'member': member_path})
                family = family_for_path(relative_archive, member_path)
                facts.append(ArchiveFact(archive_path=relative_archive, member_path=member_path, archive_sha256=archive_sha, member_sha256=member_sha, document_id=document_id, family=family, lifecycle_state=lifecycle_state, lifecycle_provenance=lifecycle_provenance))
    return (facts, diagnostics, coverage)

def _repository_record(path: str) -> dict:
    return {'location_kind': 'repository', 'target': {'path': normalize_relative_path(path)}, 'baseline': None, 'integrity': None, 'retired_at': None, 'attr_provenance': {'location_kind': 'inferred', 'target': 'inferred', 'baseline': 'inferred', 'integrity': 'inferred', 'retired_at': 'inferred'}}

def _archive_record(fact: ArchiveFact) -> dict:
    return {'location_kind': 'archive', 'target': {'path': fact.archive_path, 'member': fact.member_path}, 'baseline': None, 'integrity': {'archive_sha256': fact.archive_sha256, 'member_sha256': fact.member_sha256}, 'retired_at': None, 'attr_provenance': {'location_kind': 'inferred', 'target': 'inferred', 'baseline': 'inferred', 'integrity': 'inferred', 'retired_at': 'inferred'}}

def _record_sort_key(record: dict) -> tuple:
    return (record['location_kind'], json.dumps(record['target'], ensure_ascii=False, sort_keys=True), record.get('baseline') or '', record.get('retired_at') or '')

def _same_target(left: dict, right: dict) -> bool:
    return left['location_kind'] == right['location_kind'] and left['target'] == right['target']

def _add_record(records: list[dict], record: dict, *, declared: bool=False) -> None:
    """Merge declared enrichment over one derived record; retain real history."""
    for index, existing in enumerate(records):
        if existing == record:
            return
        if declared and _same_target(existing, record):
            existing_declared = existing.get('attr_provenance', {}).get('target') == 'declared'
            if not existing_declared:
                records[index] = record
                return
    records.append(record)

def build_location_index(texts, documents, archive_sources, family_for_path, *, archive_limits=None) -> tuple[dict, list[dict]]:
    """Build deterministic schema-v1 document/location family files."""
    archive_limits = archive_limits or ArchiveLimits()
    diagnostics: list[dict] = []
    coverage = {'active_documents_seen': len(documents), 'active_documents_identified': 0, 'active_documents_missing_id': 0, 'duplicate_document_ids': 0, 'declaration_errors': 0}
    active_by_id: dict[str, list] = collections.defaultdict(list)
    declared_locations: list[DeclaredLocation] = []
    declared_lifecycles: list[DeclaredLifecycle] = []
    for document in documents:
        document_id = document.header.get('document id', '').strip()
        if document_id:
            coverage['active_documents_identified'] += 1
            active_by_id[document_id].append(document)
        else:
            coverage['active_documents_missing_id'] += 1
        locs, lifecycles, declaration_diagnostics = parse_declarations(texts[document.path], document.path, document.family)
        declared_locations.extend(locs)
        declared_lifecycles.extend(lifecycles)
        diagnostics.extend(declaration_diagnostics)
    for document_id, group in sorted(active_by_id.items()):
        if len(group) > 1:
            coverage['duplicate_document_ids'] += 1
            diagnostics.append({'kind': 'duplicate_document_id', 'document_id': document_id, 'paths': sorted((document.path for document in group))})
    archive_facts, archive_diagnostics, archive_coverage = scan_archives(archive_sources, family_for_path, archive_limits)
    diagnostics.extend(archive_diagnostics)
    coverage.update(archive_coverage)
    facts_by_target = {(fact.archive_path, fact.member_path): fact for fact in archive_facts}
    for declared in declared_locations:
        if declared.record['location_kind'] != 'archive':
            continue
        target = declared.record['target']
        fact = facts_by_target.get((target['path'], target['member']))
        if fact is None:
            raise LocationProjectionError(f'declared archive target missing at {declared.source_path}:{declared.line}')
        if fact.document_id and fact.document_id != declared.document_id:
            raise LocationProjectionError(f'declared archive identity conflicts at {declared.source_path}:{declared.line}')
        if declared.record['integrity'] != {'archive_sha256': fact.archive_sha256, 'member_sha256': fact.member_sha256}:
            raise LocationProjectionError(f'declared archive integrity mismatch at {declared.source_path}:{declared.line}')
    accumulators: dict[str, dict] = {}

    def ensure(document_id: str, family: str) -> dict:
        current = accumulators.setdefault(document_id, {'family': family, 'locations': [], 'lifecycle_candidates': []})
        if current['family'] == 'unknown' and family != 'unknown':
            current['family'] = family
        elif family != 'unknown' and current['family'] != family:
            diagnostics.append({'kind': 'document_family_conflict', 'document_id': document_id, 'families': sorted({current['family'], family})})
        return current
    for document_id, group in sorted(active_by_id.items()):
        if len(group) != 1:
            continue
        document = group[0]
        acc = ensure(document_id, document.family)
        _add_record(acc['locations'], _repository_record(document.path))
        state, provenance, valid = resolve_lifecycle(document.header)
        if valid:
            acc['lifecycle_candidates'].append((3, state, provenance, document.path))
    for fact in archive_facts:
        if not fact.document_id:
            continue
        acc = ensure(fact.document_id, fact.family)
        _add_record(acc['locations'], _archive_record(fact))
        acc['lifecycle_candidates'].append((2, fact.lifecycle_state, fact.lifecycle_provenance, fact.member_path))
    for declared in declared_locations:
        acc = ensure(declared.document_id, declared.family)
        _add_record(acc['locations'], declared.record, declared=True)
    lifecycle_by_id: dict[str, list[DeclaredLifecycle]] = collections.defaultdict(list)
    for lifecycle in declared_lifecycles:
        lifecycle_by_id[lifecycle.document_id].append(lifecycle)
    for document_id, declarations in sorted(lifecycle_by_id.items()):
        acc = ensure(document_id, declarations[0].family)
        if len(declarations) > 1:
            diagnostics.append({'kind': 'duplicate_lifecycle_declaration', 'document_id': document_id, 'sites': [f'{d.source_path}:{d.line}' for d in declarations]})
        states = {declaration.state for declaration in declarations}
        if len(states) == 1:
            acc['lifecycle_candidates'].append((4, declarations[0].state, 'declared', declarations[0].source_path))
        else:
            acc['lifecycle_candidates'].append((4, 'unknown', 'inferred', 'conflict'))
    per_family_documents: dict[str, list[dict]] = collections.defaultdict(list)
    kind_counts: collections.Counter = collections.Counter()
    for document_id, acc in sorted(accumulators.items()):
        candidates = acc['lifecycle_candidates']
        if candidates:
            highest = max((candidate[0] for candidate in candidates))
            top = [candidate for candidate in candidates if candidate[0] == highest]
            states = {candidate[1] for candidate in top}
            if len(states) == 1:
                lifecycle_state = top[0][1]
                lifecycle_provenance = top[0][2]
            else:
                lifecycle_state = 'unknown'
                lifecycle_provenance = 'inferred'
                diagnostics.append({'kind': 'lifecycle_source_conflict', 'document_id': document_id})
        else:
            lifecycle_state, lifecycle_provenance = ('unknown', 'inferred')
        records = sorted(acc['locations'], key=_record_sort_key)
        kind_counts.update((record['location_kind'] for record in records))
        per_family_documents[acc['family']].append({'document_id': document_id, 'lifecycle_state': lifecycle_state, 'attr_provenance': {'lifecycle_state': lifecycle_provenance}, 'locations': records})
    coverage['declaration_errors'] = sum((1 for diagnostic in diagnostics if diagnostic['kind'].startswith(('location_', 'document_lifecycle_', 'invalid_'))))
    out: dict[str, dict] = {}
    for family, family_documents in sorted(per_family_documents.items()):
        family_documents.sort(key=lambda document: document['document_id'])
        record_count = sum((len(document['locations']) for document in family_documents))
        family_kind_counts = collections.Counter((record['location_kind'] for document in family_documents for record in document['locations']))
        out[family] = {'schema_version': 1, 'family': family, 'document_count': len(family_documents), 'record_count': record_count, 'kind_counts': dict(sorted(family_kind_counts.items())), 'documents': family_documents}
    out['_manifest'] = {'schema_version': 1, 'families': sorted(per_family_documents), 'family_document_counts': {family: len(per_family_documents[family]) for family in sorted(per_family_documents)}, 'family_record_counts': {family: sum((len(document['locations']) for document in per_family_documents[family])) for family in sorted(per_family_documents)}, 'total_documents': sum((len(value) for value in per_family_documents.values())), 'total_records': sum(kind_counts.values()), 'kind_counts': dict(sorted(kind_counts.items())), 'coverage_counts': dict(sorted(coverage.items()))}
    return (out, diagnostics)

def render(payload: dict) -> str:
    return json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + '\n'
