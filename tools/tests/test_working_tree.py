from dataclasses import replace
from pathlib import Path
import stat
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import test_patch_configuration as fixtures
from sbc_tools.working_tree import capture_working_tree
from sbc_tools import working_tree


class WorkingTreeTests(unittest.TestCase):
    def setUp(self):
        fixtures.ConfigurationTests.setUp(self)
        self.raw = self.raw.replace('mode = "committed"','mode = "working-tree"')
        self.config = fixtures.ConfigurationTests.verify(self)

    def capture(self):
        return capture_working_tree(self.config,required_files=())

    def test_empty_root_and_immutable_observed_bytes(self):
        empty = self.capture()
        self.assertEqual({'authority.json','registry.md'},set(empty.files))
        (self.root/'docs/note.md').write_bytes(b'first')
        observed = self.capture()
        (self.root/'docs/note.md').write_bytes(b'second')
        self.assertEqual(b'first',observed.files['docs/note.md'])
        self.assertNotEqual(observed.records,self.capture().records)
        with self.assertRaises(TypeError): observed.files['new'] = b'value'
        self.assertFalse(hasattr(observed,'source_commit'))

    def test_missing_root_and_nested_repository_reject(self):
        (self.root/'docs/nested/.git').write_bytes(b'gitdir: elsewhere')
        with self.assertRaisesRegex(ValueError,'Nested repository'): self.capture()
        (self.root/'docs/nested/.git').unlink()
        (self.root/'docs/nested').rmdir()
        (self.root/'docs').rmdir()
        with self.assertRaises(FileNotFoundError): self.capture()

    def test_link_rejected_before_content_read(self):
        original = Path.lstat
        target = self.root/'docs/nested'
        def metadata(path,*args,**kwargs):
            if path == target:
                return SimpleNamespace(st_mode=stat.S_IFDIR,st_file_attributes=0x400)
            return original(path,*args,**kwargs)
        with patch.object(Path,'lstat',metadata), patch.object(working_tree,'_read_regular',side_effect=AssertionError('Content read')):
            with self.assertRaisesRegex(ValueError,'Linked configured path'): self.capture()

    def test_change_between_passes_rejects(self):
        note = self.root/'docs/note.md'
        note.write_bytes(b'before')
        original = working_tree._read_regular
        def read(path,metadata):
            data = original(path,metadata)
            if path == note and data == b'before': note.write_bytes(b'after')
            return data
        with patch.object(working_tree,'_read_regular',read):
            with self.assertRaisesRegex(ValueError,'changed during capture'): self.capture()

    def test_excluded_subtree_is_not_read(self):
        (self.root/'docs/nested/private.md').write_bytes(b'excluded')
        self.config = replace(self.config,values=dict(self.config.values,exclude=('docs/nested',)))
        original = working_tree._read_regular
        def read(path,metadata):
            if 'nested' in path.parts: raise AssertionError('Excluded content read')
            return original(path,metadata)
        with patch.object(working_tree,'_read_regular',read):
            self.assertNotIn('docs/nested/private.md',self.capture().files)

    def test_committed_mode_mounts_and_excluded_authority_reject(self):
        original = self.config
        for change in ({'mode':'committed'}, {'submodules':(('child','child'),)},
                       {'exclude':('authority.json',)}):
            self.config = replace(original,values=dict(original.values,**change))
            with self.assertRaises(ValueError): self.capture()

    def test_replaced_file_identity_rejects_before_read(self):
        path = self.root/'registry.md'
        stale = path.lstat()
        path.unlink()
        path.write_bytes(b'replacement')
        with self.assertRaisesRegex(ValueError,'changed before read'):
            working_tree._read_regular(path,stale)
