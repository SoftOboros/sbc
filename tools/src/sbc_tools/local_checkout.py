"""Offline, local checkout evidence for observations, never committed admission."""
from dataclasses import dataclass
import hashlib
import os
from pathlib import Path
import stat

from .canonical import canonical_json
from .configuration import _path
from .working_tree import _read_regular


@dataclass(frozen=True)
class LocalCheckoutObservation:
    observed_head: str
    checkout_state: str
    evidence_sha256: str | None
    reason: str


def _ordinary_directory(path):
    metadata = path.lstat()
    if (not stat.S_ISDIR(metadata.st_mode) or stat.S_ISLNK(metadata.st_mode)
            or getattr(metadata, 'st_file_attributes', 0) & 0x400):
        raise ValueError('Checkout path must contain only ordinary directories')


def verify_checkout_location(reader, expected_path):
    """Check literal registered paths before resolution or child object reads.

    The host supplies the expected mount; matching objects do not establish
    ownership. This check is bounded and cannot lock paths against replacement.
    """
    expected = Path(expected_path)
    if not expected.is_absolute() or '..' in expected.parts:
        raise ValueError('Absolute registered checkout location required')
    actual = Path(os.fsdecode(reader._repo.path)).absolute()
    for path in (expected, actual):
        current = Path(path.anchor)
        for part in path.parts[1:]:
            current = current / part
            _ordinary_directory(current)
    if actual.resolve() != expected.resolve() or reader._repo.bare:
        raise ValueError('Reader does not own the registered checkout location')
    return expected


def observe_local_checkout(reader, head, *, expected_path, child_readers=None):
    """Inspect all local files and index, pruning explicitly registered children.

    Child HEAD changes relative to this checkout's HEAD gitlink make this
    checkout dirty; child interior dirtiness is not inherited. Missing/unsafe
    evidence returns unknown, even when another file is demonstrably dirty.
    Two equal passes provide bounded change detection, not atomic isolation.
    The evidence digest is internal stability evidence, not a corpus identity.
    """
    from dulwich.config import ConfigDict
    children = {} if child_readers is None else dict(child_readers)

    def inspect():
        root = verify_checkout_location(reader, expected_path)
        if reader.resolve_commit('HEAD') != head:
            raise ValueError('Observed HEAD changed')
        entries = {e.path: e for e in reader.entries(head)}
        gitlinks = {p: e for p, e in entries.items() if e.mode == 0o160000}
        if set(children) != set(gitlinks):
            raise ValueError('Explicit child boundary evidence incomplete')
        if any(e.mode not in (0o100644, 0o100755, 0o160000) for e in entries.values()):
            raise ValueError('Unsupported committed member')
        if os.name == 'nt' and any(e.mode == 0o100755 for e in entries.values()):
            raise ValueError('Executable mode unverifiable')
        child_heads = {}
        for path, child in sorted(children.items()):
            _path(path)
            verify_checkout_location(child, root / path)
            child_heads[path] = child.resolve_commit('HEAD')
        index_path = Path(os.fsdecode(reader._repo.index_path()))
        index_bytes = index_path.read_bytes()
        indexed = {p.decode('utf-8'): e for p, e in reader._repo.open_index(config=ConfigDict()).items()}
        dirty = set(indexed) != set(entries)
        for path, item in indexed.items():
            entry = entries.get(path)
            if (entry is None or getattr(item, 'sha', None) != entry.oid.encode()
                    or getattr(item, 'mode', None) != entry.mode):
                dirty = True
        files, boundaries = {}, set()

        def visit(directory):
            nonlocal dirty
            members = sorted(directory.iterdir(), key=lambda p: p.name)
            if directory != root and any(p.name.lower() == '.git' for p in members):
                raise ValueError('Unregistered nested repository')
            for path in members:
                if directory == root and path.name == '.git':
                    continue
                relative = path.relative_to(root).as_posix()
                _path(relative)
                metadata = path.lstat()
                if stat.S_ISLNK(metadata.st_mode) or getattr(metadata, 'st_file_attributes', 0) & 0x400:
                    raise ValueError('Linked checkout member')
                if relative in gitlinks:
                    _ordinary_directory(path)
                    boundaries.add(relative)
                    continue
                if stat.S_ISDIR(metadata.st_mode):
                    visit(path)
                elif stat.S_ISREG(metadata.st_mode):
                    raw = _read_regular(path, metadata)
                    executable = bool(metadata.st_mode & 0o111) if os.name != 'nt' else False
                    files[relative] = (hashlib.sha256(raw).hexdigest(), executable)
                    entry = entries.get(relative)
                    if (entry is None or entry.mode not in (0o100644, 0o100755)
                            or executable != (entry.mode == 0o100755)
                            or raw != reader._object(entry.oid, b'blob').data):
                        dirty = True
                else:
                    raise ValueError('Unsupported checkout member')
        visit(root)
        if boundaries != set(gitlinks):
            raise ValueError('Missing registered child boundary')
        if set(files) | boundaries != set(entries):
            dirty = True
        if any(child_heads[p] != e.oid for p, e in gitlinks.items()):
            dirty = True
        if reader.resolve_commit('HEAD') != head or index_path.read_bytes() != index_bytes:
            raise ValueError('Checkout selection changed')
        for path, child in children.items():
            verify_checkout_location(child, root / path)
            if child.resolve_commit('HEAD') != child_heads[path]:
                raise ValueError('Child HEAD changed')
        verify_checkout_location(reader, expected_path)
        evidence = canonical_json(dict(head=head, index_sha256=hashlib.sha256(index_bytes).hexdigest(),
                                       files=files, children=child_heads, dirty=dirty))
        return dirty, evidence

    try:
        first, second = inspect(), inspect()
        if first != second:
            return LocalCheckoutObservation(head, 'unknown', None, 'checkout_changed_during_observation')
        dirty, evidence = first
        return LocalCheckoutObservation(head, 'dirty' if dirty else 'clean',
                                        hashlib.sha256(evidence).hexdigest(), 'local_byte_observation')
    except (OSError, ValueError, KeyError, AttributeError, UnicodeError):
        return LocalCheckoutObservation(head, 'unknown', None, 'checkout_evidence_unavailable')
