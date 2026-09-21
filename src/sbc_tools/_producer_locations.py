"""Pinned pure parser extraction. Reproduce with tools/extract_document_parser.py.
Source blob: 31217a012c99785cd0bda3cae3a3d9feb3cf33d5.
"""
from __future__ import annotations
import dataclasses
import re
import urllib.parse
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
