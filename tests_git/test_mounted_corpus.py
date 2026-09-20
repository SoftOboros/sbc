from pathlib import Path
import tempfile
import unittest

from dulwich.repo import Repo
from sbc_tools.canonical import canonical_json
from sbc_tools.corpus import inventory_mounted_corpus
from sbc_tools.git_reader import GitCommitReader
from sbc_tools.provenance import CommittedProvenanceVerifier
from sbc_tools.store import SQLiteSnapshotStore
import test_checkout_tree as tree_fixtures
import test_provenance_integration as integration_fixtures
from test_provenance_inputs import commit_files
from test_provenance_integration import publication_identity,sha


class MountedCorpusTests(unittest.TestCase):
    def setUp(self):
        tree_fixtures.CheckoutTreeTests.setUp(self)

    def inventory(self, **kwargs):
        args = dict(repository_id="root",commit=self.parent,readers=self.readers,
            mounts=(("child","child"),("child/inner","leaf")),source_roots=("child",),required_files=())
        args.update(kwargs)
        return inventory_mounted_corpus(**args)

    def test_nested_owner_paths_and_parent_pins_preserved(self):
        result = self.inventory()
        self.assertEqual([("leaf","spec.md")],[(r.repository_id,r.path) for r in result.records])
        self.assertEqual(self.child,result.pins[1].parent_commit)
        self.assertEqual(self.leaf,result.pins[1].child_commit)

    def test_uses_pinned_history_despite_changed_child_head(self):
        before = self.inventory()
        other = commit_files(self.repos["leaf"],{"spec.md":b"changed"})
        self.repos["leaf"].refs[b"HEAD"] = other.encode()
        (self.paths["leaf"]/"spec.md").write_bytes(b"dirty")
        self.assertEqual(before,self.inventory())

    def test_excluded_child_not_read_and_required_file_cannot_be_hidden(self):
        readers = {k:v for k,v in self.readers.items() if k != "leaf"}
        self.assertEqual((),self.inventory(exclude=("child/inner",),readers=readers).records)
        with self.assertRaises(ValueError):
            self.inventory(exclude=("child/inner",),required_files=("child/inner/spec.md",))

    def test_missing_required_child_file_and_registration_fail(self):
        for args in ({"required_files":("child/inner/absent",)}, {"mounts":(("child","child"),)},
                     {"source_roots":("child/absent",)}):
            with self.subTest(args=args),self.assertRaises(ValueError): self.inventory(**args)


class MountedProvenanceTests(unittest.TestCase):
    def setUp(self):
        integration_fixtures.ProvenanceIntegrationTests.setUp(self)
        path = self.source_root/"docs/todo/vendor"
        path.mkdir(parents=True)
        self.child_repo = Repo.init(str(path))
        self.addCleanup(self.child_repo.close)
        self.child_commit = commit_files(self.child_repo,{"note.md":b"child source\n"})
        self.child_reader = GitCommitReader(str(path))
        self.addCleanup(self.child_reader.close)
        self.config = self.config.replace(b"submodules = []",b'submodules = [{path="docs/todo/vendor",repository_id="child"}]')
        self.source_files["sbc.toml"] = self.config
        (self.source_root/"sbc.toml").write_bytes(self.config)
        links = {"docs/todo/vendor":self.child_commit}
        source = commit_files(self.source_repo,self.source_files,links)
        projected = dict(self.source_files,**{"projection/"+p:b for p,b in self.bundle.items()})
        projection = commit_files(self.source_repo,projected,links)
        expected = {r:(r+" updated\n").encode() for r in ("AGENTS.md","CLAUDE.md","README.md")}
        self.verifier = CommittedProvenanceVerifier(repository_id="source",reader=self.reader,
            config_path="sbc.toml",config_bytes=self.config,tracked_branch="main",profile_path="profile.json",
            profile_sha256=sha(self.profile),patch_path="support.patch",approved_authority_sha256=sha(self.authority_bytes),
            approved_support_sha256={r:sha(b) for r,b in expected.items()},authority_readers={"fixture":self.authority_reader},
            source_readers={"child":self.child_reader})
        records = [{"repository_id":"source","path":p,"sha256":sha(b)} for p,b in self.source_files.items()]
        records.append(dict(repository_id="child",path="note.md",sha256=sha(b"child source\n")))
        for group in ("authority_inputs","producer_inputs","support_inputs"):
            for row in self.manifest[group]:
                item = row["files"][0]
                records.append(dict(repository_id="fixture",path=item["path"],sha256=item["sha256"]))
        corpus = sha(canonical_json(sorted(records,key=lambda r:(r["repository_id"],r["path"]))))
        snapshot = dict(authority_manifest_sha256=sha(self.authority_bytes),corpus_sha256=corpus,
                        files=[{"path":p,"sha256":sha(b)} for p,b in sorted(self.bundle.items())])
        self.publication = publication_identity(dict(self.publication,source_commit=source,projection_commit=projection,
                                                     snapshot_id=sha(canonical_json(snapshot))))
        self.validator = self.verifier.bundle_validator()

    def validate(self, publication=None):
        return self.validator.validate(publication or self.publication,self.bundle,sha(self.profile))

    def test_child_corpus_through_sqlite(self):
        candidate = self.validate()
        self.assertNotIsInstance(candidate,dict)
        with tempfile.TemporaryDirectory() as temp:
            store = SQLiteSnapshotStore(Path(temp)/"store.db",self.validator)
            self.assertEqual(1,store.publish(candidate,0,"child")["generation"])
            self.assertEqual((self.publication,1),store.select("source",{"kind":"current"}))

    def test_changed_parent_child_pin_changes_corpus_identity(self):
        other = commit_files(self.child_repo,{"note.md":b"changed"})
        source = commit_files(self.source_repo,self.source_files,{"docs/todo/vendor":other})
        p = publication_identity(dict(self.publication,source_commit=source))
        self.assertEqual("invalid_bundle",self.validate(p)["code"])

    def test_missing_child_objects_reject(self):
        oid = self.child_commit
        (Path(self.child_repo.controldir())/"objects"/oid[:2]/oid[2:]).unlink()
        self.assertEqual("invalid_bundle",self.validate()["code"])


if __name__ == "__main__": unittest.main()
