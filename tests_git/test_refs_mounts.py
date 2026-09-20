from pathlib import Path
import tempfile
import unittest

from dulwich.objects import Blob, Commit, Tag, Tree
from dulwich.repo import Repo
from sbc_tools.git_reader import GitCommitReader, GitReadError, GitUnavailableError
from sbc_tools.mounts import pin_child_mounts
from test_provenance_inputs import commit_files


def commit_tree(repo, tree):
    repo.object_store.add_object(tree)
    commit = Commit()
    commit.tree = tree.id
    commit.author = commit.committer = b"Fixture <fixture@example.invalid>"
    commit.author_time = commit.commit_time = 1
    commit.author_timezone = commit.commit_timezone = 0
    commit.message = b"Fixture\n"
    repo.object_store.add_object(commit)
    return commit.id.decode()


class ReferenceMountTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.repos, self.readers = {}, {}
        for name in ("root", "child", "nested"):
            path = self.root/name
            path.mkdir()
            repo = Repo.init(str(path))
            self.addCleanup(repo.close)
            reader = GitCommitReader(str(path))
            self.addCleanup(reader.close)
            self.repos[name], self.readers[name] = repo, reader
        self.nested = commit_files(self.repos["nested"], {"spec.md":b"nested"})
        tree = Tree()
        tree.add(b"inner",0o160000,self.nested.encode())
        self.child = commit_tree(self.repos["child"],tree)
        tree = Tree()
        tree.add(b"child",0o160000,self.child.encode())
        self.parent = commit_tree(self.repos["root"],tree)
        self.repos["root"].refs[b"refs/heads/main"] = self.parent.encode()
        self.repos["root"].refs.set_symbolic_ref(b"HEAD",b"refs/heads/main")

    def pin(self, **kwargs):
        args = dict(root_repository_id="root",root_commit=self.parent,
                    mounts=(("child","child"),("child/inner","nested")),
                    source_roots=("child/inner",),readers=self.readers)
        args.update(kwargs)
        return pin_child_mounts(**args)

    def tag(self, target, cls=Commit):
        tag = Tag()
        tag.object = (cls,target.encode())
        tag.name = b"fixture"
        tag.tagger = b"Fixture <fixture@example.invalid>"
        tag.tag_time = 1
        tag.tag_timezone = 0
        tag.message = b"Fixture tag\n"
        self.repos["root"].object_store.add_object(tag)
        return tag.id.decode()

    def test_head_branch_and_exact_commit_pin(self):
        reader = self.readers["root"]
        for ref in ("HEAD","refs/heads/main",self.parent):
            self.assertEqual(self.parent,reader.resolve_commit(ref))
        pinned = reader.resolve_commit("HEAD")
        new = commit_files(self.repos["root"],{"new":b"content"})
        self.repos["root"].refs[b"refs/heads/main"] = new.encode()
        self.assertEqual(self.parent,pinned)
        self.assertEqual(new,reader.resolve_commit("HEAD"))

    def test_lightweight_and_nested_annotated_tags(self):
        first = self.tag(self.parent)
        second = self.tag(first,Tag)
        for name,target in ((b"refs/tags/light",self.parent),(b"refs/tags/annotated",second)):
            self.repos["root"].refs[name] = target.encode()
            self.assertEqual(self.parent,self.readers["root"].resolve_commit(name.decode()))

    def test_missing_ref_commit_and_tag_target_are_unavailable(self):
        missing_tag = self.tag("0"*40)
        for ref in ("refs/heads/absent","0"*40,missing_tag):
            with self.subTest(ref=ref), self.assertRaises(GitUnavailableError):
                self.readers["root"].resolve_commit(ref)

    def test_wrong_type_and_disallowed_syntax(self):
        blob = Blob.from_string(b"blob")
        self.repos["root"].object_store.add_object(blob)
        for ref in (blob.id.decode(),self.tag(blob.id.decode(),Blob),"main","HEAD~1","a"*64):
            with self.subTest(ref=ref),self.assertRaises(ValueError):
                self.readers["root"].resolve_commit(ref)

    def test_symbolic_ref_cycle_rejected(self):
        self.repos["root"].refs.set_symbolic_ref(b"refs/heads/a",b"refs/heads/b")
        self.repos["root"].refs.set_symbolic_ref(b"refs/heads/b",b"refs/heads/a")
        with self.assertRaises(GitReadError): self.readers["root"].resolve_commit("refs/heads/a")

    def test_nested_mount_pins_immediate_parent(self):
        child,nested = self.pin()
        self.assertEqual(self.child,child.child_commit)
        self.assertEqual("child",nested.parent_repository_id)
        self.assertEqual(self.child,nested.parent_commit)
        self.assertEqual("inner",nested.parent_relative_path)
        self.assertEqual(self.nested,nested.child_commit)

    def test_missing_ancestor_and_wrong_mount_are_rejected(self):
        for mounts in ((("child/inner","nested"),),(("absent","child"),)):
            with self.subTest(mounts=mounts),self.assertRaises(ValueError):
                self.pin(mounts=mounts,source_roots=(mounts[0][0],))
        with self.assertRaises(ValueError): self.pin(mounts=())
        with self.assertRaises(ValueError): self.pin(mounts=(("child","child"),),source_roots=("child",))

    def test_missing_child_repository_and_objects(self):
        with self.assertRaises(GitUnavailableError): self.pin(readers={"root":self.readers["root"]})
        with self.assertRaises(GitUnavailableError):
            self.pin(readers=dict(self.readers,child=self.readers["root"]))

    def test_unselected_children_not_opened_and_cycles_rejected(self):
        self.assertEqual((),self.pin(source_roots=("elsewhere",),readers={"root":self.readers["root"]}))
        with self.assertRaises(ValueError): self.pin(mounts=(("child","root"),))

    def test_excluded_nested_child_not_opened(self):
        pins = self.pin(source_roots=("child",),exclude=("child/inner",),
                        readers={"root":self.readers["root"],"child":self.readers["child"]})
        self.assertEqual(["child"],[p.mount_path for p in pins])
        with self.assertRaises(ValueError): self.pin(exclude=("child",))
        with self.assertRaises(ValueError): self.pin(exclude="child/inner")


if __name__ == "__main__": unittest.main()
