# SBCT-05 — Interlock Repository and Governance Coordination

**Document ID:** SBCT-05
**Status:** DRAFT — pending ratification
**Revision:** 0.5.0
**Date:** 2026-09-19
**Owner:** Ira Abbott
**Depends on:** [SBCT-02](SBCT-02-QUERIES-AND-ADAPTERS.md); SBCT-04 only for UI integration.

## §0 Authority Policy [Normative]

Interlock is cross-repository dependency and governance coordination, as
confirmed by the owner. This phase MUST own its composition envelope; it MUST
not acquire governance authority over participating repositories.
`INV-SBCT-4`, `INV-SBCT-5`, `INV-SBCT-6`, `INV-SBCT-7`, `INV-SBCT-9` and
`INV-SBCT-10` are as defined in SBCT-00 §9; used without modification.

SBCT-00 is ratified as recorded in its §15 entry dated 2026-09-19. This child
is prepared for detailed review under that authority; it remains DRAFT.
Candidate detail in §8 requires this phase's owner review and ratification.

## §1 Purpose

Allow a global host to inspect explicit dependencies and their governance
evidence across repositories while each repository remains independently usable.

## §2 Evidence

Current storage identifies a snapshot by a unique commit and assumes one current
corpus. Identical IDs and commits can occur in different repositories. Selecting
several single-corpus stores does not itself define a coherent global query.

## §3 Canonical Glossary [Normative]

Interlock, repository scope and snapshot selection are as defined in SBCT-00 §3;
used without modification. Local object identity remains owned by SBC. The
repository/snapshot envelope MUST not be serialized as a new local SBC object ID.

## §4 Source-of-Truth Map [Normative]

| Surface | Owner |
|---|---|
| Local objects, status and authoritative governance records | Participating repository under its governing specs |
| Registered repository identity and accessible scope | Host configuration and authorization |
| Snapshot-set selection, relationship envelope and aggregation | This phase §5–§7 |
| Local semantic evaluation | Shared SBCT-02 implementation |
| New SBC normative edge kinds or clearing semantics | SBC/SIDX owning amendment process |

## §5 Scope and Identity [Normative]

A target MUST retain repository identity, selected snapshot identity and the
unchanged local object ID. Repository identity MUST be explicitly registered;
remote URL spelling, clone directory or array position MUST not silently choose
it. Alias/rename handling MUST preserve identity through a recorded host mapping.
An ambiguous local ID within its own repository MUST remain ambiguous globally.

One global query MUST select an immutable set of repository/snapshot pairs and
return its selection identity. Branch heads MUST be resolved before evaluation;
mixed-time reads MUST not be reported as one coherent result. Missing/stale
participants MUST remain explicitly unavailable/partial. A timestamp or commit
hash from separate repositories MUST not be treated as a global ordering proof.

Submodule references MUST preserve both the parent pin and the selected child
revision. A query MAY inspect a newer child separately, but MUST not report it
as satisfying the parent's pinned dependency without evidence and explicit policy.

The approved initial directional model is the recorded parent-to-child submodule
relation described in SBCT-00 §8. The parent gitlink pin and the registered child
identity identify a dependency, not a delegation of governance authority. The
relation envelope MUST retain parent snapshot, child pin and declared path;
nested traversal MUST preserve each owning parent's evidence and terminate on
cycles. URLs alone do not establish identity or grant fetch/access permission.
Later non-submodule relations or write orchestration require an explicit contract
and the applicable owner approvals; the initial read-only stage is not a permanent
prohibition on that evolution.

## §6 Dependency and Governance Evidence [Normative]

Interlock relationships MUST be explicit, provenance-bearing records in a
versioned, separately owned envelope. Every relation MUST identify its source,
target, exact revision scope and declaring authority/evidence. Inferred candidate
relations MUST remain labeled proposals and MUST not become binding edges.
The exact relation vocabulary/schema MUST be ratified under the parent decision
before implementation; this draft does not register new SBC `EdgeType` values.

Governance coordination in v1 MUST be read-only: evaluate dependencies, display
known owner decisions and unresolved obligations, and expose evidence. It MUST
not create or infer approvals, waivers, ratification, acknowledgments or clearing
acts. A participant's binding status cannot be strengthened by an Interlock
summary. Future write/approval orchestration requires a separately ratified
authority and transaction protocol, not an extension callback.

Cycles and duplicate declarations MUST be surfaced deterministically; traversal
MUST terminate without using input order to choose an authority or target. Local
suspicion stays owned by SBC/SIDX. Cross-repository impact findings MUST be
distinct Interlock results unless the upstream contract explicitly authorizes
propagation/clearing across that boundary.

## §7 Authorization, Capabilities and Failure [Normative]

The host MUST authorize each repository before reading its selected content or
aggregating results. Unauthorized repositories MUST not contribute hidden
counts, facets, links, error detail or cursor material. A reference from a visible
repository to an inaccessible target MAY preserve only the declaration already
visible in the source; it MUST not confirm private target existence or state.

Caches/cursors MUST bind the authorized repository set, effective authorization
context, snapshot selection and query. Revocation MUST prevent reuse of prior
privileged cached results. Extensions MUST be host-installed and explicitly
enabled. Unknown versions or unavailable resolvers MUST return an explicit
unsupported/unavailable result without rewriting core verdicts or fetching
arbitrary URLs. Safe failure MUST not erase the accessible scope's own findings.

## §8 Open Detail

`PCDN-SBCT-00-003` owns the architectural boundary. This phase, gated by
`GATE-507`, owns the exact repository identity grammar, selection digest,
relation schema, deterministic ordering and capability negotiation. These are
pre-implementation decisions, not knobs to be chosen independently by adapters.
The production host owns authentication; any supplied example host remains
subject to SBCT-03's Django and MCP OAuth example boundary.

### Prepared candidate submodule relation envelope

Propose these fields for `GATE-507` schema review: `schema_version`,
`parent_repository_id`, `parent_snapshot_id`, `submodule_path`,
`child_repository_id`, `child_commit`, and `evidence_locator`. The path and child
pin come from the selected parent tree; registered identity supplies the child
repository mapping. A remote URL is evidence for mapping, not an identity or an
instruction to fetch. Missing mapping or history yields an explicit unavailable
relation rather than a guessed target.

The envelope describes parent-to-child dependency evidence only. Each nested
relation is evaluated against its own parent snapshot; choosing a newer child
head does not rewrite the parent's recorded pin. Duplicate declarations and
cycles remain visible, and traversal terminates. No envelope field authorizes
an approval, acknowledgment, waiver or clearing operation.

Before `GATE-507`: freeze identity grammar, serialization, selection digest,
ordering, compatibility negotiation and treatment of absent/denied children.
Other relation types and write orchestration require their own explicit contract.

## §9 Invariant Application [Normative]

Interlock MUST pass the same local query fixtures as the core for each permitted
participant. Its extra envelope MUST not alter the participant's semantic answer.

## §10 Reconciliation [Normative]

Use the existing provider/query seams and scoped source evidence. Do not expand
the single-corpus global-ID grammar by concatenating repository names into
authored documents. Register any additional normative relationship upstream
before implementing it as an SBC relation. A separately named Interlock result
is delivery evidence, not a loophole for changing core obligations.

## §11 Non-Goals

1. `NONGOAL-501` — **Global sovereign authority.** Interlock MUST NOT approve or overrule an owning repository's decisions.
2. `NONGOAL-502` — **Silent cross-repository clearance.** A local acknowledgment MUST NOT clear another repository's findings implicitly.
3. `NONGOAL-503` — **Automatic repository enrollment.** Discovering a remote or submodule MUST NOT grant access or enable its scope.

## §12 Acceptance [Normative]

A conforming Interlock host MUST meet §5–§7 and §9–§10:

- [ ] `GATE-501` — Two repositories sharing a local object ID and a commit MUST remain independently addressable; ambiguity inside one MUST remain visible.
- [ ] `GATE-502` — Queries MUST pin a reproducible snapshot set; head changes mid-query and a child differing from the parent's pin MUST not silently change results.
- [ ] `GATE-503` — Unauthorized and subsequently revoked repositories MUST not leak through results, facets, locations, errors, cache hits or cursors.
- [ ] `GATE-504` — Missing evidence, incompatible extension versions and cycles MUST produce deterministic bounded results without fabricating healthy or complete state.
- [ ] `GATE-505` — Proposed relations, local approvals and local clearings MUST not acquire cross-repository binding force or modify native state.
- [ ] `GATE-506` — Disabling Interlock MUST leave the core profile fully usable; local semantic fixtures MUST still match the global host's permitted participant answers.
- [ ] `GATE-507` — Owner MUST resolve the §8 schema/authority decisions and record ratification before implementation.

### Named witness specifications [Normative]

These cases MUST be specified for review now and executed only at their
applicable acceptance stage. They are not claims that tests already exist.

| Witness | Positive case | Negative case |
|---|---|---|
| `W-501-P` / `W-501-N` | Authorized repository selections return only their scoped participant results. | A denied or revoked participant cannot leak through counts, facets, locations, errors, cursors or cached responses. |
| `W-502-P` / `W-502-N` | A proposed relationship is displayed as a proposal while native participant states stay unchanged. | An extension that infers approval, rewrites a verdict or clears another repository fails the extension contract. |

## §13 Files Cited

[SBCT-00](SBCT-00-CONCEPTS.md), [SBCT-01](SBCT-01-REPOSITORY-CORE.md),
[SBCT-02](SBCT-02-QUERIES-AND-ADAPTERS.md),
[SIDX-06E](https://github.com/iraabbott/softoboros.com/blob/751ffe62027a3030bc989d22f5c2f759234064dc/docs/todo/spec-index/TODO-SIDX-06E-C6-OBJECT-GRAPH-AND-ACKNOWLEDGMENT.md).

## §14 Unblocks

An optional Interlock host and its release-conformance suite; no governance writes.

## §15 Change Log

### 0.1.0 — 2026-09-18 — drafted

**Author:** Codex (draft author)
**Change kind:** scope
**Touches:** SBCT-05
**Commits:** none
**Summary:** Defines Interlock as explicit read-only coordination over scoped repositories.

#### Rationale

Considered and rejected: flattened IDs, ambient federation, timestamp-based
global ordering, and extension-driven approval/clearing. Deliberately unchanged:
local object grammar, native state and the authority of each repository owner.

### 0.2.0 — 2026-09-18 — owner-directed draft revision

**Author:** Codex
**Change kind:** scope
**Touches:** SBCT-05; parent INV-SBCT-3 and conformance boundaries
**Commits:** none
**Summary:** Incorporates accepted standalone conformance and explicit decision
closure; expands the example to MCP OAuth and separates consumer-specific
adoption from the portable contract. This is not family or phase ratification.

### 0.3.0 — 2026-09-19 — ratification package prepared

**Author:** Codex
**Change kind:** clarification
**Touches:** SBCT-05
**Commits:** none
**Summary:** Prepares explicit proposed decision dispositions, bounded
compatibility policy and child-owned witness specifications. Existing invariant
meanings are preserved. No decision acceptance or ratification is inferred.

### 0.4.0 — 2026-09-19 — owner decision approvals recorded

**Author:** Codex (recorder)
**Decision authority:** Ira Abbott, explicit approval on 2026-09-19
**Change kind:** clarification
**Touches:** PCDN-SBCT-00-001, PCDN-SBCT-00-002, PCDN-SBCT-00-003, PCDN-SBCT-00-004
**Commits:** none
**Summary:** Records approved semantic reuse, pure-Python/PyPI core portability,
submodule-based initial Interlock direction and separate tooling repository.
Deferred child gates remain required. Overall concepts ratification, child
ratification, implementation and publication are not inferred.

### 0.5.0 — 2026-09-19 — child draft prepared

**Author:** Codex
**Change kind:** clarification
**Touches:** SBCT-05
**Commits:** none
**Summary:** Recognizes parent ratification and prepares concrete candidate
contracts and remaining prerequisites in §8. Child ratification and acceptance
are not claimed; all implementation gates remain unchecked.
