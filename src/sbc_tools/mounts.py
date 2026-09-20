"""Pin explicitly included child repositories through immediate-parent trees.

Pins prove committed relationships only. Checkout/dirty-state acceptance is a
separate mandatory check before claiming a clean committed scan.
"""
from dataclasses import dataclass
from types import MappingProxyType

from .identity import copy_files
from .git_reader import GitReadError, GitUnavailableError


@dataclass(frozen=True)
class PinnedMount:
    mount_path: str
    repository_id: str
    parent_repository_id: str
    parent_commit: str
    parent_relative_path: str
    child_commit: str


def pin_child_mounts(*, root_repository_id, root_commit, mounts, source_roots, readers, exclude=()):
    """Use host readers and explicit mount mappings; never discover or fetch children.

    A source root below a child selects its registered ancestors too. Nested
    mounts resolve in their immediate registered parent's exact pinned tree.
    Missing ancestor registration cannot be substituted with a root-tree lookup.
    """
    mounts = tuple(mounts)
    roots = tuple(source_roots) if not isinstance(source_roots, (str, bytes)) else ()
    if not roots:
        raise ValueError("Explicit source roots required")
    if isinstance(exclude, (str, bytes)):
        raise ValueError("Exclusions must be a sequence of literal paths")
    excluded = tuple(exclude)
    for path in excluded:
        copy_files({path:b""})
    if len(set(excluded)) != len(excluded) or any(
            s == e or s.startswith(e + "/") for s in roots for e in excluded):
        raise ValueError("Invalid or source-hiding exclusions")
    def included(path):
        return (not any(path == e or path.startswith(e + "/") for e in excluded)
                and any(path == s or path.startswith(s + "/") or s.startswith(path + "/") for s in roots))
    seen_paths, seen_ids = set(), {root_repository_id}
    for path in roots:
        copy_files({path:b""})
    for path, repository_id in mounts:
        copy_files({path:b""})
        if (not isinstance(repository_id, str) or not repository_id
                or path in seen_paths or repository_id in seen_ids):
            raise ValueError("Duplicate or cyclic mount mapping")
        seen_paths.add(path)
        seen_ids.add(repository_id)
    selected = [(p,r) for p,r in mounts if included(p)]
    if root_repository_id not in readers:
        raise GitUnavailableError("Root repository unavailable")
    if readers[root_repository_id].resolve_commit(root_commit) != root_commit:
        raise GitReadError("An exact root commit is required")
    pinned = {}
    for path, repository_id in sorted(selected, key=lambda item:(item[0].count("/"),item[0])):
        ancestors = [p for p in pinned if path.startswith(p + "/")]
        parent_mount = max(ancestors, key=len) if ancestors else None
        if parent_mount is None:
            parent_id, parent_commit, relative = root_repository_id, root_commit, path
        else:
            parent = pinned[parent_mount]
            parent_id, parent_commit = parent.repository_id, parent.child_commit
            relative = path[len(parent_mount)+1:]
        entries = {e.path:e for e in readers[parent_id].entries(parent_commit)}
        if any(relative.startswith(p + "/") and e.mode == 0o160000 for p,e in entries.items()):
            raise ValueError("Nested mount requires explicit ancestor registration")
        entry = entries.get(relative)
        if entry is None or entry.mode != 0o160000:
            raise GitReadError("Configured mount is not a committed parent gitlink")
        if repository_id not in readers:
            raise GitUnavailableError("Required child repository unavailable")
        child_commit = readers[repository_id].resolve_commit(entry.oid)
        if child_commit != entry.oid:
            raise GitReadError("Child gitlink must name a commit directly")
        pinned[path] = PinnedMount(path, repository_id, parent_id, parent_commit, relative, child_commit)
    # An included but unregistered gitlink must not silently disappear from scope.
    parents = [("", root_repository_id, root_commit)] + [
        (p + "/", item.repository_id, item.child_commit) for p,item in pinned.items()]
    for prefix, repository_id, commit in parents:
        for entry in readers[repository_id].entries(commit):
            path = prefix + entry.path
            if entry.mode == 0o160000 and included(path):
                if path not in pinned:
                    raise ValueError("Included gitlink requires explicit mount registration")
    return tuple(pinned[p] for p in sorted(pinned))


@dataclass(frozen=True)
class CheckoutTreeObservation:
    pins: tuple
    observations: object
    clean: bool


def observe_checkout_tree(*, root_repository_id, root_commit, mounts, source_roots, readers, exclude=()):
    """Revalidate committed pins and observe leaves before their parents.

    Readers are host-registered and must match the physical parent mount paths.
    Excluded/unselected gitlinks receive no clean proof; a whole-repository
    observation containing them therefore remains not clean. No scoped-clean
    exemption or request-selected child evidence is inferred.
    """
    pins = pin_child_mounts(root_repository_id=root_repository_id, root_commit=root_commit,
        mounts=mounts, source_roots=source_roots, readers=readers, exclude=exclude)
    observations = {}
    ordered = sorted(pins, key=lambda p:(p.mount_path.count("/"),p.mount_path), reverse=True)
    selections = [(p.repository_id,p.child_commit) for p in ordered] + [(root_repository_id,root_commit)]
    for repository_id, commit in selections:
        children = {p.parent_relative_path:(readers[p.repository_id],observations[p.repository_id])
                    for p in pins if p.parent_repository_id == repository_id}
        observations[repository_id] = readers[repository_id].observe_checkout(commit, child_checks=children)
    return CheckoutTreeObservation(pins, MappingProxyType(observations),
                                   all(o.clean for o in observations.values()))
