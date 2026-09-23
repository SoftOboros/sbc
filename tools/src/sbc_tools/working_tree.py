"""Explicit single-repository working-tree capture; never committed evidence."""
from dataclasses import dataclass
import hashlib
import os
from pathlib import Path
import stat
from types import MappingProxyType

from .configuration import ResolvedConfiguration, _path, _paths, _reject_linked_components
from .corpus import CorpusInput


@dataclass(frozen=True)
class ObservedCorpus:
    repository_id: str
    records: tuple
    files: object


def _signature(value):
    return (value.st_dev,value.st_ino,value.st_mode,value.st_size,value.st_mtime_ns,value.st_ctime_ns)


def _read_regular(path, expected):
    flags = os.O_RDONLY | getattr(os,'O_BINARY',0) | getattr(os,'O_NOFOLLOW',0)
    descriptor = os.open(path,flags)
    with os.fdopen(descriptor,'rb') as stream:
        opened = os.fstat(stream.fileno())
        # Windows path and handle stat may disagree on ctime; compare it only
        # between observations of the same open handle below.
        if not stat.S_ISREG(opened.st_mode) or _signature(opened)[:-1] != _signature(expected)[:-1]:
            raise ValueError('Observed file changed before read')
        data = stream.read()
        if _signature(os.fstat(stream.fileno())) != _signature(opened):
            raise ValueError('Observed file changed during read')
    return data


def capture_working_tree(configuration, *, required_files):
    """Capture explicit configured scopes twice and reject observed changes.

    Host validates configuration and authority separately. This initial capture
    rejects submodule configuration and nested repositories, never discovering
    or following them. Repeated reads detect changes; they are not an atomic
    filesystem snapshot or protection against a hostile concurrent writer.
    """
    if not isinstance(configuration,ResolvedConfiguration):
        raise ValueError('Validated configuration required')
    value, root = configuration.values, configuration.repository_root
    if value['mode'] != 'working-tree' or value['submodules']:
        raise ValueError('Single-repository working-tree configuration required')
    required = _paths(list(required_files))
    required = tuple(sorted(set((*required,value['authority_manifest'],*value['registry_paths']))))
    excluded = value['exclude']
    def omitted(path):
        return any(path == e or path.startswith(e+'/') for e in excluded)
    if any(omitted(path) for path in required):
        raise ValueError('Required observation input excluded')
    def capture():
        metadata = root.lstat()
        if (not stat.S_ISDIR(metadata.st_mode)
                or getattr(metadata,'st_file_attributes',0) & 0x400):
            raise ValueError('Repository root is not an ordinary directory')
        files = {}
        def visit(relative, directory_required=False):
            _path(relative)
            if omitted(relative):
                return
            _reject_linked_components(root,relative)
            path = root/relative
            metadata = path.lstat()
            if stat.S_ISDIR(metadata.st_mode):
                if not directory_required:
                    raise ValueError('Required input is not a regular file')
                entries = sorted(path.iterdir(),key=lambda p:p.name)
                if any(p.name.lower() == '.git' for p in entries):
                    raise ValueError('Nested repository requires explicit mount support')
                for entry in entries:
                    child = entry.relative_to(root).as_posix()
                    if omitted(child):
                        continue
                    _reject_linked_components(root,child)
                    visit(child,stat.S_ISDIR(entry.lstat().st_mode))
            elif stat.S_ISREG(metadata.st_mode) and not directory_required:
                files[relative] = _read_regular(path,metadata)
            else:
                raise ValueError('Unsupported observation input')
        for source in value['source_roots']:
            visit(source,True)
        for path in required:
            visit(path)
        return files
    before, after = capture(), capture()
    if before != after:
        raise ValueError('Working tree changed during capture')
    owner = value['repository_id']
    records = tuple(CorpusInput(owner,p,hashlib.sha256(b).hexdigest()) for p,b in sorted(before.items()))
    return ObservedCorpus(owner,records,MappingProxyType(before))
