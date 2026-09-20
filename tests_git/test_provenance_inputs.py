"""Authority and corpus checks over real committed Git objects."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from dulwich.objects import Blob, Commit, Tree
from dulwich.repo import Repo
from sbc_tools.authority import ROLES, verify_authority_inputs
from sbc_tools.canonical import canonical_json
from sbc_tools.corpus import CorpusInput, corpus_digest, inventory_committed_corpus
from sbc_tools.git_reader import GitCommitReader
from sbc_tools.validation import VerifiedProvenance


def commit_files(repo, files):
    nested = {}
    for path, data in files.items():
        node = nested
        parts = path.split("/")
        for part in parts[:-1]:
            node = node.setdefault(part, {})
        node[parts[-1]] = data
    def tree_for(node):
        tree = Tree()
        for name, value in node.items():
            obj = tree_for(value) if isinstance(value, dict) else Blob.from_string(value)
            repo.object_store.add_object(obj)
            tree.add(name.encode(), 0o40000 if isinstance(value, dict) else 0o100644, obj.id)
        return tree
    tree = tree_for(nested)
    repo.object_store.add_object(tree)
    commit = Commit()
    commit.tree = tree.id
    commit.author = commit.committer = b"Fixture <fixture@example.invalid>"
    commit.author_time = commit.commit_time = 1
    commit.author_timezone = commit.commit_timezone = 0
    commit.message = b"Fixture\n"
    repo.object_store.add_object(commit)
    return commit.id.decode()


class ProvenanceInputTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.repo = Repo.init(temp.name)
        self.addCleanup(self.repo.close)
        self.files = {group + "/" + role: role.encode() for group, roles in ROLES.items() for role in roles}
        self.files.update({"docs/a.md": b"A", "docs/nested/b.md": b"B", "config.toml": b"config",
                           "authority.json": b"authority", "registry.md": b"registry"})
        self.commit = commit_files(self.repo, self.files)
        self.reader = GitCommitReader(temp.name)
        self.addCleanup(self.reader.close)
        self.patch = b"synthetic integrity fixture; not patch application evidence"
        self.manifest = dict(schema_version=1, profile="sidx-schema3-location1", license="BSD-3-Clause",
            payload_schemas={"index":3,"locations":1,"diagnostics":3}, reviewed_patches=[{
                "role":"proposed-operational-metadata-correction", "applies_to":["AGENTS.md","CLAUDE.md","README.md"],
                "sha256":hashlib.sha256(self.patch).hexdigest()}])
        for group, roles in ROLES.items():
            self.manifest[group] = []
            for role in sorted(roles):
                path = group + "/" + role
                data = self.files[path]
                self.manifest[group].append(dict(role=role, repository_id="fixture", commit=self.commit,
                    files=[dict(path=path, blob_oid=Blob.from_string(data).id.decode(), sha256=hashlib.sha256(data).hexdigest())]))

    def verify(self, manifest=None, **kwargs):
        raw = canonical_json(self.manifest if manifest is None else manifest)
        args = dict(approved_manifest_sha256=hashlib.sha256(raw).hexdigest(), patch_bytes=self.patch,
                    readers={"fixture":self.reader})
        args.update(kwargs)
        return verify_authority_inputs(raw, **args)

    def inventory(self, **kwargs):
        args = dict(repository_id="fixture", commit=self.commit, source_roots=("docs",),
                    required_files=("config.toml","authority.json","registry.md"))
        args.update(kwargs)
        return inventory_committed_corpus(self.reader, **args)

    def test_all_authority_roles_verified_and_immutable(self):
        result = self.verify()
        self.assertEqual(16, len(result.base_files_by_role))
        self.assertNotIsInstance(result, VerifiedProvenance)
        with self.assertRaises(TypeError):
            result.base_files_by_role["scan.py"] = b"changed"

    def test_approval_pin_patch_and_repository_fail_closed(self):
        for override in ({"approved_manifest_sha256":"0"*64}, {"patch_bytes":b"wrong"}, {"readers":{}}):
            with self.subTest(override=override), self.assertRaises(ValueError):
                self.verify(**override)

    def test_missing_duplicate_and_unknown_role_fail(self):
        for mutation in ("missing","duplicate","unknown"):
            manifest = copy.deepcopy(self.manifest)
            rows = manifest["producer_inputs"]
            if mutation == "missing": rows.pop()
            elif mutation == "duplicate": rows[1] = copy.deepcopy(rows[0])
            else: rows[0]["role"] = "unknown.py"
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                self.verify(manifest)

    def test_wrong_blob_digest_and_commit_fail(self):
        for key, value in (("blob_oid","0"*40),("sha256","0"*64),("path","../escape")):
            manifest = copy.deepcopy(self.manifest)
            manifest["producer_inputs"][0]["files"][0][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.verify(manifest)
        manifest = copy.deepcopy(self.manifest)
        manifest["producer_inputs"][0]["commit"] = "HEAD"
        with self.assertRaises(ValueError): self.verify(manifest)

    def test_unsorted_and_boolean_schema_fail(self):
        manifest = copy.deepcopy(self.manifest)
        manifest["support_inputs"].reverse()
        with self.assertRaises(ValueError): self.verify(manifest)
        manifest = copy.deepcopy(self.manifest)
        manifest["schema_version"] = True
        with self.assertRaises(ValueError): self.verify(manifest)

    def test_duplicate_json_keys_fail(self):
        raw = canonical_json(self.manifest).replace(b'"schema_version":1', b'"schema_version":1,"schema_version":1')
        with self.assertRaises(ValueError):
            verify_authority_inputs(raw, approved_manifest_sha256=hashlib.sha256(raw).hexdigest(),
                                    patch_bytes=self.patch, readers={"fixture":self.reader})

    def test_corpus_contains_every_selected_file_and_required_input(self):
        records = self.inventory()
        self.assertEqual(["authority.json","config.toml","docs/a.md","docs/nested/b.md","registry.md"], [r.path for r in records])
        expected = [{"repository_id":"fixture","path":r.path,"sha256":hashlib.sha256(self.files[r.path]).hexdigest()} for r in records]
        self.assertEqual(hashlib.sha256(canonical_json(expected)).hexdigest(), corpus_digest(records))

    def test_corpus_exclusion_and_missing_required_inputs(self):
        records = self.inventory(exclude=("docs/nested",))
        self.assertNotIn("docs/nested/b.md", [r.path for r in records])
        for args in ({"required_files":("absent",)}, {"exclude":("config.toml",)},
                     {"source_roots":("absent",)}, {"source_roots":("docs","docs/nested")},
                     {"source_roots":"docs"}, {"exclude":("docs",)}):
            with self.subTest(args=args), self.assertRaises(ValueError): self.inventory(**args)

    def test_corpus_identity_ignores_dirty_worktree_and_commit_metadata(self):
        before = corpus_digest(self.inventory())
        (self.root/"config.toml").write_bytes(b"dirty")
        self.assertEqual(before, corpus_digest(self.inventory()))
        changed = dict(self.files)
        changed["docs/new.md"] = b"new"
        commit = commit_files(self.repo, changed)
        self.assertNotEqual(before, corpus_digest(self.inventory(commit=commit)))

    def test_duplicate_corpus_identity_fails(self):
        record = CorpusInput("fixture","docs/a.md","0"*64)
        with self.assertRaises(ValueError): corpus_digest([record,record])


if __name__ == "__main__": unittest.main()
