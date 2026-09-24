import unittest

from dulwich.objects import Tree
from sbc_tools.observed_mounts import collect_mount_context
import test_refs_mounts as fixtures
from test_provenance_inputs import commit_files


class ObservedMountTests(unittest.TestCase):
    def setUp(self):
        fixtures.ReferenceMountTests.setUp(self)
        for name, commit in (('child', self.child), ('nested', self.nested)):
            self.repos[name].refs[b'HEAD'] = commit.encode()

    def collect(self, **overrides):
        args = dict(root_repository_id='root', root_ref='refs/heads/main',
                    mounts=(('child', 'child'), ('child/inner', 'nested')),
                    source_roots=('child/inner',), readers=self.readers)
        args.update(overrides)
        return collect_mount_context(**args)

    def test_matching_and_order_independent(self):
        result = self.collect()
        self.assertEqual(result, self.collect(mounts=(('child/inner', 'nested'), ('child', 'child'))))
        self.assertEqual(self.parent, result.root_commit)
        self.assertTrue(all(r.pin_state == 'match' for r in result.relations))
        self.assertEqual(['child', 'nested', 'root'], [p.repository_id for p in result.participants])

    def test_nested_context_follows_divergent_observed_parent(self):
        new_nested = commit_files(self.repos['nested'], {'spec.md': b'new'})
        tree = Tree()
        tree.add(b'inner', 0o160000, new_nested.encode())
        new_child = fixtures.commit_tree(self.repos['child'], tree)
        self.repos['child'].refs[b'HEAD'] = new_child.encode()
        self.repos['nested'].refs[b'HEAD'] = new_nested.encode()
        inner, outer = self.collect().relations
        self.assertEqual(('mismatch', self.child), (outer.pin_state, outer.recorded_child_commit))
        self.assertEqual(('match', new_child, new_nested),
                         (inner.pin_state, inner.parent_commit, inner.recorded_child_commit))

    def test_missing_child_blocks_descendant_without_reading_it(self):
        result = self.collect(readers={'root': self.readers['root'], 'nested': object()})
        child, nested, root = result.participants
        self.assertEqual('missing_checkout', child.availability)
        self.assertEqual('blocked_by_ancestor', nested.availability)
        self.assertIsNone(result.relations[0].parent_commit)
        self.assertEqual(self.child, result.relations[1].recorded_child_commit)

    def test_missing_pinned_history_is_not_replaced_by_observed_head(self):
        tree = Tree()
        tree.add(b'child', 0o160000, b'0' * 40)
        self.repos['root'].refs[b'refs/heads/main'] = fixtures.commit_tree(self.repos['root'], tree).encode()
        result = self.collect()
        self.assertEqual('unavailable_history', result.participants[0].availability)
        self.assertIsNone(result.participants[0].observed_head)
        self.assertEqual('blocked_by_ancestor', result.participants[1].availability)

    def test_missing_root_ref_blocks_all_descendants(self):
        result = self.collect(root_ref='refs/heads/absent')
        self.assertIsNone(result.root_commit)
        self.assertEqual(['blocked_by_ancestor', 'blocked_by_ancestor', 'unavailable_history'],
                         [p.availability for p in result.participants])

    def test_root_baseline_is_separate_from_observed_head(self):
        different = commit_files(self.repos['root'], {'other': b'content'})
        self.repos['root'].refs[b'refs/heads/other'] = different.encode()
        self.repos['root'].refs.set_symbolic_ref(b'HEAD', b'refs/heads/other')
        result = self.collect()
        self.assertEqual(self.parent, result.root_commit)
        self.assertEqual(different, result.participants[-1].observed_head)
        self.assertEqual(self.parent, result.relations[-1].parent_commit)

    def test_invalid_and_unregistered_mounts_reject(self):
        for mounts in ((), (('child/inner', 'nested'),), (('child', 'root'),),
                       (('../child', 'child'),), (('child', 'child'),),
                       (('absent', 'child'),)):
            with self.subTest(mounts=mounts), self.assertRaises(ValueError):
                self.collect(mounts=mounts)

    def test_excluded_and_unselected_readers_are_not_accessed(self):
        result = self.collect(source_roots=('child',), exclude=('child/inner',),
                              readers={'root': self.readers['root'], 'child': self.readers['child'],
                                       'nested': object()})
        self.assertEqual(['child', 'root'], [p.repository_id for p in result.participants])
        result = self.collect(source_roots=('other',), readers={'root': self.readers['root']})
        self.assertEqual((), result.relations)
