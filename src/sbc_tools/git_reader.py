"""Offline reads of exact SHA-1 Git commits using the approved Python provider.

This is a provenance primitive, not an authority or corpus-completeness verifier.
The host supplies the repository location; callers cannot select repositories.
"""
from dataclasses import dataclass
import hashlib
import os
from pathlib import Path
import re
import stat
import unicodedata


class GitReadError(ValueError):
    """Missing, corrupt, unsafe or unsupported committed evidence."""


class GitUnavailableError(GitReadError):
    """A syntactically valid selection has unavailable refs or objects."""


@dataclass(frozen=True)
class CommittedEntry:
    path: str
    mode: int
    oid: str


@dataclass(frozen=True)
class CheckoutObservation:
    commit: str
    clean: bool
    reason: str


def _path(value):
    if (not isinstance(value, str) or not value or "\\" in value or ":" in value
            or unicodedata.normalize("NFC", value) != value
            or any(ord(c) < 32 for c in value)
            or any(p in {"", ".", "..", ".git"} for p in value.split("/"))):
        raise GitReadError("Unsafe committed path")
    return value


class GitCommitReader:
    """No checkout, hooks, subprocesses or network acquisition.

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

    def _object(self, oid, kind=None):
        if not isinstance(oid, str) or not re.fullmatch(r"[0-9a-f]{40}", oid):
            raise GitReadError("This query profile requires an exact SHA-1 object ID")
        try:
            obj = self._repo.object_store[oid.encode("ascii")]
            raw = obj.as_raw_string()
            identity = hashlib.sha1(obj.type_name + b" " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
            if (kind is not None and obj.type_name != kind) or identity != oid:
                raise GitReadError("Committed object type or hash mismatch")
            obj.check()
            return obj
        except GitReadError:
            raise
        except KeyError as exc:
            raise GitUnavailableError("Committed object unavailable") from exc
        except Exception as exc:
            raise GitReadError("Committed object unavailable or invalid") from exc

    def resolve_commit(self, selection):
        """Resolve once, peel annotated tags, then return an exact commit pin.

        SHA-256 repositories remain outside the approved query profile. Missing
        refs/objects have a distinct error from malformed selections/wrong types.
        """
        from .configuration import validate_ref_syntax
        validate_ref_syntax(selection)
        if re.fullmatch(r"[0-9a-f]{64}", selection):
            raise GitReadError("SHA-256 Git is unsupported by this query profile")
        if re.fullmatch(r"[0-9a-f]{40}", selection):
            oid = selection
        else:
            try:
                chain, target = self._repo.refs.follow(selection.encode("utf-8"))
                for ref in chain:
                    validate_ref_syntax(ref.decode("utf-8"))
                if target is None:
                    raise GitUnavailableError("Selected reference unavailable")
                oid = target.decode("ascii")
            except GitReadError:
                raise
            except Exception as exc:
                raise GitReadError("Invalid symbolic reference chain") from exc
        seen, expected = set(), None
        for _ in range(64):
            if oid in seen:
                raise GitReadError("Cyclic tag chain")
            seen.add(oid)
            obj = self._object(oid, expected)
            if obj.type_name == b"commit":
                return oid
            if obj.type_name != b"tag":
                raise GitReadError("Selection does not resolve to a commit")
            target_type, target_oid = obj.object
            expected = target_type.type_name
            oid = target_oid.decode("ascii")
        raise GitReadError("Tag chain exceeds traversal limit")

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

    def observe_checkout(self, commit):
        """Bounded byte-exact observation; never runs ambient Git filters.

        All index and working files are checked. Untracked files, including
        ignored files, prevent this conservative clean result. Gitlinks and
        symlinks require additional handling and are not accepted here. This is
        an observation, not a filesystem lock or a general Git-status clone.
        """
        from dulwich.config import ConfigDict
        def failed(reason):
            return CheckoutObservation(commit, False, reason)
        if self.resolve_commit("HEAD") != commit:
            return failed("checkout_revision_mismatch")
        if self._repo.bare:
            return failed("checkout_unavailable")
        entries = {e.path:e for e in self.entries(commit)}
        if any(e.mode not in {0o100644, 0o100755} for e in entries.values()):
            return failed("unsupported_member_mode")
        if os.name == "nt" and any(e.mode == 0o100755 for e in entries.values()):
            return failed("executable_mode_unverifiable")
        try:
            index_path = Path(os.fsdecode(self._repo.index_path()))
            original_index = index_path.read_bytes()
            index = self._repo.open_index(config=ConfigDict())
            indexed = {p.decode("utf-8"):e for p,e in index.items()}
            if set(indexed) != set(entries):
                return failed("staged_membership_change")
            for path, item in indexed.items():
                if getattr(item,"sha",None) != entries[path].oid.encode() or getattr(item,"mode",None) != entries[path].mode:
                    return failed("staged_change_or_conflict")
            root = Path(os.fsdecode(self._repo.path)).resolve()
            observed = set()
            def walk_error(error):
                raise error
            for directory, dirs, files in os.walk(root, followlinks=False, onerror=walk_error):
                if Path(directory) == root:
                    dirs[:] = [d for d in dirs if d != ".git"]
                    files = [f for f in files if f != ".git"]
                for name in dirs + files:
                    path = Path(directory)/name
                    metadata = path.lstat()
                    if stat.S_ISLNK(metadata.st_mode) or getattr(metadata,"st_file_attributes",0) & 0x400:
                        return failed("symlink_or_reparse_point")
                for name in files:
                    path = Path(directory)/name
                    relative = path.relative_to(root).as_posix()
                    if relative not in entries:
                        return failed("untracked_file")
                    before = path.stat()
                    if not stat.S_ISREG(before.st_mode):
                        return failed("unsupported_worktree_member")
                    if os.name != "nt" and bool(before.st_mode & 0o111) != (entries[relative].mode == 0o100755):
                        return failed("executable_mode_changed")
                    raw = path.read_bytes()
                    after = path.stat()
                    if (before.st_size,before.st_mtime_ns,before.st_ino) != (after.st_size,after.st_mtime_ns,after.st_ino):
                        return failed("worktree_changed_during_observation")
                    if raw != self._object(entries[relative].oid,b"blob").data:
                        return failed("worktree_bytes_differ")
                    observed.add(relative)
            if observed != set(entries):
                return failed("missing_worktree_file")
            if self.resolve_commit("HEAD") != commit or index_path.read_bytes() != original_index:
                return failed("selection_changed_during_observation")
            return CheckoutObservation(commit, True, "byte_exact")
        except (OSError, ValueError, KeyError, AttributeError, UnicodeError):
            return failed("checkout_evidence_unavailable")
