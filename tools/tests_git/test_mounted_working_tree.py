import json
import unittest
from unittest.mock import patch

from dulwich.index import build_index_from_tree
from dulwich.objects import Tree
from sbc_tools.corpus import corpus_digest
from sbc_tools.mounted_working_tree import capture_mounted_working_tree, AggregateObservationUnavailable
import sbc_tools.mounted_working_tree as aggregate
from sbc_tools.observation_sets import observation_set_bytes
import test_checkout_tree as fixtures
from test_provenance_inputs import commit_files
from test_refs_mounts import commit_tree


class MountedWorkingTreeTests(unittest.TestCase):
    setUp = fixtures.CheckoutTreeTests.setUp

    def capture(self, **overrides):
        args = dict(repository_id='root', repository_root=self.root, root_ref='HEAD',
                    readers=self.readers, mounts=(('child', 'child'), ('child/inner', 'leaf')),
                    source_roots=('child',), required_files=())
        args.update(overrides)
        return capture_mounted_working_tree(**args)

    def test_clean_capture_preserves_ownership_and_immutable_bytes(self):
        result = self.capture()
        self.assertEqual([('leaf', 'spec.md')], [(r.repository_id, r.path) for r in result.records])
        self.assertEqual({'child/inner/spec.md': b'leaf\n'}, result.files)
        value = json.loads(result.observation)
        self.assertTrue(value['complete'])
        self.assertEqual(result.observation, observation_set_bytes(value))
        self.assertEqual(['clean'] * 3, [p['checkout_state'] for p in value['participants']])
        with self.assertRaises(TypeError):
            result.files['child/inner/spec.md'] = b'changed'
        (self.paths['leaf'] / 'spec.md').write_bytes(b'changed')
        self.assertEqual(b'leaf\n', result.files['child/inner/spec.md'])

    def test_dirty_child_keeps_parent_clean_and_records_observed_bytes(self):
        (self.paths['leaf'] / 'spec.md').write_bytes(b'dirty')
        result = self.capture()
        states = {p['repository_id']: p['checkout_state'] for p in json.loads(result.observation)['participants']}
        self.assertEqual({'root': 'clean', 'child': 'clean', 'leaf': 'dirty'}, states)
        self.assertEqual(b'dirty', result.files['child/inner/spec.md'])

    def test_divergent_nested_parent_uses_observed_context(self):
        new_leaf = commit_files(self.repos['leaf'], {'spec.md': b'new'})
        tree = Tree()
        tree.add(b'inner', 0o160000, new_leaf.encode())
        new_child = commit_tree(self.repos['child'], tree)
        for owner, commit in (('leaf', new_leaf), ('child', new_child)):
            repo = self.repos[owner]
            repo.refs[b'HEAD'] = commit.encode()
            build_index_from_tree(str(self.paths[owner]), repo.index_path(), repo.object_store,
                                  repo.object_store[commit.encode()].tree)
        result = self.capture()
        value = json.loads(result.observation)
        inner, outer = value['relations']
        self.assertEqual(new_child, inner['parent_commit'])
        self.assertEqual(new_leaf, inner['recorded_child_commit'])
        self.assertEqual('match', inner['pin_state'])
        self.assertEqual((self.child, 'mismatch'), (outer['recorded_child_commit'], outer['pin_state']))
        self.assertEqual('dirty', value['participants'][-1]['checkout_state'])
        self.assertEqual(b'new', result.files['child/inner/spec.md'])

    def test_missing_child_blocks_descendants_without_partial_corpus(self):
        with self.assertRaises(AggregateObservationUnavailable) as raised:
            self.capture(readers={'root': self.readers['root'], 'leaf': object()})
        states = {p.repository_id: p.availability for p in raised.exception.context.participants}
        self.assertEqual('missing_checkout', states['child'])
        self.assertEqual('blocked_by_ancestor', states['leaf'])
        self.assertFalse(hasattr(raised.exception, 'files'))

    def test_missing_physical_checkout_blocks_descendants_before_reads(self):
        from sbc_tools.local_checkout import verify_checkout_location
        def verify(reader, path):
            if reader is self.readers['child']:
                raise FileNotFoundError('checkout removed')
            return verify_checkout_location(reader, path)
        with patch('sbc_tools.local_checkout.verify_checkout_location', verify), patch.object(
                self.readers['leaf'], 'resolve_commit', side_effect=AssertionError('blocked descendant')):
            with self.assertRaises(AggregateObservationUnavailable) as raised:
                self.capture()
        self.assertEqual('missing_checkout', raised.exception.context.participants[0].availability)
        self.assertEqual('blocked_by_ancestor', raised.exception.context.participants[1].availability)

    def test_content_change_after_capture_rejects_aggregate(self):
        original = aggregate._read_regular
        def changed(path, metadata):
            data = original(path, metadata)
            path.write_bytes(b'changed')
            return data
        with patch.object(aggregate, '_read_regular', changed):
            with self.assertRaises(AggregateObservationUnavailable):
                self.capture()

    def test_ref_change_during_capture_rejects_aggregate(self):
        original = aggregate._read_regular
        other = commit_files(self.repos['root'], {'other': b'new'})
        def changed(path, metadata):
            data = original(path, metadata)
            self.repos['root'].refs[b'HEAD'] = other.encode()
            return data
        with patch.object(aggregate, '_read_regular', changed):
            with self.assertRaises(AggregateObservationUnavailable):
                self.capture()

    def test_required_input_and_excluded_file_keep_explicit_ownership(self):
        (self.root / 'config.json').write_bytes(b'{}')
        (self.paths['leaf'] / 'omit.md').write_bytes(b'excluded')
        result = self.capture(required_files=('config.json',), exclude=('child/inner/omit.md',))
        self.assertEqual({'config.json', 'child/inner/spec.md'}, set(result.files))
        self.assertIn(('root', 'config.json'), [(r.repository_id, r.path) for r in result.records])
        with self.assertRaises(ValueError):
            self.capture(required_files=('config.json',), exclude=('config.json',))

    def test_order_does_not_change_observation_or_corpus_identity(self):
        first = self.capture()
        second = self.capture(mounts=(('child/inner', 'leaf'), ('child', 'child')),
                              readers=dict(reversed(list(self.readers.items()))))
        self.assertEqual(first.observation, second.observation)
        self.assertEqual(corpus_digest(first.records), corpus_digest(second.records))

    def test_same_bytes_with_new_head_change_context_not_corpus(self):
        first = self.capture()
        repo = self.repos['leaf']
        original = repo.object_store[self.leaf.encode()]
        from dulwich.objects import Commit
        new = Commit.from_raw_string(Commit.type_num, original.as_raw_string())
        new.message = b'different context\n'
        repo.object_store.add_object(new)
        repo.refs[b'HEAD'] = new.id
        second = self.capture()
        self.assertEqual(corpus_digest(first.records), corpus_digest(second.records))
        self.assertNotEqual(json.loads(first.observation)['selection_sha256'],
                            json.loads(second.observation)['selection_sha256'])

    def test_wrong_physical_location_rejects_before_object_access(self):
        with patch.object(self.readers['leaf'], 'resolve_commit', side_effect=AssertionError('out of scope')):
            with self.assertRaises(ValueError):
                self.capture(readers=dict(self.readers, child=self.readers['leaf']))

    def test_missing_required_file_and_unregistered_mount_reject(self):
        for overrides in (dict(required_files=('absent',)), dict(mounts=(('child', 'child'),))):
            with self.subTest(overrides=overrides), self.assertRaises((ValueError, OSError)):
                self.capture(**overrides)
