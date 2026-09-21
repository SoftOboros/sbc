# SBCT-00 — SBC Supporting Tools: Concepts

**Document ID:** SBCT-00
**Status:** RATIFIED — Ira Abbott, 2026-09-19
**Revision:** 0.4.2
**Date:** 2026-09-21
**Owner:** Ira Abbott
**Blocks:** SBCT-01 through SBCT-06 implementation.

## §0 Authority Policy [Normative]

This family MUST derive SBC vocabulary and existing SIDX semantics from their
owners. It owns portable supporting-code boundaries and Interlock composition;
it MUST NOT redefine upstream object kinds, identifier grammar, edge kinds,
suspicion clearing, or ratification authority.

Ira Abbott ratified this concepts document on 2026-09-19. Its normative
architecture and approved decision dispositions govern child drafting. Child
phases remain drafts and MUST NOT be cited as implementation authority until
their own ratification and deferred prerequisites are complete.
The operational state is [AGENTS.md](AGENTS.md). Discrepancies MUST be recorded
at the owning specification before behavior changes.

The release's coherent SBC/SIDX/source pins MUST be selected under §8 before
extracting code. Extraction provenance and consumer-specific reconciliation
belong in the originating consumer's documentation, not this portable family.
A filesystem copy is not proof of a current upstream baseline.

## §1 Purpose

Deliver one reusable implementation for repository-level indexing and global
inspection, with an optional local dashboard and Interlock expansion. The
smallest tool works against an unrelated repository without consumer application services.

## §2 Evidence and Problem

Indexing helpers, query stores and dashboard hosts can couple semantic behavior
to framework settings, authentication and historical providers. This family
specifies the portable boundaries. Concrete source inventories and adoption
plans belong to each consumer and are not prerequisites for standalone use.

## §3 Canonical Glossary [Normative]

| ID | Term | Definition | Relationship |
|---|---|---|---|
| `TERM-001` | Shared core | The single implementation of parsing, validation and semantic queries; it MUST not depend on a host's framework or identity service. | Owned by SBCT-00; does not exist upstream yet. |
| `TERM-002` | Host adapter | A component supplying storage, transport, identity context or evidence acquisition to the core; it MUST not fork core semantics. | Owned by SBCT-00; does not exist upstream yet. |
| `TERM-003` | Repository scope | An explicit repository identity with source roots, selected revision and dependency pins; it MUST distinguish repositories sharing a local object ID. | Owned by SBCT-00; does not exist upstream yet. |
| `TERM-004` | Interlock | Cross-repository dependency and governance coordination over selected scopes; it MUST preserve each owning authority. | Owned by SBCT-00; does not exist upstream yet. |
| `TERM-005` | Reference backend | A minimal working Django host/example; it MUST use standard Django user/session authentication and the bounded MCP OAuth example in SBCT-03. | Owned by SBCT-00; does not exist upstream yet. |
| `TERM-006` | Snapshot selection | An immutable set of repository/snapshot pairs used for one query; it MUST not imply a global Git chronology. | Owned by SBCT-00; does not exist upstream yet. |

Spec objects, locations, amendments, suspicion and native states are as defined
in [ADDENDUM-C](../SBC-00-ADDENDUM-C.md); used without
modification. Query membership, confidence and transport parity are as defined
in [SIDX-06B](https://github.com/iraabbott/softoboros.com/blob/751ffe62027a3030bc989d22f5c2f759234064dc/docs/todo/spec-index/TODO-SIDX-06B-SHARED-QUERIES-AND-TRANSPORT-PARITY.md);
used without modification for the selected compatibility profile. Django auth
is composed as a framework facility, not redefined here.

## §4 Source-of-Truth Map [Normative]

| Surface | Sole owner | Consumer obligation |
|---|---|---|
| SBC discipline and object grammar | SBC concepts and addenda | Cite and pin; no local semantic replacement |
| Existing single-corpus delivery semantics | SIDX-00 and SIDX-06A through SIDX-06E | Preserve compatibility or obtain an owning amendment |
| Portable family invariants and profile membership | SBCT-00 | All child phases cite these definitions |
| Repository/configuration and source provenance | SBCT-01 | Reuse in local and global hosts |
| Store/provider interfaces and semantic extraction | SBCT-02 | One implementation across transports |
| Minimal Django composition | SBCT-03 | Host identity stays outside core |
| Client/dashboard composition | SBCT-04 | Consume responses; do not recalculate semantics |
| Interlock coordination envelope | SBCT-05 | No implied authority over participant repositories |
| Distribution/adoption evidence | SBCT-06 | No release claim without selected-profile evidence |
| Production identity, access, deployment | Each consuming project | Supply explicit integration outside distributed examples |

## §5 Distribution and Conformance Profiles [Normative]

The tooling MUST share the SBC repository and adoption submodule. Its code package
MUST remain separately installable from the document authority; tool installation is optional.
Its specifications MUST travel with that tooling; a migration MUST preserve
document IDs, revisions, links and provenance rather than create competing
authoritative copies. SIDX's portable source distribution is a §8 decision.

| Profile | Required phase acceptance | Conforming artifact |
|---|---|---|
| `core` | SBCT-01, SBCT-02, SBCT-06 | Installable Python package and CLI |
| `mcp-example` | `core`, SBCT-03 | Django example with OAuth-protected HTTP MCP; dashboard optional |
| `local-dashboard` | `core`, SBCT-03, SBCT-04 | Same-origin Django/OAuth example plus dashboard |
| `interlock` | `core`, SBCT-05, applicable SBCT-06 evidence | Multi-repository host; UI optional |

These SBCT profile values are ratified closed values. Registration policy:
Standards Action. They MUST NOT be reported as equivalent to all SIDX C1–C12
capabilities. Supported capabilities and unverified gates MUST be explicit.
An installation without Interlock MUST retain the complete `core` profile.

## §6 Dependency Direction [Normative]

Dependencies MUST point from hosts/adapters into the core. The core MUST NOT
import Django, FastAPI, consumer applications, cloud clients, or login/token code. The
optional Django adapter MAY depend on Django and the core. The example host
MAY additionally depend on its declared OAuth library; reusable interfaces MUST
NOT expose that library's internal types. The dashboard MUST
depend on its validated client contract and injected host interfaces. Production
integrations MUST reside in consumer code, not disabled shared-package branches.

## §7 Authority and Threat Boundaries [Normative]

Repository contents, plugin metadata, locators and remote evidence are untrusted
inputs. They MUST NOT select arbitrary executable plugins or cause network
access while scanning. Host-installed capabilities are selected explicitly.
Malformed paths, escaping symlinks and missing dependency pins MUST produce
safe findings/errors rather than scan outside declared scope or fetch silently.

The supplied example MUST use standard Django login for human queries and
OAuth for HTTP MCP as specified by SBCT-03; loopback origin is not identity.
OAuth belongs to the example host, never to the core. Downstream production auth
MUST authorize the repository scope before selection, counts, facets, locations
and cursors are produced. The initial tool and Interlock surfaces are read-only;
no dashboard action confers approval, ratification, waiver or clearance.

## §8 Decision Dispositions

Owner directions accepted on 2026-09-18: standalone conformance MUST NOT depend
on any named consumer's adoption; all concepts-level PCDNs MUST have explicit
dispositions; supplied examples include standard Django login plus minimal MCP
OAuth administration. Consumer production variants and their documentation
remain downstream. These directions supersede the earlier Django-only token
exclusion; they do not ratify this family or automatically resolve the PCDNs.

All four PCDNs were APPROVED by Ira Abbott on 2026-09-19, with the
clarifications recorded below. These approvals resolve the concepts-level
decisions and retain their bounded deferrals. They do not select unspecified schemas or pass child gates. Overall concepts
ratification was subsequently granted explicitly and is recorded in §15.

| ID | Approved disposition — Ira Abbott, 2026-09-19 | Explicit deferral and blocking gate |
|---|---|---|
| `PCDN-SBCT-00-001` | APPROVED: the bounded semantic-reuse policy in §10 and reconciliation before extraction. The reviewed-source inventory in the ratification packet identifies evidence only; it is not a selected release baseline. | Exact coherent SBC/SIDX authority and implementation commits, reviewed local patches, licenses and golden vectors MUST be selected and owner-approved at SBCT-01 `GATE-106`, with compatibility carried through SBCT-02 `GATE-206` and release `GATE-601`. No extraction or implementation before that selection. No full SIDX conformance claim. |
| `PCDN-SBCT-00-002` | APPROVED: one pure Python semantic core/CLI with validated file snapshots (Python and PyPI only; no third-party compiled C/native components, native build toolchain or administrator installation), optional Django store adapter, reusable React client/UI, and a separately packaged Django/SQLite example with standard human auth and MCP OAuth. Examples and production hosts consume public interfaces; neither may fork core semantics. | Configuration/CLI contracts: SBCT-01 `GATE-106`; typed store/provider/auth-context interfaces: SBCT-02 `GATE-206`; OAuth library/version, protocol details, admin/commands and store policy: SBCT-03 `GATE-307`; UI interfaces: SBCT-04 `GATE-406`. Each blocks its phase implementation. |
| `PCDN-SBCT-00-003` | APPROVED: optional Interlock, initially read-only with recorded submodule relationships as the initial directional model: host-registered repository identity plus immutable snapshot selection plus unchanged local object IDs. Cross-repository relationships are a separate versioned envelope, never new frozen SBC edge kinds or authority to clear another repository's findings. | Exact identity grammar, digest, relationship schema/vocabulary, ordering and capability negotiation: SBCT-05 `GATE-507`, before Interlock implementation. Core work does not depend on completing these details. |
| `PCDN-SBCT-00-004` | APPROVED, AMENDED 2026-09-21: one SBC repository and adoption submodule carrying the discipline, this portable doc family, and supporting tools; packages use explicit versions. Governing SIDX semantics have one authoritative home with provenance and must be accessible to intended consumers. Example maintenance and consumer production variants remain separate. | Repository/package names, exact SIDX authority distribution location, supported versions, license/access review, example support policy and publication process: SBCT-06 `GATE-607`, before release work; accessibility/provenance verified at `GATE-601`. Public visibility and deployment require separate owner actions. |

Decision history: revision 0.3.0 proposed these four dispositions for review;
revision 0.4.0 records the owner's explicit approvals. PCDN-002 clarifies
installation portability; PCDN-003 clarifies initial Interlock direction.
Original decision IDs and deferred gate ownership are preserved.

For PCDN-002, the standard Python interpreter and its standard library are the
baseline. Core runtime dependencies MUST be pure Python distributions available
from PyPI. Prebuilt wheels containing third-party native extensions do not meet
this requirement merely because they avoid a compiler. The core MUST NOT require
a Git executable, OS package manager, administrator permission or external
service. Git evidence capabilities MUST use an approved pure-Python provider or
explicit supplied evidence; missing evidence remains unavailable, never guessed.
Optional consumer integrations may have broader requirements, but they are not
prerequisites for the portable core. Developer UI builds are separate from
end-user installation; shipped example assets MUST not require Node to run.

For PCDN-003, a recorded parent-to-child submodule relationship identifies an
initial Interlock dependency: owning parent repository/snapshot, declared path,
registered child repository identity and recorded child commit. It does not
establish governance authority over the child. Nested relationships preserve
each parent's recorded pins; discovering a relation does not authorize fetching
or access. Submodules are the initial model, not a permanent restriction on
other explicitly specified cross-repository relations. Read-only behavior is an
initial stage; writes require the separate authority/transaction specification
already required by SBCT-05, not a new implicit permission from this approval.

## §9 Invariants [Normative]

Registration policy: Standards Action. Definitions occur only in this table.

| ID | Obligation | Verification surface |
|---|---|---|
| **INV-SBCT-1** | The CLI and global host MUST use the same versioned core semantic implementation. | Dependency graph and parity fixtures in SBCT-02/06 |
| **INV-SBCT-2** | The core MUST run without Django, consumer application services, credentials or network access. | Clean isolated installation and offline fixture in SBCT-01 |
| **INV-SBCT-3** | Every supplied backend MUST be a bounded example using standard Django human authentication plus MCP OAuth as specified by SBCT-03; enterprise and production auth integrations MUST be supplied downstream. | Source/dependency audit and auth witnesses in SBCT-03 |
| **INV-SBCT-4** | SBCT MUST preserve the pinned SBC/SIDX definitions and MUST NOT silently extend frozen grammar. | Authority manifest and compatibility review in SBCT-06 |
| **INV-SBCT-5** | Every result MUST retain its repository, snapshot and evidence context; working-tree observations MUST NOT impersonate committed evidence. | Dirty-tree, same-ID and missing-history fixtures in SBCT-01/05 |
| **INV-SBCT-6** | Authorization MUST restrict scope before aggregation; results, caches and cursors MUST NOT disclose inaccessible scopes. | Denied-repository and revocation witnesses in SBCT-05 |
| **INV-SBCT-7** | Missing, stale, ambiguous and uncomputable evidence MUST remain distinct from empty, zero or healthy results. | Provider and transport parity fixtures in SBCT-02/04 |
| **INV-SBCT-8** | Derived stores MUST remain reconstructible from declared sources; authentication records MUST NOT be treated as disposable projection data. | Rebuild and targeted-reset witnesses in SBCT-03/06 |
| **INV-SBCT-9** | Submodule evidence MUST use the recorded child pin and owning Git history, not fabricated parent paths. | Two-repository pin/missing-history witnesses in SBCT-01 |
| **INV-SBCT-10** | Extensions MUST NOT mutate core verdicts, infer approvals, or create implicit suspicion clearings. | Unsupported-extension and governance negative fixtures in SBCT-05 |
| **INV-SBCT-11** | The dashboard MUST consume shared queries and MUST NOT maintain a second semantic engine or persist a corpus in browser storage. | Client safety and cross-host UI fixtures in SBCT-04 |
| **INV-SBCT-12** | Ratification, implementation, verification, publication and deployment MUST be recorded separately; agents MUST NOT self-authorize them. | Phase/release evidence review in SBCT-06 |

## §10 Reconciliation — Adjacent Primitives [Normative]

Each row declares the six authority axes. Implementations MUST honor these boundaries.

| Upstream authority | Local representation | Mutation rights | Divergence policy | Downstream consumers | Conformance test owner |
|---|---|---|---|---|---|
| SBC concepts/addenda | Pinned document reference; `derive` | SBC owner only | Owning amendment before semantic change | All profiles | SBC for grammar; SBCT for extraction parity |
| SIDX delivery family | Pinned query/evidence contract; `derive` | SIDX owner for existing semantics | Record incompatibility; no silent profile weakening | Queries, dashboard, Interlock | SIDX semantics; SBCT adapter parity |
| Django authentication | Framework auth/session composition; `compose` | Django upstream; host config within SBCT-03 | Standard Django identity plus bounded MCP OAuth example | Reference host and adopting Django sites | SBCT-03 |
| Git | Commit/tree/gitlink evidence; `compose` | Repository owner | Missing history stays unavailable; no invented chronology | Scanner, history, Interlock | SBCT-01/05 |
| Consumer production systems | Injected adapters; `compose` | Consumer owner | No shared-core fork; compatibility failure explicit | Adopting hosts | Consumer, with SBCT-06 parity |

SIDX's dedicated database, local-host presentation policy, one-corpus identity,
fixed historical authority and MCP scope/role auth policy MUST be reviewed explicitly before selecting a
portable compatibility profile. This contract MUST NOT repeal existing SIDX gates.

In particular, SIDX `INV-SIDX-8` owns an existing host-specific authorization
policy. The portable example composes Django identity and OAuth and MUST NOT
claim that this alone satisfies that host policy. The release compatibility
map MUST identify preserved semantic clauses, excluded host-specific deployment
claims, and any required owning amendments. Consumers maintain their own policy
mapping; example OAuth is not an amendment to their production authorization.

### Approved bounded compatibility disposition

This table owns the concepts-level semantic-reuse policy approved under PCDN-001.
It applies to the reviewed clauses listed in the [ratification packet](RATIFICATION.md),
not to an unspecified future upstream revision. Final pins and any additional
conflicts remain subject to `GATE-106`/`GATE-206` and release `GATE-601`.

| Source clause | Portable disposition | Claim limit / owning amendment trigger |
|---|---|---|
| SBC concepts and ADDENDUM-C object grammar; SIDX `INV-SIDX-1` | Preserve object IDs, attributes, frozen enums and local edges. Interlock adds only a separate envelope. | New authored vocabulary requires an SBC amendment first. Scanner grammar gaps are implementation debt, not authority to redefine the grammar. |
| SIDX `INV-SIDX-2`, `INV-SIDX-9`, §7 | Preserve read-only corpus/governance queries and Git-owned mutation. | Example OAuth/login/admin writes manage identity only, outside SIDX corpus surfaces. No claim that the entire example exposes no writes. Any corpus write requires an owning amendment. |
| SIDX `INV-SIDX-3`, `INV-SIDX-5`, `INV-SIDX-12`; SIDX-06B | Preserve index commit, staleness, confidence, native state, locator and attribute provenance on applicable results. | No fabricated healthy/zero state. A changed semantic result requires an owning amendment and revised vectors. |
| SIDX `INV-SIDX-4`, §7 | Preserve named capability tools for every capability exposed; no generic SQL/DSL replacement. | Profiles declare supported capabilities; partial support is not full C1–C12 conformance. |
| SIDX `INV-SIDX-6`, `INV-SIDX-7`, §5.1 | Preserve reproducible projection ingestion from committed index/evidence. Separate CLI working-tree observations from ingestible committed snapshots. | Projection reset never drops identity data. Working-tree reports cannot impersonate committed SIDX evidence. |
| SIDX §5 store topology | Use file snapshots for core and SQLite for the example; host-selected store adapters remain possible. | Dedicated-database deployment conformance is excluded. Altering an existing consumer's topology requires its own review/amendment where governed. |
| SIDX `INV-SIDX-8` | Preserve the principle that the host authorizes scope; portable example composes Django identity plus MCP OAuth. | Existing MCP key/role policy conformance is excluded. No consumer auth policy is repealed; changing it requires an owning amendment. |
| SIDX `INV-SIDX-10`, `INV-SIDX-11`; SIDX-06B | Preserve one Python semantic engine and authorized REST/MCP payload parity for shared capabilities. | Transport identity mechanisms may differ; semantic payload differences require an owning amendment. |
| SIDX-06C host presentation | Preserve read-only query-driven presentation, provenance and unavailable-state distinctions; inject shell/navigation/auth transport. | Existing host routing/local-host deployment policy is not a portable claim. The example's loopback/auth policy belongs to SBCT-03. |
| SIDX-06D historical evidence and providers | Preserve validation strength for any declared historical compatibility profile; generic core has no default consumer history authority. | Absent history stays unavailable. Exact authority digests/providers must be declared in the selected profile; weaker validation requires an owning amendment. |
| SIDX single-corpus query scope; SBCT-05 composition | Preserve each participant's local answer; qualify identities and pin immutable snapshot selections. | Cross-repository chronology and binding governance are not inferred. Any change to a participant's answer requires the owning semantic amendment. |

### Invariant-to-witness coverage

Witness specifications are owned by the named child sections. This mapping
satisfies the documentation obligation only after review; all executions remain
unproven. Single-repository authorization witnesses apply even without Interlock.

| Invariant | Positive / negative witness names | Owning phase and acceptance gate |
|---|---|---|
| `INV-SBCT-1` | `W-201-P` / `W-201-N` | SBCT-02 §12, `GATE-201` |
| `INV-SBCT-2` | `W-101-P` / `W-101-N` | SBCT-01 §12, `GATE-101` |
| `INV-SBCT-3` | `W-301-P` / `W-301-N` | SBCT-03 §12, `GATE-304`, `GATE-308` |
| `INV-SBCT-4` | `W-601-P` / `W-601-N` | SBCT-06 §12, `GATE-601` |
| `INV-SBCT-5` | `W-102-P` / `W-102-N` | SBCT-01 §12, `GATE-104` |
| `INV-SBCT-6` | `W-302-P` / `W-302-N`; `W-501-P` / `W-501-N` when Interlock applies | SBCT-03 §12, `GATE-309`; SBCT-05 §12, `GATE-503` |
| `INV-SBCT-7` | `W-202-P` / `W-202-N` | SBCT-02 §12, `GATE-202` |
| `INV-SBCT-8` | `W-303-P` / `W-303-N` | SBCT-03 §12, `GATE-305`, `GATE-309`; core recovery under SBCT-06 `GATE-604` |
| `INV-SBCT-9` | `W-103-P` / `W-103-N` | SBCT-01 §12, `GATE-104` |
| `INV-SBCT-10` | `W-502-P` / `W-502-N` | SBCT-05 §12, `GATE-505` |
| `INV-SBCT-11` | `W-401-P` / `W-401-N` | SBCT-04 §12, `GATE-402`, `GATE-404` |
| `INV-SBCT-12` | `W-602-P` / `W-602-N` | SBCT-06 §12, `GATE-606`, `GATE-607` |

## §11 Non-Goals

1. `NONGOAL-001` — **Redefining SBC.** SBCT MUST NOT become the owner of discipline or object vocabulary.
2. `NONGOAL-002` — **Shipping production identity.** The distribution MUST NOT include consumer identity systems, billing, tenancy, social login or enterprise auth services. Minimal MCP OAuth in SBCT-03 is an explicit example-only inclusion.
3. `NONGOAL-003` — **Automatic governance mutation.** Initial tools MUST NOT ratify, waive, clear or write authored governance decisions.
4. `NONGOAL-004` — **Deployment authorization.** Ratification MUST NOT be treated as permission to expose a repository or change production access.

## §12 Acceptance [Normative]

Specification ratification requires the following review gates; implementation
acceptance is separately owned by the selected phases. A conforming artifact
MUST satisfy its §5 profile and the applicable §0/§3–§10 obligations.

- [x] `GATE-001` — Owner MUST review and accept authority, glossary and profile boundaries (§0, §3–§5).
- [x] `GATE-002` — Owner MUST resolve all §8 PCDNs with the explicit dispositions defined there and record ratification explicitly in §15.
- [x] `GATE-003` — Every §9 invariant MUST have the named positive and negative witness specified in its owning phase.
- [x] `GATE-004` — Compatibility review MUST record SIDX conflicts and their owning amendments or bounded profile claims (§10).
- [x] `GATE-005` — Backend/auth and extension threat boundaries MUST be approved without weakening the user's fixed requirement (§6–§7).

## §13 Files Cited

[SBC concepts](../SBC-00-CONCEPTS.md),
[ADDENDUM-C](../SBC-00-ADDENDUM-C.md),
[ADDENDUM-D](../SBC-00-ADDENDUM-D.md),
[SIDX-00](https://github.com/iraabbott/softoboros.com/blob/751ffe62027a3030bc989d22f5c2f759234064dc/docs/todo/spec-index/TODO-SIDX-00-CONCEPTS.md),
[SIDX-06B](https://github.com/iraabbott/softoboros.com/blob/751ffe62027a3030bc989d22f5c2f759234064dc/docs/todo/spec-index/TODO-SIDX-06B-SHARED-QUERIES-AND-TRANSPORT-PARITY.md),
[SIDX-06D](https://github.com/iraabbott/softoboros.com/blob/751ffe62027a3030bc989d22f5c2f759234064dc/docs/todo/spec-index/TODO-SIDX-06D-CONFORMANCE-INPUTS-AND-GIT-PROVIDERS.md),
[SIDX-06E](https://github.com/iraabbott/softoboros.com/blob/751ffe62027a3030bc989d22f5c2f759234064dc/docs/todo/spec-index/TODO-SIDX-06E-C6-OBJECT-GRAPH-AND-ACKNOWLEDGMENT.md),
[ERRATA](ERRATA.md).

## §14 Unblocks

Ratification unblocks detailed execution planning for selected child phases.
Each phase still requires its own ratification and resolved dependencies.

## §15 Change Log

### 0.1.0 — 2026-09-18 — drafted

**Author:** Codex (draft author; Ira Abbott is the owner and ratifier)
**Change kind:** scope
**Touches:** INV-SBCT-1, INV-SBCT-2, INV-SBCT-3, INV-SBCT-4, INV-SBCT-5, INV-SBCT-6, INV-SBCT-7, INV-SBCT-8, INV-SBCT-9, INV-SBCT-10, INV-SBCT-11, INV-SBCT-12
**Commits:** none
**Summary:** Opens the independent supporting-code family under the owner's authorization.

#### Rationale

The existing implementation contains reusable semantics but application-bound
composition. Considered and rejected: bundling runtime code into the SBC
document authority, copying the global query engine for local use, and shipping
production auth disabled by flags. Deliberately unchanged: SBC/SIDX authority,
current runtime behavior, historical evidence, and human approval rights.

### 0.2.0 — 2026-09-18 — owner-directed draft revision

**Author:** Codex
**Change kind:** scope
**Touches:** SBCT-00; parent INV-SBCT-3 and conformance boundaries
**Commits:** none
**Summary:** Incorporates accepted standalone conformance and explicit decision
closure; expands the example to MCP OAuth and separates consumer-specific
adoption from the portable contract. This is not family or phase ratification.

### 0.3.0 — 2026-09-19 — ratification package prepared

**Author:** Codex
**Change kind:** clarification
**Touches:** SBCT-00
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

### 0.4.1 — 2026-09-19 — RATIFIED

**Ratifier:** Ira Abbott
**Authority:** Explicit owner instruction: "SBCT-00 is RATIFIED"
**Recorded by:** Codex
**Change kind:** clarification
**Touches:** SBCT-00
**Commits:** none
**Decision:** Ratifies revision 0.4.0's concepts, approved PCDNs and bounded
deferrals; revision 0.4.1 records that act and updates status language only.
**Review evidence:** Two limited document reviews confirmed decision closure,
compatibility disposition and named witness coverage. GATE-001 through GATE-005
are satisfied as specification-review gates; witness execution is not claimed.
**Unblocks:** Detailed child-phase drafting and execution planning under this
contract. No child phase, extraction, implementation, runtime verification,
publication or deployment is ratified or proven by this entry. Exact source
and authority pins remain required at GATE-106 before extraction.


### 0.4.2 — 2026-09-21 — Unified repository amendment

The owner clarified that SBC and its supporting tools are one item and approved
consolidation into `SoftOboros/sbc`. This supersedes the separate-repository
portion of PCDN-SBCT-00-004 and amends §5. Package, semantic-authority, example
maintenance and downstream production boundaries remain distinct. No runtime
gate or draft phase is ratified by this repository amendment. See
[the migration record](REPOSITORY-CONSOLIDATION.md).
