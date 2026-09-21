"""Explicit in-process host registration, never ambient approval discovery."""
from contextlib import ExitStack, contextmanager
from dataclasses import dataclass, field
import os
from pathlib import Path
from types import MappingProxyType

from .cli import CommittedCheckHost
from .cli_results import CommandFailure
from .git_reader import GitCommitReader
from .identity import copy_files
from .provenance import CommittedProvenanceVerifier


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
        for name in ('source_repositories','authority_repositories'):
            paths = {key:Path(path).resolve(strict=True) for key,path in dict(getattr(self,name)).items()}
            if any(not isinstance(key,str) or not key or not path.is_dir() for key,path in paths.items()):
                raise ValueError('Invalid repository registration')
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
        if path.resolve(strict=True) != path or not path.is_file():
            raise CommandFailure('invalid_configuration')
        if path.read_bytes() != registration.config_bytes:
            raise CommandFailure('invalid_configuration')
        with ExitStack() as stack:
            repositories = dict(registration.authority_repositories)
            repositories.update(registration.source_repositories)
            readers = {key:stack.enter_context(GitCommitReader(str(root)))
                       for key,root in sorted(repositories.items())}
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
