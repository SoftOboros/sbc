from pathlib import Path
import tempfile
import unittest

from dulwich.index import build_index_from_tree
from dulwich.repo import Repo
from sbc_tools.git_reader import GitCommitReader
from test_provenance_inputs import commit_files


class CheckoutTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.repo = Repo.init(temp.name)
        self.addCleanup(self.repo.close)
        self.commit = commit_files(self.repo,{"docs/spec.md":b"committed\n"})
        self.repo.refs[b"HEAD"] = self.commit.encode()
        self.materialize(self.commit)
        self.reader = GitCommitReader(temp.name)
        self.addCleanup(self.reader.close)

    def materialize(self, commit):
        build_index_from_tree(str(self.root),self.repo.index_path(),self.repo.object_store,
                              self.repo.object_store[commit.encode()].tree)

    def test_clean_byte_exact_checkout(self):
        result = self.reader.observe_checkout(self.commit)
        self.assertTrue(result.clean, result.reason)
        self.assertEqual("byte_exact",result.reason)

    def test_modified_missing_and_untracked_files(self):
        path = self.root/"docs/spec.md"
        path.write_bytes(b"changed\n")
        self.assertEqual("worktree_bytes_differ",self.reader.observe_checkout(self.commit).reason)
        path.unlink()
        self.assertEqual("missing_worktree_file",self.reader.observe_checkout(self.commit).reason)
        path.write_bytes(b"committed\n")
        (self.root/"extra").write_bytes(b"untracked")
        self.assertEqual("untracked_file",self.reader.observe_checkout(self.commit).reason)

    def test_staged_changes_even_when_worktree_matches_index(self):
        other = commit_files(self.repo,{"docs/spec.md":b"staged\n"})
        self.materialize(other)
        self.assertEqual("staged_change_or_conflict",self.reader.observe_checkout(self.commit).reason)

    def test_staged_addition(self):
        other = commit_files(self.repo,{"docs/spec.md":b"committed\n","added":b"new"})
        self.materialize(other)
        self.assertEqual("staged_membership_change",self.reader.observe_checkout(self.commit).reason)

    def test_checkout_revision_mismatch(self):
        other = commit_files(self.repo,{"docs/spec.md":b"other\n"})
        self.repo.refs[b"HEAD"] = other.encode()
        self.assertEqual("checkout_revision_mismatch",self.reader.observe_checkout(self.commit).reason)

    def test_missing_index_and_line_endings_fail_closed(self):
        (self.root/"docs/spec.md").write_bytes(b"committed\r\n")
        self.assertFalse(self.reader.observe_checkout(self.commit).clean)
        Path(self.repo.index_path()).unlink()
        self.assertEqual("checkout_evidence_unavailable",self.reader.observe_checkout(self.commit).reason)

    def test_ambient_filter_is_not_executed(self):
        self.commit = commit_files(self.repo,{"docs/spec.md":b"committed\n",
                                              ".gitattributes":b"*.md filter=example\n"})
        self.repo.refs[b"HEAD"] = self.commit.encode()
        self.materialize(self.commit)
        config = self.repo.get_config()
        config.set((b"filter",b"example"),b"clean",b"command-that-must-never-run")
        config.set(b"core",b"fsmonitor",b"command-that-must-never-run")
        config.write_to_path()
        result = self.reader.observe_checkout(self.commit)
        self.assertTrue(result.clean,result.reason)


if __name__ == "__main__": unittest.main()
