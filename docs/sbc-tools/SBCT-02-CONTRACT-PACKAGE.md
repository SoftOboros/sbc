# SBCT-02 — Query Contract Completion Package

**Document ID:** SBCT-CONTRACT-02
**Status:** APPROVED — Ira Abbott, GATE-206, 2026-09-20
**Revision:** 0.1.1
**Date:** 2026-09-20
**Owner:** Ira Abbott
**Authority:** Ratified [SBCT-02](SBCT-02-QUERIES-AND-ADAPTERS.md) revision 0.6.1.
**Implementation status:** Authorized; runtime acceptance gates remain open.

## Purpose and approval boundary

This package completes the three accepted SBCT-02 review directions with
concrete contracts approved by Ira Abbott on 2026-09-20 under GATE-206.
It does not amend inherited query meanings. The original phase
ratification remains recorded separately from approval of these details.

The [machine-readable contract](contracts/query-contract.schema.json) owns JSON
field shapes. [Python interface declarations](contracts/query-interfaces.pyi)
own synchronous interface signatures; they are declarations, not runtime code.
The semantic payload owners remain the exact SIDX authorities below. Storage
and transport implementations must consume one extracted semantic engine.

## 1. Exact authority and compatibility selection

The query authority bundle is pinned at source revision
`751ffe62027a3030bc989d22f5c2f759234064dc`:

| Role | Revision | Git blob SHA-1 |
|---|---|---|
| SIDX-06B, shared queries and transport parity | 0.10.0 | `391e9d145428bd1491ddeb20c36472875c4ee6cc` |
| SIDX-06D, conformance inputs and Git providers | 0.8.0 | `b3c75e81ccc50c0d30508fd000089d022390f62e` |
| SIDX-06E, C6 object graph and acknowledgment | 0.8.0 | `2d29fe7c4c30300ee5919edcbaef77232e5d7aa2` |
| Shared C11/C12 reference implementation | source revision above | `374b5961b2686150cc3651dbfe77e795a6d9622d` |

SIDX-06B §§6–9 own envelope, filters, membership, ordering, metrics, facets,
location resolution and semantic errors. Its §7.5.1 owns the inherited
provider-dependent cursor identity. SIDX-06D §9 and SIDX-06E §8.3 own validated
evidence and provider composition. SIDX-06E §8.1 owns C6 eligibility and
provider envelopes. Authority/source inventories and originating-consumer
reconciliation are maintained outside this portable family. The portable
release must carry verified authority bytes, not depend on the origin being
reachable. SBCT-01's authority manifest remains a separate producer pin.

The selected public query profile is `sbct-query-v1`: C11 and C12 payload
semantics from these pins, plus the explicit SBCT context and version-1 cursor
below. The reference payload profile is `sidx-06b-0.10`. The validated
projection profile is independently `c6-v3` or `retained-v2`; selection is
host policy after full inherited profile validation, never a request parameter.
No fallback from invalid v3 to retained v2 is allowed. A historical bootstrap
profile is separately content-addressed and explicitly configured; the default
has no consumer bootstrap constants.

C6 suspicion is a provider contribution to C11. It is not a separately
advertised public query endpoint in this package. Capability advertisement
lists C11/C12 implementation support and per-selection evidence availability
separately. Missing suspicion evidence cannot disable unrelated valid classes
or fabricate completeness. Read-only Interlock invokes the same service once
per authorized repository; federation is not a new C11 sort order.

### Compatibility dispositions approved under GATE-206

| Existing contract | Proposed disposition |
|---|---|
| SIDX publication `index_commit` is 40 lowercase hex | Preserve it. This profile rejects SHA-256 Git publication IDs as `unsupported_profile`; SBCT-01 may still produce content for those repositories. Widening the SIDX wire field requires another reconciled profile. |
| Existing cursor v1/v2 uses implicit host signer | Keep as reference evidence only. The public portable profile accepts only the SBCT cursor specified in §5; legacy cursors are `invalid_cursor`. No byte-identical cursor claim. |
| Dedicated SIDX database | File/SQLite is portable SBCT conformance only. It does not claim full SIDX deployment conformance. |
| Production provider overrides forbidden | Trusted host composition supplies validated providers once; REST/MCP caller fields cannot select providers, profiles, evidence roots, signer, access context or clock. |
| Existing framework-bound implementation | Extract semantic ownership; inject immutable views. The pinned producer remains a reference, not a permitted Django dependency of the core. |
| Existing branch/bootstrap constants | Isolate in an explicitly selected downstream compatibility profile with exact validation retained; no generic default or silent strength reduction. |

An authority/implementation disagreement is a failed reconciliation, not license
to adopt implementation behavior. Reference vectors are regression evidence;
the pinned normative authorities win.

## 2. Content, publication and selection

`snapshot_id` is exactly SBCT-01's content identity. Do not recompute it from
publication, database IDs, observation times, authorization or evidence.
`Publication` is immutable and binds repository ID, snapshot ID, source commit,
projection commit, tracked branch and authority-manifest digest.
`publication_id` is SHA-256 of the canonical Publication object excluding
`publication_id`. Canonicalization is SBCT-01 wrapper JSON: sorted keys,
compact separators, UTF-8, no NaN, one final LF. All identity strings are NFC;
digests are lowercase. This wrapper rule does not replace C6's owning
canonicalization or inherited filter normalization.

A repository ID is a host-configured stable opaque identifier, not a filesystem
path or a caller-asserted tenancy claim. The same content may have publications
A and B with different projection commits. Lookup by snapshot ID must not
choose between them. Every successful selection pins both identities.
`index_commit` in the inherited semantic payload equals the selected
`projection_commit`; `source_commit` remains provenance and is never
substituted there. Working-tree previews are outside this committed-query
profile and return `publication_required`.

`Selection` includes the immutable publication, per-repository current
generation, a validated evidence identity, and the capability-profile digest.
It is captured once per invocation. Content reads are immutable, namespaced by
repository and snapshot, and cannot reselect “current.” Identical commit/object
IDs in different repositories are not shared authorization.

The host may request `current` or an explicit publication. On the first page,
`current` resolves once. For continuations it resolves once again and must
match the cursor binding, so a changed current publication fails rather than
silently following it. Explicit retained-publication continuation is permitted
only if still authorized, evidence-identical and within the token lifetime.
For an explicit selection, selection generation is that publication's recorded
generation; a later unrelated current switch does not mutate it.

Head observation is evidence, not ingest. An unavailable, invalid or older-than-
300-seconds observation yields inherited `unknown` staleness while valid
history can remain available. History, suspicion and staleness are evaluated
against the selected **publication commit**, not just content equality.
Observation state (fresh, unavailable, stale or invalid) is part of the pinned
evidence identity. Freshness is captured at entry using the injected clock.
fresh_until is the immutable observation timestamp plus 300 seconds for a
valid observation, otherwise zero. At the exact deadline the observation is
stale. A request admitted before that deadline uses its entry-time observation
throughout; a subsequent request pins stale state. Cache reuse never crosses
that deadline. A zero deadline disables caching without disabling valid history.

### Atomic publication protocol

1. Read current repository generation (zero means no selection).
2. Validate the entire object/location/diagnostic bundle, authority/profile,
   content identity, and committed publication-to-bytes binding into an
   immutable staged view. Validation is independent of Django.
3. Atomically compare-and-swap that repository's expected generation to a new
   generation and publication. A competing write returns
   `selection_conflict`; a corrupt candidate returns `invalid_bundle`.
   Neither alters current. No implicit retry or rebase onto newer evidence.
4. A replay of the same idempotency key and identical validated publication
   returns the original receipt, without resetting a newer current selection.
   The same key with different inputs is `idempotency_conflict`.
5. A crash before commit leaves the old selection usable; after commit it
   exposes the entire new one. An in-flight reader retains its pinned old
   immutable view. Garbage collection must honor reader leases and retained
   cursor lifetime; a deliberately retired view returns `selection_unavailable`.
6. Projection reset removes only rebuildable data in the selected repository
   namespace. Authentication/session/authoring stores are not in this API.

A store receipt includes repository, publication ID and committed generation.
File and SQLite/Django adapters must provide these same atomic guarantees;
filesystem rename alone without per-repository compare-and-swap is insufficient.
The validated candidate exposes the complete immutable path-to-bytes bundle
through files(); its validity is tied to the publication/profile digests.
The store verifies this binding before persisting it. A mutable mapping or
forged validation receipt must be rejected as invalid_bundle.

## 3. Access, capabilities and evidence

The host authenticates before invoking the core. `AccessContext` is an immutable
trusted value with opaque principal ID, sorted unique repository grants,
sorted unique capability grants, authorization revision, issued time and
expiry. Its digest covers all its fields by the wrapper canonicalization.
No tokens, user models, request objects, sessions or OAuth-library objects cross
the core boundary. Public callers cannot submit this structure.

Authorization is revalidated by the host on **every invocation**, before
snapshot lookup, cache lookup or cursor verification. Revocation increments
the relevant authorization revision and invalidates prior contexts. Check expiry
at entry and immediately before delivery. The response authorization
linearization point is the host's final revision/expiry check: revocation
observed there cancels delivery; an already completed delivery is not recalled.
The host must not derive the revision from user input or reuse a cached grant
after revocation. Offline CLI grants are locally constructed and limited to its
explicitly opened repository; they confer no remote access.

Unknown or unauthorized repositories return the same `access_denied` boundary
result, with no publication/evidence details. A caller capability not granted
also returns `access_denied`. A granted but unimplemented query returns
`unsupported_capability`. Runtime attention-class availability remains in
the inherited C11 payload and is not equated to access permission.

`EvidenceIdentity` binds provider/profile versions, context digest, evidence
manifest digest, head-observation digest, bootstrap digest or null, algorithm
versions, and validated per-provider envelope digests. A missing provider has
an explicit unavailable identity rather than an empty “healthy” envelope.
SIDX's exact C6 unavailable marker/digest remains part of the inherited provider
identity. `identity_sha256` hashes the complete identity excluding itself.
A provider result includes availability, coverage and the pinned semantic
envelope. Fully available, available-but-incomplete, and unavailable retain
the owning truth tables; they are never collapsed into one Boolean.

Pinning is two-stage without reselection: EvidenceProvider.pin captures an
immutable EvidenceGeneration (profile/context/manifest/observation/bootstrap/
algorithm identities, availability and freshness). After semantic resolution
determines the requested document, read receives that same generation and the
resolved locator. The core validates returned envelopes and computes their
digests into the final EvidenceIdentity before cursor/cache use. C12 history
envelope identity is document-scoped; it cannot be known before resolution.
Unused envelope digests are null. Inherited provider identity follows
SIDX-06B §7.5.1 for C11 and is SHA-256 of the object with keys generation
(the complete EvidenceGeneration) and history_envelope_sha256 for C12,
using wrapper canonicalization.
For a C11 query whose owning profile does not bind a suspicion provider,
inherited_provider_identity is SHA-256 of wrapper-canonical JSON null; this
sentinel does not advertise evidence availability or bypass any validation.

Providers receive only the pinned publication/generation and validated locator. They
cannot reread mutable “current,” scan on demand, accept caller overrides or
return a different generation. Identity mismatch fails `evidence_mismatch`.
A provider exception uses the inherited unavailable/error mapping with no
exception text in public results. Invalid evidence cannot be “fixed” by
dropping validation fields. Existing memalpha locators remain typed data;
an absent resolver is unavailable, not a fabricated link.

The production evidence validator must retain SIDX-06D/06E closure checks,
digest binding, safe paths, resource limits and historical-profile validation.
Synthetic provider seams used by reference fixtures are explicitly test-only.

## 4. Requests and responses

The shared service receives a validated request, immutable host context and
explicit dependencies. `C11` accepts only the inherited search/family/
attention_class/native_state/tag/location_kind/limit/cursor dimensions.
`C12` accepts only requested_id and selection. Unknown public fields fail
`invalid_request` before dispatch, including provider overrides. Omitted
C11 limit is 50; allowed limits are 1–200. The owning normalization, Unicode
matching, OR-within/AND-across rules and exact five-part definition-site sort
key are retained; transport code does not normalize independently.

The schema describes valid requests, not error precedence. Malformed known
SIDX filter/cursor/requested_id fields use the owning contextual semantic
errors, including snapshot-unavailable precedence. Only malformed SBCT routing
fields, unknown fields and forbidden host-only fields use invalid_request.
Authentication/authorization always precedes snapshot or domain validation.

The result is one of:

- `semantic`: pinned SBCT context plus an **unchanged inherited semantic
  envelope**, including inherited contextual errors. A no-current result keeps
  inherited snapshot_unavailable with null index_commit/branch; the outer
  selection is null. A successful query always has selection.
- `boundary_error`: fixed code, safe fixed message and retryable Boolean,
  without selection or source evidence. Used only for SBCT authorization,
  context, profile, publication/storage and contract failures.

C11 data shape is items, total, facets and page; C12 is requested_id,
resolution, document, locations and history. Their nested schemas are owned
by pinned SIDX-06B §§7–8, enforced by the extracted shared validators and
reference vectors, not redefined by a generic JSON “success” shape.
The JSON Schema supplies a closed top-level frame and capability-specific
data keys; it deliberately does not substitute for inherited nested semantic
validation. A schema-only pass is insufficient for conformance.

Preserve error codes and contextual coverage exactly, including
`invalid_filter`, `invalid_cursor`, `cursor_snapshot_mismatch`,
`snapshot_unavailable`, `capability_unavailable`, `object_not_found` and
`ambiguous_object`. Authorization failures occur outside this semantic frame.
C11 partial rows never justify recomputing snapshot-wide provider metrics.
Facets/totals use the filtered pre-page row set. C12 returns all eligible
locations and ambiguity evidence; no preferred or first matching definition.

REST and MCP carry the same result object after removing transport framing.
The REST example maps access_denied to 403, invalid_request to 400, unsupported
profile/capability to 422, selection/idempotency conflicts to 409,
publication_required to 409, unavailable to 503 and validation/integrity errors
to 422. Authentication challenge/401 belongs to the host before this API.
Inherited semantic-error REST mappings remain SIDX-06B §9.3's mappings.
MCP uses its normal tool result framing, preserving the full same object and
setting isError for boundary/semantic errors. No adapter may turn unavailable
evidence into empty successful domain data.

Boundary messages are fixed by code: access_denied = "Access denied.";
invalid_request = "Invalid request."; unsupported_profile = "Unsupported profile.";
unsupported_capability = "Unsupported capability."; publication_required =
"Committed publication required."; selection_conflict = "Selection changed.";
idempotency_conflict = "Idempotency key conflict."; selection_unavailable =
"Selection unavailable."; invalid_bundle = "Invalid projection bundle.";
evidence_mismatch = "Evidence identity mismatch."; store_unavailable =
"Store unavailable."; signer_unavailable = "Cursor signer unavailable."
Only selection_conflict, store_unavailable and signer_unavailable have
retryable=true; retry always starts a new invocation and is never automatic.

## 5. Cursor and cache contract

The new token format is `sbct1.<kid>.<payload>.<signature>`.
`kid` is 1–32 ASCII letters/digits/underscore/hyphen. Payload and signature are
unpadded base64url. The payload is the exact canonical CursorClaims JSON
defined by the schema, including its final LF. Sign HMAC-SHA256 over ASCII
`sbct1.<kid>.<payload>`; verify with constant-time comparison. Algorithm is
fixed by version, never selected by a token field. Maximum token size is
8192 ASCII bytes; duplicate JSON keys, noncanonical encoding, extra fields,
invalid key/version and wrong signature are `invalid_cursor`.

Claims bind repository, snapshot ID, publication ID, projection commit,
capability-profile digest, evidence identity digest, inherited provider cursor
identity, access-context digest, query capability, normalized filter digest,
page limit, inherited five-part last-sort tuple, issued_at and expires_at.
The filter digest is the owning SIDX normalization/digest, not a new algorithm.
Limit is additionally bound even if omitted from the inherited digest.
Evidence must include head-observation identity because it can affect context.

TTL is exactly 900 seconds from trusted integer Unix issue time. Reject when
now < issued_at or now >= expires_at; no clock-skew allowance. Expired or
future tokens return semantic `invalid_cursor` with the owning generic message.
A correctly signed token with changed binding returns
`cursor_snapshot_mismatch`. Revoked/expired access fails earlier as
`access_denied`. Error details do not reveal which unauthorized binding changed.

Keys are host-supplied random secrets of at least 32 bytes, never source or
default Django SECRET_KEY. One active signing key; bounded verification ring.
Retiring keys may verify existing tokens until their original expiry; no
renewal on decode. Removal immediately invalidates tokens. Unknown kid,
legacy cursor versions and algorithm changes are rejected; a new algorithm
requires a new profile/version. Signing failure returns `signer_unavailable`,
never an unsigned continuation.

The optional PageCache is C11-only in this version. C12 invocations MUST NOT
read or write PageCache; each requested_id is resolved independently against
the pinned view. This restriction concerns query-result caching, not immutable
content storage. Any future C12 result cache requires a versioned contract
binding requested_id and every other result-affecting input.

Cache entries are immutable **unsigned C11 semantic page results**, not reusable
access decisions or final tokens. Cache key is SHA-256 of contract/profile
version, capability, repository/snapshot/publication/generation, normalized
filter digest and limit, cursor last-sort tuple or null, access-context digest,
evidence identity, inherited provider identity and semantic-engine digest.
Validate authorization and selection before lookup; sign a fresh continuation
only after validating the cached semantic page. All deadlines are integer Unix
seconds from the injected clock. At insertion, set expires_at to
min(now + 300, access.expires_at, selection.evidence.fresh_until).
Do not insert when fresh_until is zero or expires_at <= now. At lookup an
entry is expired when now >= expires_at, including equality. The service
rechecks the current access and evidence deadlines even if the cache backend
returns an expired entry. PageCache.get receives now and returns the entry's
expires_at so the service can enforce the same rule independently.

There is no separate evidence lease deadline in this version. Cache data is
not authority to retain or use a retired publication/evidence context: every
request must successfully open its pinned view and validate its evidence
before consulting PageCache. A missing or retired publication/view returns
the existing selection/store error, even if an entry remains in storage.
A previously cached evidence identity that cannot be validated is not reusable.
An invocation pinned to a valid unavailable-provider identity still follows
the inherited degraded-evidence truth tables, including partial results or
unknown staleness; this cache rule does not impose a new whole-query failure.
It cannot reuse an entry from the old identity or repin mid-request.
Reader leases in §2 protect in-flight immutable views; they are not cache TTLs.
Never cache unavailable operations or authorization failures. A cache read/
write failure bypasses cache and computes using the same pinned inputs; it
does not turn provider/store failure into success. A corrupted or differently
bound entry is a miss. Final authorization recheck still applies on a cache hit.

## 6. Evidence and acceptance matrix

[Reference vectors](evidence/sbct-02-reference-vectors.json) were produced by
executing the exact pinned query code with an isolated in-memory database and
synthetic providers. They cover empty/null results, order/facets/pages, invalid
filters, forged and mismatched cursors, missing suspicion, staleness, location
history availability, missing objects and ambiguity. They do not establish
portable, REST/MCP, production-provider, or storage atomicity conformance.

[Contract scenarios](evidence/sbct-02-contract-scenarios.json) specify additional
proposed cases, including identical content in two publications, revocation,
evidence/observation changes, key retirement, CAS conflict and failed ingest.
Their status is **specified, not executed**. Reference-producer execution
cannot prove newly proposed wrapper behavior.

| Gate | Package evidence | Still required |
|---|---|---|
| GATE-201 | Pinned query reference results | Same vectors through file/Django and transport adapters; complete semantic matrix |
| GATE-202 | Reference absence/history/ambiguity/null cases | Partial/invalid provider and all transport cases |
| GATE-203 | Atomic protocol and negative scenarios | Crash, concurrency, corrupt ingest and auth-preserving reset execution |
| GATE-204 | Existing cursor negative reference cases; new token contract | Proposed scoped/expired/revoked/rotated-key tests |
| GATE-205 | Explicit extraction and profile boundaries | Core import/dependency audit and production-history validation |
| GATE-206 | This package, source reconciliation and limited review; owner approval 2026-09-20 | Complete as specification approval |

GATE-206 is complete as owner specification approval. Implementation can proceed
under these interfaces; each runtime gate still requires its own evidence.

### Limited review disposition

A limited subagent review found two interface blockers: history result identity
was requested before its document scope was known, and store adapters had no
public access to validated candidate bytes. Both were corrected by separating
generation pinning from result identity and exposing immutable candidate files.
No owner approval or runtime conformance is inferred from that review.

The [structural validation report](evidence/sbct-02-contract-validation.json)
records 31 passing shape/digest checks and declaration syntax validation.
The 16 pinned reference vectors reproduced byte-for-byte in a second fresh
process. The [example context](contracts/query-contract.example.json) and
28 proposed runtime scenarios remain illustrative specifications.

### 0.1.1 — 2026-09-20 — cache review corrections

Limits query-result caching to C11 and specifies absolute cache deadlines,
including equality, absent freshness and independent service enforcement.
Removes the undefined evidence-lease expiry dependency. Adds four proposed
runtime witnesses; no runtime acceptance or owner approval is recorded.
The [limited change review](evidence/sbct-02-cache-review.json) records the
targeted review and its disposition separately from runtime evidence.

### Owner approval and initial execution — 2026-09-20

Ira Abbott explicitly approved GATE-206 and directed unblocked work to proceed.
Revision 0.1.1's contracts and compatibility dispositions are approved.
The prior review evidence retains its historical pre-approval status.
The first implementation slice has
[bounded cursor test evidence](evidence/sbct-02-cursor-execution.json);
GATE-201 through GATE-205 remain open.
