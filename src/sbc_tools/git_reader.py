"""Offline reads of exact SHA-1 Git commits using the approved Python provider.

This is a provenance primitive, not an authority or corpus-completeness verifier.
The host supplies the repository location; callers cannot select repositories.
"""
from dataclasses import dataclass
import hashlib
import re
import unicodedata


class GitReadError(ValueError):
    """Missing, corrupt, unsafe or unsupported committed evidence."""


@dataclass(frozen=True)
class CommittedEntry:
    path: str
    mode: int
    oid: str


def _path(value):
    if (not isinstance(value, str) or not value or "\\" in value or ":" in value
            or unicodedata.normalize("NFC", value) != value
            or any(ord(c) < 32 for c in value)
            or any(p in {"", ".", "..", ".git"} for p in value.split("/"))):
        raise GitReadError("Unsafe committed path")
    return value


class GitCommitReader:
    """No ref resolution, checkout, hooks, subprocesses or network acquisition.

    Symlinks and gitlinks are returned as inventory entries and never followed.
    read_blob accepts only regular files. Missing objects fail without fallback.
    """
    def __init__(self, repository_path):
        from dulwich.repo import Repo
        self._repo = Repo(repository_path)

    def close(self):
        self._repo.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def _object(self, oid, kind):
        if not isinstance(oid, str) or not re.fullmatch(r"[0-9a-f]{40}", oid):
            raise GitReadError("This query profile requires an exact SHA-1 object ID")
        try:
            obj = self._repo.object_store[oid.encode("ascii")]
            raw = obj.as_raw_string()
            identity = hashlib.sha1(obj.type_name + b" " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
            if obj.type_name != kind or identity != oid:
                raise GitReadError("Committed object type or hash mismatch")
            obj.check()
            return obj
        except GitReadError:
            raise
        except Exception as exc:
            raise GitReadError("Committed object unavailable or invalid") from exc

    def entries(self, commit):
        """Return a deterministic immutable leaf inventory of one exact commit."""
        root = self._object(commit, b"commit")
        pending = [("", root.tree.decode("ascii"), 0)]
        entries = []
        while pending:
            prefix, oid, depth = pending.pop()
            if depth > 128:
                raise GitReadError("Committed tree exceeds traversal limit")
            tree = self._object(oid, b"tree")
            for name, mode, child in tree.iteritems():
                try:
                    part = name.decode("utf-8")
                    if "/" in part:
                        raise GitReadError("Invalid tree member")
                    path = _path(prefix + part)
                    child_oid = child.decode("ascii")
                except UnicodeError as exc:
                    raise GitReadError("Invalid tree encoding") from exc
                if mode == 0o40000:
                    pending.append((path + "/", child_oid, depth + 1))
                elif mode in {0o100644, 0o100755, 0o120000, 0o160000}:
                    entries.append(CommittedEntry(path, mode, child_oid))
                else:
                    raise GitReadError("Unsupported tree member mode")
                if len(entries) + len(pending) > 1_000_000:
                    raise GitReadError("Committed tree exceeds entry limit")
        return tuple(sorted(entries, key=lambda entry: entry.path))

    def read_blob(self, commit, path):
        path = _path(path)
        entry = next((e for e in self.entries(commit) if e.path == path), None)
        if entry is None or entry.mode not in {0o100644, 0o100755}:
            raise GitReadError("Committed regular file is unavailable")
        return bytes(self._object(entry.oid, b"blob").data)

    def verify_files(self, commit, prefix, files):
        """Compare the complete subtree, rejecting extra, missing or unsafe members."""
        from .identity import copy_files
        prefix = _path(prefix) + "/"
        supplied = copy_files(files)
        selected = {e.path[len(prefix):]: e for e in self.entries(commit)
                    if e.path.startswith(prefix)}
        if set(selected) != set(supplied):
            raise GitReadError("Committed projection membership mismatch")
        for path, entry in selected.items():
            if (entry.mode not in {0o100644, 0o100755}
                    or self._object(entry.oid, b"blob").data != supplied[path]):
                raise GitReadError("Committed projection bytes mismatch")
