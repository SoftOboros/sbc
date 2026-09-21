"""Pinned pure parser extraction. Reproduce with tools/extract_document_parser.py.
Source blob: 551c0ab7d70f82ad9e6fdfd99ef57a1ff78aeabb.
"""
from __future__ import annotations
import collections
import copy
import dataclasses
import datetime
import hashlib
import json
import pathlib
import re
import unicodedata
from . import _producer_locations as locations
_ID_TOKEN_LEFT = '(?<![A-Za-z0-9_:#-])'
_ID_TOKEN_RIGHT = '(?![A-Za-z0-9_:#-])'
RE_INVARIANT = re.compile(f'{_ID_TOKEN_LEFT}(?:INV-([A-Z]{{2,8}})-([0-9]+)|([A-Z]{{2,8}})-INV-([0-9]+)){_ID_TOKEN_RIGHT}', re.ASCII)
_PCDN_PHASE = '[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*'
RE_PCDN = re.compile(f'{_ID_TOKEN_LEFT}PCDN-(?P<phase>{_PCDN_PHASE})-(?P<number>[0-9]{{3}}){_ID_TOKEN_RIGHT}', re.ASCII)
RE_EOQ = re.compile(f'{_ID_TOKEN_LEFT}EOQ-(?P<number>[0-9]{{3}})-ERRATA-(?P<errata>[0-9]{{3}}){_ID_TOKEN_RIGHT}', re.ASCII)
_INV_ID = '(?:INV-[A-Z]{2,8}-[0-9]+|[A-Z]{2,8}-INV-[0-9]+)'
RE_INV_DEF_ROW = re.compile(f'^\\|\\s*\\*\\*({_INV_ID})\\*\\*\\s*\\|(.*)$')
RE_INV_DEF_BULLET = re.compile(f'^\\s*(?:[-*]|\\d+\\.)\\s+\\*\\*({_INV_ID})\\s*[—\\-–:.]?\\s*([^*]*)\\*\\*\\.?\\s*(.*)$')
RE_INV_DEF_HEADING = re.compile(f'^#{{2,4}}\\s+\\*{{0,2}}({_INV_ID})\\b\\s*[—\\-–:.]?\\s*(.*)$')
RE_INV_DEF_ROW_SPAN = re.compile('^\\|\\s*\\*\\*(?P<span>[^*]+)\\*\\*\\s*\\|(?P<rest>.*)$')
RE_INV_DEF_BULLET_SPAN = re.compile('^\\s*(?:[-*]|\\d+\\.)\\s+\\*\\*(?P<span>[^*]+)\\*\\*\\.?\\s*(?P<rest>.*)$')
RE_INV_DEF_HEADING_SPAN = re.compile('^#{2,4}\\s+\\*\\*(?P<span>[^*]+)\\*\\*\\s*(?P<rest>.*)$')
RE_ERRATA_DEF = re.compile('^#{2,3}\\s+(ERRATA-\\d+)\\s*[—-]?\\s*(.*)$')
RE_GLOSSARY_ROW = re.compile('^\\|\\s*\\*\\*([^*|]{2,60})\\*\\*\\s*\\|\\s*([^|]*)\\|\\s*([^|]*)\\|')
_TERM_HANDLE = 'TERM-(?:00[1-9]|0[1-9][0-9]|[1-9][0-9]{2})'
RE_TERM_HANDLE = re.compile(_TERM_HANDLE, re.ASCII)
RE_GLOSSARY_TERM_CELL = re.compile('^\\*\\*([^*|]{2,60})\\*\\*$')
_GATE_HANDLE = 'GATE-(?:00[1-9]|0[1-9][0-9]|[1-9][0-9]{2})'
RE_GATE_HANDLE = re.compile(_GATE_HANDLE, re.ASCII)
RE_STABLE_ACCEPTANCE_GATE = re.compile(f'^`(?P<handle>{_GATE_HANDLE})` — (?P<text>\\S.*)$', re.ASCII)
RE_ACCEPTANCE_GATE = re.compile('^\\s*-\\s*\\[([ xX])\\]\\s+(.*)$')
_NONGOAL_HANDLE = 'NONGOAL-(?:00[1-9]|0[1-9][0-9]|[1-9][0-9]{2})'
RE_NONGOAL_HANDLE = re.compile(_NONGOAL_HANDLE, re.ASCII)
RE_NONGOAL_ITEM = re.compile('^\\s*(?P<ordinal>\\d+)\\.\\s+(?P<content>\\S.*)$')
RE_STABLE_NONGOAL = re.compile(f'^`(?P<handle>{_NONGOAL_HANDLE})` — \\*\\*(?P<title>[^*\\r\\n]+\\.)\\*\\* (?P<body>\\S.*)$', re.ASCII)
RE_LEGACY_NONGOAL = re.compile('^\\*\\*(?P<title>[^*]+)\\*\\*\\.?\\s*(?P<body>.*)$')
RE_MALFORMED_NONGOAL = re.compile('^(?:`(?i:NONGOAL)-[^`]*`|(?i:NONGOAL)-\\S+).*?\\*\\*(?P<title>[^*]+)\\*\\*\\.?\\s*(?P<body>.*)$')
_SECTION_HANDLE = 'SECTION-(?:00[1-9]|0[1-9][0-9]|[1-9][0-9]{2})'
RE_SECTION_HANDLE = re.compile(_SECTION_HANDLE, re.ASCII)
RE_STABLE_SECTION_HEADING = re.compile(f'^§(?P<ordinal>[0-9]+(?:\\.[0-9]+)*) `(?P<handle>{_SECTION_HANDLE})` — (?P<title>\\S.*)$', re.ASCII)
RE_HEADER_ATTR = re.compile('^\\*\\*([A-Za-z][A-Za-z ]{2,30}):\\*\\*\\s*(.*)$')
RE_HEADING = re.compile('^(#{1,4})\\s+(.*)$')
RE_SECTION_NUM = re.compile('^§?\\s*(\\d+)(?:\\.|\\s|$)')
RE_CL_TABLE_ROW = re.compile('^\\|\\s*([0-9]+\\.[0-9]+\\.[0-9]+|Exec-[0-9.]+)\\s*\\|\\s*(\\d{4}-\\d{2}-\\d{2})\\s*\\|')
RE_CL_BULLET_ROW = re.compile('^\\s*[-*]\\s+\\*\\*(\\d{4}-\\d{2}-\\d{2})')
SECTION_HINTS = {'glossary': 3, 'acceptance': 12, 'non-goal': 11, 'change log': 15, 'invariant': 9}
AUTHORITY_AXES = {'upstream authority', 'local representation', 'mutation rights', 'divergence policy', 'downstream consumers', 'conformance test owner'}
RE_CL_SECTION = re.compile('^(#{2,3})\\s+.*change\\s*log', re.IGNORECASE)
RE_CL_BLOCK_HEAD = re.compile('^#{3,4}\\s+(?P<rev>[0-9]+\\.[0-9]+\\.[0-9]+|Exec-[0-9.]+)\\s*[—–-]\\s*(?P<date>\\d{4}-\\d{2}-\\d{2})\\s*[—–-]\\s*(?P<status>\\S(?:.*\\S)?)\\s*$')
_PROJECT_EVENT_HANDLE = 'EVENT-(?:00[1-9]|0[1-9][0-9]|[1-9][0-9]{2})'
RE_PROJECT_EVENT_HEAD = re.compile(f'^### (?P<handle>{_PROJECT_EVENT_HANDLE}) — (?P<date>\\d{{4}}-\\d{{2}}-\\d{{2}}) — project event$', re.ASCII)
RE_PROJECT_EVENT_CANDIDATE = re.compile('^#{1,6}\\s+(?i:EVENT)-')
RE_PROJECT_EVENT_FIELD = re.compile('^\\*\\*(?P<label>[A-Za-z][A-Za-z -]*):\\*\\*\\s*(?P<value>.*)$', re.ASCII)
RE_CL_FIELD = re.compile('^\\*\\*(Author|Change kind|Touches|Commits|Summary):\\*\\*\\s*(.*)$', re.IGNORECASE)
RE_CL_RATIONALE_HEAD = re.compile('^#{4,5}\\s+Rationale\\s*$', re.IGNORECASE)
RE_SPEC_EDGE_FIELD = re.compile('^\\*\\*Spec Edge:\\*\\* (?P<source>\\S*) -> (?P<target>\\S*) ;(?P<tail>.*)$')
RE_SPEC_EDGE_EXACT = re.compile('^\\*\\*Spec Edge:\\*\\* (?P<source>\\S*) -> (?P<target>\\S*) ; type=(?P<edge_type>[^\\s;]+)$')
RE_RETIRES_DEPENDENCY = re.compile('^Retires-Dependency: (?P<upstream>\\S+) -> (?P<dependent>\\S+) ; type=(?P<edge_type>[a-z-]+)$')
AMENDMENT_STATUS = {'drafted', 'ratified', 'amended', 'execution', 'superseded'}
CHANGE_KIND = {'editorial', 'clarification', 'semantic', 'scope', 'retirement'}
RATIONALE_REQUIRED = {'semantic', 'scope', 'retirement'}
EXAMPLE_PREFIXES = {'FOO', 'BAR', 'BAZ', 'EXAMPLE'}

def _definition_ids(span: str) -> tuple[list[str], str]:
    """Return every id named by a definition-head span plus its title tail.

    Authors occasionally use a compact ``INV-FOO-3/4`` form. Under
    SBC-INV-15 both ids are definition sites, so stopping at the first id
    silently undercounts the corpus (SIDX ERRATA-002). Only contiguous slash
    suffixes immediately after the first id expand; a later prose fraction
    such as ``rate 1/3`` must not become another invariant.
    """
    value = span.strip()
    first = RE_INVARIANT.match(value)
    if not first:
        return ([], value)
    if first.end() < len(value) and (value[first.end()].isalnum() or value[first.end()] in {'_', '-'}):
        return ([], value)
    ids = [first.group(0)]
    prefix = first.group(0).rsplit('-', 1)[0]
    cursor = first.end()
    while True:
        tail = value[cursor:]
        full = re.match(f'\\s*/\\s*(?P<id>{_INV_ID}){_ID_TOKEN_RIGHT}', tail, re.ASCII)
        if full:
            candidate = full.group('id')
            cursor += full.end()
        else:
            short = re.match(f'\\s*/\\s*(?P<number>[0-9]+){_ID_TOKEN_RIGHT}', tail, re.ASCII)
            if not short:
                break
            candidate = f"{prefix}-{short.group('number')}"
            cursor += short.end()
        if candidate not in ids:
            ids.append(candidate)
    title = value[cursor:].strip().lstrip('—-–:.').strip()
    return (ids, title)

def _statement_tail(value: str) -> str:
    """Return authored statement text without changing its punctuation."""
    return value.strip()
RFC2119 = re.compile('\\b(MUST NOT|MUST|SHALL NOT|SHALL|SHOULD NOT|SHOULD|MAY|RECOMMENDED)\\b')

@dataclasses.dataclass
class SpecObject:
    obj_id: str
    kind: str
    family: str
    doc: str
    line: int
    text: str = ''
    attrs: dict = dataclasses.field(default_factory=dict)
    producer_meta: dict = dataclasses.field(default_factory=dict, repr=False)

    def to_dict(self) -> dict:
        return {'obj_id': self.obj_id, 'kind': self.kind, 'family': self.family, 'doc': self.doc, 'line': self.line, 'text': self.text, 'attrs': copy.deepcopy(self.attrs)}

@dataclasses.dataclass
class Citation:
    obj_id: str
    doc: str
    line: int
    family: str
    is_definition: bool = False
    source_token: str | None = None
    edge_type_tokens: tuple[str, ...] = ()
    declared: bool = False
    recognized_edge_field: bool = False

@dataclasses.dataclass(frozen=True)
class ProjectEventRecord:
    """Validated source-only project record from ADDENDUM-D §2.5.

    The record is deliberately not a ``SpecObject`` and has no wire serializer.
    Keeping the type separate makes accidental projection a type-level mistake
    rather than a convention callers must remember.
    """
    handle: str
    date: str
    line: int
    author: str
    commits: str | None
    summary: str

@dataclasses.dataclass
class Document:
    path: str
    family: str
    header: dict = dataclasses.field(default_factory=dict)
    header_lines: dict = dataclasses.field(default_factory=dict)
    title: str = ''
    diagnostics: list = dataclasses.field(default_factory=list)
    sections: set = dataclasses.field(default_factory=set)
    changelog_shape: str = 'none'
    changelog_entries: int = 0
    project_event_entries: int = 0
    is_concepts: bool = False
    producer_errors: list = dataclasses.field(default_factory=list)
_TOUCHES_EMPTY_MARKER = re.compile('^(?:none|n/a)(?:\\s+—\\s+[^,\\r\\n]+)?$', re.IGNORECASE)

def _split_list(value: str, *, reject_mixed_empty: bool=False):
    """Parse one Touches:/Commits: value without losing member ordinals."""
    v = value.strip()
    if not v:
        return []
    if reject_mixed_empty:
        if _TOUCHES_EMPTY_MARKER.fullmatch(v):
            return []
        members = [part.strip() or None for part in v.split(',')]
        if any((member is not None and _TOUCHES_EMPTY_MARKER.fullmatch(member) for member in members)):
            raise ProjectionError('Touches mixes an empty marker with object ids')
        parsed = members
    else:
        if v.lower() in {'none', 'n/a', '—', '-'}:
            return []
        if re.match('^(none|n/a)\\b', v, re.IGNORECASE) and ',' not in v:
            return []
        members = [part.strip() for part in v.split(',')]
        empty_markers = {index for index, member in enumerate(members) if member.lower() in {'none', 'n/a', '—', '-'} or re.match('^(none|n/a)\\b', member, re.IGNORECASE)}
        parsed = [member for index, member in enumerate(members) if member and index not in empty_markers]
    if any((member is not None and locations._unsafe_kind(member) is not None for member in parsed)):
        raise ProjectionError('declared list value is unsafe')
    return parsed

def _historical_definition_ids(doc: Document, lines: list[str], definitions: list[_ProjectedDefinition], registered_prefixes, *, lifecycle_state: str, lifecycle_provenance: str) -> frozenset[str]:
    """Validate one explicit current-projection definition exclusion list.

    The rule has no banner, path, age, or replacement-name inference. A
    declaration is operative only through one contiguous pair of governed
    header fields on an explicitly superseded document, and every member must
    already be one unique edge-eligible definition owned by that document.
    """
    field = 'historical definitions'
    lifecycle_field = 'document lifecycle state'
    if field not in doc.header:
        return frozenset()
    if lifecycle_state != 'superseded' or lifecycle_provenance != 'declared':
        raise ProjectionError('historical definitions require a declared superseded lifecycle')
    header_end = max(doc.header_lines.values(), default=0)
    governed_keys = []
    for line in lines[:header_end]:
        match = locations.RE_HEADER_ATTR.match(line)
        if match:
            governed_keys.append(match.group(1).strip().lower())
    key_counts = collections.Counter(governed_keys)
    if key_counts[field] != 1 or key_counts[lifecycle_field] != 1:
        raise ProjectionError('historical definitions require one exact governed field pair')
    if doc.header_lines[field] != doc.header_lines[lifecycle_field] + 1:
        raise ProjectionError('historical definitions require contiguous lifecycle fields')
    raw = doc.header[field]
    members = [member.strip() for member in raw.split(',')]
    if not raw.strip() or any((not member for member in members)):
        raise ProjectionError('historical definitions require a nonempty exact list')
    canonical = []
    for member in members:
        normalized = _canonical_reference(member)
        if normalized is None or member != normalized:
            raise ProjectionError('historical definition id is not canonical')
        canonical.append(normalized)
    if len(set(canonical)) != len(canonical):
        raise ProjectionError('historical definitions contain a duplicate id')
    if any((not _syntactic_global_id(member, registered_prefixes) for member in canonical)):
        raise ProjectionError('historical definition id is not GlobalObjectIdV1 eligible')
    by_id: dict[str, list[_ProjectedDefinition]] = collections.defaultdict(list)
    for definition in definitions:
        payload = definition.payload
        if payload['doc'] == doc.path:
            by_id[payload['obj_id']].append(definition)
    for member in canonical:
        candidates = by_id[member]
        if len(candidates) != 1:
            raise ProjectionError('historical definition id must identify exactly one local definition')
        if candidates[0].payload['kind'] == 'document' or not _definition_is_edge_eligible(candidates[0], registered_prefixes):
            raise ProjectionError('historical definition id is not an eligible contained definition')
    return frozenset(canonical)

def _parse_spec_edge_candidate(line: str, *, document: str, line_number: int, family: str) -> tuple[Citation | None, bool]:
    """Parse one recognized ``Spec Edge`` line without inventing recovery.

    The Boolean reports a recognized-but-unrepresentable field. Missing,
    unsupported, and multiple ``type=`` clauses are representable diagnostic
    candidates; every other deviation from the frozen bytes fails generation.
    Raw unsafe tokens remain source-only and are never copied into diagnostics.
    """
    if line.lstrip().startswith('**Spec Edge:**') and (not line.startswith('**Spec Edge:**')):
        return (None, True)
    if not line.startswith('**Spec Edge:**'):
        return (None, False)
    match = RE_SPEC_EDGE_FIELD.fullmatch(line)
    if not match:
        return (None, True)
    tail = match.group('tail')
    endpoints = (match.group('source'), match.group('target'))
    if any((endpoint and (not endpoint.isascii() or locations._unsafe_kind(endpoint) is not None) for endpoint in endpoints)):
        return (None, True)
    tokens = tuple(re.findall('(?:^|[ ;])type=([^\\s;]+)', tail))
    if any((not token.isascii() or locations._unsafe_kind(token) is not None for token in tokens)):
        return (None, True)
    exact = RE_SPEC_EDGE_EXACT.fullmatch(line)
    if len(tokens) == 1:
        if exact is None or exact.group('edge_type') != tokens[0]:
            return (None, True)
    elif len(tokens) == 0:
        if tail.strip():
            return (None, True)
    else:
        expected_tail = ' ' + ' ; '.join((f'type={token}' for token in tokens))
        if tail != expected_tail:
            return (None, True)
    return (Citation(obj_id=match.group('target'), doc=document, line=line_number, family=family, source_token=match.group('source'), edge_type_tokens=tokens, declared=True, recognized_edge_field=True), False)

def parse_project_event_records(lines: list[str], doc: str) -> tuple[list[ProjectEventRecord], list[dict], set[int]]:
    """Validate ADDENDUM-D §2.5 records without creating spec objects.

    Only an explicit ``EVENT-`` heading inside a change log enters this parser.
    Legacy prose is never inspected for event meaning.  Errors carry a closed
    reason and source line but never echo authored values; publication treats
    them as fatal producer conformance diagnostics outside diagnostic-v3. The
    third result identifies every source line owned by an explicit candidate,
    allowing the general object pass to omit the complete record.
    """
    records: list[ProjectEventRecord] = []
    errors: list[dict] = []
    source_lines: set[int] = set()
    seen_handles: set[str] = set()
    in_log = False
    log_depth = 0
    pending: dict | None = None
    fence = locations.CommonMarkFence()

    def mark_problem(line: int, reason: str) -> None:
        if pending is not None and pending.get('problem_line') is None:
            pending['problem_line'] = line
            pending['problem_reason'] = reason

    def flush() -> None:
        nonlocal pending
        if pending is None:
            return
        match = pending['match']
        fields = pending['fields']
        labels = [field[0] for field in fields]
        expected = ['author', 'summary']
        if 'commits' in labels:
            expected = ['author', 'commits', 'summary']
        if match is None:
            mark_problem(pending['line'], 'invalid_heading')
        else:
            try:
                datetime.date.fromisoformat(match.group('date'))
            except ValueError:
                mark_problem(pending['line'], 'invalid_date')
        if pending.get('problem_line') is None:
            if len(labels) != len(set(labels)):
                duplicate = next((label for label in labels if labels.count(label) > 1))
                duplicate_lines = [field_line for label, _value, field_line in fields if label == duplicate]
                mark_problem(duplicate_lines[1], 'duplicate_field')
            elif labels != expected:
                mismatch_line = fields[0][2] if fields else pending['line']
                mark_problem(mismatch_line, 'invalid_field_sequence')
            elif any((not field[1].strip() for field in fields)):
                empty_line = next((field[2] for field in fields if not field[1].strip()))
                mark_problem(empty_line, 'empty_field')
            elif match.group('handle') in seen_handles:
                mark_problem(pending['line'], 'duplicate_handle')
        if pending.get('problem_line') is not None:
            errors.append({'kind': 'invalid_project_event_record', 'line': pending['problem_line'], 'reason': pending['problem_reason']})
        else:
            values = {label: value.strip() for label, value, _line in fields}
            handle = match.group('handle')
            records.append(ProjectEventRecord(handle=handle, date=match.group('date'), line=pending['line'], author=values['author'], commits=values.get('commits'), summary=values['summary']))
            seen_handles.add(handle)
        pending = None

    def compact_header(line: str) -> bool:
        return bool(line.lstrip().startswith('|') and 'change kind' in line.lower() and (not RE_CL_TABLE_ROW.match(line)))
    for lineno, line in enumerate(lines, start=1):
        if fence.consume(line):
            if pending is not None:
                source_lines.add(lineno)
                mark_problem(lineno, 'unsupported_content')
            continue
        if fence.active:
            if pending is not None:
                source_lines.add(lineno)
                mark_problem(lineno, 'unsupported_content')
            continue
        head = RE_HEADING.match(line)
        if head and RE_CL_SECTION.match(line):
            flush()
            in_log = True
            log_depth = len(head.group(1))
            continue
        if not in_log:
            continue
        if RE_PROJECT_EVENT_CANDIDATE.match(line):
            flush()
            source_lines.add(lineno)
            pending = {'line': lineno, 'match': RE_PROJECT_EVENT_HEAD.fullmatch(line), 'fields': [], 'problem_line': None, 'problem_reason': None}
            if pending['match'] is None:
                mark_problem(lineno, 'invalid_heading')
            continue
        if head and len(head.group(1)) <= log_depth:
            flush()
            in_log = False
            continue
        if pending is None:
            continue
        starts_next_entry = bool(RE_CL_BLOCK_HEAD.match(line) or RE_CL_TABLE_ROW.match(line) or RE_CL_BULLET_ROW.match(line) or compact_header(line) or (head and len(head.group(1)) == log_depth + 1))
        if starts_next_entry:
            flush()
            continue
        source_lines.add(lineno)
        if not line.strip():
            continue
        field = RE_PROJECT_EVENT_FIELD.fullmatch(line)
        if field is None:
            mark_problem(lineno, 'unsupported_content')
            continue
        authored_label = field.group('label')
        if authored_label not in {'Author', 'Commits', 'Summary'}:
            mark_problem(lineno, 'unsupported_field')
            continue
        label = authored_label.lower()
        pending['fields'].append((label, field.group('value'), lineno))
    flush()
    return (records, errors, source_lines)

def _amendment(doc: str, family: str, line: int, shape: str, **fields) -> SpecObject:
    producer_meta = fields.pop('_producer_meta', {})
    rev = fields.get('rev')
    ck = fields.get('change_kind')
    status = fields.get('status')
    declared_shape = shape in {'block', 'compact'}
    attr_provenance = {attribute: 'declared' for attribute in ('change_kind', 'touches') if declared_shape and fields.get(attribute) is not None}
    return SpecObject(obj_id=f'{doc}#{rev}' if rev else f"{doc}#{fields.get('date')}@{line}", kind='amendment', family=family, doc=doc, line=line, text=fields.get('summary') or '', attrs={'shape': shape, 'field_provenance': 'declared' if declared_shape else 'inferred', 'attr_provenance': attr_provenance, 'conformant_status': status in AMENDMENT_STATUS if status else None, 'conformant_change_kind': ck in CHANGE_KIND if ck else None, 'rationale_required': ck in RATIONALE_REQUIRED if ck else None, **fields}, producer_meta=producer_meta)

def parse_changelog_entries(lines, doc: str, family: str) -> list:
    """Parse a document's change log into amendment + rationale objects.

    Accepts all three authored shapes required by SBC-00-ADDENDUM-D §2.3:
    block (§2.1), compact (§2.2), and the legacy table/bullet forms.
    """
    objects: list[SpecObject] = []
    in_log = False
    log_depth = 0
    pending = None
    pending_line = 0
    rationale_line = 0
    rationale: list[str] = []
    in_rationale = False
    fence = locations.CommonMarkFence()
    compact_table = False

    def is_compact_header(line: str) -> bool:
        """Return whether a row declares the ADDENDUM-D §2.2 columns."""
        return bool(line.lstrip().startswith('|') and 'change kind' in line.lower() and (not RE_CL_TABLE_ROW.match(line)))

    def flush():
        nonlocal pending, rationale, in_rationale, rationale_line
        if not pending:
            return
        text = '\n'.join(rationale).strip()
        pending['has_rationale'] = bool(text)
        meta = pending.pop('_producer_meta')
        obj = _amendment(doc, family, pending_line, 'block', _producer_meta=meta, **pending)
        objects.append(obj)
        if text:
            objects.append(SpecObject(obj_id=f"{doc}#{pending['rev']}-rationale", kind='rationale', family=family, doc=doc, line=rationale_line or pending_line, text=text, attrs={'motivates': pending.get('touches') or []}, producer_meta={'amendment_revision': pending.get('rev'), 'touches_line': meta.get('touches_line')}))
        pending, rationale, in_rationale, rationale_line = (None, [], False, 0)
    for lineno, line in enumerate(lines, start=1):
        if fence.consume(line):
            continue
        if fence.active:
            continue
        head = RE_HEADING.match(line)
        if head:
            depth = len(head.group(1))
            if RE_CL_SECTION.match(line):
                flush()
                in_log, log_depth, compact_table = (True, depth, False)
                continue
            if in_log and depth <= log_depth:
                flush()
                in_log = False
                continue
        if not in_log:
            continue
        bh = RE_CL_BLOCK_HEAD.match(line)
        if bh:
            flush()
            pending_line = lineno
            pending = {'rev': bh.group('rev'), 'date': bh.group('date'), 'status': bh.group('status').strip().lower(), 'author': None, 'change_kind': None, 'touches': None, 'commits': None, 'summary': None, '_producer_meta': {'field_lines': {}, 'field_counts': collections.Counter(), 'touches_present': False, 'touches_members': [], 'retired_dependency_fields': [], 'invalid_retired_dependency_lines': []}}
            continue
        if pending is not None:
            starts_legacy_entry = bool(RE_CL_TABLE_ROW.match(line) or RE_CL_BULLET_ROW.match(line) or is_compact_header(line) or RE_PROJECT_EVENT_CANDIDATE.match(line))
            if starts_legacy_entry:
                flush()
            else:
                if RE_CL_RATIONALE_HEAD.match(line):
                    in_rationale = True
                    rationale_line = lineno
                    continue
                fm = RE_CL_FIELD.match(line)
                if fm and (not in_rationale):
                    key = fm.group(1).lower().replace(' ', '_')
                    val = fm.group(2).strip()
                    meta = pending['_producer_meta']
                    meta['field_counts'][key] += 1
                    meta['field_lines'].setdefault(key, lineno)
                    if key in {'touches', 'commits'}:
                        pending[key] = _split_list(val, reject_mixed_empty=key == 'touches')
                        if key == 'touches':
                            meta['touches_present'] = True
                            meta['touches_line'] = lineno
                            meta['touches_members'] = copy.deepcopy(pending[key])
                    elif key == 'change_kind':
                        pending[key] = val.strip().lower()
                    else:
                        pending[key] = val
                    continue
                if line.lstrip().startswith('Retires-Dependency:') and (not in_rationale):
                    meta = pending['_producer_meta']
                    retirement = RE_RETIRES_DEPENDENCY.fullmatch(line) if line.startswith('Retires-Dependency:') else None
                    if retirement:
                        meta['retired_dependency_fields'].append({'upstream': retirement.group('upstream'), 'dependent': retirement.group('dependent'), 'edge_type': retirement.group('edge_type'), 'line': lineno})
                    else:
                        meta['invalid_retired_dependency_lines'].append(lineno)
                    continue
                if in_rationale:
                    rationale.append(line)
                continue
        if is_compact_header(line):
            compact_table = True
            continue
        tm = RE_CL_TABLE_ROW.match(line)
        if tm:
            cells = [c.strip() for c in line.strip().strip('|').split('|')]
            if compact_table and len(cells) >= 7:
                compact_touches = _split_list(cells[5], reject_mixed_empty=True)
                objects.append(_amendment(doc, family, lineno, 'compact', rev=cells[0], date=cells[1], author=cells[2], status=cells[3].strip('* ').lower(), change_kind=cells[4].strip('* ').lower(), touches=compact_touches, commits=None, summary=cells[6], has_rationale=False, _producer_meta={'field_lines': {'change_kind': lineno, 'touches': lineno}, 'field_counts': {'change_kind': 1, 'touches': 1}, 'touches_present': True, 'touches_line': lineno, 'touches_members': copy.deepcopy(compact_touches), 'retired_dependency_fields': [], 'invalid_retired_dependency_lines': []}))
            else:
                objects.append(_amendment(doc, family, lineno, 'legacy-table', rev=cells[0], date=cells[1], author=cells[2] if len(cells) > 2 else None, status=cells[3].strip('* ').lower() if len(cells) > 3 else None, change_kind=None, touches=None, commits=None, summary=cells[4] if len(cells) > 4 else '', has_rationale=False))
            continue
        bm = RE_CL_BULLET_ROW.match(line)
        if bm:
            status = RE_STATUS_WORD.findall(line)
            objects.append(_amendment(doc, family, lineno, 'legacy-bullet', rev=None, date=bm.group(1), author=None, status=status[0].strip().rstrip('.').lower() if status else None, change_kind=None, touches=None, commits=None, summary=line.strip('- ').strip(), has_rationale=False))
    flush()
    amendments = [o for o in objects if o.kind == 'amendment']
    dated = [o for o in amendments if o.attrs.get('date')]
    for rank, obj in enumerate(sorted(dated, key=lambda o: (o.attrs['date'], o.line)), start=1):
        obj.attrs['chronological_rank'] = rank
    file_order = [o.attrs.get('date') for o in dated]
    for obj in amendments:
        obj.attrs['doc_entries_out_of_order'] = file_order != sorted(file_order)
    return objects
ERRATA_STATUS_BY_ICON = {'🟢': 'resolved', '🟡': 'diagnosed', '🔴': 'open', '⚪': 'deviation-pending-ratification'}

def _errata_status(value: str) -> tuple[str | None, str | None]:
    """Return the ADDENDUM-B status value and its icon, if recognized."""
    normalized = locations.strip_cell_markup(value).strip()
    for icon, status in ERRATA_STATUS_BY_ICON.items():
        if normalized.startswith(icon):
            return (status, icon)
    normalized = re.sub('\\s+', ' ', normalized.lower())
    for status in ERRATA_STATUS_BY_ICON.values():
        if normalized == status or normalized.startswith(status + ' '):
            icon = next((k for k, v in ERRATA_STATUS_BY_ICON.items() if v == status))
            return (status, icon)
    return (None, None)

def _strip_html_comments(lines: list[str]) -> list[str]:
    """Remove CommonMark HTML comments while preserving source line numbers."""
    visible: list[str] = []
    in_comment = False
    fence = locations.CommonMarkFence()
    for line in lines:
        if not in_comment and fence.consume(line):
            visible.append(line)
            continue
        if not in_comment and fence.active:
            visible.append(line)
            continue
        cursor = 0
        parts: list[str] = []
        while cursor < len(line):
            if in_comment:
                end = line.find('-->', cursor)
                if end < 0:
                    cursor = len(line)
                    break
                in_comment = False
                cursor = end + 3
                continue
            start = line.find('<!--', cursor)
            if start < 0:
                parts.append(line[cursor:])
                break
            parts.append(line[cursor:start])
            in_comment = True
            cursor = start + 4
        visible.append(''.join(parts))
    return visible

def _parse_errata_metadata(lines: list[str]) -> tuple[dict, dict, list]:
    """Join permanent ERRATA Index rows to body status declarations."""
    index_rows: dict[str, list[dict]] = collections.defaultdict(list)
    body_rows: dict[str, list[dict]] = collections.defaultdict(list)
    diagnostics: list[dict] = []
    in_index = False
    index_depth = 0
    status_col = None
    fence = locations.CommonMarkFence()
    for lineno, line in enumerate(lines, start=1):
        if fence.consume(line):
            continue
        if fence.active:
            continue
        heading = RE_HEADING.match(line)
        if heading:
            depth = len(heading.group(1))
            if in_index and depth <= index_depth:
                in_index = False
                status_col = None
            title = heading.group(2).strip().lower()
            title = re.sub('^§?\\d+(?:\\.\\d+)*\\s*', '', title).strip()
            if title == 'index':
                in_index = True
                index_depth = depth
                status_col = None
            continue
        if not in_index:
            continue
        cells = locations.split_markdown_row(line)
        if not cells:
            continue
        cleaned = [locations.strip_cell_markup(c) for c in cells]
        lowered = [c.lower() for c in cleaned]
        if lowered and lowered[0] in {'id', 'errata', 'errata id'}:
            status_col = lowered.index('status') if 'status' in lowered else None
            continue
        if not cleaned or re.fullmatch(':?-{3,}:?', cleaned[0]):
            continue
        match = re.fullmatch('ERRATA-(\\d+)', cleaned[0])
        if not match:
            match = re.fullmatch('\\[(ERRATA-\\d+)\\]\\([^)]*\\)', cleaned[0])
        if not match:
            continue
        eid = match.group(1) if match.group(1).startswith('ERRATA-') else match.group(0)
        raw = cells[status_col] if status_col is not None and status_col < len(cells) else ''
        status, icon = _errata_status(raw)
        index_rows[eid].append({'line': lineno, 'status': status, 'icon': icon, 'raw_present': bool(raw.strip())})
        if status is None:
            diagnostics.append({'kind': 'errata_unsupported_status', 'errata_id': eid, 'line': lineno, 'source': 'index'})
    current_id = None
    current_depth = 0
    fence = locations.CommonMarkFence()
    for lineno, line in enumerate(lines, start=1):
        if fence.consume(line):
            continue
        if fence.active:
            continue
        heading = RE_HEADING.match(line)
        if heading:
            depth = len(heading.group(1))
            if current_id is not None and depth <= current_depth:
                current_id = None
            match = RE_ERRATA_DEF.match(line)
            if match:
                current_id = match.group(1)
                current_depth = depth
                body_rows[current_id].append({'line': lineno, 'status': None, 'icon': None})
            continue
        if current_id is None:
            continue
        match = RE_HEADER_ATTR.match(line)
        if match and match.group(1).strip().lower() == 'status':
            status, icon = _errata_status(match.group(2))
            body_rows[current_id][-1]['status'] = status
            body_rows[current_id][-1]['icon'] = icon
            if status is None:
                diagnostics.append({'kind': 'errata_unsupported_status', 'errata_id': current_id, 'line': lineno, 'source': 'body'})
    for eid in sorted(body_rows):
        if eid not in index_rows:
            diagnostics.append({'kind': 'errata_missing_index_row', 'errata_id': eid, 'line': body_rows[eid][0]['line']})
    for eid in sorted(index_rows):
        if eid not in body_rows:
            diagnostics.append({'kind': 'errata_index_without_body', 'errata_id': eid, 'line': index_rows[eid][0]['line']})
        if len(index_rows[eid]) > 1:
            diagnostics.append({'kind': 'errata_duplicate_index_row', 'errata_id': eid, 'lines': [row['line'] for row in index_rows[eid]]})
        if eid in body_rows and len(body_rows[eid]) > 1:
            diagnostics.append({'kind': 'errata_duplicate_body', 'errata_id': eid, 'lines': [row['line'] for row in body_rows[eid]]})
        if len(index_rows[eid]) == 1 and len(body_rows.get(eid, [])) == 1:
            index_status = index_rows[eid][0]['status']
            body_status = body_rows[eid][0]['status']
            if index_status and body_status and (index_status != body_status):
                diagnostics.append({'kind': 'errata_status_disagreement', 'errata_id': eid, 'lines': [index_rows[eid][0]['line'], body_rows[eid][0]['line']], 'index_status': index_status, 'body_status': body_status})
    return (dict(index_rows), dict(body_rows), diagnostics)

def _is_open_question_heading(title: str) -> bool:
    normalized = re.sub('^§?\\d+(?:\\.\\d+)*\\s*', '', title.lower()).strip()
    return bool(re.search('\\b(?:open questions?|open decisions?|resolved decisions?|decisions?)\\b', normalized))

def _open_question_key(handle: str, family: str) -> str:
    """Qualify only EOQ handles, whose upstream scope is one errata family."""
    return f'{family}:{handle}' if RE_EOQ.fullmatch(handle) else handle

def _open_question_status(heading: str, resolution: str, lifecycle_state: str, resolution_label: str | None=None) -> tuple[str, str]:
    """Derive only the frozen status supported by authored row/section state."""
    row = locations.strip_cell_markup(resolution).lower()
    normalized = heading.lower()
    if 'resolved' in normalized or 'all resolved' in normalized:
        return ('resolved', 'inferred')
    if 'recommendations are not ratified' in normalized or 'awaiting ratification' in normalized:
        return ('pending_ratification', 'inferred')
    if resolution_label == 'recommendation' and lifecycle_state == 'draft':
        return ('pending_ratification', 'inferred')
    if re.search('^(?:resolution:\\s*)?(?:resolved|adopted|accepted)\\b', row):
        return ('resolved', 'declared')
    if 'pending ratification' in row or 'awaiting ratification' in row or 'not ratified' in row:
        return ('pending_ratification', 'declared')
    if re.search('^(?:status:\\s*)?open\\b', row):
        return ('open', 'declared')
    if 'open decision' in normalized and lifecycle_state == 'draft':
        return ('pending_ratification', 'inferred')
    if 'open question' in normalized:
        return ('open', 'inferred')
    if 'decision' in normalized and lifecycle_state == 'ratified':
        return ('resolved', 'inferred')
    return ('unknown', 'inferred')

def parse_document(text, relative_path, family, registered_prefixes) -> tuple[Document, list, list]:
    rel = pathlib.PurePosixPath(relative_path)
    doc = Document(path=str(rel), family=family, is_concepts='CONCEPTS' in rel.name.upper())
    objects: list[SpecObject] = []
    citations: list[Citation] = []
    raw_lines = text.splitlines()
    lines = _strip_html_comments(raw_lines)
    project_events, project_event_errors, project_event_lines = parse_project_event_records(lines, str(rel))
    doc.project_event_entries = len(project_events)
    doc.producer_errors.extend(project_event_errors)
    doc.header, doc.header_lines, doc.title = locations.parse_markdown_header(lines)
    if any((locations._unsafe_kind(value) is not None for value in doc.header.values())):
        raise ProjectionError('document header contains an unsafe value')
    lifecycle_state, lifecycle_provenance, lifecycle_valid = locations.resolve_lifecycle(doc.header)
    if not lifecycle_valid:
        doc.diagnostics.append({'kind': 'invalid_document_lifecycle', 'line': doc.header_lines.get('document lifecycle state')})
    errata_index, _errata_bodies, errata_diagnostics = _parse_errata_metadata(lines)
    doc.diagnostics.extend(errata_diagnostics)
    document_id = doc.header.get('document id', '').strip()
    if document_id:
        definition_line = doc.header_lines.get('document id', 1)
        objects.append(SpecObject(obj_id=document_id, kind='document', family=doc.family, doc=str(rel), line=definition_line, text=doc.title, attrs={'lifecycle_state': lifecycle_state, 'attr_provenance': {'lifecycle_state': lifecycle_provenance}}))
        citations.append(Citation(obj_id=document_id, doc=str(rel), line=definition_line, family=doc.family, is_definition=True))
    section = None
    section_heading = ''
    table_headers: list[str] | None = None
    fence = locations.CommonMarkFence()
    cl_table = cl_bullet = 0
    defined_here: set[str] = set()
    for lineno, line in enumerate(lines, start=1):
        if fence.consume(line):
            continue
        if fence.active:
            continue
        if lineno in project_event_lines:
            continue
        open_definition_handle = None
        open_definition_id = None
        spec_edge_candidate, invalid_spec_edge = _parse_spec_edge_candidate(line, document=str(rel), line_number=lineno, family=doc.family)
        if invalid_spec_edge:
            doc.producer_errors.append({'kind': 'invalid_spec_edge_field', 'line': lineno})
        elif spec_edge_candidate is not None:
            citations.append(spec_edge_candidate)
        m = RE_HEADING.match(line)
        if m:
            title = m.group(2).strip()
            section_heading = title
            table_headers = None
            stable_section = RE_STABLE_SECTION_HEADING.fullmatch(title)
            if stable_section is not None:
                objects.append(SpecObject(obj_id=f"{doc.family}:{stable_section.group('handle')}", kind='section', family=doc.family, doc=str(rel), line=lineno, text=stable_section.group('title'), attrs={}))
            num = None
            sm = RE_SECTION_NUM.match(title.lstrip('#').strip())
            if sm:
                num = int(sm.group(1))
            else:
                low = title.lower()
                for hint, hint_num in SECTION_HINTS.items():
                    if hint in low:
                        num = hint_num
                        break
            if num is not None:
                section = num
                doc.sections.add(num)
            elif m.group(1) == '##':
                section = None
        if section == 15:
            if RE_CL_TABLE_ROW.match(line):
                cl_table += 1
            elif RE_CL_BULLET_ROW.match(line):
                cl_bullet += 1
        inv_ids: list[str] = []
        statement = verified = title = None
        shape = None
        dm = RE_INV_DEF_ROW_SPAN.match(line)
        if dm:
            inv_ids, title = _definition_ids(dm.group('span'))
            if inv_ids:
                cells = [c.strip() for c in dm.group('rest').split('|')]
                statement = cells[0] if cells else ''
                verified = cells[1] if len(cells) > 1 else ''
                shape = 'table'
            else:
                legacy_dm = RE_INV_DEF_ROW.match(line)
                if legacy_dm:
                    inv_ids = [legacy_dm.group(1)]
                    cells = [c.strip() for c in legacy_dm.group(2).split('|')]
                    statement = cells[0] if cells else ''
                    verified = cells[1] if len(cells) > 1 else ''
                    title = ''
                    shape = 'table'
        else:
            bm = RE_INV_DEF_BULLET_SPAN.match(line)
            if bm:
                inv_ids, title = _definition_ids(bm.group('span'))
                if inv_ids:
                    statement = _statement_tail(bm.group('rest'))
                    verified = ''
                    shape = 'bullet'
                else:
                    legacy_bm = RE_INV_DEF_BULLET.match(line)
                    if legacy_bm:
                        inv_ids = [legacy_bm.group(1)]
                        title = legacy_bm.group(2).strip()
                        statement = legacy_bm.group(3).strip()
                        verified = ''
                        shape = 'bullet'
            else:
                hm2 = RE_INV_DEF_HEADING_SPAN.match(line)
                if hm2:
                    inv_ids, title = _definition_ids(hm2.group('span'))
                    if inv_ids:
                        statement = _statement_tail(hm2.group('rest'))
                        verified = ''
                        shape = 'heading'
                    else:
                        legacy_hm = RE_INV_DEF_HEADING.match(line)
                        if legacy_hm:
                            inv_ids = [legacy_hm.group(1)]
                            title, statement = (legacy_hm.group(2).strip(), '')
                            verified = ''
                            shape = 'heading'
                else:
                    hm3 = RE_INV_DEF_HEADING.match(line)
                    if hm3:
                        inv_ids = [hm3.group(1)]
                        title, statement = (hm3.group(2).strip(), '')
                        verified = ''
                        shape = 'heading'
        for inv_id in inv_ids:
            defined_here.add(inv_id)
            objects.append(SpecObject(obj_id=inv_id, kind='invariant', family=doc.family, doc=str(rel), line=lineno, text=statement or '', attrs={'title': title or '', 'def_shape': shape, 'verified_by': verified or '', 'has_verification': bool(verified and verified not in {'', '—', '-'}), 'attr_provenance': {'has_verification': 'inferred'}, 'normative_keywords': sorted(set(RFC2119.findall(statement or ''))), 'doc_status': doc.header.get('status', '').strip()}))
        em = RE_ERRATA_DEF.match(line)
        if em:
            eid = em.group(1)
            scoped = f'{doc.family}:{eid}'
            defined_here.add(eid)
            rows = errata_index.get(eid, [])
            status_row = rows[0] if len(rows) == 1 and rows[0].get('status') else None
            objects.append(SpecObject(obj_id=scoped, kind='errata', family=doc.family, doc=str(rel), line=lineno, text=em.group(2).strip(), attrs={'status': status_row.get('status') if status_row else None, 'status_icon': status_row.get('icon') if status_row else None, 'attr_provenance': {'status': 'declared'} if status_row else {}}))
            citations.append(Citation(obj_id=scoped, doc=str(rel), line=lineno, family=doc.family, is_definition=True))
        if section == 3:
            cells = locations.split_markdown_row(line)
            stable_row = False
            malformed_stable_row = False
            stable_handle = None
            stable_term = None
            if cells is not None and len(cells) == 4:
                candidate_handle = locations.strip_cell_markup(cells[0])
                term_match = RE_GLOSSARY_TERM_CELL.fullmatch(cells[1].strip())
                if term_match is not None:
                    stable_term = term_match.group(1).strip()
                    if RE_TERM_HANDLE.fullmatch(candidate_handle):
                        stable_row = True
                        stable_handle = candidate_handle
                    elif candidate_handle.upper().startswith('TERM-'):
                        malformed_stable_row = True
            gm = RE_GLOSSARY_ROW.match(line)
            if stable_row:
                objects.append(SpecObject(obj_id=f'{doc.family}:{stable_handle}', kind='term', family=doc.family, doc=str(rel), line=lineno, text=cells[2].strip()[:400], attrs={'relationship': cells[3].strip()[:200], 'term': stable_term}))
            elif malformed_stable_row:
                low = stable_term.lower()
                if low not in AUTHORITY_AXES and (not stable_term.startswith('Term')):
                    objects.append(SpecObject(obj_id=f'{doc.family}:term:{low}', kind='term', family=doc.family, doc=str(rel), line=lineno, text=cells[2].strip()[:400], attrs={'relationship': cells[3].strip()[:200], 'term': stable_term}))
            elif gm:
                term = gm.group(1).strip()
                low = term.lower()
                if low not in AUTHORITY_AXES and (not term.startswith('Term')):
                    objects.append(SpecObject(obj_id=f'{doc.family}:term:{low}', kind='term', family=doc.family, doc=str(rel), line=lineno, text=gm.group(2).strip()[:400], attrs={'relationship': gm.group(3).strip()[:200], 'term': term}))
        if section == 12:
            am = RE_ACCEPTANCE_GATE.match(line)
            if am:
                gate_text = am.group(2).strip()
                stable_gate = RE_STABLE_ACCEPTANCE_GATE.fullmatch(gate_text)
                if stable_gate:
                    gate_id = f"{doc.family}:{stable_gate.group('handle')}"
                    gate_text = stable_gate.group('text')
                else:
                    gate_id = f'{rel}:gate:{lineno}'
                objects.append(SpecObject(obj_id=gate_id, kind='gate', family=doc.family, doc=str(rel), line=lineno, text=gate_text[:400], attrs={'checked': am.group(1).lower() == 'x', 'attr_provenance': {'checked': 'declared'}, 'cited_ids': sorted({mm.group(0) for mm in RE_INVARIANT.finditer(gate_text)})}))
        if section == 11:
            item = RE_NONGOAL_ITEM.match(line)
            if item:
                content = item.group('content')
                stable_nongoal = RE_STABLE_NONGOAL.fullmatch(content)
                readable_nongoal = stable_nongoal or RE_LEGACY_NONGOAL.fullmatch(content)
                if readable_nongoal is None:
                    readable_nongoal = RE_MALFORMED_NONGOAL.fullmatch(content)
                if readable_nongoal is not None:
                    if stable_nongoal:
                        nongoal_id = f"{doc.family}:{stable_nongoal.group('handle')}"
                    else:
                        nongoal_id = f"{rel}:nongoal:{item.group('ordinal')}"
                    objects.append(SpecObject(obj_id=nongoal_id, kind='nongoal', family=doc.family, doc=str(rel), line=lineno, text=(readable_nongoal.group('title') + ' ' + readable_nongoal.group('body')).strip()[:400]))
        cells = locations.split_markdown_row(line)
        if cells:
            cleaned_cells = [locations.strip_cell_markup(cell) for cell in cells]
            first = cleaned_cells[0] if cleaned_cells else ''
            if first and (not (RE_PCDN.fullmatch(first) or RE_EOQ.fullmatch(first))):
                lowered = [cell.lower() for cell in cleaned_cells]
                if any((name in lowered for name in ('decision', 'question', 'ask'))):
                    table_headers = lowered
            eligible_question_section = _is_open_question_heading(section_heading)
            valid_open_handle = bool(RE_PCDN.fullmatch(first) or RE_EOQ.fullmatch(first))
            if eligible_question_section and first.startswith(('PCDN-', 'EOQ-')) and ('NNN' not in first) and (not valid_open_handle):
                doc.diagnostics.append({'kind': 'malformed_open_question_handle', 'line': lineno, 'handle': first})
            if eligible_question_section and valid_open_handle:
                open_definition_handle = first
                open_definition_id = _open_question_key(first, doc.family)
                question_index = 1
                resolution_index = None
                resolution_label = None
                if table_headers:
                    for label in ('decision', 'question', 'ask'):
                        if label in table_headers:
                            question_index = table_headers.index(label)
                            break
                    for label in ('resolution', 'recommendation', 'status'):
                        if label in table_headers:
                            resolution_index = table_headers.index(label)
                            resolution_label = label
                            break
                question = cells[question_index].strip() if question_index < len(cells) else ''
                resolution = cells[resolution_index].strip() if resolution_index is not None and resolution_index < len(cells) else ''
                question_status, status_provenance = _open_question_status(section_heading, resolution, lifecycle_state, resolution_label)
                defined_here.add(open_definition_id)
                objects.append(SpecObject(obj_id=open_definition_id, kind='open_question', family=doc.family, doc=str(rel), line=lineno, text=question, attrs={'status': question_status, 'resolution': resolution, 'def_shape': 'decision-table', 'attr_provenance': {'status': status_provenance}}))
        if spec_edge_candidate is not None or invalid_spec_edge or line.lstrip().startswith('Retires-Dependency:'):
            continue
        line_invariant_ids = [cm.group(0) for cm in RE_INVARIANT.finditer(line)]
        for cm in RE_INVARIANT.finditer(line):
            citations.append(Citation(obj_id=cm.group(0), doc=str(rel), line=lineno, family=doc.family, is_definition=cm.group(0) in inv_ids))
        for expanded_id in inv_ids:
            if expanded_id not in line_invariant_ids:
                citations.append(Citation(obj_id=expanded_id, doc=str(rel), line=lineno, family=doc.family, is_definition=True))
        for pm in RE_PCDN.finditer(line):
            citations.append(Citation(obj_id=pm.group(0), doc=str(rel), line=lineno, family=doc.family, is_definition=pm.group(0) == open_definition_handle))
        for qm in RE_EOQ.finditer(line):
            citations.append(Citation(obj_id=_open_question_key(qm.group(0), doc.family), doc=str(rel), line=lineno, family=doc.family, is_definition=qm.group(0) == open_definition_handle))
    cl_objects = parse_changelog_entries(lines, str(rel), doc.family)
    objects.extend(cl_objects)
    shapes = {o.attrs['shape'] for o in cl_objects if o.kind == 'amendment'}
    amendments = [o for o in cl_objects if o.kind == 'amendment']
    if len(shapes) > 1:
        doc.changelog_shape = 'mixed'
    elif shapes:
        doc.changelog_shape = next(iter(shapes))
    elif 15 in doc.sections or 9 in doc.sections:
        doc.changelog_shape = 'unparsed' if RE_CL_SECTION_PRESENT(lines) else 'none'
    doc.changelog_entries = len(amendments)
    retirement_lines = set()
    fence = locations.CommonMarkFence()
    for line_number, line in enumerate(lines, start=1):
        if fence.consume(line):
            continue
        if not fence.active and line_number not in project_event_lines and line.lstrip().startswith('Retires-Dependency:'):
            retirement_lines.add(line_number)
    consumed_retirement_lines = {entry['line'] for amendment in amendments for entry in amendment.producer_meta.get('retired_dependency_fields', [])} | {line_number for amendment in amendments for line_number in amendment.producer_meta.get('invalid_retired_dependency_lines', [])}
    for line_number in sorted(retirement_lines - consumed_retirement_lines):
        doc.producer_errors.append({'kind': 'invalid_retired_dependency_context', 'line': line_number})
    projected = _projected_definitions({'objects': objects})
    existing = {(_canonical_reference(citation.obj_id), citation.doc, citation.line, citation.is_definition) for citation in citations}
    for definition in projected:
        payload = definition.payload
        key = (payload['obj_id'], payload['doc'], payload['line'], True)
        if key not in existing:
            citations.append(Citation(obj_id=payload['obj_id'], doc=payload['doc'], line=payload['line'], family=payload['family'], is_definition=True))
            existing.add(key)
    _append_known_mentions(lines, doc, projected, citations, eligible_kinds={'document', 'errata', 'term', 'gate', 'nongoal', 'amendment', 'rationale'})
    historical_only_definitions = _historical_definition_ids(doc, lines, projected, registered_prefixes, lifecycle_state=lifecycle_state, lifecycle_provenance=lifecycle_provenance)
    if historical_only_definitions:
        objects = [obj for obj in objects if _canonical_reference(obj.obj_id) not in historical_only_definitions]
        citations = [citation for citation in citations if _canonical_reference(citation.obj_id) not in historical_only_definitions and _canonical_reference(citation.source_token) not in historical_only_definitions]
    return (doc, objects, citations)

def RE_CL_SECTION_PRESENT(lines) -> bool:
    return any((RE_CL_SECTION.match(ln) for ln in lines))

def _registered_invariant_prefixes(text) -> set[str]:
    prefixes = {match.group(1) for match in re.finditer('^\\| `([A-Z]{2,8})` \\|', text, re.MULTILINE)}
    prefixes.update((match.group(1) for match in re.finditer('\\*\\*Claimed[^\\n]*`([A-Z]{2,8})`', text)))
    return prefixes - EXAMPLE_PREFIXES - {'PHASE'}

def _append_known_mentions(lines: list[str], doc: Document, projected: list[_ProjectedDefinition], citations: list[Citation], *, eligible_kinds: set[str], token_map: dict[str, str] | None=None, token_pattern: re.Pattern | None=None) -> None:
    """Add citations only for exact known object-id tokens outside carriers."""
    tokens: dict[str, str] = dict(token_map or {})
    definition_ids: dict[tuple[str, int], set[str]] = collections.defaultdict(set)
    for definition in projected:
        payload = definition.payload
        definition_ids[payload['doc'], payload['line']].add(payload['obj_id'])
        if token_map is not None or payload['kind'] not in eligible_kinds:
            continue
        if payload['kind'] in {'term', 'gate', 'nongoal'}:
            prefix, separator, handle = payload['obj_id'].partition(':')
            handle_pattern = {'term': RE_TERM_HANDLE, 'gate': RE_GATE_HANDLE, 'nongoal': RE_NONGOAL_HANDLE}[payload['kind']]
            if not separator or prefix != payload['family'] or handle_pattern.fullmatch(handle) is None:
                continue
            tokens[payload['obj_id']] = payload['obj_id']
            if payload['family'] == doc.family:
                tokens[handle] = payload['obj_id']
            continue
        tokens[payload['obj_id']] = payload['obj_id']
        if payload['family'] == doc.family and payload['kind'] == 'errata':
            tokens[payload['obj_id'].split(':', 1)[1]] = payload['obj_id']
    if not tokens:
        return
    if token_pattern is None:
        alternatives = '|'.join((re.escape(token) for token in sorted(tokens, key=lambda item: (-len(item), item))))
        token_pattern = re.compile(f'{_ID_TOKEN_LEFT}(?:{alternatives}){_ID_TOKEN_RIGHT}', re.ASCII)
    existing = {(_canonical_reference(citation.obj_id), citation.doc, citation.line, citation.is_definition) for citation in citations}
    fence = locations.CommonMarkFence()
    for line_number, line in enumerate(lines, start=1):
        if fence.consume(line):
            continue
        if fence.active or line.lstrip().startswith('**Spec Edge:**') or line.lstrip().startswith('Retires-Dependency:'):
            continue
        for match in token_pattern.finditer(line):
            token = match.group(0)
            canonical = tokens[token]
            is_definition = canonical in definition_ids.get((doc.path, line_number), set())
            key = (canonical, doc.path, line_number, is_definition)
            if key in existing:
                continue
            citations.append(Citation(obj_id=canonical, doc=doc.path, line=line_number, family=doc.family, is_definition=is_definition))
            existing.add(key)

def scan(sources, registered_prefixes) -> dict:
    docs = []
    objects = []
    citations = []
    texts = {}
    registered_prefixes = sorted(registered_prefixes)
    for relative_path, family, text in sources:
        d, o, c = parse_document(text, relative_path, family, registered_prefixes)
        docs.append(d)
        objects.extend(o)
        citations.extend(c)
        texts[relative_path] = text
    projected = _projected_definitions({'objects': objects})
    eligible = [definition for definition in projected if _definition_is_edge_eligible(definition, set(registered_prefixes))]
    global_tokens = {definition.payload['obj_id']: definition.payload['obj_id'] for definition in eligible if definition.payload['kind'] in {'document', 'errata', 'term', 'gate', 'nongoal', 'amendment', 'rationale'}}
    family_aliases: dict[str, dict[str, str]] = collections.defaultdict(dict)
    for definition in eligible:
        payload = definition.payload
        if payload['kind'] in {'errata', 'term', 'gate', 'nongoal'}:
            family_aliases[payload['family']][payload['obj_id'].split(':', 1)[1]] = payload['obj_id']
    pattern_cache: dict[str, tuple[dict[str, str], re.Pattern | None]] = {}
    documents_by_path = {document.path: document for document in docs}
    for path, document in documents_by_path.items():
        lines = texts[path].splitlines()
        cached = pattern_cache.get(document.family)
        if cached is None:
            document_tokens = {**global_tokens, **family_aliases[document.family]}
            alternatives = '|'.join((re.escape(token) for token in sorted(document_tokens, key=lambda item: (-len(item), item))))
            document_pattern = re.compile(f'{_ID_TOKEN_LEFT}(?:{alternatives}){_ID_TOKEN_RIGHT}', re.ASCII) if alternatives else None
            cached = (document_tokens, document_pattern)
            pattern_cache[document.family] = cached
        document_tokens, document_pattern = cached
        _append_known_mentions(lines, document, eligible, citations, eligible_kinds={'document', 'errata', 'term', 'gate', 'nongoal', 'amendment', 'rationale'}, token_map=document_tokens, token_pattern=document_pattern)
    return {'docs': docs, 'objects': objects, 'citations': citations, 'registered_prefixes': registered_prefixes}
RE_STATUS_WORD = re.compile('\\*\\*([^*]{0,40}?(?:Ratified|Amended|DRAFT|Draft|Drafted|Execution|Superseded)[^*]{0,40}?)\\*\\*')
INDEX_SCHEMA_VERSION = 3
DIAGNOSTIC_SCHEMA_VERSION = 3
SEMANTIC_FINGERPRINT_VERSION = 1
SEMANTIC_FINGERPRINT_EXTRACTOR = {'base_fields': ['kind', 'text'], 'excluded_kinds': ['amendment', 'rationale'], 'per_kind': {'authority_row': [], 'document': ['lifecycle_state'], 'enum_value': [], 'errata': [], 'gate': ['checked'], 'invariant': ['title'], 'nongoal': [], 'open_question': ['resolution'], 'term': ['term', 'relationship']}, 'semantic_attrs_common': ['normative', 'status'], 'version': 1}
SEMANTIC_FINGERPRINT_EXTRACTOR_SHA256 = 'eadb11f7d275ed90b1455de18d2c9cae00297881e107542e564ca37a23a01a12'
DIAGNOSTIC_CODES = ('document_id_missing', 'invalid_document_lifecycle', 'open_question_definition_duplicate', 'malformed_open_question_handle', 'errata_missing_index_row', 'errata_index_without_body', 'errata_duplicate_index_row', 'errata_duplicate_body', 'errata_unsupported_status', 'errata_status_disagreement', 'dependency_source_unresolved', 'dependency_target_unresolved', 'dependency_kind_unresolved', 'change_kind_unresolved', 'touches_unresolved', 'retirement_supersedes_missing')
DECLARED_EDGE_TYPES = {'cites', 'refines', 'verifies', 'evidences', 'amends', 'supersedes', 'blocks', 'motivates', 'same-as', 'homonym-of'}
RETIRED_DEPENDENCY_TYPES = {'cites', 'refines', 'verifies', 'evidences', 'blocks', 'same-as'}
TOUCHES_REQUIRED_CHANGE_KINDS = {'clarification', 'semantic', 'scope', 'retirement'}
_CANONICAL_INVARIANT = re.compile('INV-([A-Z]{2,8})-([1-9][0-9]*)')
_GLOBAL_DOCUMENT = re.compile('[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+')
_GLOBAL_PCDN = re.compile('PCDN-(?:[A-Z0-9]+-)+[0-9]{3}')
_FAMILY_KEY = '[A-Za-z][A-Za-z0-9-]{0,63}'
_GLOBAL_EOQ = re.compile(f'({_FAMILY_KEY}):EOQ-[0-9]{{3}}-ERRATA-[0-9]{{3}}')
_GLOBAL_ERRATA = re.compile(f'({_FAMILY_KEY}):ERRATA-[0-9]{{3}}')
_GLOBAL_TERM = re.compile(f'({_FAMILY_KEY}):({_TERM_HANDLE})')
_GLOBAL_GATE = re.compile(f'({_FAMILY_KEY}):({_GATE_HANDLE})')
_GLOBAL_NONGOAL = re.compile(f'({_FAMILY_KEY}):({_NONGOAL_HANDLE})')
_GLOBAL_SECTION = re.compile(f'({_FAMILY_KEY}):({_SECTION_HANDLE})')
_REVISION = '(?:0|[1-9][0-9]*)\\.(?:0|[1-9][0-9]*)\\.(?:0|[1-9][0-9]*)'
_GLOBAL_AMENDMENT = re.compile(f'(.+)#amendment:({_REVISION})')
_GLOBAL_RATIONALE = re.compile(f'(.+)#amendment:({_REVISION})#rationale')
MAX_DIAGNOSTIC_RECORDS = 100000
MAX_DIAGNOSTIC_LOCATORS = 10000
MAX_DIAGNOSTIC_DOCUMENT_BYTES = 1024
MAX_DIAGNOSTIC_MANIFEST_BYTES = 1 * 1024 * 1024
MAX_DIAGNOSTIC_FAMILY_BYTES = 16 * 1024 * 1024
MAX_DIAGNOSTIC_TOTAL_BYTES = 64 * 1024 * 1024

class ProjectionError(RuntimeError):
    """A schema-v3 projection cannot be represented without guessing."""

@dataclasses.dataclass
class _ProjectedDefinition:
    source: SpecObject
    payload: dict

@dataclasses.dataclass(frozen=True)
class ProjectionExpectations:
    """Private, in-memory expectations derived from one parsed candidate pass."""
    registered_prefixes: frozenset[str]
    object_sha256: str
    location_sha256: str | None
    diagnostic_sha256: str
    location_descriptors: tuple[tuple[str, int, int, str], ...] | None
    diagnostic_descriptors: tuple[tuple[str, str, int, str], ...]
    diagnostic_record_keys: tuple[str, ...]

def _validate_canonical_json(value) -> None:
    if value is None or type(value) in {bool, int}:
        return
    if isinstance(value, str):
        if unicodedata.normalize('NFC', value) != value:
            raise ProjectionError('canonical JSON contains a non-NFC string')
        if any((unicodedata.category(char) == 'Cs' for char in value)):
            raise ProjectionError('canonical JSON contains a lone surrogate')
        return
    if isinstance(value, list):
        for member in value:
            _validate_canonical_json(member)
        return
    if isinstance(value, dict):
        for key, member in value.items():
            if not isinstance(key, str):
                raise ProjectionError('canonical JSON member name is not a string')
            _validate_canonical_json(key)
            _validate_canonical_json(member)
        return
    raise ProjectionError('canonical JSON contains an unsupported value type')

def _canonical_json_bytes(value) -> bytes:
    """Return the C6 canonical bytes for the closed JSON types used here."""
    _validate_canonical_json(value)
    return json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(',', ':'), sort_keys=True).encode('utf-8')

def _validate_fingerprint_descriptor() -> None:
    actual = hashlib.sha256(_canonical_json_bytes(SEMANTIC_FINGERPRINT_EXTRACTOR)).hexdigest()
    if actual != SEMANTIC_FINGERPRINT_EXTRACTOR_SHA256:
        raise ProjectionError('semantic fingerprint extractor identity mismatch')

def _diagnostic_render(payload: dict) -> str:
    return _canonical_json_bytes(payload).decode('utf-8') + '\n'

def _canonical_reference(value: str | None) -> str | None:
    if value is None:
        return None
    match = RE_INVARIANT.fullmatch(value)
    if not match:
        return value
    prefix = match.group(1) or match.group(3)
    number = match.group(2) or match.group(4)
    return f'INV-{prefix}-{int(number)}'

def _common_global_id_valid(value: str) -> bool:
    if not isinstance(value, str) or not value:
        return False
    if unicodedata.normalize('NFC', value) != value:
        return False
    try:
        if len(value.encode('utf-8')) > 512:
            return False
    except UnicodeEncodeError:
        return False
    if value != value.strip() or any((char in value for char in ('`', '/', '\\'))) or locations._unsafe_kind(value) is not None:
        return False
    if any((unicodedata.category(char) in {'Cc', 'Cs'} for char in value)):
        return False
    invariant = _CANONICAL_INVARIANT.fullmatch(value)
    return not (invariant and invariant.group(1) in EXAMPLE_PREFIXES)

def _document_id_valid(value: str) -> bool:
    return bool(_common_global_id_valid(value) and len(value.encode('utf-8')) <= 128 and _GLOBAL_DOCUMENT.fullmatch(value))

def _syntactic_global_id(value: str | None, registered_prefixes: set[str]) -> bool:
    if value is None or not _common_global_id_valid(value):
        return False
    if _document_id_valid(value):
        return True
    invariant = _CANONICAL_INVARIANT.fullmatch(value)
    if invariant and invariant.group(1) in registered_prefixes and (invariant.group(1) not in EXAMPLE_PREFIXES):
        return True
    if len(value.encode('utf-8')) <= 128 and _GLOBAL_PCDN.fullmatch(value):
        return True
    if _GLOBAL_EOQ.fullmatch(value) or _GLOBAL_ERRATA.fullmatch(value) or _GLOBAL_TERM.fullmatch(value) or _GLOBAL_GATE.fullmatch(value) or _GLOBAL_NONGOAL.fullmatch(value) or _GLOBAL_SECTION.fullmatch(value):
        return True
    rationale = _GLOBAL_RATIONALE.fullmatch(value)
    if rationale:
        return _document_id_valid(rationale.group(1))
    amendment = _GLOBAL_AMENDMENT.fullmatch(value)
    if amendment:
        return _document_id_valid(amendment.group(1))
    return _document_id_valid(value)

def _definition_is_edge_eligible(definition: _ProjectedDefinition, registered_prefixes: set[str]) -> bool:
    value = definition.payload['obj_id']
    kind = definition.payload['kind']
    family = definition.payload['family']
    if not _common_global_id_valid(value):
        return False
    if kind == 'document':
        return _document_id_valid(value)
    if kind == 'invariant':
        match = _CANONICAL_INVARIANT.fullmatch(value)
        return bool(match and match.group(1) in registered_prefixes)
    if kind == 'open_question':
        pcdn = _GLOBAL_PCDN.fullmatch(value)
        eoq = _GLOBAL_EOQ.fullmatch(value)
        return bool(pcdn and len(value.encode('utf-8')) <= 128 or (eoq and eoq.group(1) == family))
    if kind == 'errata':
        match = _GLOBAL_ERRATA.fullmatch(value)
        return bool(match and match.group(1) == family)
    if kind == 'term':
        match = _GLOBAL_TERM.fullmatch(value)
        return bool(match and match.group(1) == family)
    if kind == 'gate':
        match = _GLOBAL_GATE.fullmatch(value)
        return bool(match and match.group(1) == family)
    if kind == 'nongoal':
        match = _GLOBAL_NONGOAL.fullmatch(value)
        return bool(match and match.group(1) == family)
    if kind == 'section':
        match = _GLOBAL_SECTION.fullmatch(value)
        return bool(match and match.group(1) == family)
    if kind == 'amendment':
        match = _GLOBAL_AMENDMENT.fullmatch(value)
        return bool(match and _document_id_valid(match.group(1)))
    if kind == 'rationale':
        match = _GLOBAL_RATIONALE.fullmatch(value)
        return bool(match and _document_id_valid(match.group(1)))
    return False

def _projected_definitions(data: dict) -> list[_ProjectedDefinition]:
    objects: list[SpecObject] = data.get('objects', [])
    document_objects: dict[str, list[SpecObject]] = collections.defaultdict(list)
    for obj in objects:
        if obj.kind == 'document':
            document_objects[obj.doc].append(obj)
    projected: list[_ProjectedDefinition] = []
    for obj in objects:
        payload = obj.to_dict()
        if obj.kind == 'invariant':
            payload['obj_id'] = _canonical_reference(obj.obj_id)
        elif obj.kind in {'amendment', 'rationale'}:
            revision = obj.attrs.get('rev') if obj.kind == 'amendment' else obj.producer_meta.get('amendment_revision')
            owner = document_objects.get(obj.doc, [])
            if len(owner) == 1 and revision and re.fullmatch(_REVISION, revision) and _document_id_valid(owner[0].obj_id) and (obj.kind == 'rationale' or obj.attrs.get('shape') in {'block', 'compact'}):
                amendment_id = f'{owner[0].obj_id}#amendment:{revision}'
                payload['obj_id'] = amendment_id if obj.kind == 'amendment' else f'{amendment_id}#rationale'
        projected.append(_ProjectedDefinition(obj, payload))
    return projected

def _definition_locator(definition: _ProjectedDefinition) -> dict:
    return {'document': definition.payload['doc'], 'line': definition.payload['line']}

def _safe_locator(document: str, line: int, *, admitted_documents) -> dict:
    if not isinstance(document, str) or not isinstance(line, int) or isinstance(line, bool) or (not 1 <= line <= 2 ** 31 - 1) or (len(document.encode('utf-8')) > MAX_DIAGNOSTIC_DOCUMENT_BYTES) or ('\\' in document) or (locations._unsafe_kind(document) is not None):
        raise ProjectionError('diagnostic locator is outside the closed safety grammar')
    path = pathlib.PurePosixPath(document)
    if path.is_absolute() or any((part == '..' for part in path.parts)):
        raise ProjectionError('diagnostic locator is outside the closed safety grammar')
    if document not in admitted_documents:
        raise ProjectionError('diagnostic locator is outside the scanned corpus')
    return {'document': document, 'line': line}

def _dedupe_locators(locators: list[dict]) -> list[dict]:
    unique = {(loc['document'], loc['line']) for loc in locators}
    if len(unique) > MAX_DIAGNOSTIC_LOCATORS:
        raise ProjectionError('diagnostic locator count limit exceeded')
    return [{'document': document, 'line': line} for document, line in sorted(unique)]

def _diagnostic_record(*, code: str, family: str, subject_token: str | None, locators: list[dict], facts: dict) -> dict:
    if code not in DIAGNOSTIC_CODES:
        raise ProjectionError('unregistered diagnostic code')
    safe_locators = _dedupe_locators(locators)
    if not safe_locators:
        raise ProjectionError('diagnostic record has no safe locator')
    body = {'code': code, 'family': family, 'subject_token': subject_token, 'locators': safe_locators, 'facts': facts, 'provenance': 'inferred'}
    record_key = hashlib.sha256(_canonical_json_bytes(body)).hexdigest()
    return {'record_key': record_key, **body}

def _edge_candidate_key(locator: dict, target_token: str | None) -> str:
    return hashlib.sha256(_canonical_json_bytes({'locator': locator, 'target_token': target_token})).hexdigest()

def canonical_edge_key(edge: dict) -> str:
    preimage = {'edge_type': edge['edge_type'], 'kind_provenance': edge['kind_provenance'], 'locator': edge['locator'], 'source_object_id': edge['source']['object_id'], 'target_object_id': edge['target']['object_id']}
    return hashlib.sha256(_canonical_json_bytes(preimage)).hexdigest()

def _projection_maps(projected: list[_ProjectedDefinition]) -> tuple[dict, dict, dict]:
    by_id: dict[str, list[_ProjectedDefinition]] = collections.defaultdict(list)
    by_doc: dict[str, list[_ProjectedDefinition]] = collections.defaultdict(list)
    by_doc_line: dict[tuple[str, int], list[_ProjectedDefinition]] = collections.defaultdict(list)
    for definition in projected:
        by_id[definition.payload['obj_id']].append(definition)
        by_doc[definition.payload['doc']].append(definition)
        by_doc_line[definition.payload['doc'], definition.payload['line']].append(definition)
    return (by_id, by_doc, by_doc_line)

def _resolve_endpoint(token: str | None, *, by_id: dict[str, list[_ProjectedDefinition]], registered_prefixes: set[str], local_section_family: str | None=None) -> tuple[str, str | None, list[_ProjectedDefinition]]:
    if token in {None, ''}:
        return ('missing', None, [])
    if not isinstance(token, str) or not _common_global_id_valid(token):
        return ('invalid', None, [])
    if local_section_family is not None and RE_SECTION_HANDLE.fullmatch(token):
        token = f'{local_section_family}:{token}'
    candidate_ids: list[str] = []
    if _syntactic_global_id(token, registered_prefixes):
        candidate_ids.append(token)
    alias = _canonical_reference(token)
    if alias != token and _CANONICAL_INVARIANT.fullmatch(alias or '') and _syntactic_global_id(alias, registered_prefixes):
        candidate_ids.append(alias)
    if not candidate_ids:
        return ('invalid', None, [])
    definitions = [definition for candidate_id in candidate_ids for definition in by_id.get(candidate_id, [])]
    resolved_ids = {definition.payload['obj_id'] for definition in definitions}
    if len(resolved_ids) == 1:
        canonical = next(iter(resolved_ids))
    elif token in candidate_ids:
        canonical = token
    else:
        canonical = alias
    if not definitions:
        return ('missing', canonical, [])
    if len(definitions) > 1:
        return ('ambiguous', canonical, definitions)
    if not _definition_is_edge_eligible(definitions[0], registered_prefixes):
        return ('invalid', canonical, definitions)
    return ('resolved', canonical, definitions)

def _wire_endpoint(definition: _ProjectedDefinition) -> dict:
    return {'family': definition.payload['family'], 'object_id': definition.payload['obj_id'], 'definition': _definition_locator(definition)}

def _validate_retired_dependencies(projected: list[_ProjectedDefinition], *, by_id: dict[str, list[_ProjectedDefinition]], registered_prefixes: set[str]) -> None:
    """Attach only exact, representable retirement members to amendment rows."""
    for definition in projected:
        if definition.payload['kind'] != 'amendment':
            continue
        meta = definition.source.producer_meta
        authored_touches = definition.payload['attrs'].get('touches')
        if isinstance(authored_touches, list):
            normalized_touches = []
            for member in authored_touches:
                status, canonical, _definitions = _resolve_endpoint(member, by_id=by_id, registered_prefixes=registered_prefixes, local_section_family=definition.payload['family'])
                normalized_touches.append(canonical if status != 'invalid' and canonical is not None else member)
            definition.payload['attrs']['touches'] = normalized_touches
        field_counts = meta.get('field_counts', {})
        if field_counts.get('touches', 0) > 1:
            raise ProjectionError(f"duplicate Touches field at {definition.payload['doc']}:{definition.payload['line']}")
        invalid_lines = meta.get('invalid_retired_dependency_lines', [])
        if invalid_lines:
            raise ProjectionError(f"invalid Retires-Dependency field at {definition.payload['doc']}:{invalid_lines[0]}")
        fields = meta.get('retired_dependency_fields', [])
        if not fields:
            continue
        if not _definition_is_edge_eligible(definition, registered_prefixes):
            raise ProjectionError(f"Retires-Dependency belongs to an edge-ineligible amendment at {definition.payload['doc']}:{definition.payload['line']}")
        change_kind = definition.payload['attrs'].get('change_kind')
        if change_kind not in {'semantic', 'scope', 'retirement'}:
            raise ProjectionError(f"Retires-Dependency has an ineligible ChangeKind at {definition.payload['doc']}:{definition.payload['line']}")
        touch_values = set(definition.payload['attrs'].get('touches') or [])
        members = set()
        for field in fields:
            upstream = field['upstream']
            dependent = field['dependent']
            edge_type = field['edge_type']
            if not _syntactic_global_id(upstream, registered_prefixes) or not _syntactic_global_id(dependent, registered_prefixes) or edge_type not in RETIRED_DEPENDENCY_TYPES:
                raise ProjectionError(f"invalid Retires-Dependency field at {definition.payload['doc']}:{field['line']}")
            if edge_type == 'same-as' and upstream >= dependent:
                raise ProjectionError(f"noncanonical same-as retirement at {definition.payload['doc']}:{field['line']}")
            endpoint_resolutions = {}
            for endpoint in (upstream, dependent):
                status, canonical, endpoint_definitions = _resolve_endpoint(endpoint, by_id=by_id, registered_prefixes=registered_prefixes)
                invariant_alias = _canonical_reference(endpoint)
                exact_document_resolution = status == 'resolved' and len(endpoint_definitions) == 1 and (endpoint_definitions[0].payload['obj_id'] == endpoint) and (endpoint_definitions[0].payload['kind'] == 'document')
                if status in {'invalid', 'ambiguous'} or canonical != endpoint or (invariant_alias != endpoint and (not exact_document_resolution)):
                    raise ProjectionError(f"unresolved Retires-Dependency endpoint at {definition.payload['doc']}:{field['line']}")
                endpoint_resolutions[endpoint] = status
            required_touches = {upstream, dependent} if edge_type == 'same-as' else {dependent}
            if not required_touches <= touch_values:
                raise ProjectionError(f"Retires-Dependency lacks Touches authority at {definition.payload['doc']}:{field['line']}")
            if endpoint_resolutions[upstream] != 'resolved':
                raise ProjectionError(f"unresolved Retires-Dependency authority at {definition.payload['doc']}:{field['line']}")
            dependent_status = endpoint_resolutions[dependent]
            parent_resolved_retirement = change_kind == 'retirement' and dependent_status == 'missing'
            if dependent_status != 'resolved' and (not parent_resolved_retirement):
                raise ProjectionError(f"unresolved Retires-Dependency authority at {definition.payload['doc']}:{field['line']}")
            members.add((upstream, dependent, edge_type))
        serialized = [{'upstream_object_id': upstream, 'dependent_object_id': dependent, 'edge_type': edge_type} for upstream, dependent, edge_type in sorted(members)]
        attrs = definition.payload['attrs']
        attrs['retired_dependencies'] = serialized
        provenance = copy.deepcopy(attrs.get('attr_provenance') or {})
        provenance['retired_dependencies'] = 'declared'
        attrs['attr_provenance'] = provenance

def _build_edges_and_c6_diagnostics(data: dict, projected: list[_ProjectedDefinition], *, by_id: dict[str, list[_ProjectedDefinition]], by_doc: dict[str, list[_ProjectedDefinition]], by_doc_line: dict[tuple[str, int], list[_ProjectedDefinition]], registered_prefixes: set[str], admitted_documents) -> tuple[dict[str, list[dict]], list[dict]]:
    edges_by_family: dict[str, dict[str, dict]] = collections.defaultdict(dict)
    diagnostic_records: list[dict] = []
    declared_edges: list[dict] = []

    def definition_locators(definitions: list[_ProjectedDefinition]) -> list[dict]:
        return [_safe_locator(item.payload['doc'], item.payload['line'], admitted_documents=admitted_documents) for item in definitions]

    def add_diagnostic(*, code: str, family: str, subject_token: str | None, locators: list[dict], facts: dict) -> None:
        diagnostic_records.append(_diagnostic_record(code=code, family=family, subject_token=subject_token, locators=locators, facts=facts))

    def add_edge(*, edge_type: str, source_definition: _ProjectedDefinition, target_definition: _ProjectedDefinition, locator: dict, family: str, kind_provenance: str) -> None:
        source = _wire_endpoint(source_definition)
        target = _wire_endpoint(target_definition)
        if source['object_id'] == target['object_id']:
            return
        if edge_type == 'same-as' and source['object_id'] > target['object_id']:
            source, target = (target, source)
        edge = {'edge_type': edge_type, 'source': source, 'target': target, 'locator': locator, 'kind_provenance': kind_provenance}
        key = canonical_edge_key(edge)
        previous = edges_by_family[family].get(key)
        if previous is not None and previous != edge:
            raise ProjectionError('canonical edge-key collision')
        edges_by_family[family][key] = edge
        if kind_provenance == 'declared':
            declared_edges.append(edge)

    def process_direct_candidate(*, source_token: str | None, target_token: str | None, edge_type_tokens: tuple[str, ...], locator: dict, family: str, kind_provenance: str, declared: bool, source_definition: _ProjectedDefinition | None=None, source_reason: str | None=None, source_reason_definitions: list[_ProjectedDefinition] | None=None) -> None:
        target_status, target_canonical, target_definitions = _resolve_endpoint(target_token, by_id=by_id, registered_prefixes=registered_prefixes)
        safe_target = target_canonical if _syntactic_global_id(target_canonical, registered_prefixes) else None
        candidate_key = _edge_candidate_key(locator, safe_target)
        if source_reason is not None:
            source_status = 'ownership'
            source_canonical = None
            source_definitions = source_reason_definitions or []
            facts = {'edge_candidate_key': candidate_key, 'reason': source_reason}
            if source_reason in {'ambiguous_definition_line', 'ambiguous_document'}:
                facts['definition_count'] = len(source_definitions)
            add_diagnostic(code='dependency_source_unresolved', family=family, subject_token=None, locators=[locator, *definition_locators(source_definitions)], facts=facts)
        else:
            effective_source = source_definition.payload['obj_id'] if source_definition is not None else source_token
            source_status, source_canonical, source_definitions = _resolve_endpoint(effective_source, by_id=by_id, registered_prefixes=registered_prefixes)
            if source_status != 'resolved':
                reason = 'global_identity_ambiguous' if source_status == 'ambiguous' else source_status
                facts = {'edge_candidate_key': candidate_key, 'reason': reason}
                if source_status == 'ambiguous':
                    facts['definition_count'] = len(source_definitions)
                add_diagnostic(code='dependency_source_unresolved', family=family, subject_token=source_canonical if _syntactic_global_id(source_canonical, registered_prefixes) else None, locators=[locator, *definition_locators(source_definitions)] if source_status == 'ambiguous' else [locator], facts=facts)
        if target_status != 'resolved':
            reason = 'ambiguous' if target_status == 'ambiguous' else target_status
            facts = {'edge_candidate_key': candidate_key, 'reason': reason}
            if target_status == 'ambiguous':
                facts['definition_count'] = len(target_definitions)
            add_diagnostic(code='dependency_target_unresolved', family=family, subject_token=target_canonical if _syntactic_global_id(target_canonical, registered_prefixes) else None, locators=[locator, *definition_locators(target_definitions)] if target_status == 'ambiguous' else [locator], facts=facts)
        kind_reason = None
        edge_type = None
        if len(edge_type_tokens) == 0:
            kind_reason = 'missing'
        elif len(edge_type_tokens) > 1:
            kind_reason = 'ambiguous'
        else:
            edge_type = edge_type_tokens[0]
            if edge_type not in DECLARED_EDGE_TYPES or edge_type in {'defines', 'verifies'}:
                kind_reason = 'unsupported'
        if kind_provenance == 'inferred' and edge_type in {'defines', 'cites', 'amends', 'motivates'}:
            kind_reason = None
        if kind_reason is not None:
            add_diagnostic(code='dependency_kind_unresolved', family=family, subject_token=source_canonical if _syntactic_global_id(source_canonical, registered_prefixes) else None, locators=[locator], facts={'edge_candidate_key': candidate_key, 'reason': kind_reason})
        if source_status == 'resolved' and target_status == 'resolved' and (kind_reason is None) and (edge_type is not None):
            add_edge(edge_type=edge_type, source_definition=source_definitions[0], target_definition=target_definitions[0], locator=locator, family=family, kind_provenance=kind_provenance)
    for citation in data.get('citations', []):
        target = _canonical_reference(citation.obj_id)
        if not citation.declared and isinstance(target, str) and target.startswith('INV-') and (target.split('-', 2)[1] in EXAMPLE_PREFIXES) and (not by_id.get(citation.obj_id)):
            continue
        locator = _safe_locator(citation.doc, citation.line, admitted_documents=admitted_documents)
        if citation.declared:
            process_direct_candidate(source_token=citation.source_token, target_token=citation.obj_id, edge_type_tokens=citation.edge_type_tokens, locator=locator, family=citation.family, kind_provenance='declared', declared=True)
            continue
        edge_type = 'defines' if citation.is_definition else 'cites'
        source_definition = None
        source_reason = None
        source_reason_definitions = None
        if citation.is_definition:
            documents = [item for item in by_doc.get(citation.doc, []) if item.payload['kind'] == 'document']
            if not documents:
                source_reason = 'missing_document'
            elif len(documents) > 1:
                source_reason = 'ambiguous_document'
                source_reason_definitions = documents
            else:
                source_definition = documents[0]
        else:
            line_definitions = by_doc_line.get((citation.doc, citation.line), [])
            if len(line_definitions) > 1:
                source_reason = 'ambiguous_definition_line'
                source_reason_definitions = line_definitions
            elif len(line_definitions) == 1:
                source_definition = line_definitions[0]
            else:
                documents = [item for item in by_doc.get(citation.doc, []) if item.payload['kind'] == 'document']
                if not documents:
                    source_reason = 'missing_document'
                elif len(documents) > 1:
                    source_reason = 'ambiguous_document'
                    source_reason_definitions = documents
                else:
                    source_definition = documents[0]
        process_direct_candidate(source_token=None, target_token=citation.obj_id, edge_type_tokens=(edge_type,), locator=locator, family=citation.family, kind_provenance='inferred', declared=False, source_definition=source_definition, source_reason=source_reason, source_reason_definitions=source_reason_definitions)
    rationale_by_amendment: dict[tuple[str, str | None], list[_ProjectedDefinition]] = collections.defaultdict(list)
    for definition in projected:
        if definition.payload['kind'] == 'rationale':
            rationale_by_amendment[definition.payload['doc'], definition.source.producer_meta.get('amendment_revision')].append(definition)
    resolved_retirement_touches: list[tuple[_ProjectedDefinition, str, dict]] = []
    for amendment in projected:
        if amendment.payload['kind'] != 'amendment':
            continue
        amendment_is_eligible = _definition_is_edge_eligible(amendment, registered_prefixes)
        amendment_is_unique = amendment_is_eligible and len(by_id[amendment.payload['obj_id']]) == 1
        meta = amendment.source.producer_meta
        change_kind = amendment.payload['attrs'].get('change_kind')
        definition_locator = _safe_locator(amendment.payload['doc'], amendment.payload['line'], admitted_documents=admitted_documents)
        field_lines = meta.get('field_lines', {})
        if amendment_is_unique and (not change_kind):
            add_diagnostic(code='change_kind_unresolved', family=amendment.payload['family'], subject_token=amendment.payload['obj_id'], locators=[definition_locator], facts={'reason': 'missing'})
        elif amendment_is_unique and change_kind not in CHANGE_KIND:
            add_diagnostic(code='change_kind_unresolved', family=amendment.payload['family'], subject_token=amendment.payload['obj_id'], locators=[_safe_locator(amendment.payload['doc'], field_lines.get('change_kind', amendment.payload['line']), admitted_documents=admitted_documents)], facts={'reason': 'unsupported'})
        members = meta.get('touches_members', [])
        nonempty = [member for member in members if member is not None]
        if amendment_is_unique and change_kind in TOUCHES_REQUIRED_CHANGE_KINDS and (not nonempty):
            add_diagnostic(code='touches_unresolved', family=amendment.payload['family'], subject_token=amendment.payload['obj_id'], locators=[definition_locator], facts={'reason': 'missing', 'touch_ordinal': 0, 'target_token': None})
        touches_line = meta.get('touches_line', amendment.payload['line'])
        touches_locator = _safe_locator(amendment.payload['doc'], touches_line, admitted_documents=admitted_documents)
        valid_targets: dict[str, _ProjectedDefinition] = {}
        if nonempty:
            for ordinal, member in enumerate(members, start=1):
                if member is None:
                    if not amendment_is_unique:
                        continue
                    add_diagnostic(code='touches_unresolved', family=amendment.payload['family'], subject_token=amendment.payload['obj_id'], locators=[touches_locator], facts={'reason': 'unknown', 'touch_ordinal': ordinal, 'target_token': None})
                    continue
                status, canonical, definitions = _resolve_endpoint(member, by_id=by_id, registered_prefixes=registered_prefixes, local_section_family=amendment.payload['family'])
                if status == 'resolved':
                    valid_targets[canonical] = definitions[0]
                    if change_kind == 'retirement' and amendment_is_unique:
                        resolved_retirement_touches.append((amendment, canonical, touches_locator))
                    continue
                if status == 'missing' and change_kind == 'retirement' and (canonical is not None):
                    continue
                reason = 'ambiguous' if status == 'ambiguous' else 'unknown'
                facts = {'reason': reason, 'touch_ordinal': ordinal, 'target_token': canonical if _syntactic_global_id(canonical, registered_prefixes) else None}
                locators = [touches_locator]
                if status == 'ambiguous':
                    facts['definition_count'] = len(definitions)
                    locators.extend(definition_locators(definitions))
                if amendment_is_unique:
                    add_diagnostic(code='touches_unresolved', family=amendment.payload['family'], subject_token=amendment.payload['obj_id'], locators=locators, facts=facts)
        for canonical, target_definition in sorted(valid_targets.items()):
            process_direct_candidate(source_token=amendment.payload['obj_id'], target_token=canonical, edge_type_tokens=('amends',), locator=touches_locator, family=amendment.payload['family'], kind_provenance='inferred', declared=False, source_definition=amendment)
            rationale_key = (amendment.payload['doc'], amendment.source.attrs.get('rev'))
            for rationale in rationale_by_amendment.get(rationale_key, []):
                process_direct_candidate(source_token=rationale.payload['obj_id'], target_token=canonical, edge_type_tokens=('motivates',), locator=touches_locator, family=rationale.payload['family'], kind_provenance='inferred', declared=False, source_definition=rationale)
    for amendment, retired_id, touches_locator in resolved_retirement_touches:
        candidates = [edge for edge in declared_edges if edge['edge_type'] == 'supersedes' and edge['target']['object_id'] == retired_id]
        successors = {edge['source']['object_id'] for edge in candidates}
        if len(successors) == 1:
            continue
        reason = 'missing' if not successors else 'ambiguous'
        facts = {'retired_object_id': retired_id, 'reason': reason, 'successor_count': len(successors)}
        add_diagnostic(code='retirement_supersedes_missing', family=amendment.payload['family'], subject_token=amendment.payload['obj_id'], locators=[touches_locator, *[edge['locator'] for edge in candidates]], facts=facts)
    return ({family: sorted(keyed.values(), key=lambda edge: (edge['source']['object_id'], edge['target']['object_id'], edge['edge_type'], edge['locator']['document'], edge['locator']['line'], edge['kind_provenance'])) for family, keyed in edges_by_family.items()}, diagnostic_records)

def _build_base_diagnostics(data: dict, projected: list[_ProjectedDefinition], *, admitted_documents) -> list[dict]:
    records: list[dict] = []

    def add(code: str, family: str, subject: str | None, locators: list[dict], facts: dict) -> None:
        records.append(_diagnostic_record(code=code, family=family, subject_token=subject, locators=locators, facts=facts))
    for doc in data.get('docs', []):
        document_id = doc.header.get('document id', '').strip()
        if not document_id:
            add('document_id_missing', doc.family, None, [_safe_locator(doc.path, 1, admitted_documents=admitted_documents)], {})
        for diagnostic in doc.diagnostics:
            code = diagnostic.get('kind')
            if code == 'invalid_document_lifecycle':
                subject = document_id if _document_id_valid(document_id) else None
                add(code, doc.family, subject, [_safe_locator(doc.path, diagnostic.get('line') or doc.header_lines.get('status') or 1, admitted_documents=admitted_documents)], {})
            elif code == 'malformed_open_question_handle':
                facts = {}
                observed = diagnostic.get('handle')
                if isinstance(observed, str) and re.fullmatch('(?:PCDN|EOQ)-[A-Z0-9][A-Z0-9-]{0,95}', observed, re.ASCII):
                    facts['observed_token'] = observed
                add(code, doc.family, None, [_safe_locator(doc.path, diagnostic['line'], admitted_documents=admitted_documents)], facts)
            elif code in {'errata_missing_index_row', 'errata_index_without_body', 'errata_duplicate_index_row', 'errata_duplicate_body', 'errata_unsupported_status', 'errata_status_disagreement'}:
                subject = f"{doc.family}:{diagnostic['errata_id']}"
                lines = diagnostic.get('lines') or [diagnostic.get('line')]
                locators = [_safe_locator(doc.path, line, admitted_documents=admitted_documents) for line in lines if line]
                facts = {}
                if code in {'errata_duplicate_index_row', 'errata_duplicate_body'}:
                    facts['occurrence_count'] = len(lines)
                elif code == 'errata_unsupported_status':
                    facts['source'] = diagnostic['source']
                elif code == 'errata_status_disagreement':
                    facts = {'index_status': diagnostic['index_status'], 'body_status': diagnostic['body_status']}
                add(code, doc.family, subject, locators, facts)
    questions: dict[str, list[_ProjectedDefinition]] = collections.defaultdict(list)
    for definition in projected:
        if definition.payload['kind'] == 'open_question':
            questions[definition.payload['obj_id']].append(definition)
    for object_id, definitions in sorted(questions.items()):
        if len(definitions) < 2:
            continue
        add('open_question_definition_duplicate', definitions[0].payload['family'], object_id, [_safe_locator(item.payload['doc'], item.payload['line'], admitted_documents=admitted_documents) for item in definitions], {'definition_count': len(definitions)})
    return records

def _record_sort_key(record: dict) -> tuple:
    return (record['code'], record['subject_token'] is None, record['subject_token'] or '', tuple(((loc['document'], loc['line']) for loc in record['locators'])), record['record_key'])

def _diagnostic_coverage(data: dict, projected: list[_ProjectedDefinition], records: list[dict]) -> dict:
    docs: list[Document] = data.get('docs', [])
    questions = [item for item in projected if item.payload['kind'] == 'open_question']
    question_ids = collections.Counter((item.payload['obj_id'] for item in questions))
    status_counts = {name: 0 for name in ('open', 'pending_ratification', 'resolved', 'unknown')}
    for item in questions:
        status = item.payload.get('attrs', {}).get('status')
        status_counts[status if status in status_counts else 'unknown'] += 1
    code_counts = collections.Counter((record['code'] for record in records))
    return {'f18': {'eligible_documents': len(docs), 'identified_documents': sum((bool(doc.header.get('document id', '').strip()) for doc in docs)), 'missing_document_ids': sum((not bool(doc.header.get('document id', '').strip()) for doc in docs)), 'invalid_document_lifecycle': code_counts['invalid_document_lifecycle']}, 'f19': {'emitted_definitions': len(questions), 'unique_definition_ids': len(question_ids), 'duplicate_definition_ids': sum((count > 1 for count in question_ids.values())), 'malformed_handles': code_counts['malformed_open_question_handle'], 'status_counts': status_counts}, 'f20': {'diagnostic_records': sum((code_counts[code] for code in DIAGNOSTIC_CODES[4:10]))}}

def _build_projection_bundle(data: dict, *, admitted_documents) -> tuple[dict, dict, ProjectionExpectations]:
    _validate_fingerprint_descriptor()
    for doc in data.get('docs', []):
        if doc.producer_errors:
            first = min(doc.producer_errors, key=lambda error: (error.get('line', 1), 0 if error.get('kind') == 'invalid_project_event_record' else 1))
            labels = {'invalid_spec_edge_field': 'Spec Edge field', 'invalid_project_event_record': 'project-event record', 'invalid_retired_dependency_context': 'Retires-Dependency field'}
            label = labels.get(first.get('kind'), 'producer input')
            raise ProjectionError(f"invalid {label} at {doc.path}:{first.get('line', 1)}")
    registered_prefixes = set(data.get('registered_prefixes', []))
    projected = _projected_definitions(data)
    by_id, by_doc, by_doc_line = _projection_maps(projected)
    _validate_retired_dependencies(projected, by_id=by_id, registered_prefixes=registered_prefixes)
    edges_by_family, c6_records = _build_edges_and_c6_diagnostics(data, projected, by_id=by_id, by_doc=by_doc, by_doc_line=by_doc_line, registered_prefixes=registered_prefixes, admitted_documents=admitted_documents)
    diagnostic_records = [*_build_base_diagnostics(data, projected, admitted_documents=admitted_documents), *c6_records]
    if len(diagnostic_records) > MAX_DIAGNOSTIC_RECORDS:
        raise ProjectionError('diagnostic record count limit exceeded')
    per_family: dict[str, list[dict]] = collections.defaultdict(list)
    for definition in projected:
        per_family[definition.payload['family']].append(definition.payload)
    object_families = sorted(set(per_family) | set(edges_by_family))
    object_index: dict[str, dict] = {}
    for family in object_families:
        objects = sorted(per_family.get(family, []), key=lambda obj: (obj['doc'], obj['line'], obj['kind'], obj['obj_id']))
        edges = edges_by_family.get(family, [])
        object_index[family] = {'schema_version': INDEX_SCHEMA_VERSION, 'family': family, 'object_count': len(objects), 'edge_count': len(edges), 'kind_counts': dict(sorted(collections.Counter((obj['kind'] for obj in objects)).items())), 'objects': objects, 'edges': edges}
    object_index['_manifest'] = {'schema_version': INDEX_SCHEMA_VERSION, 'families': object_families, 'family_counts': {family: len(per_family.get(family, [])) for family in object_families}, 'total_objects': sum((len(values) for values in per_family.values())), 'total_edges': sum((len(values) for values in edges_by_family.values())), 'semantic_fingerprint_version': SEMANTIC_FINGERPRINT_VERSION, 'semantic_fingerprint_extractor_sha256': SEMANTIC_FINGERPRINT_EXTRACTOR_SHA256}
    scanned_families = {doc.family for doc in data.get('docs', [])} | set(per_family) | set(edges_by_family) | {record['family'] for record in diagnostic_records}
    records_by_family: dict[str, dict[str, dict]] = collections.defaultdict(dict)
    for record in diagnostic_records:
        previous = records_by_family[record['family']].get(record['record_key'])
        if previous is not None and previous != record:
            raise ProjectionError('diagnostic record-key collision')
        records_by_family[record['family']][record['record_key']] = record
    diagnostic_index: dict[str, dict] = {}
    descriptors = []
    final_records: list[dict] = []
    total_family_bytes = 0
    for family in sorted(scanned_families):
        records = sorted(records_by_family.get(family, {}).values(), key=_record_sort_key)
        final_records.extend(records)
        wrapper = {'schema_version': DIAGNOSTIC_SCHEMA_VERSION, 'family': family, 'record_count': len(records), 'records': records}
        family_bytes = _diagnostic_render(wrapper).encode('utf-8')
        if len(family_bytes) > MAX_DIAGNOSTIC_FAMILY_BYTES:
            raise ProjectionError('diagnostic family-file size limit exceeded')
        total_family_bytes += len(family_bytes)
        diagnostic_index[family] = wrapper
        descriptors.append({'family': family, 'filename': f'{family}.json', 'record_count': len(records), 'sha256': hashlib.sha256(family_bytes).hexdigest()})
    code_counts = collections.Counter((record['code'] for record in final_records))
    manifest = {'schema_version': DIAGNOSTIC_SCHEMA_VERSION, 'families': descriptors, 'total_records': len(final_records), 'code_counts': {code: code_counts[code] for code in DIAGNOSTIC_CODES}, 'coverage': _diagnostic_coverage(data, projected, final_records)}
    manifest_bytes = _diagnostic_render(manifest).encode('utf-8')
    if len(manifest_bytes) > MAX_DIAGNOSTIC_MANIFEST_BYTES:
        raise ProjectionError('diagnostic manifest size limit exceeded')
    if total_family_bytes + len(manifest_bytes) > MAX_DIAGNOSTIC_TOTAL_BYTES:
        raise ProjectionError('diagnostic projection size limit exceeded')
    diagnostic_index['_manifest'] = manifest
    expectations = ProjectionExpectations(registered_prefixes=frozenset(registered_prefixes), object_sha256=hashlib.sha256(_canonical_json_bytes(object_index)).hexdigest(), location_sha256=None, diagnostic_sha256=hashlib.sha256(_canonical_json_bytes(diagnostic_index)).hexdigest(), location_descriptors=None, diagnostic_descriptors=tuple(((descriptor['family'], descriptor['filename'], descriptor['record_count'], descriptor['sha256']) for descriptor in descriptors)), diagnostic_record_keys=tuple((record['record_key'] for family in sorted((name for name in diagnostic_index if name != '_manifest')) for record in diagnostic_index[family]['records'])))
    return (object_index, diagnostic_index, expectations)

def build_projection_bundle_with_expectations(data: dict, *, admitted_documents) -> tuple[dict, dict, ProjectionExpectations]:
    """Build one triple's wire views and private pre-publication expectations."""
    return _build_projection_bundle(data, admitted_documents=admitted_documents)

def _render(payload: dict) -> str:
    return json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + '\n'
