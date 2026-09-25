"""Command path witnesses with separate injected and native-link matrices."""
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
        # Include file bytes and link destinations without descending into native
        # symlinks or Windows junctions, even on Python versions without is_junction.
        result = {}
        def visit(directory):
            for path in directory.iterdir():
                info = path.lstat()
                key = path.relative_to(fixture.root).as_posix()
                if stat.S_ISLNK(info.st_mode) or getattr(info,'st_file_attributes',0) & 0x400:
                    result[key] = ('link',os.readlink(path))
                elif stat.S_ISDIR(info.st_mode):
                    visit(path)
                elif stat.S_ISREG(info.st_mode):
                    result[key] = ('file',path.read_bytes())
        visit(fixture.root)
        return result

    @contextmanager
    def guarded(self, targets, *, link=None, attributes=0, mode=0, native_link=None):
        attempted = []
        original_lstat, original_resolve = Path.lstat, Path.resolve
        def under(path, target):
            return path == target or target in path.parents
        def reject(path, operation):
            if any(under(path, target) for target in targets):
                attempted.append((str(path), operation))
                raise AssertionError('Out-of-scope ' + operation)
        def metadata(path, *args, **kwargs):
            if native_link is not None and path != native_link:
                reject(path, 'descendant metadata')
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

    def native_matrix(self, create_link, label):
        for kind in ('committed','single','mounted'):
            roles = ['source','registry','authority','output']
            if kind == 'mounted': roles.append('mount')
            for role in roles:
                fixture = self.fixture(kind)
                outside = fixture.root/'native-target'
                outside.mkdir()
                (outside/'secret.md').write_bytes(b'not selected')
                (outside/'registry.md').write_bytes(b'not selected')
                (outside/'authority.json').write_bytes(b'{}')
                link = fixture.source_root/'native-link'
                target = outside
                raw = fixture.registration.config_bytes
                if role == 'source':
                    raw = raw.replace(b'source_roots = ["docs/todo"]',b'source_roots = ["native-link"]')
                elif role == 'registry':
                    raw = raw.replace(b'registry_paths = []',b'registry_paths = ["native-link/registry.md"]')
                elif role == 'authority':
                    raw = raw.replace(b'authority_manifest = "authority.json"',
                                      b'authority_manifest = "native-link/authority.json"')
                elif role == 'output':
                    raw = raw.replace(b'output_root = "projection"',b'output_root = "native-link/projection"')
                else:
                    link = fixture.source_root/'docs/todo/child'
                    target = outside/'child'
                    link.rename(target)
                if role != 'mount': self.assertNotEqual(raw,fixture.registration.config_bytes)
                try:
                    create_link(link,target)
                except OSError as exc:
                    self.skipTest(f'{label} unavailable: errno={exc.errno}, winerror={getattr(exc,"winerror",None)}')
                # Remove only the link before the fixture's recursive cleanup.
                self.addCleanup(lambda p=link: p.unlink() if p.is_symlink() else p.rmdir())
                info = link.lstat()
                self.assertTrue(stat.S_ISLNK(info.st_mode) or getattr(info,'st_file_attributes',0) & 0x400)
                self.configure(fixture,raw)
                before = self.snapshot(fixture)
                for command in ('scan','check'):
                    with self.subTest(kind=kind,role=role,command=command,native=label):
                        with self.guarded((outside,link),native_link=link) as attempted:
                            code,result = fixture.invoke(command)
                        self.assertEqual([],attempted)
                        self.assertEqual((2,'invalid_configuration'),(code,result['error']['code']))
                        self.assertIsNone(result['selection'])
                        self.assertEqual(before,self.snapshot(fixture))

    def test_native_directory_symlink_matrix_rejects_without_reads_or_mutations(self):
        self.native_matrix(lambda link,target: link.symlink_to(target,target_is_directory=True),
                           'Native directory symlink')

    @unittest.skipUnless(os.name == 'nt','Windows junction witness')
    def test_native_junction_matrix_rejects_without_reads_or_mutations(self):
        # Standard-library Windows helper; no process, compiler or elevation.
        from _winapi import CreateJunction
        self.native_matrix(lambda link,target: CreateJunction(str(target),str(link)),
                           'Native Windows junction')
