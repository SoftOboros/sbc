# SBCT-02 — Shared Queries, Stores and Provider Adapters

**Document ID:** SBCT-02
**Status:** RATIFIED — Ira Abbott, 2026-09-19
**Revision:** 0.6.2
**Date:** 2026-09-19
**Owner:** Ira Abbott
**Depends on:** [SBCT-00](SBCT-00-CONCEPTS.md), [SBCT-01](SBCT-01-REPOSITORY-CORE.md).

## §0 Authority Policy [Normative]

SIDX owns current query membership, filters, metrics, confidence and errors.
This phase MUST extract their implementation without changing those meanings.
`INV-SBCT-1`, `INV-SBCT-4`, `INV-SBCT-5`, `INV-SBCT-7` and `INV-SBCT-8`
are as defined in SBCT-00 §9; used without modification.

SBCT-00 is ratified as recorded in its §15 entry dated 2026-09-19. This child
was explicitly ratified by Ira Abbott on 2026-09-19, as recorded in §15.
The completed §8 contract package revision 0.1.1 was explicitly approved under
GATE-206 on 2026-09-20. Implementation is authorized; runtime gates remain open.

## §1 Purpose

Provide one semantic engine for file-backed local queries, Django-backed
queries, HTTP, MCP and Interlock. The transports only frame requests/results.

## §2 Evidence

Semantic queries and validation must be independent of ORM transactions,
framework settings, cache services and consumer-specific historical providers.

## §3 Canonical Glossary [Normative]

Host adapter and snapshot selection are as defined in SBCT-00 §3; used without
modification. Confidence, current snapshot and C11/C12 are as defined in
[SIDX-06B](https://github.com/iraabbott/softoboros.com/blob/751ffe62027a3030bc989d22f5c2f759234064dc/docs/todo/spec-index/TODO-SIDX-06B-SHARED-QUERIES-AND-TRANSPORT-PARITY.md);
used without modification in the selected compatibility profile.

## §4 Source-of-Truth Map [Normative]

| Surface | Owner |
|---|---|
| Query/result semantics and compatibility | SIDX-06B/06D/06E |
| Explicit core input interfaces and storage separation | This phase §5–§7 |
| Repository provenance | SBCT-01 |
| Request authentication/authorization | Host, subject to SBCT-03/05 |
| Interlock multi-repository composition | SBCT-05 |

## §5 Query Invocation [Normative]

One invocation MUST pin its repository scope, immutable snapshot content and
committed-publication provenance separately, validated
evidence context, capability set and authorization scope. The host MUST supply
store access, evidence/history providers, clock, optional cache and cursor
signer explicitly. The core MUST not read framework globals or select a newer
snapshot mid-response. These interfaces MUST have typed, versioned contracts
and unavailable/error behavior before implementation begins.

The core MUST own filtering, ordering, facets, pagination, membership and
confidence. Adapters MUST not duplicate these algorithms. Request adapters MUST
reject malformed inputs through the shared validation contract. Exception-to-
transport mapping MUST preserve the semantic error code and body.

## §6 Storage and Ingestion [Normative]

Validation MUST be callable without Django. Each adapter MUST expose the same
validated snapshot view. Candidate object/location/diagnostic projections MUST
be validated as one coherent bundle before atomic current-snapshot selection.
Failure MUST leave the previous selected snapshot intact.

The core file-backed view and Django store MUST produce equivalent semantics,
including duplicate-definition ambiguity and absent evidence. Projection reset
MUST delete only rebuildable projection data, never users, sessions or authored
source. Storage identifiers MUST not overwrite an existing repository's state
when another repository has the same commit or object ID. Global current
selection is per repository; the global host owns its selection of those states.

Ingesting a candidate and observing source head MUST remain separate operations.
A host MUST not silently ingest on read to hide a behind/stale condition.

## §7 Evidence, Capabilities and Cursors [Normative]

An evidence provider MUST return its identity, coverage and availability with
its result. Absence MUST not yield fabricated healthy metrics. Existing
`memalpha` locator records MUST remain readable as data even when their runtime
resolver is absent; resolving them MUST report the established unavailable
capability rather than require installing an external resolver service or invent a URL.

A consumer's historical bootstrap manifest/digests MUST move to an explicitly
selected compatibility profile. The generic validator MUST not default to that
profile. Selection MUST retain its exact validation strength; dependency
injection is not permission to accept unvalidated historical evidence.

A cursor MUST bind query/filter context, repository/snapshot selection and
authorized scope. Signer implementations MUST reject tampering and cross-scope
reuse. A cache key MUST include every context component affecting the result;
cache failure MUST not become fabricated query success. Key/algorithm/version
changes MUST have an explicit compatibility/rejection policy, owned by this
interface contract and reconciled with SIDX's existing cursor behavior.

## §8 Deferred Detail

**Completion package prepared, 2026-09-19:** The proposed
[typed contract package](SBCT-02-CONTRACT-PACKAGE.md) now supplies concrete
selection, provider, access, cursor/cache and atomic-publication interfaces,
exact query authority pins, schemas and reference evidence. Its details
were approved under GATE-206 on 2026-09-20; the historical accepted
directions below remain the record of the ratified architecture.

The parent layout decisions are approved. Detailed interfaces, query compatibility
profiles and cursor contracts remain required before implementation; the approved file-store/SQLite direction is not reopened. A different storage topology MUST not be labeled full SIDX
deployment conformance without reconciliation of SIDX's dedicated-store rule.

### Accepted review directions — 2026-09-19

Ira Abbott explicitly ACCEPTED all three review recommendations below. These
approvals authorize completion of the specified contracts; they do not assign
unspecified field values or claim successful acceptance evidence. Subsequent
explicit phase ratification is recorded in §15.

| Review item | Accepted direction | Required completion for full GATE-206 closure |
|---|---|---|
| 1 — Content and publication | Separate immutable snapshot content from its committed publication/provenance; pin both for each query. A content snapshot may have multiple publication commits. | Specify content/publication selection types and the mapping to index_commit, history and staleness; witness identical content in two commits without provenance conflation. |
| 2 — Query baseline | Pin exact SIDX-06B/06D/06E query authorities, implementation files and supported compatibility profiles. | Prepare the source/authority inventory and golden request/result reference fixtures; do not assume SBCT-01's producer baseline establishes query conformance. |
| 3 — Public contracts | Complete typed authorization/capability context, evidence identity, cursor binding/expiration, cache invalidation, atomic selection and error results. | Freeze concrete types and behavior, including revocation and stale-context negative cases; preserve pure-Python and host-owned identity boundaries. |

These review items are not new unresolved concepts PCDNs. Their architectural
direction is accepted; the named deliverables remain incomplete phase work.

### Historical interface direction — superseded by approved completion package

The following table records the pre-completion directions. The approved
SBCT-CONTRACT-02 revision 0.1.1 now owns the exact types and contracts.

| Interface | Candidate operation | Result / boundary |
|---|---|---|
| SnapshotStore | Content lookup and explicit committed-publication selection (exact signatures pending item 1) | Immutable content plus pinned publication/provenance, or typed unavailable result; content identity alone MUST NOT choose a publication |
| QueryService | `query(capability, selection, filters, access_context)` | Existing semantic payload plus provenance; no transport identity parsing |
| EvidenceProvider | `read(selection, locator)` | Evidence with coverage, integrity and availability |
| AccessContext | Immutable authorized repository set and authorization revision | Created by the host; never selected from caller-supplied user claims |
| CursorCodec | `encode(context)` / `decode(cursor, expected_context)` | Signed scope/filter/snapshot binding, rejection on mismatch |

An adapter first authenticates and authorizes; only the resulting immutable
scope enters the shared query service. A scope/authorization revision change
invalidates prior cache/cursor use. Storage/transport errors are typed adapter
results and do not manufacture domain values. File-store and Django-store
fixtures use the same validated bundle and shared query vectors.

To complete `GATE-206` before implementation: freeze types, capability-specific response schemas, cursor
serialization/signing/key lifecycle, atomic selection protocol and compatibility
versions. Choose no framework class or OAuth-library object as a public type.

## §9 Invariant Application [Normative]

The selected implementation MUST demonstrate §0's parent invariants with the
same semantic fixtures in every adapter. Transport-specific authentication is
outside semantic parity; authorized semantic payloads remain within it.

## §10 Reconciliation [Normative]

Split existing validation and semantic functions from their ORM composition.
Do not copy them into a parallel implementation. Keep production HTTP/MCP
authentication wrappers in each consumer; the distributed HTTP example is the
Django host specified by SBCT-03. MCP transport support MUST not import
a consumer MCP server or its identity system into the core.

## §11 Non-Goals

1. `NONGOAL-201` — **Query-time repair.** Queries MUST NOT repair source documents, clear suspicion, or update canonical indexes.
2. `NONGOAL-202` — **Invented capability completeness.** Extraction MUST NOT advertise unimplemented SIDX capabilities as available.

## §12 Acceptance [Normative]

A conforming query package MUST satisfy §5–§7 and §9–§10:

- [ ] `GATE-201` — Local/file and Django stores MUST pass identical golden request/result fixtures, including errors, ordering, facets and pagination.
- [ ] `GATE-202` — Missing/stale providers, ambiguous IDs, unavailable history and `null`/uncomputable metrics MUST remain distinct across Python, authorized REST and MCP framing.
- [ ] `GATE-203` — A corrupt candidate bundle MUST not replace the selected snapshot; deleting and rebuilding only projections MUST reproduce it while preserving auth data.
- [ ] `GATE-204` — Snapshot changes, altered filters, forged cursors and unauthorized scope reuse MUST be rejected according to the ratified compatibility contract.
- [ ] `GATE-205` — Core import/dependency audit MUST find no Django/settings/ORM/application auth imports; production profile fixtures MUST retain exact historical validation.
- [x] `GATE-206` — Owner MUST approve typed interfaces and applicable SIDX reconciliation before recording phase ratification.

**GATE-206 disposition (2026-09-20):** Ira Abbott explicitly approved GATE-206
after completion and limited review of contract package revision 0.1.1.
This closes the detailed-interface and compatibility approval prerequisite.
The earlier phase ratification remains recorded in §15. Implementation under
the approved package is now authorized; GATE-201 through GATE-205 remain open.


### Named witness specifications [Normative]

These cases MUST be specified for review now and executed only at their
applicable acceptance stage. They are not claims that tests already exist.

| Witness | Positive case | Negative case |
|---|---|---|
| `W-201-P` / `W-201-N` | Two independent adapters and CLI return the same semantic golden result from the same core version. | A deliberately altered adapter result or duplicate semantic engine fails parity review. |
| `W-202-P` / `W-202-N` | Empty, zero, null/uncomputable, stale and unavailable fixtures retain distinct prescribed results. | A provider that substitutes healthy/zero for missing evidence fails the semantic fixture. |

## §13 Files Cited

[SBCT-00](SBCT-00-CONCEPTS.md), [SIDX-06B](https://github.com/iraabbott/softoboros.com/blob/751ffe62027a3030bc989d22f5c2f759234064dc/docs/todo/spec-index/TODO-SIDX-06B-SHARED-QUERIES-AND-TRANSPORT-PARITY.md),
[SIDX-06D](https://github.com/iraabbott/softoboros.com/blob/751ffe62027a3030bc989d22f5c2f759234064dc/docs/todo/spec-index/TODO-SIDX-06D-CONFORMANCE-INPUTS-AND-GIT-PROVIDERS.md),
[SIDX-06E](https://github.com/iraabbott/softoboros.com/blob/751ffe62027a3030bc989d22f5c2f759234064dc/docs/todo/spec-index/TODO-SIDX-06E-C6-OBJECT-GRAPH-AND-ACKNOWLEDGMENT.md).

## §14 Unblocks

SBCT-03 reference backend, SBCT-04 dashboard integration and SBCT-05 Interlock.

## §15 Change Log

### 0.1.0 — 2026-09-18 — drafted

**Author:** Codex (draft author)
**Change kind:** scope
**Touches:** SBCT-02
**Commits:** none
**Summary:** Specifies one semantic engine with explicit storage and evidence adapters.

#### Rationale

Considered and rejected: independent CLI/global query implementations, implicit
framework state, and deleting historical validation while removing application
defaults. Deliberately unchanged: existing SIDX answers and error meanings.

### 0.2.0 — 2026-09-18 — owner-directed draft revision

**Author:** Codex
**Change kind:** scope
**Touches:** SBCT-02; parent INV-SBCT-3 and conformance boundaries
**Commits:** none
**Summary:** Incorporates accepted standalone conformance and explicit decision
closure; expands the example to MCP OAuth and separates consumer-specific
adoption from the portable contract. This is not family or phase ratification.

### 0.3.0 — 2026-09-19 — ratification package prepared

**Author:** Codex
**Change kind:** clarification
**Touches:** SBCT-02
**Commits:** none
**Summary:** Prepares explicit proposed decision dispositions, bounded
compatibility policy and child-owned witness specifications. Existing invariant
meanings are preserved. No decision acceptance or ratification is inferred.

### 0.5.0 — 2026-09-19 — child draft prepared

**Author:** Codex
**Change kind:** clarification
**Touches:** SBCT-02
**Commits:** none
**Summary:** Recognizes parent ratification and prepares concrete candidate
contracts and remaining prerequisites in §8. Child ratification and acceptance
are not claimed; all implementation gates remain unchecked.

### 0.6.0 — 2026-09-19 — review directions accepted

**Author:** Codex (recorder)
**Decision authority:** Ira Abbott, explicit acceptance of review items 1, 2 and 3
**Change kind:** clarification
**Touches:** SBCT-02
**Commits:** none
**Summary:** Records accepted content/publication separation, exact query baseline
preparation and completion of public contracts. The old content-only selection
signature is superseded as a proposal. Detailed types, reference fixtures and
negative witnesses remain pre-ratification work; no phase ratification or runtime
acceptance is inferred.

### 0.6.1 — 2026-09-19 — RATIFIED

**Ratifier:** Ira Abbott
**Authority:** Explicit owner instruction: "SBCT-02 is RATIFIED"
**Recorded by:** Codex
**Change kind:** clarification
**Touches:** SBCT-02
**Commits:** none
**Decision:** Ratifies revision 0.6.0's shared-query architecture and accepted
review directions. This entry records the owner act without inventing the
unfinished typed contracts, query baseline, reference fixtures or negative cases.
**Gate disposition:** GATE-206's requested ordering was overtaken by the explicit
owner ratification. Its outstanding specification deliverables remain an
implementation prerequisite, and the gate remains unchecked until those are
completed and reviewed. No runtime acceptance is claimed.
**Unblocks:** Dependent phase drafting and completion of §8's contract package.
No incomplete interface, extraction, implementation, publication or deployment
is implicitly approved by this record.

### 2026-09-19 — supporting completion package prepared (informative)

Codex prepared §8 navigation and the separate supporting contract/evidence
package for owner review.
The ratified architecture revision remains 0.6.1. No approval of new interface
details, GATE-206 completion or implementation acceptance is inferred.

### 0.6.2 — 2026-09-20 — GATE-206 approved

**Author:** Codex (recorder)
**Decision authority:** Ira Abbott
**Change kind:** clarification
**Touches:** SBCT-02
**Commits:** none
**Authority:** Explicit owner instruction: "GATE-206 is APPROVED - mark as such and proceed with unblocked work"
**Summary:** Approves SBCT-CONTRACT-02 revision 0.1.1, its typed interfaces,
compatibility dispositions and reviewed cache corrections. Checks GATE-206
and authorizes implementation under those contracts. Runtime acceptance,
dependent-phase ratification and release authorization remain separate.
