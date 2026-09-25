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


class WorkingTreeChangedError(ValueError):
    """A selected file changed while acquiring observation bytes."""


def _read_regular(path, expected):
    flags = os.O_RDONLY | getattr(os,'O_BINARY',0) | getattr(os,'O_NOFOLLOW',0)
    descriptor = os.open(path,flags)
    with os.fdopen(descriptor,'rb') as stream:
        opened = os.fstat(stream.fileno())
        # Windows path and handle stat may disagree on ctime; compare it only
        # between observations of the same open handle below.
        if not stat.S_ISREG(opened.st_mode) or _signature(opened)[:-1] != _signature(expected)[:-1]:
            raise WorkingTreeChangedError('Observed file changed before read')
        data = stream.read()
        if _signature(os.fstat(stream.fileno())) != _signature(opened):
            raise WorkingTreeChangedError('Observed file changed during read')
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


@dataclass(frozen=True)
class ObservedProjection:
    corpus: object
    authority_sha256: str
    files: object
    location_diagnostics: bytes


class _RejectCommittedProof:
    def verify(self, *args, **kwargs):
        raise ValueError('Working-tree observation cannot verify committed publication')


def generate_working_tree(registration, *, authority_readers):
    """Verify explicit host pins and generate from captured single-repository bytes.

    Returned data does not contain VerifiedProvenance or committed admission.
    All authority objects must already exist in the supplied offline readers.
    """
    from .configuration import validate_configuration
    configured = validate_configuration(registration.config_bytes,
        config_directory=registration.configuration_file.parent,
        registered_repositories=registration.source_repositories)
    if configured.values['repository_id'] != registration.repository_id:
        raise ValueError('Registered repository identity mismatch')
    captured = capture_working_tree(configured,required_files=(registration.config_path,
        registration.profile_path,registration.patch_path,*registration.evidence_paths))
    return _generate_captured_working_tree(registration, configured, captured, authority_readers)


def _generate_captured_working_tree(registration, configured, captured, authority_readers):
    """One authority and producer path for single and mounted observations."""
    from .authority import verify_authority_inputs
    from .canonical import canonical_json
    from .patches import verify_support_patch
    from .projections import build_configured_projection
    from .validation import BundleValidator
    from .provenance import AuthorityValidationError
    if captured.files[registration.config_path] != registration.config_bytes:
        raise ValueError('Captured configuration differs from registered bytes')
    if hashlib.sha256(captured.files[registration.profile_path]).hexdigest() != registration.profile_sha256:
        raise ValueError('Captured profile differs from registered digest')
    raw = captured.files[configured.values['authority_manifest']]
    patch = captured.files[registration.patch_path]
    try:
        authority = verify_authority_inputs(raw,
            approved_manifest_sha256=registration.approved_authority_sha256,
            patch_bytes=patch,readers=authority_readers)
        verify_support_patch(authority,patch,approved_result_sha256=registration.approved_support_sha256)
    except ValueError:
        raise AuthorityValidationError('Invalid authority inputs') from None
    validator = BundleValidator(source_roots=configured.values['source_roots'],
        profile_sha256=registration.profile_sha256,provenance_verifier=_RejectCommittedProof())
    files,diagnostics = build_configured_projection(captured.files,
        source_roots=configured.values['source_roots'],registry_paths=configured.values['registry_paths'],
        document_families=registration.document_families,archive_families=registration.archive_families,
        validator=validator)
    return ObservedProjection(captured,authority.manifest_sha256,files,canonical_json(diagnostics))


@dataclass(frozen=True)
class WorkingTreeHost:
    """Explicit CLI host; observations never carry committed provenance claims."""
    registration: object
    readers: object
    configuration: object
    authority_readers: object = None

    def execute(self, invocation):
        import json
        from .cli_results import failure_envelope
        from .git_reader import GitReadError, GitUnavailableError
        from ._sidx_validation import IngestError
        from .observations import check_observation
        from .validation import BundleValidator
        from .provenance import AuthorityValidationError, read_committed_projection
        from .directory_store import DirectoryProjectionStore
        from .mounted_working_tree import generate_mounted_working_tree, AggregateObservationUnavailable
        value = self.configuration.values
        result = None
        mounted = bool(value['submodules'])
        observation = None
        def failure(code):
            error = failure_envelope(code,command=invocation.command,mode='working-tree')
            if mounted:
                error.update(schema_version=2, observation=observation)
            if result is not None:
                error.update(selection=result['selection'],findings=result['findings'])
            return error
        if invocation.command not in value['capabilities']:
            return failure('invalid_configuration')
        try:
            if mounted:
                observed = generate_mounted_working_tree(self.registration, source_readers=self.readers,
                    authority_readers=self.authority_readers)
                observation = json.loads(observed.corpus.observation)
            else:
                observed = generate_working_tree(self.registration,authority_readers=self.readers)
            validator = BundleValidator(source_roots=value['source_roots'],
                profile_sha256=self.registration.profile_sha256,provenance_verifier=_RejectCommittedProof())
            args = dict(repository_id=self.registration.repository_id,corpus_records=observed.corpus.records,
                authority_sha256=observed.authority_sha256,candidate_files=observed.files,
                validator=validator,location_diagnostics=json.loads(observed.location_diagnostics))
            if mounted:
                args['observation_set'] = observation
            result = check_observation(**args,reference_files=observed.files)
            if invocation.command == 'check':
                reader = self.readers[self.registration.repository_id]
                try:
                    commit = reader.resolve_commit(value['tracked_ref'])
                    reference = read_committed_projection(reader,commit,value['output_root'],validator)
                except (GitReadError,OSError,ValueError,IngestError):
                    return failure('evidence_unavailable')
                return check_observation(**args,reference_files=reference)
            root = self.configuration.repository_root/value['output_root']
            if any((root/name).exists() for name in ('index','locations','diagnostics')):
                return failure('invalid_configuration')
            DirectoryProjectionStore(root,validator,create=True).publish(observed.files)
            result.update(command='scan')
            result['result'].update(publication='published',comparison='not_applicable')
            return result
        except AuthorityValidationError:
            return failure('invalid_authority')
        except AggregateObservationUnavailable as exc:
            observation = json.loads(exc.observation_bytes(self.registration.repository_id))
            return failure('evidence_unavailable')
        except GitUnavailableError:
            return failure('evidence_unavailable')
        except OSError:
            return failure('io_failure')
        except ValueError:
            return failure('invalid_configuration' if mounted else 'internal_failure')
        except Exception:
            return failure('internal_failure')
