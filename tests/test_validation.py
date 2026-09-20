"""Pinned producer projections against extracted real semantic validation."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from sbc_tools.canonical import canonical_json
from sbc_tools.store import SQLiteSnapshotStore
from sbc_tools.validation import BundleValidator, VerifiedProvenance

FIXTURES = json.loads((Path(__file__).parent / "fixtures/projection-vectors.json").read_text())
PROFILE = "c"*64
CORPUS = "d"*64
AUTHORITY = "e"*64


class FixtureProvenance:
    """Synthetic stand-in for the separately required committed-source verifier."""
    def __init__(self, files):
        self.files = files
        self.calls = 0

    def verify(self, publication, files, profile_sha256):
        self.calls += 1
        if dict(files) != self.files or profile_sha256 != PROFILE:
            raise ValueError("Unexpected committed bytes")
        return VerifiedProvenance(CORPUS, AUTHORITY)


def publication(files, commit="a"):
    snapshot = {
        "authority_manifest_sha256": AUTHORITY, "corpus_sha256": CORPUS,
        "files": [{"path": p, "sha256": hashlib.sha256(files[p]).hexdigest()} for p in sorted(files)],
    }
    p = dict(repository_id="fixture", snapshot_id=hashlib.sha256(canonical_json(snapshot)).hexdigest(),
             source_commit="f"*40, projection_commit=commit*40, tracked_branch="main",
             authority_manifest_sha256=AUTHORITY)
    p["publication_id"] = hashlib.sha256(canonical_json(p)).hexdigest()
    return p


def ingest_files(case):
    """Adapt only diagnostic wire formatting; preserve all semantic payloads.

    Historical producer vectors are pretty-printed. Pinned ingestion requires
    compact diagnostic JSON and matching family byte hashes. Keep the originals
    unchanged so their rejection remains an explicit compatibility witness.
    """
    files = {p: s.encode() for p, s in case["files"].items()}
    for path in files:
        if path.startswith("diagnostics/") and not path.endswith("_manifest.json"):
            files[path] = canonical_json(json.loads(files[path]))
    manifest = json.loads(files["diagnostics/_manifest.json"])
    for descriptor in manifest["families"]:
        descriptor["sha256"] = hashlib.sha256(
            files["diagnostics/" + descriptor["filename"]]).hexdigest()
    files["diagnostics/_manifest.json"] = canonical_json(manifest)
    return files


class ValidationTests(unittest.TestCase):
    def setUp(self):
        self.files = ingest_files(FIXTURES["cases"][1])

    def validator(self, files=None, roots=("docs/todo",), verifier=None):
        return BundleValidator(source_roots=roots, profile_sha256=PROFILE,
                               provenance_verifier=verifier or FixtureProvenance(files or self.files))

    def test_original_producer_format_is_rejected(self):
        for case in FIXTURES["cases"]:
            files = {p:s.encode() for p,s in case["files"].items()}
            proof = FixtureProvenance(files)
            with self.subTest(case=case["name"]):
                result = self.validator(files, verifier=proof).validate(publication(files), files, PROFILE)
                self.assertEqual("invalid_bundle", result["code"])
                self.assertEqual(0, proof.calls)

    def test_all_vectors_with_ingest_canonical_wire_format(self):
        for case in FIXTURES["cases"]:
            files = ingest_files(case)
            with self.subTest(case=case["name"]):
                result = self.validator(files).validate(publication(files), files, PROFILE)
                self.assertNotIsInstance(result, dict, case["name"])
                self.assertEqual(files, dict(result.files()))

    def test_real_validator_store_integration_and_corrupt_rejection(self):
        validator = self.validator()
        p = publication(self.files)
        result = validator.validate(p, self.files, PROFILE)
        with tempfile.TemporaryDirectory() as temp:
            store = SQLiteSnapshotStore(Path(temp)/"store.db", validator)
            self.assertEqual(1, store.publish(result, 0, "first")["generation"])
            self.assertEqual(self.files["index/_manifest.json"],
                             store.open_view(p).projection_bytes("index/_manifest.json"))
            malformed = dict(self.files)
            malformed["diagnostics/_manifest.json"] = b"{}\n"
            rejected = validator.validate(publication(malformed,"b"), malformed, PROFILE)
            self.assertEqual("invalid_bundle", rejected["code"])
            self.assertEqual((p,1), store.select("fixture", {"kind":"current"}))

    def test_cross_projection_inconsistency_rejected_before_provenance(self):
        files = dict(self.files)
        manifest = json.loads(files["locations/_manifest.json"])
        manifest["total_records"] += 1
        files["locations/_manifest.json"] = json.dumps(manifest).encode()
        proof = FixtureProvenance(files)
        result = self.validator(files,verifier=proof).validate(publication(files),files,PROFILE)
        self.assertEqual("invalid_bundle",result["code"])
        self.assertEqual(0,proof.calls)

    def test_duplicate_json_and_extra_file_rejected(self):
        for target, value in [("index/_manifest.json",b'{"schema_version":3,"schema_version":3}'),
                              ("unlisted.json",b"{}")]:
            files = dict(self.files)
            files[target] = value
            self.assertEqual("invalid_bundle",self.validator(files).validate(publication(files),files,PROFILE)["code"])

    def test_digest_and_profile_mismatch(self):
        p = publication(self.files)
        self.assertEqual("invalid_bundle",self.validator().validate(p,self.files,"b"*64)["code"])
        p["snapshot_id"] = "0"*64
        p.pop("publication_id")
        p["publication_id"] = hashlib.sha256(canonical_json(p)).hexdigest()
        self.assertEqual("invalid_bundle",self.validator().validate(p,self.files,PROFILE)["code"])

    def test_source_roots_are_instance_scoped(self):
        good = self.validator()
        bad = self.validator(roots=("other/corpus",))
        p = publication(self.files)
        self.assertEqual("invalid_bundle",bad.validate(p,self.files,PROFILE)["code"])
        self.assertNotIsInstance(good.validate(p,self.files,PROFILE),dict)

    def test_provenance_is_required_and_fail_closed(self):
        with self.assertRaises(ValueError):
            BundleValidator(source_roots=("docs/todo",),profile_sha256=PROFILE,provenance_verifier=None)
        class MissingProof:
            def verify(self,*args):
                return None
        self.assertEqual("invalid_bundle",self.validator(verifier=MissingProof()).validate(
            publication(self.files),self.files,PROFILE)["code"])

    def test_diagnostic_family_hash_is_checked(self):
        files = dict(self.files)
        manifest = json.loads(files["diagnostics/_manifest.json"])
        manifest["families"][0]["sha256"] = "0"*64
        files["diagnostics/_manifest.json"] = canonical_json(manifest)
        proof = FixtureProvenance(files)
        self.assertEqual("invalid_bundle", self.validator(files, verifier=proof).validate(
            publication(files), files, PROFILE)["code"])
        self.assertEqual(0, proof.calls)

    def test_validated_inputs_are_copied_and_read_only(self):
        p = publication(self.files)
        result = self.validator().validate(p, self.files, PROFILE)
        original = result.files()["index/_manifest.json"]
        self.files["index/_manifest.json"] = b"{}"
        p["repository_id"] = "changed"
        self.assertEqual(original, result.files()["index/_manifest.json"])
        self.assertEqual("fixture", result.publication["repository_id"])
        with self.assertRaises(TypeError):
            result.files()["index/_manifest.json"] = b"{}"

    def test_roots_require_a_sequence_of_safe_paths(self):
        for roots in ("docs/todo", (), ("../escape",)):
            with self.subTest(roots=roots), self.assertRaises(ValueError):
                self.validator(roots=roots)


if __name__ == "__main__":
    unittest.main()
