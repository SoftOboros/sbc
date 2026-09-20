"""Complete committed byte inventory for explicitly configured source scopes.

Selection configuration is trusted host input. This module does not infer
source roots, resolve child mounts or authorize a semantic profile.
"""
from dataclasses import dataclass
import hashlib
import unicodedata

from .canonical import canonical_json
from .identity import copy_files


@dataclass(frozen=True, order=True)
class CorpusInput:
    repository_id: str
    path: str
    sha256: str


def _paths(values):
    if isinstance(values, (str, bytes)):
        raise ValueError("Expected a sequence of paths")
    paths = tuple(values)
    if len(set(paths)) != len(paths):
        raise ValueError("Duplicate configured paths")
    for path in paths:
        copy_files({path: b""})
    return paths


def _within(path, root):
    return path == root or path.startswith(root + "/")


def inventory_committed_corpus(reader, *, repository_id, commit, source_roots,
                               required_files, exclude=()):
    """Inventory every nonexcluded source member plus all required input files.

    required_files must include configuration, authority manifest, registries and
    other selected evidence. Caller completeness is a separate configuration
    obligation; this primitive never emits VerifiedProvenance by itself.
    Unsupported symlinks/gitlinks in the selected scope fail, not disappear.
    """
    return inventory_mounted_corpus(repository_id=repository_id, commit=commit,
        readers={repository_id:reader}, mounts=(), source_roots=source_roots,
        required_files=required_files, exclude=exclude).records


def corpus_digest(records):
    records = sorted(records)
    keys = [(r.repository_id, r.path) for r in records]
    if len(set(keys)) != len(keys):
        raise ValueError("Duplicate corpus identity")
    payload = [{"repository_id": r.repository_id, "path": r.path, "sha256": r.sha256}
               for r in records]
    return hashlib.sha256(canonical_json(payload)).hexdigest()


@dataclass(frozen=True)
class MountedCorpus:
    records: tuple
    pins: tuple


def inventory_mounted_corpus(*, repository_id, commit, readers, mounts,
                             source_roots, required_files, exclude=()):
    """Select in parent-relative coordinates, hash in owning-repository coordinates.

    Every child is opened at the gitlink commit in its immediate pinned parent.
    Exclusions are literal parent-relative paths; they never hide required files.
    No checkout files or current child HEADs contribute committed corpus bytes.
    """
    from .mounts import pin_child_mounts
    if (not isinstance(repository_id,str) or not repository_id
            or unicodedata.normalize("NFC",repository_id) != repository_id):
        raise ValueError("Invalid registered repository ID")
    roots, required, excluded = map(_paths,(source_roots,required_files,exclude))
    if not roots or any(_within(a,b) for a in roots for b in roots if a != b):
        raise ValueError("Source roots must be nonempty and nonoverlapping")
    if any(_within(p,e) for p in (*roots,*required) for e in excluded):
        raise ValueError("Exclusions cannot hide required inputs or whole roots")
    scopes = tuple(sorted(set((*roots,*required))))
    pins = pin_child_mounts(root_repository_id=repository_id,root_commit=commit,
        mounts=mounts,source_roots=scopes,readers=readers,exclude=excluded)
    mounted_paths = {p.mount_path for p in pins}
    selections = [("",repository_id,commit)] + [
        (p.mount_path + "/",p.repository_id,p.child_commit) for p in pins]
    virtual, directories = {}, set(mounted_paths)
    for prefix, owner, selected_commit in selections:
        for entry in readers[owner].entries(selected_commit):
            path = prefix + entry.path
            parts = path.split("/")
            directories.update("/".join(parts[:i]) for i in range(1,len(parts)))
            if path in mounted_paths and entry.mode == 0o160000:
                continue
            if path in virtual:
                raise ValueError("Conflicting mounted corpus paths")
            virtual[path] = (owner,selected_commit,entry)
    if any(root not in directories or root in virtual for root in roots):
        raise ValueError("Missing committed source directory")
    if any(path not in virtual for path in required):
        raise ValueError("Missing required committed input")
    selected = set(required) | {p for p in virtual if any(_within(p,r) for r in roots)
                               and not any(_within(p,e) for e in excluded)}
    records = []
    for path in sorted(selected):
        owner, selected_commit, entry = virtual[path]
        if entry.mode not in {0o100644,0o100755}:
            raise ValueError("Selected corpus member is not a regular committed file")
        data = readers[owner].read_blob(selected_commit,entry.path)
        records.append(CorpusInput(owner,entry.path,hashlib.sha256(data).hexdigest()))
    # Verify unique ownership now, even when the caller only consumes records.
    corpus_digest(records)
    return MountedCorpus(tuple(sorted(records)),pins)
