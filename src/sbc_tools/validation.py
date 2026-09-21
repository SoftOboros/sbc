"""Real projection semantics with mandatory trusted provenance verification."""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import re
from types import MappingProxyType

from .canonical import canonical_json
from ._sidx_validation import IngestError, ProjectionSemantics
from .identity import copy_publication, copy_files

_SHA = re.compile(r"[0-9a-f]{64}\Z")


@dataclass(frozen=True)
class VerifiedProvenance:
    """Returned only by the host's trusted committed-source verifier.

    Its verify(publication, files, profile_sha256) operation must verify exact
    committed bytes, approved authority/profile and full authoritative corpus.
    There is no default, request-selected verifier or self-attestation path.
    """
    corpus_sha256: str
    authority_manifest_sha256: str


@dataclass(frozen=True)
class ValidatedBundle:
    publication: object
    validation_profile_sha256: str
    _files: object

    def files(self):
        return self._files


class _MemoryPath:
    """Only a supplied byte mapping is addressable; never touches the filesystem."""
    def __init__(self, path, files, consumed):
        self.path, self.files, self.consumed = path, files, consumed

    def __truediv__(self, part):
        return _MemoryPath(self.path + "/" + part, self.files, self.consumed)

    def __str__(self):
        return self.path

    def exists(self):
        return self.path in self.files

    def read_bytes(self):
        if self.path not in self.files:
            raise FileNotFoundError(self.path)
        self.consumed.add(self.path)
        return self.files[self.path]


class BundleValidator:
    """New ingestion supports the exact c6-v3 triple only, as in the pinned source.

    Legacy loaders remain internal for future explicit retained-profile support.
    The supplied provenance verifier is trusted host composition. Tests using a
    synthetic verifier prove projection semantics only, not Git provenance.
    """
    def __init__(self, *, source_roots, profile_sha256, provenance_verifier):
        if not isinstance(profile_sha256, str) or not _SHA.fullmatch(profile_sha256):
            raise ValueError("An exact approved profile digest is required")
        if not callable(getattr(provenance_verifier, "verify", None)):
            raise ValueError("Committed provenance verifier is required")
        try:
            self._semantics = ProjectionSemantics(source_roots)
        except IngestError as exc:
            raise ValueError("Invalid source roots") from exc
        self._profile = profile_sha256
        self._provenance = provenance_verifier

    def validate(self, publication, files, profile_sha256):
        try:
            if profile_sha256 != self._profile:
                raise ValueError("Profile mismatch")
            published = copy_publication(publication)
            bundle = self.validate_files(files)
            pinned = MappingProxyType(published)
            pinned_files = MappingProxyType(bundle)
            proof = self._provenance.verify(pinned, pinned_files, profile_sha256)
            if not isinstance(proof, VerifiedProvenance):
                raise ValueError("Missing verified provenance")
            if (not isinstance(proof.corpus_sha256, str) or not _SHA.fullmatch(proof.corpus_sha256)
                    or proof.authority_manifest_sha256 != published["authority_manifest_sha256"]):
                raise ValueError("Authority or corpus mismatch")
            snapshot = {
                "authority_manifest_sha256": proof.authority_manifest_sha256,
                "corpus_sha256": proof.corpus_sha256,
                "files": [{"path": path, "sha256": hashlib.sha256(bundle[path]).hexdigest()}
                          for path in sorted(bundle)],
            }
            if hashlib.sha256(canonical_json(snapshot)).hexdigest() != published["snapshot_id"]:
                raise ValueError("Content identity mismatch")
            return ValidatedBundle(pinned, profile_sha256, pinned_files)
        except Exception:
            return {"code": "invalid_bundle", "message": "Invalid projection bundle.", "retryable": False}

    def validate_files(self, files):
        """Check projection semantics only; no provenance or publication claim."""
        bundle = copy_files(files)
        consumed = set()
        roots = [_MemoryPath(name, bundle, consumed)
                 for name in ("index", "locations", "diagnostics")]
        self._semantics.validate_triple(*roots)
        if consumed != set(bundle):
            raise ValueError("Unlisted bundle members")
        return MappingProxyType(bundle)
