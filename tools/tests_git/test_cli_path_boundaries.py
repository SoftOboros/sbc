"""Command-level path witnesses; injected metadata is not a native-link proof."""
import builtins
from contextlib import contextmanager
from dataclasses import replace
import hashlib
import io
import os
from pathlib import Path
import stat
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import test_console_host as committed
import test_working_cli as single
import test_mounted_working_cli as mounted


class CLIPathBoundaryTests(unittest.TestCase):
    def fixture(self, kind):
        cls = {'committed': committed.ConsoleHostTests, 'single': single.WorkingCLITests,
               'mounted': mounted.MountedWorkingCLITests}[kind]
        value = cls()
        self.addCleanup(value.doCleanups)
        value.setUp()
        return value

    def configure(self, fixture, raw):
        fixture.registration = replace(fixture.registration, config_bytes=raw)
        fixture.registration.configuration_file.write_bytes(raw)
        if hasattr(fixture, 'binding'):
            fixture.binding['config_sha256'] = hashlib.sha256(raw).hexdigest()
            fixture.write()
        else:
            fixture.write_binding()

    def snapshot(self, fixture):
        # Include Git metadata, inputs, host binding and any existing output.
        return {p.relative_to(fixture.root).as_posix(): p.read_bytes()
                for p in fixture.root.rglob('*') if p.is_file() and not p.is_symlink()}

    @contextmanager
    def guarded(self, targets, *, link=None, attributes=0, mode=0):
        attempted = []
        original_lstat, original_resolve = Path.lstat, Path.resolve
        def under(path, target):
            return path == target or target in path.parents
        def reject(path, operation):
            if any(under(path, target) for target in targets):
                attempted.append((str(path), operation))
                raise AssertionError('Out-of-scope ' + operation)
        def metadata(path, *args, **kwargs):
            if path == link:
                return SimpleNamespace(st_mode=mode, st_file_attributes=attributes)
            if link is not None and link in path.parents:
                attempted.append((str(path), 'descendant metadata'))
                raise AssertionError('Descendant metadata accessed through link')
            return original_lstat(path, *args, **kwargs)
        def resolve(path, *args, **kwargs):
            reject(path, 'resolution')
            return original_resolve(path, *args, **kwargs)
        def opening(original):
            def call(path, *args, **kwargs):
                if isinstance(path, (str, bytes, os.PathLike)):
                    reject(Path(os.fsdecode(path)).absolute(), 'file open')
                return original(path, *args, **kwargs)
            return call
        with patch.object(Path, 'lstat', metadata), patch.object(Path, 'resolve', resolve), \
             patch('builtins.open', opening(builtins.open)), patch('io.open', opening(io.open)), \
             patch('os.open', opening(os.open)):
            yield attempted

    def test_link_and_reparse_matrix_rejects_without_reads_or_mutations(self):
        for kind in ('committed', 'single', 'mounted'):
            fixture = self.fixture(kind)
            original = fixture.registration.config_bytes
            roles = [('source', 'docs/todo', original),
                     ('registry', 'registry.md', original.replace(b'registry_paths = []',
                                                                  b'registry_paths = ["registry.md"]')),
                     ('authority', 'authority.json', original),
                     ('output', 'projection', original)]
            if kind == 'mounted':
                roles.append(('mount', 'docs/todo/child', original))
            else:
                nested = fixture.source_root / 'docs/todo/nested'
                nested.mkdir()
                roles.append(('nested_source', 'docs/todo/nested', original.replace(
                    b'source_roots = ["docs/todo"]', b'source_roots = ["docs/todo/nested"]')))
            for role, relative, raw in roles:
                self.configure(fixture, raw)
                before = self.snapshot(fixture)
                target = fixture.source_root / relative
                for attributes, mode in ((0, stat.S_IFLNK), (0x400, stat.S_IFDIR)):
                    for command in ('scan', 'check'):
                        with self.subTest(kind=kind, role=role, attributes=attributes, command=command):
                            with self.guarded((target,), link=target, attributes=attributes, mode=mode) as attempted:
                                code, result = fixture.invoke(command)
                            self.assertEqual([], attempted)
                            self.assertEqual((2, 'invalid_configuration'), (code, result['error']['code']))
                            self.assertIsNone(result['selection'])
                            self.assertEqual(before, self.snapshot(fixture))

    def test_escaping_scope_matrix_rejects_without_reads_or_mutations(self):
        for kind in ('committed', 'single', 'mounted'):
            fixture = self.fixture(kind)
            outside = fixture.root / 'outside'
            outside.mkdir()
            (outside / 'secret.md').write_bytes(b'not selected')
            raw = fixture.registration.config_bytes.replace(b'source_roots = ["docs/todo"]',
                                                            b'source_roots = ["../outside"]')
            self.configure(fixture, raw)
            before = self.snapshot(fixture)
            for command in ('scan', 'check'):
                with self.subTest(kind=kind, command=command):
                    with self.guarded((outside,)) as attempted:
                        code, result = fixture.invoke(command)
                    self.assertEqual([], attempted)
                    self.assertEqual((2, 'invalid_configuration'), (code, result['error']['code']))
                    self.assertEqual(before, self.snapshot(fixture))

    def test_native_directory_symlink_rejects_without_target_reads(self):
        fixture = self.fixture('mounted')
        outside = fixture.root / 'native-target'
        outside.mkdir()
        (outside / 'secret.md').write_bytes(b'not selected')
        link = fixture.source_root / 'linked-specs'
        try:
            link.symlink_to(outside, target_is_directory=True)
        except OSError as exc:
            self.skipTest('Native directory symlink unavailable: ' + str(exc.errno))
        raw = fixture.registration.config_bytes.replace(b'source_roots = ["docs/todo"]',
                                                        b'source_roots = ["linked-specs"]')
        self.configure(fixture, raw)
        # Snapshot outside the symlink; recursive fixture traversal may follow links.
        source_before = fixture.registration.configuration_file.read_bytes()
        target_before = (outside / 'secret.md').read_bytes()
        with self.guarded((outside, link)) as attempted:
            code, result = fixture.invoke('scan')
        self.assertEqual([], attempted)
        self.assertEqual((2, 'invalid_configuration'), (code, result['error']['code']))
        self.assertEqual(source_before, fixture.registration.configuration_file.read_bytes())
        self.assertEqual(target_before, (outside / 'secret.md').read_bytes())
        self.assertFalse((fixture.source_root / 'projection').exists())
