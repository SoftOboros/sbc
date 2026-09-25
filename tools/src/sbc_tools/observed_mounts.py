"""Offline relationship context only; not capture, checkout state, or publication."""
from dataclasses import dataclass

from .configuration import _path
from .git_reader import GitReadError, GitUnavailableError
from .observation_sets import _name


@dataclass(frozen=True)
class ParticipantContext:
    repository_id: str
    availability: str
    observed_head: str | None


@dataclass(frozen=True)
class RelationContext:
    parent_repository_id: str
    path: str
    repository_id: str
    parent_commit: str | None
    recorded_child_commit: str | None
    pin_state: str


@dataclass(frozen=True)
class MountContext:
    root_commit: str | None
    participants: tuple
    relations: tuple


def collect_mount_context(*, root_repository_id, root_ref, mounts, source_roots,
                          readers, exclude=(), checkout_root=None):
    """Read explicitly registered readers; absent readers mean missing checkouts.

    The host must establish registration first. If checkout_root is supplied,
    verify each reader's physical location before reading its objects; otherwise
    the host must establish physical ownership separately. This function neither
    opens repositories nor certifies
    captured bytes, dirty state, or stability across an aggregate capture.
    Root context resolves once; nested context follows observed parent HEAD.
    """
    _name(root_repository_id)
    if isinstance(source_roots, (str, bytes)) or isinstance(exclude, (str, bytes)):
        raise ValueError('Explicit path sequences required')
    roots, excluded, mounts = tuple(source_roots), tuple(exclude), tuple(mounts)
    if not roots:
        raise ValueError('Explicit source roots required')
    for path in roots + excluded:
        _path(path)
    if len(set(excluded)) != len(excluded) or any(
            s == e or s.startswith(e + '/') for s in roots for e in excluded):
        raise ValueError('Invalid or source-hiding exclusions')

    def included(path):
        return (not any(path == e or path.startswith(e + '/') for e in excluded)
                and any(path == s or path.startswith(s + '/') or s.startswith(path + '/')
                        for s in roots))

    paths, ids = set(), {root_repository_id}
    for path, owner in mounts:
        _path(path)
        _name(owner)
        if path in paths or owner in ids:
            raise ValueError('Duplicate or cyclic mount mapping')
        paths.add(path)
        ids.add(owner)
    selected = sorted(((p, r) for p, r in mounts if included(p)),
                      key=lambda item: (item[0].count('/'), item[0]))
    ownership = {'': root_repository_id}
    children = {root_repository_id: []}
    for path, owner in selected:
        ancestor = max((p for p in ownership if not p or path.startswith(p + '/')), key=len)
        parent = ownership[ancestor]
        relative = path[len(ancestor) + 1:] if ancestor else path
        children.setdefault(parent, []).append((relative, owner, path))
        children[owner] = []
        ownership[path] = owner
    participants, relations = [], []
    root_commit = None

    def visit(owner, prefix, pin=None, blocked=False):
        nonlocal root_commit
        head, context, entries = None, None, {}
        availability = 'blocked_by_ancestor' if blocked else 'missing_checkout'
        if not blocked and owner in readers:
            reader = readers[owner]
            try:
                if checkout_root is not None:
                    from pathlib import Path
                    from .local_checkout import verify_checkout_location
                    verify_checkout_location(reader, Path(checkout_root) / prefix)
                head = reader.resolve_commit('HEAD')
                if pin is not None and reader.resolve_commit(pin) != pin:
                    raise GitReadError('Child gitlink must name a commit directly')
                context = reader.resolve_commit(root_ref) if owner == root_repository_id else head
                entries = {e.path: e for e in reader.entries(context)}
                availability = 'available'
                if owner == root_repository_id:
                    root_commit = context
            except GitUnavailableError:
                availability, head, context = 'unavailable_history', None, None
            except FileNotFoundError:
                availability, head, context = 'missing_checkout', None, None
        participant = ParticipantContext(owner, availability, head)
        participants.append(participant)
        available = availability == 'available'
        if available:
            registered = {p for p, _, _ in children[owner]}
            for path, entry in entries.items():
                if entry.mode == 0o160000 and included(prefix + path) and path not in registered:
                    raise ValueError('Included gitlink requires explicit ancestor/mount registration')
        for path, child, full_path in children[owner]:
            recorded = None
            if available:
                entry = entries.get(path)
                if entry is None or entry.mode != 0o160000:
                    raise ValueError('Configured mount is not a selected parent gitlink')
                recorded = entry.oid
            child_row = visit(child, full_path + '/', recorded, not available)
            state = 'unavailable'
            if available and child_row.availability == 'available':
                state = 'match' if recorded == child_row.observed_head else 'mismatch'
            relations.append(RelationContext(owner, path, child, context, recorded, state))
        return participant

    visit(root_repository_id, '')
    return MountContext(root_commit, tuple(sorted(participants, key=lambda r: r.repository_id)),
                        tuple(sorted(relations, key=lambda r: (r.parent_repository_id, r.path))))
