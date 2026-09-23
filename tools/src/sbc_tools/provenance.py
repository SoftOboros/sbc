"""Committed integrity composition for explicitly registered source repositories.

Trusted host construction fixes repositories, configuration, profile and approval
pins. Verification reads immutable objects, so retained publications do not
depend on today's checkout. This is not a clean-scan admission or authorization
decision; checkout observations remain a separate prerequisite at production.
"""
from dataclasses import dataclass
import hashlib
import json
import re
from types import MappingProxyType

from .authority import ROLES, verify_authority_inputs
from .configuration import validate_configuration
from .corpus import CorpusInput, corpus_digest, inventory_mounted_corpus
from .identity import copy_files, copy_publication
from .patches import verify_support_patch
from .mounts import observe_checkout_tree
from .validation import BundleValidator, VerifiedProvenance
from .canonical import canonical_json


@dataclass(frozen=True)
class AdmittedSource:
    """Bounded scan-start observation; not authorization, a lease or publication."""
    repository_id: str
    source_commit: str
    profile_sha256: str
    provenance: VerifiedProvenance
    checkout: object


@dataclass(frozen=True)
class GeneratedProjection:
    """Semantically checked generation result; not a committed publication."""
    admission: AdmittedSource
    snapshot_id: str
    files: object
    location_diagnostics: bytes


class ReferenceUnavailableError(ValueError):
    """The committed comparison reference cannot support a complete check."""
    def __init__(self, candidate):
        super().__init__('Committed projection reference is unavailable.')
        self.candidate = candidate


class ScanPublicationError(ValueError):
    def __init__(self, candidate, code):
        super().__init__('Projection publication failed.')
        self.candidate, self.code = candidate, code


class AuthorityValidationError(ValueError):
    """Authority validation failed at its identified semantic boundary."""


@dataclass(frozen=True)
class CheckedProjection:
    """Candidate identity remains distinct from the committed reference."""
    candidate: GeneratedProjection
    projection_commit: str
    differing_paths: tuple

    @property
    def comparison(self):
        return 'different' if self.differing_paths else 'equal'


class CommittedProvenanceVerifier:
    """Exact binding of committed projections, configuration, corpus and authority.

    No caller-selected repositories, roots, profiles, patches or approval pins.
    Child source repositories use explicitly registered parent gitlink history.
    Authority repositories may be separately registered, with exact manifest pins.
    """
    def __init__(self, *, repository_id, reader, config_path, config_bytes,
                 tracked_branch, profile_path, profile_sha256, patch_path,
                 approved_authority_sha256, approved_support_sha256,
                 authority_readers, evidence_paths=(), source_readers=None):
        for digest in (profile_sha256, approved_authority_sha256):
            if not isinstance(digest,str) or not re.fullmatch(r"[0-9a-f]{64}",digest):
                raise ValueError("Exact trusted profile and authority digests required")
        if isinstance(evidence_paths, (str, bytes)):
            raise ValueError("Evidence paths must be an explicit sequence")
        paths = (config_path, profile_path, patch_path, *tuple(evidence_paths))
        if len(set(paths)) != len(paths):
            raise ValueError("Duplicate provenance input paths")
        for path in paths:
            copy_files({path:b""})
        sources = {} if source_readers is None else dict(source_readers)
        if repository_id in sources and sources[repository_id] is not reader:
            raise ValueError("Conflicting source repository registration")
        sources[repository_id] = reader
        configured = validate_configuration(config_bytes,
            config_directory=(reader.checkout_path/config_path).parent,
            registered_repositories={key:value.checkout_path for key,value in sources.items()})
        config = configured.values
        if config["repository_id"] != repository_id or config["mode"] != "committed":
            raise ValueError("Committed registered repository configuration required")
        if not isinstance(tracked_branch,str) or not tracked_branch:
            raise ValueError("Explicit tracked branch required")
        if config["tracked_ref"] != "refs/heads/" + tracked_branch:
            raise ValueError("This composition requires an explicit tracked branch")
        if any(p == config["output_root"] or p.startswith(config["output_root"] + "/") for p in paths):
            raise ValueError("Provenance inputs cannot be generated outputs")
        registered = dict(authority_readers)
        for key,value in sources.items():
            if key in registered and registered[key] is not value:
                raise ValueError("Conflicting repository registration")
            registered[key] = value
        self._repository_id, self._reader = repository_id, reader
        self._config_path, self._config_bytes = config_path, bytes(config_bytes)
        self._config, self._branch = config, tracked_branch
        self._profile_path, self._profile_sha = profile_path, profile_sha256
        self._patch_path, self._authority_sha = patch_path, approved_authority_sha256
        self._support_sha = MappingProxyType(dict(approved_support_sha256))
        self._readers = MappingProxyType(registered)
        self._sources = MappingProxyType(sources)
        self._required = tuple(sorted(set((*paths,config["authority_manifest"],*config["registry_paths"]))))

    def bundle_validator(self):
        """Construct semantic validation with the same trusted roots and profile."""
        return BundleValidator(source_roots=self._config["source_roots"],
                               profile_sha256=self._profile_sha,provenance_verifier=self)

    def supports(self, capability):
        """Expose configured CLI capability membership without mutable config."""
        return capability in self._config['capabilities']

    def verify(self, publication, files, profile_sha256):
        publication, files = copy_publication(publication), copy_files(files)
        if (publication["repository_id"] != self._repository_id
                or publication["tracked_branch"] != self._branch
                or profile_sha256 != self._profile_sha
                or publication["authority_manifest_sha256"] != self._authority_sha):
            raise ValueError("Publication does not match trusted host context")
        source = publication["source_commit"]
        proof = self._verify_source(source)
        if dict(self._committed_projection(publication['projection_commit'])) != files:
            raise ValueError('Committed projection bytes mismatch')
        return proof

    def admit_source(self):
        """Observe clean checkout and verified inputs before producer execution.

        Selection comes only from trusted configuration. No publication or output
        writes occur. Retained-publication verify intentionally does not call this.
        """
        source = self._reader.resolve_commit(self._config["tracked_ref"])
        def observe():
            # Recheck existence and linked-path boundaries at both admission ends.
            validate_configuration(self._config_bytes,
                config_directory=(self._reader.checkout_path/self._config_path).parent,
                registered_repositories={key:reader.checkout_path
                                         for key,reader in self._sources.items()})
            return observe_checkout_tree(root_repository_id=self._repository_id,
                root_commit=source, mounts=self._config["submodules"],
                source_roots=tuple(sorted(set((*self._config["source_roots"],*self._required)))),
                readers=self._sources,exclude=self._config["exclude"])
        before = observe()
        if not before.clean:
            raise ValueError("Source checkout is not byte-exact clean at its configured pin")
        proof = self._verify_source(source)
        after = observe()
        if (not after.clean or before.pins != after.pins
                or self._reader.resolve_commit(self._config["tracked_ref"]) != source):
            raise ValueError("Source selection or checkout changed during admission")
        return AdmittedSource(self._repository_id,source,self._profile_sha,proof,after)

    def _verify_source(self, source):
        return self._source_inputs(source)[0]

    def generate_source(self, *, document_families, archive_families):
        """Admit and generate from pinned bytes with explicit host family routing.

        Every selected Markdown file needs a family; caller omissions fail.
        Prefixes come only from configured committed registry files. Source roots
        are visited in configuration order, with paths sorted within each root.
        No files, refs, commits or store selections are written by this operation.
        """
        from .projections import build_configured_projection
        admission = self.admit_source()
        proof, inventory = self._source_inputs(admission.source_commit)
        if proof != admission.provenance or inventory.pins != admission.checkout.pins:
            raise ValueError("Admitted source inventory changed")
        checked, diagnostics = build_configured_projection(inventory.files,
            source_roots=self._config['source_roots'],registry_paths=self._config['registry_paths'],
            document_families=document_families,archive_families=archive_families,
            validator=self.bundle_validator())
        snapshot = {'authority_manifest_sha256':proof.authority_manifest_sha256,
                    'corpus_sha256':proof.corpus_sha256,
                    'files':[{'path':p,'sha256':hashlib.sha256(b).hexdigest()}
                             for p,b in sorted(checked.items())]}
        return GeneratedProjection(admission,hashlib.sha256(canonical_json(snapshot)).hexdigest(),
                                   checked,canonical_json(diagnostics))

    def check_source(self, *, document_families, archive_families):
        """Regenerate and compare with the complete reference at the selected pin.

        Missing or invalid references are unavailable, never ordinary drift.
        Equality does not clear source findings or constitute acceptance. This
        operation performs no persistent writes and never rereads a moved ref.
        """
        from ._sidx_validation import IngestError
        from .git_reader import GitReadError
        candidate = self.generate_source(document_families=document_families,
                                         archive_families=archive_families)
        commit = candidate.admission.source_commit
        try:
            reference = self._committed_projection(commit)
        except (GitReadError, OSError, ValueError, IngestError):
            raise ReferenceUnavailableError(candidate) from None
        changed = tuple(sorted(p for p in set(reference) | set(candidate.files)
                               if reference.get(p) != candidate.files.get(p)))
        return CheckedProjection(candidate,commit,changed)

    def _committed_projection(self, commit):
        from .directory_store import read_selected_bundle
        prefix = self._config['output_root'] + '/'
        files = {}
        for entry in self._reader.entries(commit):
            if not entry.path.startswith(prefix):
                continue
            if entry.mode not in {0o100644,0o100755}:
                raise ValueError('Reference contains unsupported entries')
            files[entry.path[len(prefix):]] = self._reader.read_blob(commit,entry.path)
        if 'current.json' in files:
            if any(p.startswith(('index/','locations/','diagnostics/')) for p in files):
                raise ValueError('Ambiguous flat and selected projection layouts')
            try:
                files = read_selected_bundle(files['current.json'],files.__getitem__,set(files))
            except KeyError:
                raise ValueError('Incomplete selected projection') from None
        return self.bundle_validator().validate_files(files)

    def scan_source(self, *, document_families, archive_families):
        """Generate and publish at the configured output root; no Git commit."""
        from .directory_store import DirectoryProjectionStore
        from ._sidx_validation import IngestError
        candidate = self.generate_source(document_families=document_families,
                                         archive_families=archive_families)
        try:
            root = self._reader.checkout_path/self._config['output_root']
            # Flat tracked payloads require explicit migration, never a mixed layout.
            if any((root/name).exists() for name in ('index','locations','diagnostics')):
                raise ValueError('Flat output layout requires migration before scan')
            store = DirectoryProjectionStore(root,self.bundle_validator(),create=True)
            store.publish(candidate.files)
        except OSError:
            raise ScanPublicationError(candidate,'io_failure') from None
        except (ValueError,IngestError):
            raise ScanPublicationError(candidate,'internal_failure') from None
        return candidate

    def _source_inputs(self, source):
        reader = self._reader
        if reader.read_blob(source,self._config_path) != self._config_bytes:
            raise ValueError("Committed configuration differs from trusted configuration")
        profile = reader.read_blob(source,self._profile_path)
        if hashlib.sha256(profile).hexdigest() != self._profile_sha:
            raise ValueError("Committed profile bytes mismatch")
        raw = reader.read_blob(source,self._config["authority_manifest"])
        patch = reader.read_blob(source,self._patch_path)
        from .git_reader import GitReadError
        try:
            authority = verify_authority_inputs(raw, approved_manifest_sha256=self._authority_sha,
                                                patch_bytes=patch, readers=self._readers)
            verify_support_patch(authority,patch,approved_result_sha256=self._support_sha)
        except GitReadError:
            raise
        except ValueError:
            raise AuthorityValidationError('Invalid authority inputs') from None
        inventory = inventory_mounted_corpus(repository_id=self._repository_id,
            commit=source, readers=self._sources, mounts=self._config["submodules"],
            source_roots=self._config["source_roots"],required_files=self._required,
            exclude=self._config["exclude"],allow_empty_roots=True)
        combined = {(r.repository_id,r.path):r for r in inventory.records}
        # Authority input pins may live outside source roots or in another registered repo.
        manifest = json.loads(raw)
        for group in ROLES:
            for row in manifest[group]:
                item = row["files"][0]
                record = CorpusInput(row["repository_id"],item["path"],item["sha256"])
                key = (record.repository_id,record.path)
                if key in combined and combined[key] != record:
                    raise ValueError("Conflicting corpus identity across authority revisions")
                combined[key] = record
        return VerifiedProvenance(corpus_digest(combined.values()), authority.manifest_sha256), inventory
