import difflib
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from dulwich.repo import Repo
from sbc_tools.authority import PATCH_ROLES
from sbc_tools.canonical import canonical_json
from sbc_tools.git_reader import GitCommitReader
from sbc_tools.provenance import CommittedProvenanceVerifier
from sbc_tools.store import SQLiteSnapshotStore
from sbc_tools.validation import ValidatedBundle
import test_provenance_inputs as provenance_fixtures
from test_provenance_inputs import commit_files


def sha(data):
    return hashlib.sha256(data).hexdigest()


def publication_identity(publication):
    result = dict(publication)
    result.pop("publication_id",None)
    result["publication_id"] = sha(canonical_json(result))
    return result


class ProvenanceIntegrationTests(unittest.TestCase):
    def setUp(self):
        # Real authority Git objects; synthetic approval pins, not production approvals.
        provenance_fixtures.ProvenanceInputTests.setUp(self)
        self.authority_reader = self.reader
        expected = {r:(r+" updated\n").encode() for r in PATCH_ROLES}
        # Base helper bytes lack final LF; use newline-terminated support inputs
        # and a new authority commit so the exact unified patch is supported.
        authority_files = dict(self.files)
        for r in PATCH_ROLES: authority_files["support_inputs/"+r] = (r+"\n").encode()
        authority_commit = commit_files(self.repo,authority_files)
        from dulwich.objects import Blob
        for rows in (self.manifest[g] for g in ("authority_inputs","producer_inputs","support_inputs")):
            for row in rows:
                row["commit"] = authority_commit
                item = row["files"][0]
                data = authority_files[item["path"]]
                item["sha256"],item["blob_oid"] = sha(data),Blob.from_string(data).id.decode()
        patch = "".join("".join(difflib.unified_diff(
            [r+"\n"],expected[r].decode().splitlines(True),fromfile="a/"+r,tofile="b/"+r)) for r in sorted(PATCH_ROLES)).encode()
        self.manifest["reviewed_patches"][0]["sha256"] = sha(patch)
        self.authority_bytes = canonical_json(self.manifest)
        self.source_root = self.root/"source_checkout"
        self.source_root.mkdir()
        repo = Repo.init(str(self.source_root))
        self.addCleanup(repo.close)
        self.source_repo = repo
        self.profile = b"Synthetic approved query profile fixture\n"
        self.config = b'''schema_version = 1
repository_id = "source"
repository_root = "."
source_roots = ["docs/todo"]
exclude = []
registry_paths = []
output_root = "projection"
tracked_ref = "refs/heads/main"
mode = "committed"
capabilities = ["scan", "check"]
authority_manifest = "authority.json"
submodules = []
'''
        self.source_files = {"sbc.toml":self.config,"authority.json":self.authority_bytes,
            "profile.json":self.profile,"support.patch":patch,"docs/todo/spec.md":b"Synthetic source\n"}
        for path,data in self.source_files.items():
            target = self.source_root/path
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(data)
        source_commit = commit_files(repo,self.source_files)
        fixtures = Path(__file__).resolve().parents[1]/"tests/fixtures/projection-wire-vectors.json"
        self.bundle = {p:s.encode() for p,s in json.loads(fixtures.read_bytes())["cases"][1]["files"].items()}
        self.projection_files = dict(self.source_files,**{"projection/"+p:b for p,b in self.bundle.items()})
        projection_commit = commit_files(repo,self.projection_files)
        repo.refs[b"HEAD"] = projection_commit.encode()
        reader = GitCommitReader(str(self.source_root))
        self.addCleanup(reader.close)
        self.reader = reader
        self.verifier = CommittedProvenanceVerifier(repository_id="source",reader=reader,
            config_path="sbc.toml",config_bytes=self.config,tracked_branch="main",
            profile_path="profile.json",profile_sha256=sha(self.profile),patch_path="support.patch",
            approved_authority_sha256=sha(self.authority_bytes),
            approved_support_sha256={r:sha(b) for r,b in expected.items()},authority_readers={"fixture":self.authority_reader})
        records = [{"repository_id":"source","path":p,"sha256":sha(b)} for p,b in self.source_files.items()]
        for group in ("authority_inputs","producer_inputs","support_inputs"):
            for row in self.manifest[group]:
                item = row["files"][0]
                records.append(dict(repository_id="fixture",path=item["path"],sha256=item["sha256"]))
        self.corpus = sha(canonical_json(sorted(records,key=lambda r:(r["repository_id"],r["path"]))))
        snapshot = {"authority_manifest_sha256":sha(self.authority_bytes),"corpus_sha256":self.corpus,
                    "files":[{"path":p,"sha256":sha(b)} for p,b in sorted(self.bundle.items())]}
        self.publication = publication_identity(dict(repository_id="source",snapshot_id=sha(canonical_json(snapshot)),
            source_commit=source_commit,projection_commit=projection_commit,tracked_branch="main",
            authority_manifest_sha256=sha(self.authority_bytes)))
        self.validator = self.verifier.bundle_validator()

    def validate(self, publication=None, files=None):
        return self.validator.validate(publication or self.publication, self.bundle if files is None else files,sha(self.profile))

    def test_full_committed_validation_and_sqlite_publication(self):
        proof = self.verifier.verify(self.publication,self.bundle,sha(self.profile))
        self.assertEqual(self.corpus,proof.corpus_sha256)
        candidate = self.validate()
        self.assertNotIsInstance(candidate,dict)
        with tempfile.TemporaryDirectory() as temp:
            store = SQLiteSnapshotStore(Path(temp)/"store.db",self.validator)
            self.assertEqual(1,store.publish(candidate,0,"first")["generation"])
            self.assertEqual(self.bundle["index/_manifest.json"],store.open_view(self.publication).projection_bytes("index/_manifest.json"))

    def test_retained_validation_independent_of_checkout(self):
        (self.source_root/"sbc.toml").write_bytes(b"dirty")
        self.source_repo.refs[b"HEAD"] = commit_files(self.source_repo,{"unrelated":b"new"}).encode()
        self.assertNotIsInstance(self.validate(),dict)

    def test_wrong_repository_branch_and_source_fail(self):
        for key,value in (("repository_id","other"),("tracked_branch","other"),("source_commit","0"*40)):
            p = publication_identity(dict(self.publication,**{key:value}))
            with self.subTest(key=key): self.assertEqual("invalid_bundle",self.validate(p)["code"])

    def test_extra_committed_projection_file_rejected(self):
        changed = dict(self.projection_files,**{"projection/extra.json":b"{}"})
        p = publication_identity(dict(self.publication,projection_commit=commit_files(self.source_repo,changed)))
        self.assertEqual("invalid_bundle",self.validate(p)["code"])

    def test_changed_committed_config_profile_and_patch_rejected(self):
        for path in ("sbc.toml","profile.json","support.patch","authority.json"):
            changed = dict(self.source_files,**{path:b"changed"})
            p = publication_identity(dict(self.publication,source_commit=commit_files(self.source_repo,changed)))
            with self.subTest(path=path): self.assertEqual("invalid_bundle",self.validate(p)["code"])

    def test_changed_source_corpus_rejected_by_snapshot_identity(self):
        changed = dict(self.source_files,**{"docs/todo/new.md":b"new"})
        p = publication_identity(dict(self.publication,source_commit=commit_files(self.source_repo,changed)))
        self.assertEqual("invalid_bundle",self.validate(p)["code"])

    def test_store_revalidates_forged_candidate_and_preserves_current(self):
        with tempfile.TemporaryDirectory() as temp:
            store = SQLiteSnapshotStore(Path(temp)/"store.db",self.validator)
            store.publish(self.validate(),0,"valid")
            changed = dict(self.source_files,**{"profile.json":b"wrong"})
            p = publication_identity(dict(self.publication,source_commit=commit_files(self.source_repo,changed)))
            forged = ValidatedBundle(p,sha(self.profile),self.bundle)
            self.assertEqual("invalid_bundle",store.publish(forged,1,"forged")["code"])
            self.assertEqual((self.publication,1),store.select("source",{"kind":"current"}))


if __name__ == "__main__": unittest.main()
