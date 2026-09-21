"""Proposed declarations only. JSON shapes: query-contract.schema.json.

Values are validated, deep-immutable copies at the implementation boundary.
Semantic payloads follow pinned SIDX contracts; JSON mapping aliases are not
permission to bypass their capability-specific validators.
"""
from typing import Literal, Mapping, NotRequired, Protocol, Sequence, TypeAlias, TypedDict

JSON: TypeAlias = None | bool | int | float | str | Sequence["JSON"] | Mapping[str, "JSON"]
Digest: TypeAlias = str  # 64 lowercase hex; schema plus digest verification.
Capability: TypeAlias = Literal["C11", "C12"]

class Publication(TypedDict):
    repository_id: str
    snapshot_id: Digest
    source_commit: str
    projection_commit: str
    tracked_branch: str
    authority_manifest_sha256: Digest
    publication_id: Digest

class AccessContext(TypedDict):
    principal_id: str
    repository_grants: Sequence[str]
    capability_grants: Sequence[Capability]
    authorization_revision: str
    issued_at: int
    expires_at: int

class ProviderVersions(TypedDict):
    staleness: str
    history: str
    suspicion: str

class EvidenceGeneration(TypedDict):
    profile_sha256: Digest
    context_sha256: Digest | None
    evidence_manifest_sha256: Digest | None
    head_observation_sha256: Digest | None
    bootstrap_manifest_sha256: Digest | None
    algorithm_versions: ProviderVersions
    availability: Literal["validated", "unavailable"]
    observation_state: Literal["fresh", "unavailable", "stale", "invalid"]
    fresh_until: int

class EvidenceIdentity(EvidenceGeneration):
    identity_sha256: Digest
    suspicion_envelope_sha256: Digest | None
    history_envelope_sha256: Digest | None
    inherited_provider_identity: Digest

class Selection(TypedDict):
    publication: Publication
    generation: int
    evidence: EvidenceIdentity
    capability_profile_sha256: Digest

class CurrentSelector(TypedDict):
    kind: Literal["current"]

class PublicationSelector(TypedDict):
    kind: Literal["publication"]
    publication_id: Digest

Selector: TypeAlias = CurrentSelector | PublicationSelector

class AttributeFilter(TypedDict):
    attribute: str
    value: str

class TagFilter(TypedDict):
    key: str
    value: str

class Filters(TypedDict, total=False):
    search: str | None
    family: Sequence[str]
    attention_class: Sequence[str]
    native_state: Sequence[AttributeFilter]
    tag: Sequence[TagFilter]
    location_kind: Sequence[str]

class WorkItemsRequest(TypedDict):
    version: Literal[1]
    repository_id: str
    selector: Selector
    capability: Literal["C11"]
    filters: NotRequired[Filters]
    limit: NotRequired[int]
    cursor: NotRequired[str | None]

class LocationsRequest(TypedDict):
    version: Literal[1]
    repository_id: str
    selector: Selector
    capability: Literal["C12"]
    requested_id: str

Request: TypeAlias = WorkItemsRequest | LocationsRequest

class BoundaryError(TypedDict):
    code: Literal["access_denied", "invalid_request", "unsupported_profile",
                  "unsupported_capability", "publication_required",
                  "selection_conflict", "idempotency_conflict",
                  "selection_unavailable", "invalid_bundle",
                  "evidence_mismatch", "store_unavailable", "signer_unavailable"]
    message: str
    retryable: bool

class BoundaryResult(TypedDict):
    version: Literal[1]
    kind: Literal["boundary_error"]
    error: BoundaryError

class SemanticResult(TypedDict):
    version: Literal[1]
    kind: Literal["semantic"]
    capability: Capability
    selection: Selection | None
    semantic: Mapping[str, JSON]  # Pinned C11/C12 success/error contract.

Result: TypeAlias = SemanticResult | BoundaryResult

class Receipt(TypedDict):
    repository_id: str
    publication_id: Digest
    generation: int

class ImmutableView(Protocol):
    @property
    def publication(self) -> Publication: ...
    def projection_bytes(self, relative_path: str) -> bytes: ...
    def close(self) -> None: ...

class ValidatedCandidate(Protocol):
    @property
    def publication(self) -> Publication: ...
    @property
    def validation_profile_sha256(self) -> Digest: ...
    def files(self) -> Mapping[str, bytes]: ...
    # Complete immutable validated bundle, including canonical manifests.
    # Opaque engine-created receipt; host callers cannot forge validation.

class SnapshotStore(Protocol):
    def select(self, repository_id: str, selector: Selector) -> tuple[Publication, int] | BoundaryError | None: ...
    def open_view(self, publication: Publication) -> ImmutableView | BoundaryError: ...
    def publish(self, candidate: ValidatedCandidate, expected_generation: int,
                idempotency_key: str) -> Receipt | BoundaryError: ...
    # None from select means no current; an absent explicit pin is an error.

class BundleValidator(Protocol):
    def validate(self, publication: Publication, files: Mapping[str, bytes],
                 profile_sha256: Digest) -> ValidatedCandidate | BoundaryError: ...

class EvidenceProvider(Protocol):
    def pin(self, publication: Publication, now: int) -> EvidenceGeneration | BoundaryError: ...
    def read(self, publication: Publication, generation: EvidenceGeneration,
             kind: Literal["suspicion", "history", "staleness"],
             locator: Mapping[str, JSON] | None) -> Mapping[str, JSON] | BoundaryError: ...
    # Result envelope and identity checked against the pinned SIDX validator.

class AccessValidator(Protocol):
    def validate(self, context: AccessContext, repository_id: str,
                 capability: Capability, now: int) -> bool: ...
    # Trusted host implementation checks current revision/revocation.

class Clock(Protocol):
    def now(self) -> int: ...

class CursorBinding(TypedDict):
    repository_id: str
    snapshot_id: Digest
    publication_id: Digest
    projection_commit: str
    capability_profile_sha256: Digest
    evidence_identity_sha256: Digest
    inherited_provider_identity: Digest
    access_context_sha256: Digest
    capability: Literal["C11"]
    filter_digest: Digest
    limit: int

class CursorClaims(CursorBinding):
    version: Literal[1]
    last: tuple[str, str | None, str, str, int]
    issued_at: int
    expires_at: int

class CursorFailure(TypedDict):
    code: Literal["invalid_cursor", "cursor_snapshot_mismatch"]

class CursorCodec(Protocol):
    def encode(self, claims: CursorClaims) -> str | BoundaryError: ...
    def decode(self, token: str, expected: CursorBinding,
               now: int) -> CursorClaims | CursorFailure: ...
    # QueryService maps CursorFailure into inherited contextual semantic errors.

class CachedPage(TypedDict):
    unsigned_page: Mapping[str, JSON]
    expires_at: int

class PageCache(Protocol):
    # C11 only. C12 MUST NOT call get/put. Deadlines are Unix seconds.
    # get returns None when now >= expires_at; QueryService also checks expiry.
    def get(self, key: Digest, now: int) -> CachedPage | None: ...
    def put(self, key: Digest, unsigned_page: Mapping[str, JSON], expires_at: int) -> None: ...

class Dependencies(TypedDict):
    store: SnapshotStore
    evidence: EvidenceProvider
    access_validator: AccessValidator
    clock: Clock
    cursors: CursorCodec
    cache: PageCache | None
    capability_profile_sha256: Digest
    semantic_engine_sha256: Digest

class QueryService(Protocol):
    def query(self, request: Request, access: AccessContext,
              dependencies: Dependencies) -> Result: ...
