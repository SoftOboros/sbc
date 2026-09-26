from pathlib import Path
import tempfile
import unittest

from dulwich.index import build_index_from_tree
from dulwich.objects import Tree
from dulwich.repo import Repo
from sbc_tools.git_reader import GitCommitReader
from sbc_tools.mounts import observe_checkout_tree
from test_provenance_inputs import commit_files
from test_refs_mounts import commit_tree


class CheckoutTreeTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name).resolve()
        self.paths = {"root":self.root,"child":self.root/"child","leaf":self.root/"child/inner"}
        self.repos, self.readers = {}, {}
        for name,path in self.paths.items():
            path.mkdir(parents=True,exist_ok=True)
            repo = Repo.init(str(path))
            self.addCleanup(repo.close)
            self.repos[name] = repo
            reader = GitCommitReader(str(path))
            self.addCleanup(reader.close)
            self.readers[name] = reader
        self.leaf = commit_files(self.repos["leaf"],{"spec.md":b"leaf\n"})
        tree = Tree()
        tree.add(b"inner",0o160000,self.leaf.encode())
        self.child = commit_tree(self.repos["child"],tree)
        tree = Tree()
        tree.add(b"child",0o160000,self.child.encode())
        self.parent = commit_tree(self.repos["root"],tree)
        for name,commit in (("leaf",self.leaf),("child",self.child),("root",self.parent)):
            repo = self.repos[name]
            repo.refs[b"HEAD"] = commit.encode()
            build_index_from_tree(str(self.paths[name]),repo.index_path(),repo.object_store,
                                  repo.object_store[commit.encode()].tree)

    def observe(self, **kwargs):
        args = dict(root_repository_id="root",root_commit=self.parent,
            mounts=(("child","child"),("child/inner","leaf")),source_roots=("child",),readers=self.readers)
        args.update(kwargs)
        return observe_checkout_tree(**args)

    def test_clean_nested_tree_and_immutable_observations(self):
        result = self.observe()
        self.assertTrue(result.clean,{k:v.reason for k,v in result.observations.items()})
        self.assertEqual(self.leaf,result.observations["leaf"].commit)
        with self.assertRaises(TypeError): result.observations["root"] = None

    def test_dirty_leaf_propagates_through_both_parents(self):
        (self.paths["leaf"]/"spec.md").write_bytes(b"dirty")
        result = self.observe()
        self.assertFalse(result.clean)
        self.assertEqual("worktree_bytes_differ",result.observations["leaf"].reason)
        self.assertEqual("child_checkout_not_clean",result.observations["child"].reason)
        self.assertFalse(result.observations["root"].clean)

    def test_different_child_checkout_revision_rejected(self):
        other = commit_files(self.repos["leaf"],{"spec.md":b"different\n"})
        self.repos["leaf"].refs[b"HEAD"] = other.encode()
        result = self.observe()
        self.assertFalse(result.clean)
        self.assertEqual("checkout_revision_mismatch",result.observations["leaf"].reason)

    def test_child_untracked_file_prevents_clean(self):
        (self.paths["child"]/"extra").write_bytes(b"untracked")
        result = self.observe()
        self.assertFalse(result.clean)
        self.assertEqual("untracked_file",result.observations["child"].reason)

    def test_excluded_child_is_not_assumed_clean(self):
        result = self.observe(exclude=("child/inner",),readers={k:v for k,v in self.readers.items() if k != "leaf"})
        self.assertNotIn("leaf",result.observations)
        self.assertFalse(result.clean)
        self.assertEqual("child_checkout_evidence_incomplete",result.observations["child"].reason)

    def test_reader_for_identical_commit_in_other_checkout_rejected(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        repo = Repo.init(temp.name)
        self.addCleanup(repo.close)
        same = commit_files(repo,{"spec.md":b"leaf\n"})
        self.assertEqual(self.leaf,same)
        repo.refs[b"HEAD"] = same.encode()
        build_index_from_tree(temp.name,repo.index_path(),repo.object_store,repo.object_store[same.encode()].tree)
        reader = GitCommitReader(temp.name)
        self.addCleanup(reader.close)
        result = self.observe(readers=dict(self.readers,leaf=reader))
        self.assertFalse(result.clean)
        self.assertEqual("child_checkout_location_mismatch",result.observations["child"].reason)


if __name__ == "__main__": unittest.main()
