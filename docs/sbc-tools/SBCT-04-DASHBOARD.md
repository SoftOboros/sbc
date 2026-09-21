# SBCT-04 — Reusable Dashboard and Client

**Document ID:** SBCT-04
**Status:** DRAFT — pending ratification
**Revision:** 0.5.0
**Date:** 2026-09-19
**Owner:** Ira Abbott
**Depends on:** [SBCT-02](SBCT-02-QUERIES-AND-ADAPTERS.md); [SBCT-03](SBCT-03-DJANGO-REFERENCE.md) for the reference host.

## §0 Authority Policy [Normative]

This phase MUST own UI/client packaging without owning query semantics.
`INV-SBCT-1`, `INV-SBCT-7` and `INV-SBCT-11` are as defined in SBCT-00 §9;
used without modification. SIDX-06C remains the existing dashboard behavior
authority; any portable variation MUST be reconciled explicitly.

SBCT-00 is ratified as recorded in its §15 entry dated 2026-09-19. This child
is prepared for detailed review under that authority; it remains DRAFT.
Candidate detail in §8 requires this phase's owner review and ratification.

## §1 Purpose

Run the same inspectors, filters and work-item presentation in the Django
example and a consumer's global shell, with optional Interlock panels.

## §2 Evidence

Application context, navigation, localization and authenticated transport are
host responsibilities supplied through public interfaces.

## §3 Canonical Glossary [Normative]

Host adapter is as defined in SBCT-00 §3; used without modification. Work-item
membership, confidence and location results are as defined in SIDX-06B; used
without modification. The client MUST validate those responses, not redefine them.

## §4 Source-of-Truth Map [Normative]

| Surface | Owner |
|---|---|
| Query/result semantics | SIDX and shared SBCT-02 implementation |
| Response validation and portable component interfaces | This phase §5–§7 |
| Login, navigation, localization and site shell | Consuming host |
| Optional cross-repository findings | SBCT-05 |

## §5 Package Interfaces [Normative]

The client MUST accept an injected request transport with a base URL, request
cancellation and typed response/error handling. It MUST not import a production
token store, refresh handler or endpoint module. The reference host uses Django
sessions on the same origin; the consumer application host supplies its production transport.

Components MUST accept host navigation/location-opening, labels/localization
and shell integration through explicit interfaces. The reusable package MUST
not require framework routing, application context or a consumer header. It MAY retain
React/Chakra presentation dependencies, declared as versioned package contracts.
Exact exported interface signatures MUST be frozen before implementation.

## §6 Query and Session Behavior [Normative]

The dashboard MUST render server-computed membership, counts, confidence,
staleness and facets. It MUST not load committed corpus JSON as a substitute
semantic engine or persist corpus data in localStorage/IndexedDB. Transient
in-memory session state MAY support ordinary navigation and inspection.

Results and pagination MUST remain bound to the response context. A changed
repository, selected snapshot, filter or authorization scope MUST invalidate
incompatible pages and late responses. Pending requests MUST be canceled or
ignored after logout/scope change; prior protected data MUST be removed from
view and memory when the session loses access. Authentication expiry MUST
be handled by the host interface without interpreting a login page as data.

Zero, empty, partial, stale and uncomputable values MUST remain visibly distinct.
Locations requiring unavailable adapters MUST render as unavailable; the UI
MUST not fabricate URLs or auto-open locators from untrusted schemes.

## §7 Extension Panels [Normative]

Interlock panels MUST consume a declared capability contract. They MUST remain
separate from core findings and cannot overwrite a core confidence or native
state. Missing Interlock support MUST leave ordinary repo inspection usable.
Unrecognized extension versions MUST fail explicitly without executing code
supplied by repository content. There is no governance-write UI in this phase.

## §8 Deferred Detail

The proposed [dashboard host contract](SBCT-04-HOST-CONTRACT.md), prepared
2026-09-20, now supplies interface declarations, request/session lifecycle,
navigation boundaries, packaging requirements and named acceptance cases.
It remains draft work under GATE-406; source/dependency pins and owner review
are still required before implementation.

Host prop interfaces and navigation/error contracts require a recorded design
before code. The existing SIDX local-host admission policy must be reconciled
for a remote global host; removing the UI check is not an authorization design.

### Prepared candidate host contract

Propose a dashboard entry component accepting `client`, `navigation`, `labels`
and `scope` inputs. The client supplies work-item queries, facets, location
lookup and cancellation; navigation maps validated links; labels supply display
text; scope carries opaque selected repository/snapshot identities. Authentication
lives in the injected transport, never in component props containing credentials.

The client validates versioned payloads before presentation. A scope change
cancels pending work and drops protected rows; a late response for the old scope
is ignored. The component does not calculate semantic verdicts. An independent
shell fixture and the Django example consume the same built artifact.

Before `GATE-406`: freeze TypeScript types and API versions, loading/error and
pagination behavior, accessibility witnesses and static asset packaging. Node
may be a developer build tool but is not required to run shipped example assets.

## §9 Invariant Application [Normative]

The local and production shells MUST use the same component/client package
version for parity evidence. Host styling differences MUST not change semantics.

## §10 Reconciliation [Normative]

Extract existing review models, response validators and components. Consumer application
MUST retain its application providers in its wrapper, not in the package. Keep
existing source-safety, response-context and human-conformance tests as portable
fixtures; add host-specific tests outside the shared suite.

## §11 Non-Goals

1. `NONGOAL-401` — **Client semantic engine.** Browser code MUST NOT recalculate suspicion, membership or confidence from a cached corpus.
2. `NONGOAL-402` — **Governance editor.** UI controls MUST NOT ratify, clear, waive or amend specifications.

## §12 Acceptance [Normative]

A conforming dashboard package MUST meet §5–§7 and §9–§10:

- [ ] `GATE-401` — The same build MUST render in the minimal Django host and a host fixture without host routing, application context or production auth imports.
- [ ] `GATE-402` — Contract fixtures MUST preserve zero/null/uncomputable/stale distinctions, malformed-response rejection and context-safe pagination.
- [ ] `GATE-403` — Logout, revoked access and scope changes MUST clear protected rows and reject late responses; location adapters MUST reject unsafe schemes.
- [ ] `GATE-404` — Source/runtime checks MUST show no committed-corpus imports or browser corpus persistence; keyboard operation and readable status labels MUST work in both shells.
- [ ] `GATE-405` — With Interlock absent or incompatible, core views MUST remain usable and extension availability MUST be explicit.
- [ ] `GATE-406` — Owner MUST approve the host-interface contract and SIDX policy reconciliation before ratification.

### Named witness specifications [Normative]

These cases MUST be specified for review now and executed only at their
applicable acceptance stage. They are not claims that tests already exist.

| Witness | Positive case | Negative case |
|---|---|---|
| `W-401-P` / `W-401-N` | The same dashboard consumes shared response fixtures in independent hosts and retains metric/provenance distinctions. | A client recalculating semantic verdicts or persisting a corpus in browser storage fails source/runtime review. |

## §13 Files Cited

[SBCT-00](SBCT-00-CONCEPTS.md), [SBCT-02](SBCT-02-QUERIES-AND-ADAPTERS.md),
[SIDX-06B](https://github.com/iraabbott/softoboros.com/blob/751ffe62027a3030bc989d22f5c2f759234064dc/docs/todo/spec-index/TODO-SIDX-06B-SHARED-QUERIES-AND-TRANSPORT-PARITY.md),
[SIDX-06C](https://github.com/iraabbott/softoboros.com/blob/751ffe62027a3030bc989d22f5c2f759234064dc/docs/todo/spec-index/TODO-SIDX-06C-LOCAL-TSX-DASHBOARD.md).

## §14 Unblocks

Local-dashboard distribution and optional Interlock/global presentation.

## §15 Change Log

### 0.1.0 — 2026-09-18 — drafted

**Author:** Codex (draft author)
**Change kind:** scope
**Touches:** SBCT-04
**Commits:** none
**Summary:** Defines a host-independent consumer of shared query results.

#### Rationale

Considered and rejected: forking a local dashboard, carrying production token
refresh in the package and rebuilding query semantics in TypeScript.
Deliberately unchanged: upstream query answers and downstream shell ownership.

### 0.2.0 — 2026-09-18 — owner-directed draft revision

**Author:** Codex
**Change kind:** scope
**Touches:** SBCT-04; parent INV-SBCT-3 and conformance boundaries
**Commits:** none
**Summary:** Incorporates accepted standalone conformance and explicit decision
closure; expands the example to MCP OAuth and separates consumer-specific
adoption from the portable contract. This is not family or phase ratification.

### 0.3.0 — 2026-09-19 — ratification package prepared

**Author:** Codex
**Change kind:** clarification
**Touches:** SBCT-04
**Commits:** none
**Summary:** Prepares explicit proposed decision dispositions, bounded
compatibility policy and child-owned witness specifications. Existing invariant
meanings are preserved. No decision acceptance or ratification is inferred.

### 0.5.0 — 2026-09-19 — child draft prepared

**Author:** Codex
**Change kind:** clarification
**Touches:** SBCT-04
**Commits:** none
**Summary:** Recognizes parent ratification and prepares concrete candidate
contracts and remaining prerequisites in §8. Child ratification and acceptance
are not claimed; all implementation gates remain unchecked.
