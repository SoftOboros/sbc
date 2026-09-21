"""Storage witnesses use a synthetic validator, not SIDX conformance evidence."""
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from dataclasses import dataclass
import hashlib
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import threading
import unittest

from sbc_tools.canonical import canonical_json
from sbc_tools.store import SQLiteSnapshotStore


@dataclass
class Candidate:
    publication: dict
    validation_profile_sha256: str
    payload: dict

    def files(self):
        return self.payload


class SyntheticValidator:
    """Test-only exact-byte allowlist standing in for the required validator."""
    def __init__(self):
        self.expected = {}

    def validate(self, publication, files, profile):
        if profile != "a"*64 or dict(files) != self.expected.get(publication["publication_id"]):
            return {"code": "invalid_bundle"}
        return Candidate(dict(publication), profile, dict(files))


class StoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.db = Path(self.temp.name) / "store.sqlite3"
        self.validator = SyntheticValidator()
        self.store = SQLiteSnapshotStore(self.db, self.validator)

    def candidate(self, commit="b", repo="repo", data=b"example"):
        publication = dict(repository_id=repo, snapshot_id=hashlib.sha256(data).hexdigest(),
                           source_commit="a"*40, projection_commit=commit*40,
                           tracked_branch="main", authority_manifest_sha256="1"*64)
        publication["publication_id"] = hashlib.sha256(canonical_json(publication)).hexdigest()
        files = {"index/family.json": data}
        self.validator.expected[publication["publication_id"]] = dict(files)
        return Candidate(publication, "a"*64, files)

    def current(self, repo="repo"):
        return self.store.select(repo, {"kind": "current"})

    def test_equal_content_distinct_publications_and_pinned_reader(self):
        a, b = self.candidate("b"), self.candidate("c")
        self.assertEqual(a.publication["snapshot_id"], b.publication["snapshot_id"])
        self.assertEqual(1, self.store.publish(a, 0, "a")["generation"])
        view = self.store.open_view(a.publication)
        self.assertEqual(2, self.store.publish(b, 1, "b")["generation"])
        self.assertEqual(b.publication, self.current()[0])
        self.assertEqual(a.publication, dict(view.publication))
        self.assertEqual(b"example", view.projection_bytes("index/family.json"))
        explicit = self.store.select("repo", {"kind": "publication", "publication_id": a.publication["publication_id"]})
        self.assertEqual((a.publication, 1), explicit)
        view.close()
        with self.assertRaises(ValueError):
            view.projection_bytes("index/family.json")

    def test_failed_validation_preserves_current(self):
        a, b = self.candidate("b"), self.candidate("c")
        self.store.publish(a, 0, "a")
        b.payload["index/family.json"] = b"corrupt"
        self.assertEqual("invalid_bundle", self.store.publish(b, 1, "b")["code"])
        self.assertEqual((a.publication, 1), self.current())

    def test_transaction_failure_rolls_back_entire_candidate(self):
        a, b = self.candidate("b"), self.candidate("c")
        self.store.publish(a, 0, "a")
        with closing(sqlite3.connect(self.db, isolation_level=None)) as db:
            db.execute("CREATE TRIGGER fail_selection BEFORE INSERT ON sbct_current BEGIN SELECT RAISE(ABORT, 'injected failure'); END")
        self.assertEqual("store_unavailable", self.store.publish(b, 1, "b")["code"])
        self.assertEqual((a.publication, 1), self.current())
        self.assertEqual("selection_unavailable", self.store.open_view(b.publication)["code"])
        with closing(sqlite3.connect(self.db, isolation_level=None)) as db:
            self.assertEqual(1, db.execute("SELECT count(*) FROM sbct_replays").fetchone()[0])

    def test_two_competing_writers(self):
        candidates = [self.candidate("b"), self.candidate("c")]
        barrier = threading.Barrier(2)
        def publish(i):
            barrier.wait()
            return self.store.publish(candidates[i], 0, str(i))
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(publish, range(2)))
        self.assertEqual(1, sum("generation" in r for r in results))
        self.assertEqual(1, sum(r.get("code") == "selection_conflict" for r in results))
        self.assertEqual(1, self.current()[1])

    def test_idempotency_does_not_reset_newer_current(self):
        a, b = self.candidate("b"), self.candidate("c")
        receipt = self.store.publish(a, 0, "a")
        self.store.publish(b, 1, "b")
        self.assertEqual(receipt, self.store.publish(a, 0, "a"))
        self.assertEqual((b.publication, 2), self.current())
        self.assertEqual("idempotency_conflict", self.store.publish(b, 2, "a")["code"])

    def test_repository_isolation(self):
        a, b = self.candidate(repo="one"), self.candidate(repo="two")
        self.store.publish(a, 0, "same-key")
        self.store.publish(b, 0, "same-key")
        self.assertEqual((a.publication, 1), self.current("one"))
        self.assertEqual((b.publication, 1), self.current("two"))
        self.assertIsNone(self.current("missing"))

    def test_candidate_and_view_immutability(self):
        candidate = self.candidate()
        publication = dict(candidate.publication)
        self.store.publish(candidate, 0, "a")
        candidate.payload.clear()
        candidate.publication["tracked_branch"] = "modified"
        view = self.store.open_view(publication)
        self.assertEqual(b"example", view.projection_bytes("index/family.json"))
        with self.assertRaises(TypeError):
            view.publication["tracked_branch"] = "modified"

    def test_corrupt_persisted_bytes_rejected(self):
        candidate = self.candidate()
        self.store.publish(candidate, 0, "a")
        with closing(sqlite3.connect(self.db, isolation_level=None)) as db:
            db.execute("UPDATE sbct_files SET data=?", (b"tampered",))
        self.assertEqual("invalid_bundle", self.store.open_view(candidate.publication)["code"])

    def test_reopen_and_identity_table_preservation(self):
        with closing(sqlite3.connect(self.db, isolation_level=None)) as db:
            db.execute("CREATE TABLE auth_users (username TEXT)")
            db.execute("INSERT INTO auth_users VALUES ('example')")
        candidate = self.candidate()
        self.store.publish(candidate, 0, "a")
        reopened = SQLiteSnapshotStore(self.db, self.validator)
        self.assertEqual((candidate.publication, 1), reopened.select("repo", {"kind": "current"}))
        with closing(sqlite3.connect(self.db, isolation_level=None)) as db:
            self.assertEqual([("example",)], db.execute("SELECT * FROM auth_users").fetchall())

    def test_invalid_publication_and_path_rejected(self):
        candidate = self.candidate()
        candidate.publication["projection_commit"] = "f"*40
        self.assertEqual("invalid_bundle", self.store.publish(candidate, 0, "a")["code"])
        candidate = self.candidate()
        candidate.payload = {"../outside": b"example"}
        self.assertEqual("invalid_bundle", self.store.publish(candidate, 0, "a")["code"])

    def test_process_exit_before_commit_preserves_selection(self):
        candidate = self.candidate()
        self.store.publish(candidate, 0, "a")
        program = (
            "import os,sqlite3,sys; "
            "db=sqlite3.connect(sys.argv[1],isolation_level=None); "
            "db.execute('BEGIN IMMEDIATE'); "
            "db.execute('UPDATE sbct_current SET generation=999'); "
            "os._exit(7)"
        )
        result = subprocess.run([sys.executable, "-I", "-S", "-c", program, str(self.db)],
                                check=False, timeout=15)
        self.assertEqual(7, result.returncode)
        self.assertEqual((candidate.publication, 1), self.current())

    def test_corrupt_retained_publication_cannot_be_reselected(self):
        a, b = self.candidate("b"), self.candidate("c")
        self.store.publish(a, 0, "a")
        self.store.publish(b, 1, "b")
        with closing(sqlite3.connect(self.db, isolation_level=None)) as db:
            db.execute("DELETE FROM sbct_files WHERE pub=?", (a.publication["publication_id"],))
        self.assertEqual("invalid_bundle", self.store.publish(a, 2, "reselect-a")["code"])
        self.assertEqual((b.publication, 2), self.current())


if __name__ == "__main__":
    unittest.main()
