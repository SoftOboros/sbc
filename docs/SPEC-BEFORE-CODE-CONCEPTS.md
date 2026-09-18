# TODO-SBC-00 — Spec-Before-Code: Concepts, Vocabulary, and Frozen Invariants

**Document ID:** SPEC-BEFORE-CODE-CONCEPTS

> ⛔ **SUPERSEDED — 2026-05-31.** This is the **predecessor / input** document. It was the
> in-repo, softoboros-relative rendering of the discipline (paths point at `../CLAUDE.md` and
> `todo/…`). It has been synthesised into the portable, self-contained
> [`SBC-00-CONCEPTS.md`](SBC-00-CONCEPTS.md), which is now the **sole canonical concepts artifact**
> for the `sbc` family. **Do not cite this document's `SBC-INV-N` handles** — they renumbered in
> the successor (notably this doc's `SBC-INV-6`/`SBC-INV-10` rebound, and its conformance-target
> rule became `SBC-INV-14`). See [`SBC-ERRATA.md`](SBC-ERRATA.md) **ERRATA-003** for the
> supersession record. Retained as institutional memory only (SBC-INV-10); not normative.

**Status:** SUPERSEDED 2026-05-31 by `SBC-00-CONCEPTS.md` (see ERRATA-003). Historical note: ratified 2026-05-31 as the in-repo Phase-0 gate before the portable extraction existed.
**Blocks:** nothing directly — it is the meta-gate every initiative family already cites transitively.
**Does not block:** any existing initiative; this doc crystallizes a discipline that is already in force.
**Reads:** [`../CLAUDE.md`](../CLAUDE.md) §`Spec-Before-Code Planning Discipline` (the operational narrative this doc renders normative), [`todo/streamz/semantic-servo/TODO-SSV-00-CONCEPTS.md`](todo/streamz/semantic-servo/TODO-SSV-00-CONCEPTS.md) and [`todo/streamz/schematic-exec/TODO-SE-00-CONCEPTS.md`](todo/streamz/schematic-exec/TODO-SE-00-CONCEPTS.md) (the reference shapes this doc conforms to), [`todo/memalpha/ERRATA.md`](todo/memalpha/ERRATA.md) (errata reference shape).

> 🛑 **NO CODE IN THIS DOC.** This is a terms doc — and, uniquely, its subject *is* the form of terms docs. Its deliverables are vocabulary, ownership decisions, and frozen invariants for the Spec-Before-Code discipline. It contains no executable artifact and prescribes none.

> 🔁 **Self-conformance note.** This document is the one concepts doc whose subject is the concepts-doc form. It therefore conforms to the very discipline it specifies: it carries the §0–§15 layout (SBC-INV-9), the RFC 2119 keyword notice, a citing-not-restating glossary (SBC-INV-2), frozen enums with declared registration policies (SBC-INV-3), numbered invariants, an acceptance checklist, and a change log. If a reader finds this doc violating a rule it states, that is a ratifiable bug, not licence.

**Normative keywords.** The key words **MUST**, **MUST NOT**, **SHALL**, **SHOULD**, **SHOULD NOT**, **MAY**, and **RECOMMENDED** in this doc are interpreted per RFC 2119 and RFC 8174 when, and only when, they appear in capitals. Lowercase uses are ordinary English. Narrative text without capitalised keywords is advisory, not binding.

**Normative vs. informative sections.** Sections referenced by the Acceptance checklist in §12 are **normative** and binding: §0, §3, §4, §5, §6, §7, §8, §9, §10. The remaining sections — §1 (purpose), §2 (problem statement), §11 (non-goals), §13 (files cited), §14 (unblocks), §15 (change log) — are **informative**. The `CLAUDE.md` §`Spec-Before-Code Planning Discipline` section is informative narrative; **this doc is the normative artifact** for the discipline's vocabulary and invariants.

## 0. Ratified policy — authoritative side

Two authorities coexist, and this doc fixes their relationship so no future initiative re-litigates it.

**`CLAUDE.md` is the operational authority; this doc is the normative authority.** The `Spec-Before-Code Planning Discipline` and `Parallel-Agent Workflow` sections of [`../CLAUDE.md`](../CLAUDE.md) are loaded into every agent session and are the day-to-day operating instructions. This doc does not replace them, override them, or fork them. It **renders** the discipline they describe into the same standards-body form every other `-00-CONCEPTS` doc uses, so that the discipline can be cited by section number, amended by §15 entry, and conformance-tested like any other frozen contract. The relationship is exactly parallel to the rule the discipline states for phases: *the README entry for a phase is informative; the per-phase doc is the normative artifact.* Here, the `CLAUDE.md` narrative is the README-equivalent; this doc is the per-phase-equivalent.

Concrete consequences this policy forces:

- Where this doc and the `CLAUDE.md` narrative agree (they MUST), a citation MAY point at either; this doc is preferred for normative claims because it carries stable section and invariant identifiers.
- Where they disagree, that disagreement is a **bug in one of the two**, filed against this family's errata log, not a silent fork. The resolution amends whichever artifact was wrong and cites the other.
- New vocabulary for the discipline (a new frozen enum value, a new invariant, a new identifier shape) is **owned by this doc**. It lands here first via §15 amendment, then propagates to the `CLAUDE.md` narrative — never the reverse order for normative content.
- Existing repo primitives that the discipline merely *references* (RFC 2119/8174, git, GitHub Issues, the worktree mechanism) remain authoritative for themselves; this doc composes them, it does not redefine them (see §10).

This policy supersedes the implicit "the rules live wherever someone last wrote them down" posture. It turns every row in §3's glossary from folklore into a ratified decision.

## 1. Purpose

The Spec-Before-Code discipline now governs four-plus initiative families (`semantic-servo`, `schematic-exec`, `sz-container`, the PCB-editor phase docs, the DAA subrepo) and a parallel-agent workflow that landed 40+ commits in a single day. The discipline's own vocabulary — *concepts doc*, *normative/informative*, *frozen enum*, *registration policy*, *conformance target*, *authority relationship*, *errata entry*, *EOQ*, *stealth revert*, *wave*, *worktree isolation* — has crossed the threshold the discipline itself names: once a family of rules passes ~3 interacting concepts, vocabulary drift and invariant erosion become the dominant failure mode. The discipline has no concepts doc of its own; it is described only as narrative in `CLAUDE.md`. That is the exact gap the discipline exists to close, left open for the discipline itself.

This doc closes it. Its deliverables are:

1. One canonical glossary every initiative cites for the *meta*-vocabulary (§3).
2. A source-of-truth map naming exactly one owner per meta-concept (§4).
3. The frozen enums of the discipline — registration policies, authority relationships, errata statuses, the glossary relationship markers — closed and tagged with their own registration policy (§5–§8).
4. The discipline's invariants restated as numbered, enforceable `SBC-INV-N` rules with an owner and a verification surface (§9).
5. Explicit reconciliation against the external grammars the discipline borrows (RFC 2119, git, GitHub) and against adjacent repo conventions (§10).

This doc is **writing-only**: no code, no schema, no behaviour change. It is the artifact a reviewer reads to answer "what *is* the spec-before-code method, precisely, and which of its rules are binding?"

## 2. Problem statement (evidence)

The discipline's narrative is load-bearing but unaddressable: you cannot cite "the part of `CLAUDE.md` about stealth reverts" by a stable identifier, you cannot amend a single rule without editing a prose paragraph that several initiatives depend on, and you cannot conformance-test a phase doc against the rules because the rules are not enumerated. Each row below is pinned to an existing artifact so this doc starts from the same map every initiative already knows.

**The rules exist only as narrative, with no stable handles.** [`../CLAUDE.md`](../CLAUDE.md) §`Spec-Before-Code Planning Discipline` defines normative-keyword usage, normative-vs-informative sectioning, conformance targets, the reference-vs-restatement glossary discipline, frozen-enum registration policy, the §0–§15 phase-document shape, execution discipline, errata logs, the stealth-revert prohibition, and the authority-boundary matrix — all as prose. None carry an `SBC-INV-N`-style identifier, so no phase doc can say "preserves SBC-INV-7" the way SSV phases say "preserves INV-SSV-3."

**The reference shapes already encode the form, but each re-derives it.** [`todo/streamz/semantic-servo/TODO-SSV-00-CONCEPTS.md`](todo/streamz/semantic-servo/TODO-SSV-00-CONCEPTS.md) §15 records a same-day amendment whose entire job was "conform this doc to `CLAUDE.md` §Spec-Before-Code" — adding the RFC notice, the normative/informative labels, the three-phrasing glossary discipline, and per-enum registration policies. [`todo/streamz/schematic-exec/TODO-SE-00-CONCEPTS.md`](todo/streamz/schematic-exec/TODO-SE-00-CONCEPTS.md) §0 independently re-states the "authoritative side" pattern. Every new `-00` doc re-derives the same skeleton from prose because there is no normative skeleton to cite.

**The enums of the discipline are named but never frozen as enums.** "Standards Action / Specification Required / Expert Review" (registration policy), the seven-value `AuthorityRelationship` (mirror / adapt / extend / compose / own / derive / represent), and the errata status legend (🟢/🟡/🔴/⚪) are each defined once in `CLAUDE.md` prose. They are exactly the kind of cross-phase contract the discipline says MUST declare its own registration policy — yet they declare none, because the discipline never turned its own vocabulary into frozen enums.

**Errata and EOQ identifier shapes are specified by example, not by grammar.** [`todo/memalpha/ERRATA.md`](todo/memalpha/ERRATA.md) is named the reference shape; `ERRATA-NNN` and `EOQ-NNN-<ERRATA-id>` are defined in `CLAUDE.md` prose. A new family copying the shape has no normative source to cite for the identifier grammar — only a sibling file to imitate.

None of these are errors. They are the boundary at which the discipline stopped applying itself to itself. This doc crosses that boundary once, so every family afterward cites a spec instead of imitating a sibling.

## 3. Canonical glossary

For every term that also appears in `CLAUDE.md` or an external standard, the entry cites the authoritative source and marks the relationship per SBC-INV-2, using the discipline's own three phrasings.

| Term | Definition | Relationship |
|------|-----------|--------------|
| **Spec-Before-Code discipline** | The planning cycle in which every behaviour change is preceded by a ratified terms doc, to prevent vocabulary drift and invariant erosion across multi-phase initiatives. | As narrated in [`../CLAUDE.md`](../CLAUDE.md) §`Spec-Before-Code Planning Discipline`; rendered normative here without modification. |
| **Concepts doc** (terms doc) | The normative artifact of a phase: a `-NN-CONCEPTS.md` carrying vocabulary, ownership decisions, and frozen invariants — no executable artifact. | As narrated in `CLAUDE.md` §`Phase document shape`; used without modification. |
| **Normative section** | A section referenced by the doc's §12 Acceptance checklist; binding on implementers. | As narrated in `CLAUDE.md` §`Normative vs. informative sections`; used without modification. |
| **Informative section** | Any section not referenced by §12 — problem statement, narrative, non-goals, change log. Advisory only. | As narrated in `CLAUDE.md` §`Normative vs. informative sections`; used without modification. |
| **Normative keyword** | MUST / MUST NOT / SHALL / SHOULD / SHOULD NOT / MAY / RECOMMENDED, binding only when capitalised. | As defined in RFC 2119 / RFC 8174; used without modification (external grammar — see §10 row 1). |
| **Frozen enum** | A closed value set encoding an invariant or cross-phase contract (claim class, servo mode, registration policy, etc.); adding a value follows its declared registration policy. | As narrated in `CLAUDE.md` §`Frozen enumerations — registration policy`; used without modification. |
| **Registration policy** | The named rule governing how a frozen enum gains a value: Standards Action, Specification Required, or Expert Review (§5). | As narrated in `CLAUDE.md` §`Frozen enumerations`; the three values are frozen as an enum here — adapted: this doc owns them as `RegistrationPolicy` (§5). |
| **Conformance target** | The named artifact an initiative's acceptance list binds ("a conforming SSV deployment MUST satisfy gates (a)–(d)"). Optional phases yield a second conformance level. | As narrated in `CLAUDE.md` §`Conformance targets`; used without modification. |
| **Authority relationship** | The declared relationship between a repo concept and an externally-authored grammar it crosses: mirror / adapt / extend / compose / own / derive / represent (§6). | As narrated in `CLAUDE.md` §`Standards integration`; the seven values are frozen as an enum here — adapted: this doc owns them as `AuthorityRelationship` (§6). |
| **Errata entry** | A permanent, sequentially-numbered record (`ERRATA-NNN`) of a known issue, execution deviation, infrastructure bug, or stealth revert, kept in a family's living `ERRATA.md`. | As narrated in `CLAUDE.md` §`Errata logs` and §`Convention: per-initiative ERRATA.md`; used without modification. Reference shape: [`todo/memalpha/ERRATA.md`](todo/memalpha/ERRATA.md). |
| **Errata status** | The lifecycle icon on an entry: 🟢 resolved / 🟡 diagnosed / 🔴 open / ⚪ deviation-pending-ratification (§7). | As narrated in `CLAUDE.md` §`Errata logs`; frozen as an enum here — adapted: this doc owns the legend as `ErrataStatus` (§7). |
| **EOQ** | Errata Open Question, identifier `EOQ-NNN-<ERRATA-id>`: a stable handle for an open (⚪/🔴) question in a family's errata log. | As narrated in `CLAUDE.md` §`EOQ identifiers`; used without modification. Identifier grammar frozen in §8. |
| **PCDN** | A per-concept-doc open question carried inside a concepts doc, shape `PCDN-<PHASE>-NNN`, resolved during ratification. | As narrated in `CLAUDE.md` (referenced under EOQ identifiers as the parallel shape); used without modification. |
| **Stealth revert** | A behaviour change that undoes ratified-and-implemented phase content while riding an unrelated commit's scope. Prohibited by construction (SBC-INV-7). | As narrated in `CLAUDE.md` §`Stealth-revert prohibition`; used without modification. |
| **§15 amendment** | A dated change-log entry that ratifies a change to a normative section, frozen-enum value, or invariant. Must land **before** any behaviour PR that depends on the change. | As narrated in `CLAUDE.md` §`Execution discipline`; used without modification. |
| **Phase code** | The commit-subject citation `<INITIATIVE><NN><letter>` (e.g. `SSV02a:`, `SE03b:`) naming the originating phase of an execution PR. | As narrated in `CLAUDE.md` §`Execution discipline`; used without modification. Grammar frozen in §8. |
| **Spec family** | A `docs/todo/<family>/` (or co-located subrepo `docs/concepts/`) tree of `-NN-CONCEPTS` docs + README + `ERRATA.md` running this discipline. | As narrated in `CLAUDE.md` §`Errata logs` and §`Convention: subrepo-private spec lineage`; used without modification. |
| **Wave** | A batch of parallel-agent invocations sharing one base SHA, in the fan-out workflow (Wave 0 ratification … Wave N i18n sweep). | Owned by `CLAUDE.md` §`Parallel-Agent Workflow`; referenced here as the *execution* counterpart to this doc's *planning* scope — does not exist as a meta-vocabulary term in this doc's frozen enums (§11 non-goal 2). |

## 4. Source-of-truth map — one owner per meta-concept

| Meta-concept | Authoritative owner | Notes |
|--------------|--------------------|-------|
| What the discipline *is* (operating narrative) | `CLAUDE.md` §`Spec-Before-Code Planning Discipline` | Loaded every session; informative per §0. |
| Discipline vocabulary + invariants (normative) | **This doc** (`docs/SPEC-BEFORE-CODE-CONCEPTS.md`) | Stable section + `SBC-INV-N` identifiers. |
| `RegistrationPolicy` enum values | **This doc §5** | New value ⇒ §15 amendment here (Standards Action). |
| `AuthorityRelationship` enum values | **This doc §6** | New value ⇒ §15 amendment here (Standards Action). |
| `ErrataStatus` legend | **This doc §7** | New status ⇒ §15 amendment here (Standards Action). |
| Identifier grammars (`ERRATA-NNN`, `EOQ-NNN-<id>`, `PCDN-<PHASE>-NNN`, phase code) | **This doc §8** | New shape ⇒ §15 amendment here. |
| Concepts-doc §0–§15 section layout | **This doc §9 (SBC-INV-9)** | Mirrors SSV-00 / SE-00 precedent. |
| Errata log file shape + lifecycle | `CLAUDE.md` §`Errata logs`; reference shape [`todo/memalpha/ERRATA.md`](todo/memalpha/ERRATA.md) | This doc references; it does not re-author the row shape. |
| Parallel-agent fan-out (waves, worktrees, cherry-pick cadence) | `CLAUDE.md` §`Parallel-Agent Workflow` | Execution-side; out of this doc's planning scope (§11). |
| RFC 2119 / 8174 keyword semantics | IETF (external) | Composed, not owned (§10 row 1). |
| Per-family phase vocabularies (SSV, SE, SZ, DAA, …) | Each family's own `-00-CONCEPTS` doc | This doc owns the *form*, not any family's *content*. |

## 5. Frozen enum — `RegistrationPolicy`

The policy governing how any frozen enum (including the three in this doc) gains a value.

| Value | Meaning | When to use |
|-------|---------|-------------|
| **Standards Action** | Adding a value requires a §15 amendment to the owning `-00-CONCEPTS` doc **and** a ratification session. | Enums encoding invariants or cross-phase contracts. Default when in doubt. |
| **Specification Required** | Adding a value requires a phase-owner walkthrough update; no CONCEPTS amendment. | Enums local to one phase's contract surface. |
| **Expert Review** | Phase owner MAY add a value with a PR-level note. | Internal enums with no cross-phase coupling. |

**Registration policy of `RegistrationPolicy` itself: Standards Action.** Adding, removing, or renaming a registration-policy value requires a §15 amendment to this doc and a ratification session. Demotion of a specific enum elsewhere (Standards Action → Specification Required) is permitted later "if churn justifies," per the discipline, and is itself a §15 amendment in that enum's owning doc.

## 6. Frozen enum — `AuthorityRelationship`

The seven-value relationship every externally-authored concept crossing the repo boundary MUST declare (SBC-INV-8). An undeclared local mirror reads as `mirror` with no mutation rights — never silently as `own`.

| Value | Meaning |
|-------|---------|
| **mirror** | Copy verbatim; no local divergence on field names or value grammars. |
| **adapt** | Copy verbatim, add named local affordances (envelope, audit, retry) that MUST NOT leak across the upstream wire boundary. |
| **extend** | Add named local fields/values on an unchanged upstream grammar, in a declared namespace (e.g. `__streamz`). |
| **compose** | Use upstream terms as components of a higher-level construct this repo owns. |
| **own** | This repo authors the grammar; full mutation rights gated by this discipline. |
| **derive** | Interpret/evaluate/preflight against an upstream grammar without owning it; outputs local, inputs upstream. |
| **represent** | Visualize the upstream grammar (typically UI); display semantics local, payload round-trip preserves upstream names. |

Each external-grammar concept MUST be recorded with six axes: **upstream authority**, **local representation**, **mutation rights**, **divergence policy**, **downstream consumers**, **conformance test owner**. Promoting a row to `own` (or `mirror` → `adapt`/`extend`) requires an explicit §15 amendment to the owning phase doc.

**Registration policy: Standards Action.** Reference shape: [`todo/streamz/TODO-STREAMZ-06-PROTOCOL-MEDIA-INTEGRATION.md`](todo/streamz/TODO-STREAMZ-06-PROTOCOL-MEDIA-INTEGRATION.md) §0/§4/§6.5.

## 7. Frozen enum — `ErrataStatus`

The lifecycle legend for every entry in a family's `ERRATA.md`.

| Icon | Status | Meaning |
|------|--------|---------|
| 🟢 | resolved | Root-caused and fixed; resolving commit + verification evidence recorded. |
| 🟡 | diagnosed | Root cause known, clear fix-prescription, no longer needs user input. |
| 🔴 | open | Undiagnosed or unresolved; appears in the Open Questions list. |
| ⚪ | deviation-pending-ratification | A deviation from ratified spec (incl. a structurally-necessary revert) awaiting ratification; appears in the Open Questions list. |

Entries are **permanent** — a resolved entry stays in the log as institutional memory; status transitions, the entry is never deleted. A question leaves the Open Questions list when its entry reaches 🟢 or 🟡.

**Registration policy: Standards Action.**

## 8. Frozen identifier grammars

The stable handle shapes the discipline relies on. Each is closed; adding a new shape is a §15 amendment to this doc.

| Identifier | Grammar | Scope | Owner |
|-----------|---------|-------|-------|
| **Phase code** | `<INITIATIVE><NN><letter>` (e.g. `SSV02a`, `SE03b`, `SZ09c`) | Commit subject of an execution PR | This doc §8 |
| **Invariant id** | `INV-<FAMILY>-<N>` (e.g. `INV-SSV-3`, `INV-PMI-9`); this family uses `SBC-INV-<N>` | §9 of a family's `-00` doc | Each family |
| **Errata id** | `ERRATA-NNN`, monotonic within one `ERRATA.md` | A family's errata log | Each family |
| **EOQ id** | `EOQ-NNN-<ERRATA-id>`, `NNN` monotonic within the file; stable across resolution | A family's errata Open Questions | Each family |
| **PCDN id** | `PCDN-<PHASE>-NNN` | Open question inside a concepts doc | Each phase |

An assigned `EOQ`/`ERRATA`/`PCDN` id is **stable across resolution** — the resolving commit may cite it and the handle never re-binds. **Registration policy of this grammar set: Standards Action.**

## 9. Frozen invariants

Restated as enforceable rules. Each names the surface that verifies it. Touching any `SBC-INV-N` requires a §15 amendment to this doc **first**, in a separate PR (this is SBC-INV-4 applied to this doc).

| Id | Invariant | Verified by |
|----|-----------|-------------|
| **SBC-INV-1** | Every behaviour change in a ≥3-phase initiative MUST be preceded by a ratified terms doc (a `-NN-CONCEPTS` with a dated §15 entry and all PCDNs resolved). | Reviewer: no execution PR cites an unratified phase. |
| **SBC-INV-2** | A glossary entry for a term that also exists in the repo MUST cite the authoritative source and mark the relationship (used-without-modification / adapted: Δ / owned-by-`<PHASE>`). Silent restatement is prohibited. | Concepts-doc review of §3. |
| **SBC-INV-3** | Every frozen enum MUST declare its registration policy (§5 values) in its concepts doc. | Concepts-doc review of the enum sections. |
| **SBC-INV-4** | Touching a frozen-enum value or an invariant MUST land a §15 amendment **first**, in a separate PR; no behaviour PR rides an unamended invariant. | Commit/PR ordering review. |
| **SBC-INV-5** | An execution PR MUST cite its phase code (§8) in the commit subject and name in its description which §9 invariants it touches and how each is preserved. | Commit-subject + PR-description review. |
| **SBC-INV-6** | Every spec family running this discipline MUST maintain a living `ERRATA.md` (correct location per the co-location convention); entries are permanent. | Family-tree review; reference shape [`todo/memalpha/ERRATA.md`](todo/memalpha/ERRATA.md). |
| **SBC-INV-7** | A stealth revert is prohibited by construction: any revert of ratified-and-implemented content MUST produce (a) an errata entry filed first at status ⚪, (b) a dated §15 entry in the affected phase doc pointing at the errata, and (c) a commit-subject citation of the errata id. | Errata + §15 + commit-subject cross-check. |
| **SBC-INV-8** | Each externally-authored concept that crosses the repo boundary MUST declare an `AuthorityRelationship` (§6) and the six-axis row. An undeclared mirror is never silently `own`. | Concepts-doc review of the authority matrix. |
| **SBC-INV-9** | A `-00` concepts doc MUST carry the load-bearing sections §0, §3/§4, §10, §12, §15; later phases MAY omit non-applicable sections but keep the load-bearing set. | Concepts-doc structural review. |
| **SBC-INV-10** | An initiative-level acceptance list MUST name its conforming artifact; optional phases yield a second conformance level. | README acceptance-list review. |

**Registration policy for adding an `SBC-INV-N`: Standards Action.**

## 10. Reconciliation decisions vs. adjacent primitives

| # | Adjacent primitive | Decision |
|---|--------------------|----------|
| 1 | **RFC 2119 / RFC 8174** (IETF normative keywords) | `AuthorityRelationship` = **compose**. The discipline uses MUST/SHOULD/MAY as components; it does not redefine them. Capitalisation gate is upstream's; the "binding only when capitalised" rule is upstream text, restated for convenience, not owned. |
| 2 | **`CLAUDE.md` §`Spec-Before-Code Planning Discipline`** | This doc **renders** that narrative normative (§0). Not a fork: divergence between the two is a bug filed against this family's errata, not a second source of truth. |
| 3 | **`CLAUDE.md` §`Parallel-Agent Workflow`** (waves, worktree isolation, cherry-pick cadence) | Out of scope. That section governs *how many agents build it concurrently* (execution); this doc governs *what gets built and how its vocabulary is frozen* (planning). They are complementary; this doc does not absorb the wave/worktree vocabulary (§11 non-goal 2). |
| 4 | **GitHub Issues** (intake triage queue) | `derive`/**compose**: GH Issues is the outward intake surface; once an issue is *accepted*, the canonical record moves into the family's `ERRATA.md`. Never-accepted reports stay in GH Issues only. The boundary is owned by `CLAUDE.md` §`Convention: per-initiative ERRATA.md`; this doc references it. |
| 5 | **git** (commit subjects, separate-PR ordering, cherry-pick) | **compose**. The discipline rides git's commit-subject and PR mechanics to carry phase codes and amendment ordering; it does not modify git semantics. |
| 6 | **Family `-00` docs (SSV-00, SE-00, DAA-00, …)** | Those are **instances** of the form this doc specifies. This doc owns the form; each family owns its content. A conflict where a family doc's *structure* contradicts §9/SBC-INV-9 is resolved in favour of this doc; a conflict in a family's *vocabulary* is the family doc's to resolve. |

## 11. Non-goals

1. **Not a replacement for `CLAUDE.md`.** The operating narrative stays where agents load it. This doc gives it stable identifiers; it does not relocate it.
2. **Not a spec for the parallel-agent execution workflow.** Waves, worktree isolation, docker contention, cherry-pick cadence, bench authorization — all stay owned by `CLAUDE.md` §`Parallel-Agent Workflow`. Reason: those are execution-time concurrency rules, a different contract surface; folding them in would couple planning vocabulary to fan-out mechanics that change independently.
3. **Not a per-family content authority.** This doc never freezes a claim class, servo mode, or netlist dialect — those belong to their families. It freezes only the *meta*-vocabulary every family shares.
4. **Not retroactive enforcement.** Existing single-doc TODOs and phase-1 prototypes MAY remain informal; the discipline (and this doc) bind a family only from the moment it produces a `-NN-CONCEPTS` gate.

## 12. Acceptance

This TODO is considered landed when:

- [x] Every meta-term used across the initiative families appears in §3 with a citation and a relationship marker (SBC-INV-2 applied to this doc).
- [x] Every row in §4 names exactly one authoritative owner.
- [x] The three discipline enums (`RegistrationPolicy` §5, `AuthorityRelationship` §6, `ErrataStatus` §7) are closed and each declares its own registration policy (SBC-INV-3).
- [x] The identifier grammars in §8 are closed and marked Standards Action.
- [x] All ten discipline rules appear in §9 as `SBC-INV-N` with a verification surface.
- [x] Every adjacency named in §2 / §10 carries a reconciliation decision with an `AuthorityRelationship` where an external grammar is involved (SBC-INV-8).
- [x] Non-goals in §11 each name the owner of the excluded surface or the reason it is out of scope.
- [x] This doc carries the load-bearing section set §0/§3/§4/§10/§12/§15 (SBC-INV-9 applied to itself).

## 13. Files cited

- [`../CLAUDE.md`](../CLAUDE.md) — §`Spec-Before-Code Planning Discipline`, §`Parallel-Agent Workflow`: the operating narrative this doc renders normative.
- [`todo/streamz/semantic-servo/TODO-SSV-00-CONCEPTS.md`](todo/streamz/semantic-servo/TODO-SSV-00-CONCEPTS.md) — reference shape; its §15 records the "conform to `CLAUDE.md` §Spec-Before-Code" amendment that motivated this doc.
- [`todo/streamz/schematic-exec/TODO-SE-00-CONCEPTS.md`](todo/streamz/schematic-exec/TODO-SE-00-CONCEPTS.md) — reference shape for the §0 authoritative-side pattern.
- [`todo/streamz/TODO-STREAMZ-06-PROTOCOL-MEDIA-INTEGRATION.md`](todo/streamz/TODO-STREAMZ-06-PROTOCOL-MEDIA-INTEGRATION.md) — reference shape for the §6 `AuthorityRelationship` matrix.
- [`todo/memalpha/ERRATA.md`](todo/memalpha/ERRATA.md) — reference shape for the errata log + EOQ identifiers.
- [`../streamz/submodules/disco-analyzer/docs/concepts/ERRATA.md`](../streamz/submodules/disco-analyzer/docs/concepts/ERRATA.md) — reference shape for a subrepo-co-located errata log (DAA).
- RFC 2119, RFC 8174 (IETF) — normative-keyword grammar, composed per §10 row 1.

## 14. Unblocks

- **All current initiative families** (`semantic-servo`, `schematic-exec`, `sz-container`, PCB editor, DAA): MAY now cite `SBC-INV-N` and the §5–§8 enums by identifier instead of re-deriving the form from `CLAUDE.md` prose. No family is re-blocked; existing ratifications stand.
- **Future families:** a new `-00-CONCEPTS` doc SHOULD open by citing this doc for its form (the §0–§15 layout, the glossary discipline, the enum registration-policy requirement) and reserve its own content for its domain vocabulary.
- **`CLAUDE.md` maintenance:** future edits to the discipline narrative SHOULD land the normative change here (via §15) first, then mirror the prose — per §0.

## 15. Change log

- **2026-05-31** — Ratified. Crystallizes the Spec-Before-Code discipline (previously narrative-only in `CLAUDE.md`) into a normative `-00-CONCEPTS` artifact in its own form. §0 dual-authority policy fixed (`CLAUDE.md` operational, this doc normative). Three discipline enums frozen: `RegistrationPolicy` (§5), `AuthorityRelationship` (§6, transcribed from `CLAUDE.md` §`Standards integration`), `ErrataStatus` (§7) — all Standards Action. Identifier grammars frozen in §8. Ten discipline rules transcribed as `SBC-INV-1`…`SBC-INV-10` in §9 with verification surfaces. Six reconciliation decisions in §10, including the explicit non-absorption of the parallel-agent execution workflow (row 3). No existing family is re-blocked; this doc adds stable handles to rules already in force.
