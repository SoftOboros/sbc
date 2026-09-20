"""SBCT-02 transactional SQLite storage over explicitly validated bundles.

The caller supplies the semantic/provenance validator. No permissive default
validator is provided; this module does not replace SIDX bundle validation.
"""
from __future__ import annotations

from contextlib import closing
from dataclasses import dataclass
import hashlib
import json
import re
import sqlite3
from types import MappingProxyType
import unicodedata

from .canonical import canonical_json as _canonical

_FIELDS = {"repository_id", "snapshot_id", "source_commit", "projection_commit",
           "tracked_branch", "authority_manifest_sha256", "publication_id"}
_HEX64 = re.compile(r"[0-9a-f]{64}\Z")
_HEX40 = re.compile(r"[0-9a-f]{40}\Z")
_MESSAGES = {
    "invalid_bundle": "Invalid projection bundle.",
    "selection_conflict": "Selection changed.",
    "idempotency_conflict": "Idempotency key conflict.",
    "selection_unavailable": "Selection unavailable.",
    "store_unavailable": "Store unavailable.",
    "invalid_request": "Invalid request.",
}


def _error(code):
    return {"code": code, "message": _MESSAGES[code],
            "retryable": code in {"selection_conflict", "store_unavailable"}}


def _publication(value):
    value = dict(value)
    if set(value) != _FIELDS:
        raise ValueError("Invalid publication")
    for key, item in value.items():
        if not isinstance(item, str) or unicodedata.normalize("NFC", item) != item:
            raise ValueError("Invalid publication field")
        if key in {"repository_id", "tracked_branch"}:
            if not 1 <= len(item) <= 256:
                raise ValueError("Invalid identifier")
        elif not (_HEX40 if key.endswith("commit") else _HEX64).fullmatch(item):
            raise ValueError("Invalid digest")
    identity = dict(value)
    identity.pop("publication_id")
    if hashlib.sha256(_canonical(identity)).hexdigest() != value["publication_id"]:
        raise ValueError("Publication identity mismatch")
    return value


def _files(value):
    copied = dict(value)
    if not copied:
        raise ValueError("Empty bundle")
    for path, data in copied.items():
        if (not isinstance(path, str) or not path or "\\" in path or ":" in path
                or path.startswith("/") or any(p in {"", ".", ".."} for p in path.split("/"))
                or unicodedata.normalize("NFC", path) != path
                or any(ord(c) < 32 for c in path) or not isinstance(data, bytes)):
            raise ValueError("Invalid bundle member")
    return copied


def _bundle_digest(publication, profile, files):
    return hashlib.sha256(_canonical({
        "publication": publication, "profile": profile,
        "files": [{"path": p, "sha256": hashlib.sha256(files[p]).hexdigest()}
                  for p in sorted(files)],
    })).hexdigest()


@dataclass(frozen=True)
class _Candidate:
    publication: object
    validation_profile_sha256: str
    _files: object

    def files(self):
        return self._files


class ImmutableView:
    """Eagerly pinned bytes remain stable after another selection or DB close."""

    def __init__(self, publication, files):
        self._publication = MappingProxyType(dict(publication))
        self._files = MappingProxyType(dict(files))
        self._closed = False

    @property
    def publication(self):
        return self._publication

    def projection_bytes(self, relative_path):
        if self._closed:
            raise ValueError("View is closed")
        return self._files[relative_path]

    def close(self):
        self._closed = True
        self._files = MappingProxyType({})


class SQLiteSnapshotStore:
    """One file-backed database; per-repository current state and replay keys.

    validator.validate must perform the approved full semantic, content and
    committed-publication checks. It is trusted composition, never request input.
    Each operation opens its own connection; no global current/settings state.
    """

    def __init__(self, database, validator):
        if str(database) == ":memory:":
            raise ValueError("Use a persistent database path")
        self.database = str(database)
        self.validator = validator
        with closing(self._connect()) as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS sbct_publications (
                    repo TEXT NOT NULL, pub TEXT NOT NULL, metadata TEXT NOT NULL,
                    profile TEXT NOT NULL, digest TEXT NOT NULL, generation INTEGER NOT NULL,
                    PRIMARY KEY(repo,pub));
                CREATE TABLE IF NOT EXISTS sbct_files (
                    repo TEXT NOT NULL, pub TEXT NOT NULL, path TEXT NOT NULL,
                    data BLOB NOT NULL, PRIMARY KEY(repo,pub,path),
                    FOREIGN KEY(repo,pub) REFERENCES sbct_publications(repo,pub));
                CREATE TABLE IF NOT EXISTS sbct_current (
                    repo TEXT PRIMARY KEY, pub TEXT NOT NULL, generation INTEGER NOT NULL,
                    FOREIGN KEY(repo,pub) REFERENCES sbct_publications(repo,pub));
                CREATE TABLE IF NOT EXISTS sbct_replays (
                    repo TEXT NOT NULL, replay_key TEXT NOT NULL, digest TEXT NOT NULL,
                    receipt TEXT NOT NULL, PRIMARY KEY(repo,replay_key));
            """)

    def _connect(self):
        db = sqlite3.connect(self.database, timeout=0, isolation_level=None)
        db.execute("PRAGMA foreign_keys=ON")
        db.execute("PRAGMA synchronous=FULL")
        return db

    def _validated(self, publication, files, profile):
        publication = _publication(publication)
        files = _files(files)
        if not isinstance(profile, str) or not _HEX64.fullmatch(profile):
            raise ValueError("Invalid profile")
        # Copy before validation, then reject a validator that substitutes bytes.
        result = self.validator.validate(
            MappingProxyType(publication), MappingProxyType(files), profile)
        if (isinstance(result, dict) or dict(result.publication) != publication
                or result.validation_profile_sha256 != profile
                or dict(result.files()) != files):
            raise ValueError("Bundle rejected")
        return _Candidate(MappingProxyType(publication), profile, MappingProxyType(files))

    def publish(self, candidate, expected_generation, idempotency_key):
        if (type(expected_generation) is not int or expected_generation < 0
                or not isinstance(idempotency_key, str) or not idempotency_key):
            return _error("invalid_request")
        try:
            candidate = self._validated(candidate.publication, candidate.files(),
                                        candidate.validation_profile_sha256)
        except Exception:
            return _error("invalid_bundle")
        p, files = dict(candidate.publication), candidate.files()
        profile = candidate.validation_profile_sha256
        digest = _bundle_digest(p, profile, files)
        repo, pub = p["repository_id"], p["publication_id"]
        try:
            with closing(self._connect()) as db:
                db.execute("BEGIN IMMEDIATE")
                replay = db.execute(
                    "SELECT digest,receipt FROM sbct_replays WHERE repo=? AND replay_key=?",
                    (repo, idempotency_key)).fetchone()
                if replay:
                    return json.loads(replay[1]) if replay[0] == digest else _error("idempotency_conflict")
                current = db.execute("SELECT generation FROM sbct_current WHERE repo=?", (repo,)).fetchone()
                generation = current[0] if current else 0
                if generation != expected_generation:
                    return _error("selection_conflict")
                existing = db.execute("SELECT digest FROM sbct_publications WHERE repo=? AND pub=?",
                                      (repo, pub)).fetchone()
                if existing and existing[0] != digest:
                    return _error("invalid_bundle")
                if existing:
                    retained = dict(db.execute(
                        "SELECT path,data FROM sbct_files WHERE repo=? AND pub=?",
                        (repo, pub)).fetchall())
                    if retained != dict(files):
                        return _error("invalid_bundle")
                next_generation = generation + 1
                if not existing:
                    db.execute("INSERT INTO sbct_publications VALUES (?,?,?,?,?,?)",
                               (repo, pub, _canonical(p).decode(), profile, digest, next_generation))
                    db.executemany("INSERT INTO sbct_files VALUES (?,?,?,?)",
                                   [(repo, pub, path, files[path]) for path in sorted(files)])
                db.execute("INSERT INTO sbct_current VALUES (?,?,?) ON CONFLICT(repo) DO UPDATE SET pub=excluded.pub,generation=excluded.generation",
                           (repo, pub, next_generation))
                receipt = {"repository_id": repo, "publication_id": pub, "generation": next_generation}
                db.execute("INSERT INTO sbct_replays VALUES (?,?,?,?)",
                           (repo, idempotency_key, digest, _canonical(receipt).decode()))
                db.execute("COMMIT")
                return receipt
        except sqlite3.OperationalError as exc:
            return _error("selection_conflict" if getattr(exc, "sqlite_errorcode", None) in
                          {sqlite3.SQLITE_BUSY, sqlite3.SQLITE_LOCKED} else "store_unavailable")
        except sqlite3.Error:
            return _error("store_unavailable")

    def select(self, repository_id, selector):
        if not isinstance(selector, dict) or selector.get("kind") not in {"current", "publication"}:
            return _error("invalid_request")
        explicit = selector["kind"] == "publication"
        if set(selector) != ({"kind", "publication_id"} if explicit else {"kind"}):
            return _error("invalid_request")
        try:
            with closing(self._connect()) as db:
                if explicit:
                    row = db.execute("SELECT metadata,generation FROM sbct_publications WHERE repo=? AND pub=?",
                                     (repository_id, selector["publication_id"])).fetchone()
                else:
                    row = db.execute("SELECT p.metadata,c.generation FROM sbct_current c JOIN sbct_publications p ON p.repo=c.repo AND p.pub=c.pub WHERE c.repo=?",
                                     (repository_id,)).fetchone()
                if not row:
                    return _error("selection_unavailable") if explicit else None
                publication = _publication(json.loads(row[0]))
                if (publication["repository_id"] != repository_id or
                        (explicit and publication["publication_id"] != selector["publication_id"])):
                    return _error("invalid_bundle")
                return publication, row[1]
        except (ValueError, TypeError):
            return _error("invalid_bundle")
        except sqlite3.Error:
            return _error("store_unavailable")

    def open_view(self, publication):
        try:
            p = _publication(publication)
        except (ValueError, TypeError):
            return _error("invalid_bundle")
        try:
            with closing(self._connect()) as db:
                db.execute("BEGIN")
                row = db.execute("SELECT metadata,profile,digest FROM sbct_publications WHERE repo=? AND pub=?",
                                 (p["repository_id"], p["publication_id"])).fetchone()
                if not row:
                    return _error("selection_unavailable")
                files = dict(db.execute("SELECT path,data FROM sbct_files WHERE repo=? AND pub=?",
                                        (p["repository_id"], p["publication_id"])).fetchall())
                if json.loads(row[0]) != p or _bundle_digest(p, row[1], files) != row[2]:
                    return _error("invalid_bundle")
                checked = self._validated(p, files, row[1])
                return ImmutableView(checked.publication, checked.files())
        except sqlite3.Error:
            return _error("store_unavailable")
        except Exception:
            return _error("invalid_bundle")
