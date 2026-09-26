"""Real Git objects; no Git executable, network, hooks or checkout required."""
from pathlib import Path
import stat
import tempfile
import unittest
import zlib

from dulwich.objects import Blob, Commit, Tree
from dulwich.repo import Repo
from sbc_tools.git_reader import GitCommitReader, GitReadError


class GitReaderTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.repo = Repo.init(str(self.root))
        self.addCleanup(self.repo.close)
        self.blob = Blob.from_string(b"committed\n")
        self.repo.object_store.add_object(self.blob)
        subtree = Tree()
        subtree.add(b"record.json", 0o100644, self.blob.id)
        self.repo.object_store.add_object(subtree)
        tree = Tree()
        tree.add(b"projections", 0o40000, subtree.id)
        tree.add(b"link", 0o120000, self.blob.id)
        tree.add(b"child", 0o160000, b"a"*40)
        self.repo.object_store.add_object(tree)
        commit = Commit()
        commit.tree = tree.id
        commit.author = commit.committer = b"Fixture <fixture@example.invalid>"
        commit.author_time = commit.commit_time = 1
        commit.author_timezone = commit.commit_timezone = 0
        commit.message = b"Fixture\n"
        self.repo.object_store.add_object(commit)
        self.commit = commit.id.decode()
        self.reader = GitCommitReader(str(self.root))
        self.addCleanup(self.reader.close)

    def test_exact_committed_bytes_ignore_worktree(self):
        (self.root/"projections").mkdir()
        (self.root/"projections/record.json").write_bytes(b"dirty")
        self.assertEqual(b"committed\n", self.reader.read_blob(self.commit, "projections/record.json"))

    def test_inventory_retains_relations_without_following_them(self):
        entries = self.reader.entries(self.commit)
        self.assertEqual(["child", "link", "projections/record.json"], [e.path for e in entries])
        self.assertEqual(0o160000, entries[0].mode)
        self.assertEqual("a"*40, entries[0].oid)
        for path in ("link", "child", "child/file"):
            with self.subTest(path=path), self.assertRaises(GitReadError):
                self.reader.read_blob(self.commit, path)

    def test_exact_subtree_membership_and_bytes(self):
        self.reader.verify_files(self.commit, "projections", {"record.json": b"committed\n"})
        for files in ({"record.json": b"changed"}, {"extra": b"x"},
                      {"record.json": b"committed\n", "extra": b"x"}):
            with self.subTest(files=files), self.assertRaises(GitReadError):
                self.reader.verify_files(self.commit, "projections", files)

    def test_exact_commit_and_type_required(self):
        for oid in ("HEAD", "main", "a"*64, "A"*40, "0"*40, self.blob.id.decode()):
            with self.subTest(oid=oid), self.assertRaises(GitReadError):
                self.reader.entries(oid)

    def test_unsafe_paths_fail(self):
        for path in ("../record", "/absolute", "projections/../record", "C:/file", "a\\b", ".git/config"):
            with self.subTest(path=path), self.assertRaises(GitReadError):
                self.reader.read_blob(self.commit, path)

    def test_missing_blob_does_not_fall_back(self):
        oid = self.blob.id.decode()
        (self.root/".git/objects"/oid[:2]/oid[2:]).unlink()
        with self.assertRaises(GitReadError):
            self.reader.read_blob(self.commit, "projections/record.json")

    def test_corrupt_blob_is_rejected(self):
        oid = self.blob.id.decode()
        target = self.root/".git/objects"/oid[:2]/oid[2:]
        # Dulwich creates read-only loose objects on POSIX. This fixture owns the
        # object; permit the deliberate corruption before testing reader rejection.
        target.chmod(target.stat().st_mode | stat.S_IWUSR)
        target.write_bytes(zlib.compress(b"blob 5\0wrong"))
        with self.assertRaises(GitReadError):
            self.reader.read_blob(self.commit, "projections/record.json")

    def test_context_manager_and_missing_file(self):
        with GitCommitReader(str(self.root)) as reader:
            with self.assertRaises(GitReadError):
                reader.read_blob(self.commit, "absent")


if __name__ == "__main__":
    unittest.main()
