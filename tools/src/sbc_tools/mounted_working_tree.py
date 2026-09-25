"""Bounded aggregate capture of explicitly mounted working-tree source bytes."""
from dataclasses import asdict, dataclass
import hashlib
from pathlib import Path
import stat
from types import MappingProxyType

from .configuration import _path, _reject_linked_components
from .corpus import CorpusInput, _paths, _within, corpus_digest
from .local_checkout import observe_local_checkout
from .observed_mounts import collect_mount_context
from .observation_sets import build_observation_set
from .working_tree import _read_regular


class AggregateObservationUnavailable(ValueError):
    """No usable aggregate; retained relationship context is not a partial corpus."""
    def __init__(self, reason, context):
        super().__init__(reason)
        self.context = context


@dataclass(frozen=True)
class MountedWorkingCorpus:
    records: tuple
    files: object
    observation: bytes


def capture_mounted_working_tree(*, repository_id, repository_root, root_ref,
                                 readers, mounts, source_roots, required_files, exclude=()):
    """Capture all required participants or return no corpus at all.

    Host registration, approved authority inputs, output separation and required
    input completeness are caller obligations. Readers are already registered;
    this function never opens, discovers or fetches a repository. Its immutable
    bytes are observations only, never committed provenance or publication.
    Unavailable failures retain relationship context for subsequent CLI framing.
    """
    roots, required, excluded = map(_paths, (source_roots, required_files, exclude))
    if not roots or any(_within(a, b) for a in roots for b in roots if a != b):
        raise ValueError('Explicit nonoverlapping source roots required')
    if any(_within(p, e) for p in (*roots, *required) for e in excluded):
        raise ValueError('Exclusions cannot hide required inputs')
    root = Path(repository_root)
    mounts = tuple(mounts)
    scopes = tuple(sorted(set((*roots, *required))))
    arguments = dict(root_repository_id=repository_id, mounts=mounts, source_roots=scopes,
                     readers=readers, exclude=excluded, checkout_root=root)
    context = collect_mount_context(root_ref=root_ref, **arguments)
    if any(p.availability != 'available' for p in context.participants):
        raise AggregateObservationUnavailable('Required participant unavailable', context)
    participants = {p.repository_id: p for p in context.participants}
    prefixes = {repository_id: ''}
    prefixes.update({owner: path for path, owner in mounts if owner in participants})
    boundaries = {path: owner for owner, path in prefixes.items() if path}
    children = {owner: {} for owner in participants}
    for relation in context.relations:
        children[relation.parent_repository_id][relation.path] = readers[relation.repository_id]

    def checkout_evidence():
        result = {}
        for owner in sorted(participants):
            row = observe_local_checkout(readers[owner], participants[owner].observed_head,
                expected_path=root / prefixes[owner], child_readers=children[owner])
            if row.checkout_state == 'unknown':
                raise AggregateObservationUnavailable('Local checkout evidence unavailable', context)
            result[owner] = row
        return result

    def omitted(path):
        return any(_within(path, e) for e in excluded)

    def guard(relative):
        _path(relative)
        _reject_linked_components(root, relative)
        # A configured root below an unregistered checkout must not skip its
        # ancestor boundary merely because traversal starts below that boundary.
        parts = relative.split('/')
        for count in range(1, len(parts) + 1):
            prefix = '/'.join(parts[:count])
            path = root / prefix
            if path.is_dir() and prefix not in boundaries:
                if any(p.name.lower() == '.git' for p in path.iterdir()):
                    raise ValueError('Unregistered nested repository')

    def capture():
        files = {}
        def visit(relative, directory_required):
            if omitted(relative):
                return
            guard(relative)
            path = root / relative
            metadata = path.lstat()
            if stat.S_ISDIR(metadata.st_mode) and directory_required:
                for child in sorted(path.iterdir(), key=lambda p: p.name):
                    if relative in boundaries and child.name == '.git':
                        continue
                    name = child.relative_to(root).as_posix()
                    if omitted(name):
                        continue
                    _reject_linked_components(root, name)
                    visit(name, stat.S_ISDIR(child.lstat().st_mode))
            elif stat.S_ISREG(metadata.st_mode) and not directory_required:
                files[relative] = _read_regular(path, metadata)
            else:
                raise ValueError('Required corpus input has unsupported type')
        for path in roots:
            visit(path, True)
        for path in required:
            visit(path, False)
        return files

    before = checkout_evidence()
    first, second = capture(), capture()
    after = checkout_evidence()
    current = collect_mount_context(root_ref=context.root_commit, **arguments)
    if (first != second or before != after or current != context
            or readers[repository_id].resolve_commit(root_ref) != context.root_commit):
        raise AggregateObservationUnavailable('Aggregate changed during capture', context)
    records = []
    for path, data in sorted(first.items()):
        prefix = max((p for p in boundaries if _within(path, p)), key=len, default='')
        owner = boundaries[prefix] if prefix else repository_id
        relative = path[len(prefix) + 1:] if prefix else path
        records.append(CorpusInput(owner, relative, hashlib.sha256(data).hexdigest()))
    records = tuple(sorted(records))
    corpus_digest(records)
    rows = [dict(repository_id=owner, availability='available', observed_head=p.observed_head,
                 checkout_state=before[owner].checkout_state,
                 corpus_sha256=corpus_digest(r for r in records if r.repository_id == owner))
            for owner, p in participants.items()]
    observation = build_observation_set(root_repository_id=repository_id, participants=rows,
        relations=[asdict(r) for r in context.relations], complete=True)
    return MountedWorkingCorpus(records, MappingProxyType(first), observation)
