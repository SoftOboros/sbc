from dataclasses import FrozenInstanceError
import unittest
from unittest.mock import patch

from dulwich.index import build_index_from_tree
import test_provenance_integration as single_fixtures
import test_mounted_corpus as mounted_fixtures
from test_provenance_inputs import commit_files


def checkout(repo, root, commit):
    repo.refs[b"refs/heads/main"] = commit.encode()
    repo.refs.set_symbolic_ref(b"HEAD",b"refs/heads/main")
    build_index_from_tree(str(root),repo.index_path(),repo.object_store,repo.object_store[commit.encode()].tree)


class AdmissionTests(unittest.TestCase):
    def setUp(self):
        single_fixtures.ProvenanceIntegrationTests.setUp(self)
        checkout(self.source_repo,self.source_root,self.publication["source_commit"])

    def test_clean_source_admitted_with_fixed_provenance(self):
        before = {p.relative_to(self.source_root).as_posix():p.read_bytes()
                  for p in self.source_root.rglob("*") if p.is_file() and ".git" not in p.parts}
        admitted = self.verifier.admit_source()
        self.assertEqual(self.publication["source_commit"],admitted.source_commit)
        self.assertEqual(self.corpus,admitted.provenance.corpus_sha256)
        self.assertTrue(admitted.checkout.clean)
        with self.assertRaises(FrozenInstanceError): admitted.source_commit = "0"*40
        after = {p.relative_to(self.source_root).as_posix():p.read_bytes()
                 for p in self.source_root.rglob("*") if p.is_file() and ".git" not in p.parts}
        self.assertEqual(before,after)

    def test_dirty_admission_rejected_but_retained_integrity_still_valid(self):
        (self.source_root/"docs/todo/spec.md").write_bytes(b"dirty")
        with self.assertRaises(ValueError): self.verifier.admit_source()
        self.assertNotIsInstance(self.validator.validate(self.publication,self.bundle,
            self.publication_profile()),dict)

    def publication_profile(self):
        from test_provenance_integration import sha
        return sha(self.profile)

    def test_clean_checkout_with_changed_profile_rejected(self):
        source = commit_files(self.source_repo,dict(self.source_files,**{"profile.json":b"changed"}))
        checkout(self.source_repo,self.source_root,source)
        with self.assertRaises(ValueError): self.verifier.admit_source()

    def test_worktree_change_during_provenance_checks_rejected(self):
        original = self.verifier._verify_source
        def changed(source):
            proof = original(source)
            (self.source_root/"docs/todo/spec.md").write_bytes(b"concurrent edit")
            return proof
        with patch.object(self.verifier,"_verify_source",side_effect=changed):
            with self.assertRaises(ValueError): self.verifier.admit_source()

    def test_empty_root_removed_after_host_construction_rejects(self):
        files = {p:b for p,b in self.source_files.items() if p != 'docs/todo/spec.md'}
        (self.source_root/'docs/todo/spec.md').unlink()
        commit = commit_files(self.source_repo,files)
        checkout(self.source_repo,self.source_root,commit)
        self.assertTrue(self.verifier.admit_source().checkout.clean)
        (self.source_root/'docs/todo').rmdir()
        with self.assertRaisesRegex(ValueError,'Missing source directory'):
            self.verifier.admit_source()

    def test_checkout_at_other_commit_is_rejected(self):
        other = commit_files(self.source_repo,{"other":b"other"})
        self.source_repo.refs[b"HEAD"] = other.encode()
        # HEAD was symbolic: restore configured branch and detach at the other pin.
        self.source_repo.refs[b"refs/heads/main"] = self.publication["source_commit"].encode()
        self.source_repo.refs.remove_if_equals(b"HEAD",None)
        self.source_repo.refs[b"HEAD"] = other.encode()
        self.assertEqual(self.publication["source_commit"],self.reader.resolve_commit("refs/heads/main"))
        self.assertEqual(other,self.reader.resolve_commit("HEAD"))
        with self.assertRaises(ValueError): self.verifier.admit_source()


class MountedAdmissionTests(unittest.TestCase):
    def setUp(self):
        mounted_fixtures.MountedProvenanceTests.setUp(self)
        checkout(self.child_repo,self.child_reader.checkout_path,self.child_commit)
        checkout(self.source_repo,self.source_root,self.publication["source_commit"])

    def test_clean_registered_child_admitted(self):
        admitted = self.verifier.admit_source()
        self.assertTrue(admitted.checkout.clean)
        self.assertEqual(self.child_commit,admitted.checkout.pins[0].child_commit)

    def test_dirty_child_rejects_admission(self):
        (self.child_reader.checkout_path/"note.md").write_bytes(b"dirty child")
        with self.assertRaises(ValueError): self.verifier.admit_source()


if __name__ == "__main__": unittest.main()
