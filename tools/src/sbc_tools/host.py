"""Explicit in-process host registration, never ambient approval discovery."""
from contextlib import ExitStack, contextmanager
from dataclasses import dataclass, field
import os
import hashlib
import json
import re
import stat
import tomllib
from pathlib import Path
from types import MappingProxyType

from .cli import CommittedCheckHost
from .cli_results import CommandFailure
from .git_reader import GitCommitReader
from .identity import copy_files
from .provenance import CommittedProvenanceVerifier


def _mounted_observation(raw):
    value = tomllib.loads(raw.decode('utf-8'))
    return value.get('mode') == 'working-tree' and bool(value.get('submodules'))


def _regular_input(path):
    info = path.lstat()
    if (not stat.S_ISREG(info.st_mode) or getattr(info,'st_file_attributes',0) & 0x400
            or path.resolve(strict=True) != path):
        raise ValueError('Linked or nonregular host input')
    return path.read_bytes()


def load_console_host(host_path, config_path):
    """Read one explicit data binding; never infer approvals or search for it."""
    def unique(pairs):
        result = {}
        for key,value in pairs:
            if key in result:
                raise ValueError('Duplicate binding key')
            result[key] = value
        return result
    def invalid_constant(value):
        raise ValueError('Nonfinite binding value')
    try:
        path = Path(os.path.abspath(host_path))
        value = json.loads(_regular_input(path),object_pairs_hook=unique,parse_constant=invalid_constant)
        keys = set(HostRegistration.__dataclass_fields__) - {'config_bytes'} | {'schema_version','config_sha256'}
        if not isinstance(value,dict) or set(value) != keys or type(value['schema_version']) is not int or value['schema_version'] != 1:
            raise ValueError('Unsupported binding schema')
        for name in ('repository_id','tracked_branch'):
            if not isinstance(value[name],str) or not value[name]:
                raise ValueError('Invalid binding identifier')
        for name in ('config_path','profile_path','patch_path'):
            copy_files({value[name]:b''})
        for name in ('config_sha256','profile_sha256','approved_authority_sha256'):
            if not isinstance(value[name],str) or not re.fullmatch('[0-9a-f]{64}',value[name]):
                raise ValueError('Invalid binding digest')
        support = value['approved_support_sha256']
        if not isinstance(support,dict) or set(support) != {'AGENTS.md','CLAUDE.md','README.md'}:
            raise ValueError('Invalid support pins')
        if any(not isinstance(v,str) or not re.fullmatch('[0-9a-f]{64}',v) for v in support.values()):
            raise ValueError('Invalid support digest')
        for name in ('source_repositories','authority_repositories'):
            if not isinstance(value[name],dict):
                raise ValueError('Invalid repository map')
            paths = {}
            for key,location in value[name].items():
                if not key or not isinstance(location,str) or not location or '://' in location or location.startswith('~'):
                    raise ValueError('Invalid local repository path')
                # Keep source bindings literal until configuration determines
                # whether missing mounted participants can be observed.
                paths[key] = Path(os.path.abspath(path.parent/location))
            value[name] = paths
        if value['repository_id'] not in value['source_repositories']:
            raise ValueError('Root repository missing')
        config = value['source_repositories'][value['repository_id']]/value['config_path']
        if config != Path(os.path.abspath(config_path)):
            raise ValueError('Configuration path mismatch')
        raw_config = _regular_input(config)
        if hashlib.sha256(raw_config).hexdigest() != value.pop('config_sha256'):
            raise ValueError('Configuration digest mismatch')
        families = value['document_families']
        if not isinstance(families,dict):
            raise ValueError('Invalid family map')
        def family(name):
            copy_files({name:b''})
            if '/' in name:
                raise ValueError('Invalid family')
        for source,name in families.items():
            copy_files({source:b''})
            family(name)
        rows = value['archive_families']
        if not isinstance(rows,list):
            raise ValueError('Invalid archive family list')
        archives = {}
        for row in rows:
            if not isinstance(row,dict) or set(row) != {'archive','member','family'}:
                raise ValueError('Invalid archive family')
            copy_files({row['archive']:b'',row['member']:b''})
            family(row['family'])
            key = (row['archive'],row['member'])
            if key in archives:
                raise ValueError('Duplicate archive member')
            archives[key] = row['family']
        evidence = value['evidence_paths']
        if not isinstance(evidence,list) or len(set(evidence)) != len(evidence):
            raise ValueError('Invalid evidence paths')
        for member in evidence:
            copy_files({member:b''})
        value.pop('schema_version')
        value.update(config_bytes=raw_config,archive_families=archives)
        return RegisteredHostLoader([HostRegistration(**value)])
    except (ValueError,TypeError,KeyError):
        raise CommandFailure('invalid_configuration') from None


@dataclass(frozen=True)
class HostRegistration:
    """Host-authorized inputs, copied at registration; not a config-file schema.

    The host is responsible for obtaining approval pins and family policy. This
    type neither discovers nor grants approval and is not loaded from TOML.
    """
    repository_id: str
    source_repositories: object
    authority_repositories: object
    config_path: str
    config_bytes: bytes
    tracked_branch: str
    profile_path: str
    profile_sha256: str
    patch_path: str
    approved_authority_sha256: str
    approved_support_sha256: object
    document_families: object
    archive_families: object = field(default_factory=dict)
    evidence_paths: tuple = ()

    def __post_init__(self):
        copy_files({self.config_path:self.config_bytes})
        mounted = _mounted_observation(self.config_bytes)
        for name in ('source_repositories','authority_repositories'):
            paths = {}
            for key, location in dict(getattr(self,name)).items():
                deferred = mounted and name == 'source_repositories' and key != self.repository_id
                path = Path(os.path.abspath(location)) if deferred else Path(location).resolve(strict=True)
                if not isinstance(key,str) or not key or (not deferred and not path.is_dir()):
                    raise ValueError('Invalid repository registration')
                paths[key] = path
            object.__setattr__(self,name,MappingProxyType(paths))
        if self.repository_id not in self.source_repositories:
            raise ValueError('Root repository is not registered')
        for key in set(self.source_repositories) & set(self.authority_repositories):
            if self.source_repositories[key] != self.authority_repositories[key]:
                raise ValueError('Conflicting repository registration')
        for name in ('approved_support_sha256','document_families','archive_families'):
            values = dict(getattr(self,name))
            if any(not isinstance(value,str) for value in values.values()):
                raise ValueError('Registration values must be immutable strings')
            object.__setattr__(self,name,MappingProxyType(values))
        if isinstance(self.evidence_paths,(str,bytes)):
            raise ValueError('Evidence paths must be an explicit sequence')
        object.__setattr__(self,'evidence_paths',tuple(self.evidence_paths))

    @property
    def configuration_file(self):
        return self.source_repositories[self.repository_id]/self.config_path


class RegisteredHostLoader:
    """Allowlisted configuration paths with scoped, offline Git readers."""
    def __init__(self, registrations):
        selected = {}
        for registration in registrations:
            if not isinstance(registration,HostRegistration):
                raise ValueError('Explicit host registration required')
            path = registration.configuration_file
            if path in selected:
                raise ValueError('Duplicate configuration registration')
            selected[path] = registration
        self._registrations = MappingProxyType(selected)

    @contextmanager
    def __call__(self, config_path):
        # Match before reading: an arbitrary CLI path is never opened.
        path = Path(os.path.abspath(config_path))
        registration = self._registrations.get(path)
        if registration is None:
            raise CommandFailure('invalid_configuration')
        try:
            config_bytes = _regular_input(path)
        except ValueError:
            raise CommandFailure('invalid_configuration') from None
        if config_bytes != registration.config_bytes:
            raise CommandFailure('invalid_configuration')
        with ExitStack() as stack:
            if _mounted_observation(registration.config_bytes):
                from .configuration import validate_configuration
                from .working_tree import WorkingTreeHost
                from .registered_readers import RegisteredCheckoutReaders
                try:
                    configured = validate_configuration(registration.config_bytes,
                        config_directory=registration.configuration_file.parent,
                        registered_repositories=registration.source_repositories,
                        allow_missing_mount_inputs=True)
                except ValueError:
                    raise CommandFailure('invalid_configuration', mounted_observation=True) from None
                readers = RegisteredCheckoutReaders(registration.source_repositories, stack)
                authority = {key: stack.enter_context(GitCommitReader(str(root)))
                             for key, root in sorted(registration.authority_repositories.items())}
                yield WorkingTreeHost(registration, readers, configured, authority)
                return
            repositories = dict(registration.authority_repositories)
            repositories.update(registration.source_repositories)
            readers = {key:stack.enter_context(GitCommitReader(str(root)))
                       for key,root in sorted(repositories.items())}
            from .configuration import validate_configuration
            from .working_tree import WorkingTreeHost
            try:
                configured = validate_configuration(registration.config_bytes,
                    config_directory=registration.configuration_file.parent,
                    registered_repositories=registration.source_repositories)
            except ValueError:
                raise CommandFailure('invalid_configuration') from None
            if configured.values['mode'] == 'working-tree':
                if configured.values['submodules'] or len(registration.source_repositories) != 1:
                    raise CommandFailure('invalid_configuration')
                yield WorkingTreeHost(registration,MappingProxyType(readers),configured)
                return
            try:
                verifier = CommittedProvenanceVerifier(
                    repository_id=registration.repository_id,reader=readers[registration.repository_id],
                    config_path=registration.config_path,config_bytes=registration.config_bytes,
                    tracked_branch=registration.tracked_branch,profile_path=registration.profile_path,
                    profile_sha256=registration.profile_sha256,patch_path=registration.patch_path,
                    approved_authority_sha256=registration.approved_authority_sha256,
                    approved_support_sha256=registration.approved_support_sha256,
                    authority_readers={key:readers[key] for key in registration.authority_repositories},
                    source_readers={key:readers[key] for key in registration.source_repositories},
                    evidence_paths=registration.evidence_paths)
            except ValueError:
                raise CommandFailure('invalid_configuration') from None
            yield CommittedCheckHost(verifier,registration.document_families,registration.archive_families)
