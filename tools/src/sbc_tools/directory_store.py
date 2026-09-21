"""Local complete-bundle publication through one atomic pointer replacement.

Trusted local directory ownership is required. This is not an OS sandbox or a
power-loss durability guarantee. Unselected staging directories are retained;
garbage collection is separate work.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import stat
from types import MappingProxyType
import uuid

from .canonical import canonical_json
from .identity import copy_files


def _safe_existing(path, *, directory):
    info = path.lstat()
    if stat.S_ISLNK(info.st_mode) or getattr(info,'st_file_attributes',0) & 0x400:
        raise ValueError('Linked publication paths are unsupported')
    if directory != stat.S_ISDIR(info.st_mode) or (not directory and not stat.S_ISREG(info.st_mode)):
        raise ValueError('Invalid publication path type')


def _write_new(path, raw):
    with path.open('xb') as handle:
        handle.write(raw)
        handle.flush()
        os.fsync(handle.fileno())


def _walk_error(error):
    raise error


class DirectoryProjectionStore:
    """Host-supplied root and mandatory semantic validator; last switch wins.

    Readers load the pointer once and return copied, revalidated bytes. Retained
    views remain pinned after later switches. No operation overwrites a bundle.
    """
    def __init__(self, root, validator, *, create=False):
        if not callable(getattr(validator,'validate_files',None)):
            raise ValueError('Semantic validator required')
        self.root = Path(os.path.abspath(root))
        for path in reversed((self.root,*self.root.parents)):
            if create and not os.path.lexists(path):
                path.mkdir()
            _safe_existing(path,directory=True)
        self.validator = validator

    def _checked(self, files):
        copied = copy_files(files)
        if dict(self.validator.validate_files(copied)) != copied:
            raise ValueError('Validator changed candidate bytes')
        return copied

    def publish(self, files):
        candidate = self._checked(files)
        _safe_existing(self.root,directory=True)
        name = 'bundle-' + uuid.uuid4().hex
        bundle = self.root/name
        bundle.mkdir()
        content = bundle/'files'
        content.mkdir()
        for path, raw in sorted(candidate.items()):
            target = content/path
            target.parent.mkdir(parents=True,exist_ok=True)
            _write_new(target,raw)
        manifest = canonical_json({'files':[{'path':p,'sha256':hashlib.sha256(b).hexdigest()}
                                           for p,b in sorted(candidate.items())]})
        _write_new(bundle/'manifest.json',manifest)
        pointer = canonical_json({'bundle':name,'manifest_sha256':hashlib.sha256(manifest).hexdigest()})
        # Re-read every staged byte and rerun semantics before selecting it.
        staged = self._read(pointer)
        if dict(staged) != candidate:
            raise ValueError('Staged projection differs from candidate')
        temporary = self.root/('pointer-'+uuid.uuid4().hex+'.tmp')
        _write_new(temporary,pointer)
        selected = self.root/'current.json'
        if os.path.lexists(selected):
            _safe_existing(selected,directory=False)
        _safe_existing(self.root,directory=True)
        os.replace(temporary,selected)
        return staged

    def open_view(self):
        _safe_existing(self.root,directory=True)
        path = self.root/'current.json'
        _safe_existing(path,directory=False)
        return self._read(path.read_bytes())

    def _read(self, raw):
        paths = set()
        # Validate directories without following symlinks/reparse points.
        for directory, dirs, names in os.walk(self.root,followlinks=False,onerror=_walk_error):
            for name in dirs:
                _safe_existing(Path(directory)/name,directory=True)
            for name in names:
                path = Path(directory)/name
                _safe_existing(path,directory=False)
                paths.add(path.relative_to(self.root).as_posix())
        def read(path):
            return (self.root/path).read_bytes()
        return MappingProxyType(self._checked(read_selected_bundle(raw,read,paths)))


def read_selected_bundle(raw, read, paths):
    """Decode one selected bundle using disk or exact committed byte access."""
    pointer = json.loads(raw)
    if (not isinstance(pointer,dict) or set(pointer) != {'bundle','manifest_sha256'} or canonical_json(pointer) != raw
            or not isinstance(pointer['bundle'],str)
            or not re.fullmatch(r'bundle-[0-9a-f]{32}',pointer['bundle'])):
        raise ValueError('Invalid selection pointer')
    bundle = pointer['bundle']
    manifest_raw = read(bundle + '/manifest.json')
    if hashlib.sha256(manifest_raw).hexdigest() != pointer['manifest_sha256']:
        raise ValueError('Manifest integrity mismatch')
    manifest = json.loads(manifest_raw)
    if not isinstance(manifest,dict) or set(manifest) != {'files'} or canonical_json(manifest) != manifest_raw:
        raise ValueError('Invalid bundle manifest')
    rows = manifest['files']
    if not isinstance(rows,list):
        raise ValueError('Invalid bundle members')
    files = {}
    content = bundle + '/files/'
    for row in rows:
        if not isinstance(row,dict) or set(row) != {'path','sha256'}:
            raise ValueError('Invalid member descriptor')
        path = row['path']
        if not isinstance(path,str):
            raise ValueError('Invalid member path')
        copy_files({path:b''})
        if path in files:
            raise ValueError('Duplicate bundle member')
        data = read(content + path)
        if hashlib.sha256(data).hexdigest() != row['sha256']:
            raise ValueError('Projection integrity mismatch')
        files[path] = data
    actual = {p[len(content):] for p in paths if p.startswith(content)}
    if {p for p in paths if p.startswith(bundle + '/')} != {content+p for p in files} | {bundle+'/manifest.json'}:
        raise ValueError('Unlisted selected-bundle members')
    if actual != set(files):
        raise ValueError('Unlisted bundle members')
    return files
