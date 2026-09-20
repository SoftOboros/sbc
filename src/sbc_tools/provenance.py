"""Committed integrity composition for the initial single-source-repository path.

Trusted host construction fixes repositories, configuration, profile and approval
pins. Verification reads immutable objects, so retained publications do not
depend on today's checkout. This is not a clean-scan admission or authorization
decision; checkout observations remain a separate prerequisite at production.
"""
import hashlib
import json
import re
from types import MappingProxyType

from .authority import ROLES, verify_authority_inputs
from .configuration import validate_configuration
from .corpus import CorpusInput, corpus_digest, inventory_committed_corpus
from .identity import copy_files, copy_publication
from .patches import verify_support_patch
from .validation import BundleValidator, VerifiedProvenance


class CommittedProvenanceVerifier:
    """Exact binding of committed projections, configuration, corpus and authority.

    No caller-selected repositories, roots, profiles, patches or approval pins.
    Child source repositories remain unsupported rather than partially verified.
    Authority repositories may be separately registered, with exact manifest pins.
    """
    def __init__(self, *, repository_id, reader, config_path, config_bytes,
                 tracked_branch, profile_path, profile_sha256, patch_path,
                 approved_authority_sha256, approved_support_sha256,
                 authority_readers, evidence_paths=()):
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
        configured = validate_configuration(config_bytes,
            config_directory=(reader.checkout_path/config_path).parent,
            registered_repositories={repository_id:reader.checkout_path})
        config = configured.values
        if config["repository_id"] != repository_id or config["mode"] != "committed":
            raise ValueError("Committed registered repository configuration required")
        if config["submodules"]:
            raise ValueError("Child corpus composition is not implemented")
        if not isinstance(tracked_branch,str) or not tracked_branch:
            raise ValueError("Explicit tracked branch required")
        if config["tracked_ref"] != "refs/heads/" + tracked_branch:
            raise ValueError("This composition requires an explicit tracked branch")
        if any(p == config["output_root"] or p.startswith(config["output_root"] + "/") for p in paths):
            raise ValueError("Provenance inputs cannot be generated outputs")
        registered = dict(authority_readers)
        if repository_id in registered and registered[repository_id] is not reader:
            raise ValueError("Conflicting repository registration")
        registered[repository_id] = reader
        self._repository_id, self._reader = repository_id, reader
        self._config_path, self._config_bytes = config_path, bytes(config_bytes)
        self._config, self._branch = config, tracked_branch
        self._profile_path, self._profile_sha = profile_path, profile_sha256
        self._patch_path, self._authority_sha = patch_path, approved_authority_sha256
        self._support_sha = MappingProxyType(dict(approved_support_sha256))
        self._readers = MappingProxyType(registered)
        self._required = tuple(sorted(set((*paths,config["authority_manifest"],*config["registry_paths"]))))

    def bundle_validator(self):
        """Construct semantic validation with the same trusted roots and profile."""
        return BundleValidator(source_roots=self._config["source_roots"],
                               profile_sha256=self._profile_sha,provenance_verifier=self)

    def verify(self, publication, files, profile_sha256):
        publication, files = copy_publication(publication), copy_files(files)
        if (publication["repository_id"] != self._repository_id
                or publication["tracked_branch"] != self._branch
                or profile_sha256 != self._profile_sha
                or publication["authority_manifest_sha256"] != self._authority_sha):
            raise ValueError("Publication does not match trusted host context")
        source = publication["source_commit"]
        reader = self._reader
        if reader.read_blob(source,self._config_path) != self._config_bytes:
            raise ValueError("Committed configuration differs from trusted configuration")
        profile = reader.read_blob(source,self._profile_path)
        if hashlib.sha256(profile).hexdigest() != self._profile_sha:
            raise ValueError("Committed profile bytes mismatch")
        raw = reader.read_blob(source,self._config["authority_manifest"])
        patch = reader.read_blob(source,self._patch_path)
        authority = verify_authority_inputs(raw, approved_manifest_sha256=self._authority_sha,
                                            patch_bytes=patch, readers=self._readers)
        verify_support_patch(authority,patch,approved_result_sha256=self._support_sha)
        records = inventory_committed_corpus(reader, repository_id=self._repository_id,
            commit=source, source_roots=self._config["source_roots"],
            required_files=self._required, exclude=self._config["exclude"])
        combined = {(r.repository_id,r.path):r for r in records}
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
        reader.verify_files(publication["projection_commit"],self._config["output_root"],files)
        return VerifiedProvenance(corpus_digest(combined.values()), authority.manifest_sha256)
