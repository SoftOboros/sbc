from contextlib import ExitStack
from pathlib import Path
import unittest
from unittest.mock import patch

from sbc_tools.git_reader import GitCommitReader
from sbc_tools.observed_mounts import collect_mount_context
from sbc_tools.registered_readers import RegisteredCheckoutReaders
import test_checkout_tree as fixtures


class RegisteredReaderTests(unittest.TestCase):
    setUp = fixtures.CheckoutTreeTests.setUp

    def collect(self, readers):
        return collect_mount_context(root_repository_id='root', root_ref='HEAD',
            mounts=(('child', 'child'), ('child/inner', 'leaf')), source_roots=('child',),
            readers=readers, checkout_root=self.root)

    def test_registration_opens_nothing_and_lookup_is_cached_and_closed(self):
        opened, closed = [], []
        def factory(path):
            reader = GitCommitReader(path)
            opened.append(reader)
            return reader
        original = GitCommitReader.close
        def close(reader):
            closed.append(reader)
            original(reader)
        with patch.object(GitCommitReader, 'close', close), ExitStack() as stack:
            readers = RegisteredCheckoutReaders(self.paths, stack, reader_factory=factory)
            self.assertEqual([], opened)
            self.assertEqual(set(self.paths), set(readers))
            self.assertIn('root', readers)
            self.assertIs(readers['root'], readers['root'])
            self.assertEqual(1, len(opened))
        self.assertEqual(opened, closed)

    def test_missing_child_blocks_descendant_acquisition(self):
        opened = []
        from dulwich.errors import NotGitRepository
        def factory(path):
            opened.append(Path(path))
            if Path(path) == self.paths['child']:
                raise NotGitRepository(path)
            if Path(path) == self.paths['leaf']:
                raise AssertionError('Blocked descendant opened')
            return GitCommitReader(path)
        with ExitStack() as stack:
            result = self.collect(RegisteredCheckoutReaders(self.paths, stack, reader_factory=factory))
        self.assertEqual([self.paths['root'], self.paths['child']], opened)
        states = {p.repository_id: p.availability for p in result.participants}
        self.assertEqual('missing_checkout', states['child'])
        self.assertEqual('blocked_by_ancestor', states['leaf'])

    def test_unavailable_parent_history_blocks_descendant_acquisition(self):
        self.repos['child'].refs[b'HEAD'] = b'0' * 40
        opened = []
        def factory(path):
            opened.append(Path(path))
            self.assertNotEqual(self.paths['leaf'], Path(path))
            return GitCommitReader(path)
        with ExitStack() as stack:
            result = self.collect(RegisteredCheckoutReaders(self.paths, stack, reader_factory=factory))
        self.assertEqual('unavailable_history', result.participants[0].availability)
        self.assertEqual('blocked_by_ancestor', result.participants[1].availability)

    def test_unselected_registration_and_missing_path_not_opened(self):
        with ExitStack() as stack:
            readers = RegisteredCheckoutReaders(dict(self.paths, absent=self.root / 'absent'), stack,
                reader_factory=lambda p: (_ for _ in ()).throw(AssertionError('Opened')))
            self.assertNotIn('unregistered', readers)
            self.assertNotIn('absent', readers)

    def test_linked_path_rejects_before_repository_open(self):
        with ExitStack() as stack, patch('sbc_tools.registered_readers._ordinary_directory',
                side_effect=ValueError('Linked path')):
            readers = RegisteredCheckoutReaders(self.paths, stack,
                reader_factory=lambda p: (_ for _ in ()).throw(AssertionError('Opened')))
            with self.assertRaises(ValueError): readers['child']
