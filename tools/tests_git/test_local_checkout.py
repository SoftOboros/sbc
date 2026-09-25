from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from dulwich.index import build_index_from_tree
from dulwich.repo import Repo
from sbc_tools.git_reader import GitCommitReader
from sbc_tools.local_checkout import observe_local_checkout, verify_checkout_location
import sbc_tools.local_checkout as local
import test_checkout_tree as fixtures
from test_provenance_inputs import commit_files


class LocalCheckoutTests(unittest.TestCase):
    setUp = fixtures.CheckoutTreeTests.setUp

    def observe(self, owner='root', **overrides):
        commits = dict(root=self.parent, child=self.child, leaf=self.leaf)
        children = dict(root={'child': self.readers['child']},
                        child={'inner': self.readers['leaf']}, leaf={})
        args = dict(expected_path=self.paths[owner], child_readers=children[owner])
        args.update(overrides)
        return observe_local_checkout(self.readers[owner], commits[owner], **args)

    def test_clean_nested_checkouts(self):
        for owner in self.paths:
            result = self.observe(owner)
            self.assertEqual('clean', result.checkout_state)
            self.assertEqual(64, len(result.evidence_sha256))

    def test_dirty_child_interior_is_not_inherited(self):
        (self.paths['leaf'] / 'spec.md').write_bytes(b'dirty')
        self.assertEqual('dirty', self.observe('leaf').checkout_state)
        self.assertEqual('clean', self.observe('child').checkout_state)
        self.assertEqual('clean', self.observe().checkout_state)
        # Committed admission deliberately retains recursive clean requirements.
        self.assertFalse(fixtures.CheckoutTreeTests.observe(self).clean)

    def test_child_head_mismatch_dirties_only_immediate_parent(self):
        new = commit_files(self.repos['leaf'], {'spec.md': b'new'})
        self.repos['leaf'].refs[b'HEAD'] = new.encode()
        self.assertEqual('dirty', self.observe('child').checkout_state)
        self.assertEqual('clean', self.observe().checkout_state)

    def test_deleted_untracked_and_staged_files_are_dirty(self):
        path = self.paths['leaf'] / 'spec.md'
        path.unlink()
        self.assertEqual('dirty', self.observe('leaf').checkout_state)
        path.write_bytes(b'leaf\n')
        extra = self.paths['leaf'] / 'extra'
        extra.write_bytes(b'untracked')
        self.assertEqual('dirty', self.observe('leaf').checkout_state)
        extra.unlink()
        other = commit_files(self.repos['leaf'], {'spec.md': b'staged'})
        repo = self.repos['leaf']
        build_index_from_tree(str(self.paths['leaf']), repo.index_path(), repo.object_store,
                              repo.object_store[other.encode()].tree)
        path.write_bytes(b'leaf\n')
        self.assertEqual('dirty', self.observe('leaf').checkout_state)

    def test_missing_child_evidence_is_unknown_even_when_parent_dirty(self):
        (self.paths['root'] / 'extra').write_bytes(b'dirty')
        result = self.observe(child_readers={})
        self.assertEqual('unknown', result.checkout_state)
        self.assertIsNone(result.evidence_sha256)

    def test_identical_objects_at_wrong_location_do_not_establish_ownership(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        repo = Repo.init(temp.name)
        self.addCleanup(repo.close)
        commit = commit_files(repo, {'spec.md': b'leaf\n'})
        self.assertEqual(self.leaf, commit)
        repo.refs[b'HEAD'] = commit.encode()
        reader = GitCommitReader(temp.name)
        self.addCleanup(reader.close)
        with patch.object(reader, 'resolve_commit', side_effect=AssertionError('must not read HEAD')):
            result = self.observe('child', child_readers={'inner': reader})
        self.assertEqual('unknown', result.checkout_state)

    def test_linked_component_rejects_before_child_head_read(self):
        original = Path.lstat
        mount = self.paths['leaf']
        class ReparseDirectory:
            st_mode = 0o40755
            st_file_attributes = 0x400
        def metadata(path, *args, **kwargs):
            return ReparseDirectory() if path == mount else original(path, *args, **kwargs)
        with patch.object(Path, 'lstat', metadata), patch.object(
                self.readers['leaf'], 'resolve_commit', side_effect=AssertionError('must not read HEAD')):
            self.assertEqual('unknown', self.observe('child').checkout_state)

    def test_unregistered_nested_checkout_is_unknown(self):
        nested = self.paths['leaf'] / 'unexpected'
        nested.mkdir()
        (nested / '.git').write_bytes(b'not traversed')
        (nested / 'private').write_bytes(b'not read')
        original = local._read_regular
        def guarded(path, metadata):
            self.assertNotIn(nested, path.parents)
            return original(path, metadata)
        with patch.object(local, '_read_regular', guarded):
            self.assertEqual('unknown', self.observe('leaf').checkout_state)

    def test_dirty_content_changes_between_passes_are_unknown(self):
        path = self.paths['leaf'] / 'spec.md'
        path.write_bytes(b'dirty one')
        original = local._read_regular
        def changing(path, metadata):
            data = original(path, metadata)
            path.write_bytes(b'dirty two')
            return data
        with patch.object(local, '_read_regular', changing):
            result = self.observe('leaf')
        self.assertEqual('unknown', result.checkout_state)
        self.assertEqual('checkout_changed_during_observation', result.reason)

    def test_head_and_index_changes_are_unknown(self):
        original = local._read_regular
        for target in ('head', 'index'):
            with self.subTest(target=target):
                repo = self.repos['leaf']
                repo.refs[b'HEAD'] = self.leaf.encode()
                build_index_from_tree(str(self.paths['leaf']), repo.index_path(), repo.object_store,
                                      repo.object_store[self.leaf.encode()].tree)
                other = commit_files(repo, {'spec.md': b'other'})
                def changing(path, metadata):
                    data = original(path, metadata)
                    if target == 'head':
                        repo.refs[b'HEAD'] = other.encode()
                    else:
                        Path(repo.index_path()).write_bytes(b'changed')
                    return data
                with patch.object(local, '_read_regular', changing):
                    self.assertEqual('unknown', self.observe('leaf').checkout_state)

    def test_explicit_absolute_location_required(self):
        with self.assertRaises(ValueError):
            verify_checkout_location(self.readers['root'], Path('relative'))
