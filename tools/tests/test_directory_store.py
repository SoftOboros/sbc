import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from sbc_tools.directory_store import DirectoryProjectionStore
from sbc_tools.projections import build_projection_files
from sbc_tools.validation import BundleValidator


class DirectoryStoreTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name).resolve()
        validator = BundleValidator(source_roots=['specs'],profile_sha256='1'*64,
                                    provenance_verifier=SimpleNamespace(verify=lambda *args:None))
        self.store = DirectoryProjectionStore(self.root,validator)
        self.first, _ = build_projection_files([],registered_prefixes=[],archives={},archive_families={})
        self.second, _ = build_projection_files([('specs/A.md','example',b'# No ID\n')],
                                                registered_prefixes=[],archives={},archive_families={})

    def test_pinned_view_survives_later_switch(self):
        original = self.store.publish(self.first)
        self.assertEqual(self.first,self.store.open_view())
        self.store.publish(self.second)
        self.assertEqual(self.second,self.store.open_view())
        self.assertEqual(self.first,original)
        with self.assertRaises(TypeError): original['extra'] = b'bad'

    def test_invalid_candidate_does_not_write_or_replace_selection(self):
        self.store.publish(self.first)
        before = sorted(p.relative_to(self.root) for p in self.root.rglob('*'))
        with self.assertRaises(Exception): self.store.publish({'index/_manifest.json':b'{}'})
        self.assertEqual(before,sorted(p.relative_to(self.root) for p in self.root.rglob('*')))
        self.assertEqual(self.first,self.store.open_view())

    def test_failed_switch_leaves_prior_selection_usable(self):
        self.store.publish(self.first)
        pointer = (self.root/'current.json').read_bytes()
        with patch('sbc_tools.directory_store.os.replace',side_effect=PermissionError('injected')):
            with self.assertRaises(OSError): self.store.publish(self.second)
        self.assertEqual(pointer,(self.root/'current.json').read_bytes())
        self.assertEqual(self.first,self.store.open_view())

    def test_interrupted_file_write_never_selects_partial_bundle(self):
        from sbc_tools import directory_store
        self.store.publish(self.first)
        original = directory_store._write_new
        writes = []
        def fail_later(path,raw):
            writes.append(path)
            if len(writes) == 2: raise OSError('injected write failure')
            return original(path,raw)
        with patch.object(directory_store,'_write_new',side_effect=fail_later):
            with self.assertRaises(OSError): self.store.publish(self.second)
        self.assertEqual(self.first,self.store.open_view())

    def test_tampered_or_unlisted_member_is_rejected_on_read(self):
        self.store.publish(self.first)
        selected = json.loads((self.root/'current.json').read_bytes())['bundle']
        content = self.root/selected/'files'
        extra = content/'extra.json'
        extra.write_bytes(b'{}')
        with self.assertRaises(ValueError): self.store.open_view()
        extra.unlink()
        (content/'index/_manifest.json').write_bytes(b'corrupt')
        with self.assertRaises(ValueError): self.store.open_view()

    def test_pointer_cannot_select_an_outside_path(self):
        from sbc_tools.canonical import canonical_json
        (self.root/'current.json').write_bytes(canonical_json({'bundle':'../outside','manifest_sha256':'0'*64}))
        with self.assertRaises(ValueError): self.store.open_view()

    def test_old_selection_remains_visible_until_switch(self):
        from sbc_tools import directory_store
        self.store.publish(self.first)
        replace = directory_store.os.replace
        def switch(source,target):
            self.assertEqual(self.first,self.store.open_view())
            replace(source,target)
            self.assertEqual(self.second,self.store.open_view())
        with patch.object(directory_store.os,'replace',side_effect=switch):
            self.store.publish(self.second)

    def test_semantic_validation_is_mandatory(self):
        with self.assertRaises(ValueError): DirectoryProjectionStore(self.root,None)

    def test_staged_byte_corruption_is_detected_before_switch(self):
        from sbc_tools import directory_store
        self.store.publish(self.first)
        original = directory_store._write_new
        def corrupt(path,raw):
            original(path,raw)
            if path.name == 'example.json': path.write_bytes(b'corrupt staged data')
        with patch.object(directory_store,'_write_new',side_effect=corrupt):
            with self.assertRaises(ValueError): self.store.publish(self.second)
        self.assertEqual(self.first,self.store.open_view())


if __name__ == '__main__': unittest.main()
