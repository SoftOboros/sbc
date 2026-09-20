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
    if (not isinstance(repository_id, str) or not repository_id
            or unicodedata.normalize("NFC", repository_id) != repository_id):
        raise ValueError("Invalid registered repository ID")
    roots, required, excluded = map(_paths, (source_roots, required_files, exclude))
    if not roots or any(_within(a, b) for a in roots for b in roots if a != b):
        raise ValueError("Source roots must be nonempty and nonoverlapping")
    if any(_within(path, e) for path in (*required, *roots) for e in excluded):
        raise ValueError("Exclusions cannot hide required inputs or whole roots")
    entries = {e.path: e for e in reader.entries(commit)}
    for root in roots:
        if root in entries or not any(p.startswith(root + "/") for p in entries):
            raise ValueError("Missing committed source directory")
    if any(path not in entries for path in required):
        raise ValueError("Missing required committed input")
    selected = set(required) | {p for p in entries
        if any(_within(p, root) for root in roots)
        and not any(_within(p, e) for e in excluded)}
    records = []
    for path in sorted(selected):
        if entries[path].mode not in {0o100644, 0o100755}:
            raise ValueError("Selected corpus member is not a regular committed file")
        data = reader.read_blob(commit, path)
        records.append(CorpusInput(repository_id, path, hashlib.sha256(data).hexdigest()))
    return tuple(records)


def corpus_digest(records):
    records = sorted(records)
    keys = [(r.repository_id, r.path) for r in records]
    if len(set(keys)) != len(keys):
        raise ValueError("Duplicate corpus identity")
    payload = [{"repository_id": r.repository_id, "path": r.path, "sha256": r.sha256}
               for r in records]
    return hashlib.sha256(canonical_json(payload)).hexdigest()
