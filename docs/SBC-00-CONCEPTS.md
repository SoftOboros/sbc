# SBC-00-CONCEPTS — Spec Before Code: Foundational Concepts

**Document ID:** SBC-00-CONCEPTS
**Status:** RATIFIED AMENDMENT — exact condition-verification packet accepted 2026-09-13; implementation remains outstanding
**Revision:** 0.17.0
**Date:** 2026-09-13
**Author:** Ira Abbott / SoftOboros Inc.
**Canonical path:** `docs/SBC-00-CONCEPTS.md`
**Blocks:** every initiative family's `-00-CONCEPTS` gate (transitively).
**Does not block:** any currently ratified initiative; this doc crystallises a discipline already in force.

---

## §0 Authority Policy

Two authorities coexist; this section fixes their relationship so no future initiative re-litigates it.

**The project's operational context document (`CLAUDE.md` or equivalent) is the operational authority; this doc is the normative authority.** The operational context is loaded into every agent session and carries day-to-day instructions. This doc does not replace it. It renders the discipline into the same standards-body form every `-00-CONCEPTS` doc uses, so that rules can be cited by section and invariant identifier, amended by §15 entry, and conformance-tested.

The relationship mirrors the rule the discipline itself states for phases: *the README entry for a phase is informative; the per-phase doc is the normative artifact.* The operational context is the README-equivalent; this doc is the per-phase-equivalent.

Consequences:

- Where this doc and the operational context agree (they MUST), a citation MAY point at either; this doc is preferred for normative claims because it carries stable identifiers.
- Where they disagree, that is a **bug in one of the two**, not a silent fork. The resolution amends whichever was wrong and cites the other.
- New vocabulary for the discipline (a new enum value, a new invariant, a new identifier grammar) is **owned by this doc**. It lands here first via §15 amendment, then propagates to the operational context — never the reverse.
- External primitives this discipline composes (RFC 2119, git, issue trackers) remain authoritative for themselves; this doc composes them, it does not redefine them (see §10).

---

## §1 Purpose

This document's deliverables are:

1. One canonical glossary every initiative cites for the *meta*-vocabulary (§3).
2. A source-of-truth map naming exactly one owner per meta-concept (§4).
3. The discipline's frozen enums — registration policy, authority relationships, errata lifecycle — closed and tagged with their own registration policy (§5–§7).
4. Frozen identifier grammars for the stable handles the discipline relies on (§8).
5. The discipline's invariants as numbered, enforceable `SBC-INV-N` rules with a verification surface (§9).
6. Explicit reconciliation against external grammars the discipline composes (§10).

This doc is **writing-only**: no code, no schema, no behaviour change. It is the artifact a reviewer reads to answer *"what is the Spec-Before-Code method, precisely, and which of its rules are binding?"*

**Normative keywords.** The key words **MUST**, **MUST NOT**, **SHALL**, **SHOULD**, **SHOULD NOT**, **MAY**, and **RECOMMENDED** in this document and all SBC-governed docs are interpreted per RFC 2119 and RFC 8174 when, and only when, they appear in capitals. Lowercase uses are ordinary English.

**Normative vs. informative sections.** Sections referenced by the §12 Acceptance checklist are **normative** and binding. All other sections (§1 purpose, §2 problem statement, §11 non-goals, §13 files cited, §14 unblocks, §15 change log) are **informative**.

**Self-conformance.** This document is the one concepts doc whose subject is the concepts-doc form. It therefore conforms to the very discipline it specifies. If a reader finds this doc violating a rule it states, that is a ratifiable bug, not licence.

---

## §2 Problem Statement

The discipline's failure modes are well-characterised. Each row names the mechanism.

| Failure mode | Mechanism | SBC mitigation |
|---|---|---|
| Vocabulary drift | Terms re-derived independently per agent/phase; meanings diverge silently | Canonical glossary with citing-not-restating invariant (SBC-INV-2) |
| Invariant erosion | Rules exist only as prose; no stable handle for citation or amendment | Numbered `SBC-INV-N` with registration policy (SBC-INV-4, §5) |
| Spec drift | Code written without a concurrent spec update | Phase gates; execution PRs must name touched invariants (SBC-INV-5) |
| Semantic debt | Ambiguity survives refactoring; each onboarding event re-resolves it independently | Glossary terms are normative; unregistered synonyms are undefined references |
| Stealth revert | A behaviour change undoes ratified content under an unrelated commit's scope | Three-part construction makes stealth reverts impossible (SBC-INV-7) |
| Hallucinated bridge | Agent fills a spec gap with plausible-but-wrong code | Gaps MUST be deferred items, not silent assumptions (SBC-INV-6) |
| Authority ambiguity | Multiple docs claim to own the same rule; divergence goes undetected | Source-of-truth map (§4); one owner per concept |
| External grammar creep | Imported standard spawns local schema, local names, local mythology | `AuthorityRelationship` declaration required for every external grammar (SBC-INV-8) |

The onboarding-tax framing: every agent context window is a cold start. Without a ratified spec as primary context, the onboarding tax is paid in full on every call, re-derived from code whose intent is implicit. An agent that reads code to infer intent is performing reverse engineering, not development.

The standards-body precedent: IETF, SMPTE, W3C, and ISO/IEC JTC 1 resolved this problem decades ago. RFC 2119 keywords exist precisely because the distinction between normative and advisory is load-bearing when multiple independent implementors must converge. In an agentic pipeline, every agent call is an independent implementor.

---

## §3 Canonical Glossary [Normative]

For every term that also appears in an external standard or the project's operational context, the entry MUST cite the authoritative source and mark the relationship using one of three phrasings (SBC-INV-2):

- **"As defined in `<source>`; used without modification."** — upstream is canonical; this doc references it.
- **"As defined in `<source>`; adapted: `<delta>`."** — upstream is canonical; this doc extends or narrows it with a named delta.
- **"Owned by `<PHASE>`; does not exist upstream yet."** — this doc is canonical; upstream will mirror once the phase lands.

Silent restatement of an existing definition is how forks form. It is prohibited.

| Term id | Term | Definition | Relationship |
|---|---|---|---|
| `TERM-001` | **Spec (specification)** | A document or file describing *what* a system MUST do, *how* states transition, and *what* invariants hold — without encoding *how* the implementation achieves those ends. | Owned by SBC; does not exist in upstream RFC vocabulary. |
| `TERM-002` | **Code (executable artifact)** | Any file whose primary consumer is a compiler, interpreter, linker, or runtime: source files, build scripts, migration files, hardware description files, generated output from template engines. Test suites are code. | Owned by SBC. |
| `TERM-003` | **Spec-before-code ordering** | The invariant that the spec's ratification timestamp precedes any code artifact derived from it, and that the code was derived from the spec, not the reverse. | Owned by SBC. |
| `TERM-004` | **Onboarding event** | Any context initialisation from which an agent (human or AI) must derive sufficient understanding to produce correct, consistent work. Each LLM context window constitutes a distinct onboarding event with zero carry-over. | Owned by SBC. |
| `TERM-005` | **Semantic debt** | Ambiguity, naming collision, or undefined behaviour embedded in a codebase that forces each onboarding event to resolve the same ambiguity independently and potentially inconsistently. | Owned by SBC. |
| `TERM-006` | **Spec drift** | The condition in which executable code diverges from the spec that authorised it without an explicit spec revision. | Owned by SBC. |
| `TERM-007` | **Phase gate** | A commit boundary or review checkpoint at which transition to the next lifecycle phase MUST be explicitly authorised. No phase gate MAY be traversed without a spec artefact in `RATIFIED` status. | Owned by SBC. |
| `TERM-008` | **Ratified** | A spec status indicating designated reviewers have accepted the spec as the authoritative description for the current phase. Ratification MUST be recorded in §15 of the spec. | Owned by SBC. |
| `TERM-009` | **Template** | A parameterised spec fragment that, when instantiated, produces a normative spec section or a code artifact. Templates are specs; their instantiations are code. | Owned by SBC. |
| `TERM-010` | **Concepts doc** | The normative artifact of a phase: a `-NN-CONCEPTS.md` carrying vocabulary, ownership decisions, and frozen invariants. Contains no executable artifact. | Owned by SBC. |
| `TERM-011` | **Frozen enum** | A closed value set encoding an invariant or cross-phase contract. Adding a value follows the declared registration policy (§5). | Owned by SBC. |
| `TERM-012` | **Registration policy** | The named rule governing how a frozen enum gains a value: Standards Action, Specification Required, or Expert Review (§5). | Owned by SBC §5. |
| `TERM-013` | **Authority relationship** | The declared relationship between a project concept and an externally-authored grammar it crosses (§6). | Owned by SBC §6. |
| `TERM-014` | **Conformance target** | The named artifact an initiative's acceptance list binds ("a conforming deployment MUST satisfy gates (a)–(d)"). Optional phases yield a second conformance level. | Owned by SBC. |
| `TERM-015` | **Errata entry** | A permanent, sequentially-numbered record of a known issue, execution deviation, or stealth revert, kept in a family's living `ERRATA.md`. | Owned by SBC. |
| `TERM-016` | **Stealth revert** | A behaviour change that undoes ratified-and-implemented phase content while riding an unrelated commit's scope. Prohibited by construction (SBC-INV-7). | Owned by SBC. |
| `TERM-017` | **Phase code** | The commit-subject citation `<INITIATIVE><NN><letter>` naming the originating phase of an execution PR. Grammar frozen in §8. | Owned by SBC §8. |
| `TERM-018` | **Traceability mode** | The declared mechanism by which a code artifact was derived from its spec: `DERIVED`, `MANUAL`, or `VALIDATED` (§7). | Owned by SBC §7. |
| `TERM-019` | **Normative keyword** | MUST / MUST NOT / SHALL / SHOULD / SHOULD NOT / MAY / RECOMMENDED — binding only when capitalised. | As defined in RFC 2119 / RFC 8174; used without modification. |
| `TERM-020` | **Wave** | A batch of parallel-agent invocations sharing one base commit, in a fan-out execution workflow. | Referenced here as the execution counterpart to this doc's planning scope; not owned by SBC (§11 non-goal 3). |

---

## §4 Source-of-Truth Map [Normative]

Exactly one owner per meta-concept. An undeclared owner defaults to this doc.

| Meta-concept | Authoritative owner | Notes |
|---|---|---|
| Operating narrative (what the discipline *is*, day-to-day) | Project operational context document | Informative per §0; loaded every session. |
| Discipline vocabulary + invariants (normative) | **This doc** | Stable section + `SBC-INV-N` identifiers. |
| `RegistrationPolicy` enum values | **This doc §5** | New value ⇒ §15 amendment here (Standards Action). |
| `AuthorityRelationship` enum values | **This doc §6** | New value ⇒ §15 amendment here (Standards Action). |
| Traceability mode enum values | **This doc §7** | New value ⇒ §15 amendment here (Standards Action). |
| Identifier grammars | **This doc §8** | New shape ⇒ §15 amendment here (Standards Action). |
| Concepts-doc §0–§15 section layout | **This doc §9 (SBC-INV-9)** | |
| Spec object model (`ObjectKind`, attribute schema) | **`SBC-00-ADDENDUM-C.md` §4** | What a spec object *is*, as a data structure. |
| Identifier canonicalisation + allocation authority | **`SBC-00-ADDENDUM-C.md` §4.3** | Cited by §8 below. |
| `EdgeType` enum values | **`SBC-00-ADDENDUM-C.md` §5** | Typed relationships between objects. |
| `ChangeKind` enum + suspicion propagation | **`SBC-00-ADDENDUM-C.md` §8** | Governs what an amendment invalidates downstream. |
| §15 change-log shape; `AmendmentStatus` | **`SBC-00-ADDENDUM-D.md` §2, §3** | The `amendment` object's authored form. |
| `ErrataStatus` enum values + lifecycle rules | **`SBC-00-ADDENDUM-B.md` §1** | New value ⇒ §4 amendment there (Standards Action). |
| ERRATA vs. §15 boundary decision rule | **`SBC-00-ADDENDUM-B.md` §2** | Which artifact is canonical when a resolution lands. |
| ERRATA vs. issue tracker boundary | **`SBC-00-ADDENDUM-B.md` §2** | Intake vs. accepted-log split. |
| `ERRATA.md` file shape + how-to | **`SBC-00-ADDENDUM-B.md` §3** | Copyable template; each family owns its content. |
| Parallel-agent execution workflow | Project operational context document | Execution-side; out of planning scope (§11). |
| RFC 2119 / 8174 keyword semantics | IETF (external) | Composed, not owned (§10 row 1). |
| Per-family phase vocabularies | Each family's own `-00-CONCEPTS` doc | This doc owns the *form*; each family owns its *content*. |

---

### §4.1 Errata assessment and operational review ownership [Normative]

ADDENDUM-B §1.1 owns errata assessment, disposition, authority, and record grammar.
ADDENDUM-C §4.7 and §7.1 own derived assessment facts, occurrence matching, and
forward/as-of effects. SIDX-06B owns delivery of C13 operational review; SIDX-06C
owns its presentation. These are extensions to the existing errata record and
derived views, not a second issue tracker or new `ObjectKind`.

The local decision identity is `<family-key>:ERRATA-NNN/decision/<n>`, where
the errata identity resolves uniquely under ADDENDUM-C and `<n>` is a positive
ASCII decimal integer without leading zeroes. Allocation is monotone within
that erratum and never reused. This is non-graph metadata, not an additional
`GlobalObjectIdV1` grammar. Its frozen values are owned by ADDENDUM-B under
Standards Action. The parent §8 identifier register incorporates this local
grammar by reference; no legacy subject acquires an object identity from it.

### §4.2 Recorded condition verification ownership [Normative]

ADDENDUM-B §1.2 owns append-only recorded verification of an exact continuing
condition, its human authority meaning, and its closed record/result values.
ADDENDUM-C §7.2 owns the supported before/after transition and subsequent
validity. SIDX-06A §5.10 owns retained candidates, SIDX-06D §7.7 owns independent
verification trust and generation admission, and SIDX-06B §7.8 and SIDX-06C §7.8
own query and presentation. Each imports the other owners without restatement.

A verification record is identified by the SHA-256 of its complete canonical
JSON body, using the existing encoding. This is a content digest, not an
allocated handle, decision number, SpecObject, or graph endpoint. No local
decision identity, native lifecycle, C6 clearing, or diagnostic vocabulary
changes. The frozen registration policy for these new profiles is Standards
Action. Existing approvals of dispositions do not grant verification authority.

---

## §5 Frozen Enum — `RegistrationPolicy` [Normative]

The policy governing how any frozen enum (including the three in this doc) gains a value.

| Value | Meaning | Default use |
|---|---|---|
| **Standards Action** | Adding a value requires a §15 amendment to the owning `-00-CONCEPTS` doc and a ratification session. | Enums encoding invariants or cross-phase contracts. Default when in doubt. |
| **Specification Required** | Adding a value requires a phase-owner walkthrough update; no CONCEPTS amendment. | Enums local to one phase's contract surface. |
| **Expert Review** | Phase owner MAY add a value with a PR-level note. | Internal enums with no cross-phase coupling. |

**Registration policy of `RegistrationPolicy` itself: Standards Action.** Demoting a specific enum elsewhere (Standards Action → Specification Required) is permitted if churn justifies and is itself a §15 amendment in that enum's owning doc.

---

## §6 Frozen Enum — `AuthorityRelationship` [Normative]

The relationship every externally-authored concept crossing a project boundary MUST declare (SBC-INV-8). An undeclared local mirror reads as `mirror` with no mutation rights — never silently as `own`.

| Value | Meaning |
|---|---|
| **mirror** | Copy verbatim; no local divergence on field names or value grammars. |
| **adapt** | Copy verbatim; add named local affordances (envelope, audit, retry) that MUST NOT leak across the upstream wire boundary. |
| **extend** | Add named local fields/values on an unchanged upstream grammar, in a declared namespace. |
| **compose** | Use upstream terms as components of a higher-level construct this project owns. |
| **own** | This project authors the grammar; full mutation rights gated by this discipline. |
| **derive** | Interpret or evaluate against an upstream grammar without owning it; outputs are local, inputs are upstream. |
| **represent** | Visualise the upstream grammar; display semantics are local, payload round-trip preserves upstream names. |

Each external-grammar concept MUST be recorded as a row with six axes: **upstream authority**, **local representation**, **mutation rights**, **divergence policy**, **downstream consumers**, **conformance test owner**. Promoting a row to `own` (or from `mirror` to `adapt`/`extend`) requires an explicit §15 amendment to the owning phase doc.

The failure mode this prevents: *"we copied it into our schema, therefore we own it."* Without this discipline, every imported standard eventually spawns local schema, local names, local adapter mythology — and no one can answer which layer owns a given field name.

**Registration policy: Standards Action.**

---

## §7 Frozen Enum — Traceability Mode [Normative]

The declared mechanism by which a code artifact was derived from its authorising spec.

| Value | Meaning | Restriction |
|---|---|---|
| **DERIVED** | Code generated from the spec by a template or tool | None |
| **MANUAL** | Code written by hand against the spec | None |
| **VALIDATED** | Pre-existing code validated against the spec post-hoc | Permitted only for external dependencies; MUST NOT be used for first-party production code |

**Registration policy: Standards Action.**

---

## §8 `SECTION-002` — Frozen Identifier Grammars [Normative]

Stable handle shapes the discipline relies on. Each is closed; adding a new shape is a §15 amendment.

| Identifier | Grammar | Scope | Owner |
|---|---|---|---|
| **Phase code** | `<INITIATIVE><NN><letter>` (e.g., `FOO02a`, `BAR03b`) | Commit subject of an execution PR | This doc §8 |
| **Invariant id** | `SBC-INV-<N>` for this family; `INV-<FAMILY>-<N>` for initiative families | §9 of a family's `-00` doc | Each family |
| **Errata id** | `ERRATA-NNN`, monotonically increasing within one `ERRATA.md` | A family's errata log | Each family |
| **Open-question id** | `EOQ-NNN-ERRATA-NNN` — stable across resolution | A family's errata open questions | Each family |
| **Concepts-doc open question** | `PCDN-<PHASE>-NNN` — `<PHASE>` consumes the complete registered phase token and the final `NNN` is the decision number | Inside a concepts doc | Each phase |
| **Term id** | `TERM-NNN`, monotonically increasing and never reused within one family | A family's §3 glossary rows | Each family |
| **Gate id** | `GATE-NNN`, monotonically increasing and never reused within one family | A family's §12 acceptance checklist | Each family |
| **Non-goal id** | `NONGOAL-NNN`, monotonically increasing and never reused within one family | A family's §11 non-goal ordered list | Each family |

An assigned id is **stable across resolution** — the resolving commit MAY cite it and the handle never re-binds.

A term definition uses the complete `TERM-NNN` handle in the first cell of a
four-column §3 glossary row and the bold term in the second cell. `NNN` is
exactly three decimal digits from `001` through `999`. A cross-family compiled
identity pairs the registry-owned family key with the authored handle as
`<family-key>:TERM-NNN`; the family qualifier does not alter or rebind the
authored handle. The family owner allocates the next unused number, and an
allocated number **MUST NOT** be reused after a term is renamed, retired, moved,
or superseded. Existing three-column glossary rows remain readable legacy
objects but are positional until migrated explicitly.

A gate definition uses the complete `GATE-NNN` handle in inline code at the
beginning of a §12 checklist item's content, followed by exactly space, em dash,
space, and nonempty gate text: ``- [x] `GATE-001` — <gate text>``. The checklist
marker continues to own declared checked state. `NNN` is exactly three ASCII
decimal digits from `001` through `999`; the family owner allocates the next
unused number, and an allocated number **MUST NOT** be reused. A cross-family
compiled identity is `<family-key>:GATE-NNN`, and the number conveys identity
only. A malformed or unmodified checklist item remains a readable positional
gate and **MUST NOT** be silently promoted. Stable identity does not infer
`blocks` or `verifies`, and it does not register `gate` as a checking source
kind for `verifies`.

A non-goal definition uses the complete `NONGOAL-NNN` handle in inline code at
the beginning of a §11 ordered-list item's content, followed by exactly space,
em dash, space, a bold non-goal title ending in a period, one space, and
nonempty body text: ``1. `NONGOAL-001` — **<non-goal title>.** <body>``. The
ordered-list number remains presentation only, and the handle is not part of
`nongoal.text`. `NNN` is exactly three ASCII decimal digits from `001` through
`999`; the family owner allocates the next unused number, and an allocated
number **MUST NOT** be reused. A cross-family compiled identity is
`<family-key>:NONGOAL-NNN`, and the number conveys identity only. A malformed or
unmodified item remains a readable positional non-goal and **MUST NOT** be
silently promoted. Stable identity does not infer equivalence, disambiguate a
cited target, or register any relationship outside the closed inference
registry.

**Full-handle recognition.** `NNN` is exactly three decimal digits. A PCDN
phase token begins with an uppercase letter and MAY contain uppercase letters,
digits, and internal hyphen-delimited components. Recognition is greedy to the
final `-NNN`: `PCDN-SIDX-00-001`, `PCDN-SIDX-06A-001`, and
`PCDN-SBC-00-C-001` therefore bind three complete, distinct handles. A parser
**MUST** consume the entire handle or reject it; it **MUST NOT** accept a valid
prefix of a longer alphanumeric or hyphenated token. EOQ recognition is
likewise exact: `EOQ-001-ERRATA-005` is one handle, not a prefix pattern.
Because the table above scopes EOQs to one family, a cross-family compiled key
**MUST** pair the family key with the exact authored EOQ handle; qualification
does not alter, truncate, or rebind the authored handle. A PCDN's complete
registered phase token already supplies its family/phase allocation.

**Canonicalisation.** An invariant id canonicalises to `INV-<FAMILY>-<N>` with `<N>` unpadded decimal. `INV-FOO-01`, `INV-FOO-1`, and `FOO-INV-1` denote the same object and MUST resolve identically. Both authored orderings remain valid input; zero-padding is NOT RECOMMENDED and MUST NOT create a distinct object. Full rules: `SBC-00-ADDENDUM-C.md` §4.3.

**Allocation authority.** Every family prefix MUST be registered with a named owner before use, and MUST be globally unique across the corpus. Claiming a prefix is Expert Review; reassigning or retiring one is Standards Action. An id MUST resolve identically regardless of whether its document is in-repo, archived, or handed off to a retrieval tier — a prefix scoped to a single document (rather than a family) does not satisfy this and is a conformance failure. Registry location is per-project and operational.

**Registration policy of this grammar set: Standards Action.**

---

## §9 Frozen Invariants [Normative]

Each invariant names a verification surface. Touching any `SBC-INV-N` requires a §15 amendment to this doc **first**, in a separate commit (this is SBC-INV-4 applied to itself).

| Id | Invariant | Verified by |
|---|---|---|
| **SBC-INV-1** | Every behaviour change in a ≥3-phase initiative MUST be preceded by a ratified concepts doc (a `-NN-CONCEPTS` with a dated §15 entry and all PCDNs resolved). | Reviewer: no execution PR cites an unratified phase. |
| **SBC-INV-2** | A glossary entry for a term that also exists in the project or an external standard MUST cite the authoritative source and mark the relationship using one of the three phrasings in §3. Silent restatement is prohibited. | Concepts-doc review of §3. |
| **SBC-INV-3** | Every frozen enum MUST declare its registration policy (§5 values) in its concepts doc. | Concepts-doc review of enum sections. |
| **SBC-INV-4** | Touching a frozen-enum value or an invariant MUST land a §15 amendment **first**, in a separate commit. No behaviour commit rides an unamended invariant. | Commit ordering review. |
| **SBC-INV-5** | An execution commit MUST cite its phase code (§8) in the commit subject and name in its description which §9 invariants it touches and how each is preserved. | Commit-subject and PR-description review. |
| **SBC-INV-6** | Spec gaps discovered during any phase MUST be recorded as deferred items with classification before the phase gate is traversed. Silent deferral is prohibited. | Phase-gate review of open items. |
| **SBC-INV-7** | A stealth revert is prohibited by construction: any revert of ratified-and-implemented content MUST produce (a) an errata entry filed first at status ⚪, (b) a dated §15 entry in the affected phase doc pointing at the errata id, and (c) a commit-subject citation of the errata id. All three parts are required; any one missing is a conformance failure. | Errata + §15 + commit-subject cross-check. |
| **SBC-INV-8** | Each externally-authored concept that crosses a project boundary MUST declare an `AuthorityRelationship` (§6) and a six-axis row. An undeclared mirror is never silently `own`. | Concepts-doc review of the authority matrix. |
| **SBC-INV-9** | A `-00` concepts doc MUST carry the load-bearing sections §0, §3/§4, §10, §12, §15. Later phases MAY omit non-applicable sections but MUST keep the load-bearing set. | Structural review. |
| **SBC-INV-10** | Every spec family running this discipline MUST maintain a living `ERRATA.md`; entries are permanent. A resolved entry stays in the log with status 🟢; it is never deleted. | Family-tree review. |
| **SBC-INV-11** | Templates are specs. A template MUST be ratified before any instantiation may enter production. | Template registration review. |
| **SBC-INV-12** | When an AI agent participates in any SBC phase, the agent MUST receive the ratified spec as primary context. Discrepancies between agent output and spec MUST be resolved at the spec layer; they MUST NOT be resolved by silently updating the code. | Post-agent review. |
| **SBC-INV-13** | When a resolution lands: if it edits a normative section of a `-NN-CONCEPTS.md`, the §15 entry is the canonical record and the errata entry MUST cite it. If it edits code, tests, or non-normative docs only, the errata entry is canonical and the §15 entry (if any) MUST cite the errata id. The two records are complementary; neither replaces the other. Boundary owned by `SBC-00-ADDENDUM-B.md §2`. | ERRATA + §15 cross-reference audit. |
| **SBC-INV-14** | An initiative-level acceptance list MUST name its conforming artifact (e.g. "a conforming deployment MUST satisfy gates (a)–(d)"). An optional phase yields a second conformance level naming the partial-deployment target ("a conforming deployment without phase `-NN` satisfies gates (a)–(c)"). | README / initiative acceptance-list review. |
| **SBC-INV-15** | Every spec object MUST have exactly one definition site. **The default definition site is recognised syntactically as an object's id emphasised in bold at the head of a table cell, list item, or heading. For an `open_question` only, the complete PCDN or EOQ handle in the first cell of a row under an explicitly titled Open Questions, Open Decisions, Decisions, or Resolved Decisions heading is the registered definition shape, whether the handle is bold, code-formatted, or plain.** Restating an id in a definition position in a second document constitutes a second definition site and is prohibited **regardless of the text that follows it**. Every other occurrence is a citation. Outside the registered open-question row shape, a reference MUST use one of the three §3 citation phrasings **and MUST NOT place the id in bold at the head**; inline code (`` `INV-FOO-1` ``) is the required form, with bold reserved for surrounding labels. Extended from glossary terms to all object kinds. | Parser: duplicate-definition report. |
| **SBC-INV-16** | An object in a section bound by a §12 Acceptance checklist MUST contain at least one capitalised RFC 2119 keyword in its statement. An object failing this MUST be reported as non-normative regardless of the section it occupies. | Parser: normativity report. |
| **SBC-INV-17** | An amendment whose `ChangeKind` is `semantic`, `scope`, or `retirement` MUST carry a linked rationale object recording what was considered and rejected, and what deliberately did not change. | Parser: amendments lacking a `motivates` edge. |
| **SBC-INV-18** | Any compiled representation of a spec corpus MUST be derivable from the authored corpus, a declared parser, version-control history, and the retained, independently trusted human authority evidence specified by ADDENDUM-B §1.1–§1.2 and ADDENDUM-C §7.1–§7.2. A fact held only in a compiled store is prohibited. Human decisions MUST be recorded and bound to exact subjects before they affect a derived result. Suspicion clearings remain version-control commit trailers under ADDENDUM-C §8.3; errata dispositions MUST NOT substitute for them. | Store audit: rebuild from retained inputs; rejection of untrusted or unbound decisions. |
| **SBC-INV-19** | Suspicion MUST propagate according to the amending change's `ChangeKind`; untyped blanket propagation across all citation sites is prohibited. Suspicion metrics MUST be reported as open count, median clear latency, and re-suspect rate together. | Suspicion-report review; re-suspect rate. |
| **SBC-INV-20** | A committed object index, where a project maintains one, MUST regenerate to a no-op at `HEAD`. History MUST NOT be reconstructed by replaying a current parser over past revisions. **Reading a recorded diff is not a parser replay and is permitted**: the prohibition targets *synthesising* past object state with today's parser, not *reading* what version control recorded as having changed. `SBC-INV-18` already names version-control history as a permitted derivation input, so a fact derived from a recorded diff is derivable in the sense that invariant requires. | CI: regenerate-and-diff. |
| **SBC-INV-21** | A change that alters an object's **binding status** — whether a conformance claim citing it asserts an obligation at all — MUST be ratified by the authority that owns the object, and MUST be recorded as a §15 amendment whose `ChangeKind` carries semantic force. It MUST NOT be recorded as `editorial`, **even when the change preserves the object's meaning**: under SBC-INV-16 adding or removing a capitalised RFC 2119 keyword changes what every existing conformance claim against that object asserts, so it is never merely formatting. A change that preserves both meaning and binding status MAY land as `editorial` without ratification. | Parser: per-object `normative_keywords` delta across revisions; any transition between empty and non-empty without a matching non-`editorial` §15 amendment is a violation. |

**Registration policy for adding an `SBC-INV-N`: Standards Action.**

---

## §10 Reconciliation — Adjacent Primitives [Normative]

| # | Primitive | Decision |
|---|---|---|
| 1 | **RFC 2119 / RFC 8174** | `AuthorityRelationship` = **compose**. The discipline uses MUST/SHOULD/MAY as components; it does not redefine them. The capitalisation gate is upstream's. |
| 2 | **Project operational context document** | `AuthorityRelationship` = **compose**. This doc renders it normative (§0); not a fork. Divergence is a bug filed against this family's errata. |
| 3 | **Parallel-agent execution workflow** | Out of scope. That governs *how many agents build it concurrently* (execution); this doc governs *what gets built and how its vocabulary is frozen* (planning). They are complementary; this doc does not absorb wave/worktree vocabulary (§11 non-goal 3). |
| 4 | **Issue tracker** | **compose** / **derive**. The issue tracker is the outward intake surface. Once an issue is accepted, the canonical record moves into the family's `ERRATA.md`. Never-accepted reports stay in the tracker only. The boundary is owned by the operational context; this doc references it. |
| 5 | **git** | **compose**. The discipline rides git commit-subject and merge mechanics to carry phase codes and amendment ordering; it does not modify git semantics. |
| 6 | **Family `-00` docs** | Those are **instances** of the form this doc specifies. This doc owns the form; each family owns its content. A family doc's *structure* conflicting with SBC-INV-9 is resolved in favour of this doc. A family doc's *vocabulary* conflict is the family's to resolve. |
| 7 | **W3C SCXML** | **compose**. SCXML is the RECOMMENDED format for state-dependent behavioural specs; this doc composes it as the preferred spec medium. It does not redefine SCXML semantics. |

---

## §11 Non-Goals

1. `NONGOAL-001` — **Not a project management methodology.** Sprint planning, story pointing, and velocity tracking are orthogonal.
2. `NONGOAL-002` — **Not a mandate on spec format beyond §9 (SBC-INV-9).** SCXML/SCJSON is RECOMMENDED for state-dependent systems; prose Markdown is acceptable for structural or policy specs.
3. `NONGOAL-003` — **Not a spec for the parallel-agent execution workflow.** Waves, worktree isolation, cherry-pick cadence, bench authorisation — those are execution-time concurrency rules owned by the operational context. Different contract surface; folding them in would couple planning vocabulary to fan-out mechanics that change independently.
4. `NONGOAL-004` — **Not a prohibition on exploratory coding.** Spikes and prototypes are not governed by SBC provided they are not merged to a governed branch without a ratified spec.
5. `NONGOAL-005` — **Not retroactive enforcement.** Single-doc TODOs and phase-1 prototypes MAY remain informal. The discipline binds a family from the moment it produces a `-NN-CONCEPTS` gate.
6. `NONGOAL-006` — **Not a test methodology.** SBC requires normative constraints to be covered by tests (gate condition for Phase 3); it does not prescribe unit vs. integration vs. formal verification.

---

## §12 Acceptance [Normative]

Conformance to this proposed revision additionally requires §4.2's recorded
condition-verification contract and its cited cross-owner requirements.
Existing acceptance criteria and their recorded states remain unchanged.

This document is considered ratified when all of the following are true:

- [x] `GATE-001` — Every meta-term used in the initiative families appears in §3 with a citation and a relationship marker (SBC-INV-2 applied to this doc).
- [x] `GATE-002` — Every row in §4 names exactly one authoritative owner.
- [x] `GATE-003` — The three discipline enums (§5, §6, §7) are closed and each declares its own registration policy (SBC-INV-3).
- [x] `GATE-004` — Identifier grammars in §8 are closed and marked Standards Action.
- [x] `GATE-005` — All twenty-one invariants appear in §9 as `SBC-INV-N` with a verification surface.
- [x] `GATE-006` — The conformance-target rule is carried by a numbered invariant (SBC-INV-14), not left as glossary-only prose.
- [x] `GATE-007` — The rule governing who may change an object's binding status is carried by a numbered invariant (SBC-INV-21), not left to per-case judgement in dispatch instructions.
- [x] `GATE-008` — Every adjacency in §10 carries a reconciliation decision with an `AuthorityRelationship` where an external grammar is involved (SBC-INV-8).
- [x] `GATE-009` — Non-goals in §11 each name the owner of the excluded surface or the reason it is out of scope.
- [x] `GATE-010` — This doc carries the load-bearing section set §0/§3/§4/§10/§12/§15 (SBC-INV-9 applied to itself).
- [x] `GATE-011` — Security-sensitive behaviour, if present, includes a threat model section (none applicable in this doc — no credentials, secrets, or PII are described).
- [x] `GATE-012` — §15 reflects the ratification event with reviewer identity and date.

---

## §13 Files Cited

| File | Role |
|---|---|
| `docs/SBC-00-CONCEPTS.md` | This document |
| `docs/SBC-00-ADDENDUM-A.md` | Operational context injection template |
| `docs/SBC-00-ADDENDUM-B.md` | `ErrataStatus` enum; ERRATA boundary rules; `ERRATA.md` file template |
| `docs/SBC-00-ADDENDUM-C.md` | Spec object model; identifier canonicalisation + allocation authority; `EdgeType`; `ChangeKind`; suspicion |
| `docs/SBC-00-ADDENDUM-D.md` | §15 change-log shape; `AmendmentStatus`; the rationale sub-block |
| `docs/SBC-ERRATA.md` | Living errata log for the `sbc` family (SBC-INV-10) |
| `docs/SPEC-BEFORE-CODE-CONCEPTS.md` | Superseded predecessor; the input this doc was synthesised from (see ERRATA-003) |
| `docs/SBC-01-DESIGN.md` | Next artefact in sequence (not yet created) |
| RFC 2119, RFC 8174 (IETF) | Normative-keyword grammar; composed per §10 row 1 |
| W3C SCXML | Recommended spec format; composed per §10 row 7 |

---

## §14 Unblocks

- **All current initiative families**: MAY now cite `SBC-INV-N` and the §5–§8 enums by identifier instead of re-deriving the form from the operational context narrative.
- **Future families**: a new `-00-CONCEPTS` doc SHOULD open by citing this doc for its form (§0–§15 layout, glossary discipline, enum registration-policy requirement) and reserve its own content for domain vocabulary.
- **Operational context maintenance**: future edits to the discipline narrative SHOULD land the normative change here via §15 first, then mirror the prose — per §0.

---

## §15 Change Log

| Rev | Date | Author | Status | Summary |
|---|---|---|---|---|
| 0.1.0 | 2026-05-31 | I. Abbott | DRAFT | Initial draft |
| 0.2.0 | 2026-05-31 | I. Abbott | DRAFT | Stripped downstream examples; abstracted to RFC-upstream framing |
| 0.3.0 | 2026-05-31 | I. Abbott | DRAFT | Synthesis with Opus 4.8 in-repo version and CLAUDE.md source: added §0 authority policy, §4 source-of-truth map, `RegistrationPolicy` (§5), `AuthorityRelationship` (§6), identifier grammars (§8), expanded to 12 invariants, §10 reconciliation table, §14 unblocks |
| 0.4.0 | 2026-05-31 | I. Abbott | DRAFT | Closed two gaps against ADDENDUM-B: §4 source-of-truth map now points `ErrataStatus`, ERRATA/§15 boundary, and ERRATA/tracker boundary to ADDENDUM-B; SBC-INV-13 added (ERRATA vs. §15 canonical-record decision rule); §13 files cited updated to include addenda |
| 0.5.0 | 2026-05-31 | I. Abbott | DRAFT | Self-conformance pass (cites ERRATA-003). Re-homed the conformance-target rule, dropped during the synthesis from `SPEC-BEFORE-CODE-CONCEPTS.md`, as **SBC-INV-14** (it had survived only as §3 glossary prose). Synced header revision to match this change log (was stale at 0.3.0). Corrected §12 invariant count (twelve → fourteen). Added `docs/SBC-ERRATA.md` and the superseded predecessor `docs/SPEC-BEFORE-CODE-CONCEPTS.md` to §13. Marked the predecessor SUPERSEDED; this doc is the sole canonical concepts artifact for the `sbc` family. |
| 0.6.0 | 2026-07-31 | I. Abbott (ratifier) | **Ratified** | **Ratification only — no normative change.** Closes §12 at the content that had been in force since 0.5.0 (2026-05-31). Filed against ERRATA-004: the family had operated for two months on an unratified normative root while 51 families, 56 concepts docs, and 585 phase-coded commits cited its rules, and while the project operational context had already been rewritten to name this document as the sole normative owner. Ratifying at existing content rather than editing forward is deliberate — the record must show what the corpus was actually governed by, not a retroactively improved version of it. Content changes accumulated during the gap land separately at 0.7.0. |
| 0.7.0 | 2026-07-31 | I. Abbott (ratifier) | **Ratified (amendment)** | **Object-model amendment**, adopting the four parent changes enumerated in `SBC-00-ADDENDUM-C.md` §12.2. Landed as a *separate revision from the 0.6.0 ratification* so the record distinguishes what the corpus was governed by before this date from what changed on it (ERRATA-004). **(1) §4** gains five source-of-truth rows: object model + attribute schema, identifier canonicalisation + allocation authority, `EdgeType`, `ChangeKind` + suspicion → ADDENDUM-C; §15 change-log shape + `AmendmentStatus` → ADDENDUM-D. **(2) §8** gains a canonicalisation rule (`INV-FOO-01` ≡ `INV-FOO-1` ≡ `FOO-INV-1`) and an allocation authority requiring globally-unique, family-scoped, owner-registered prefixes — motivated by a measured active collision, `PHASE-INV-1` defined in seven documents with seven meanings, and by two padding conventions coexisting inside one family. **(3) §9** adopts `SBC-INV-15`…`SBC-INV-20`: one definition site per object (measured: 54 ids with multiple definition sites, extending SBC-INV-2's anti-restatement rule from glossary terms to all object kinds); normativity measured not asserted (measured: 42.9% of invariant statements carry no capitalised keyword, so they bind nothing under the §1 capitalisation gate); rationale required for semantic/scope/retirement amendments; the compiled-store derivability rule; typed suspicion propagation with mandatory latency + re-suspect metrics; committed-index no-op regeneration. **(4) §13** cites ADDENDUM-C and ADDENDUM-D. No existing invariant's obligation changed; SBC-INV-1…14 are untouched. Evidence base: `scripts/specidx/scan.py` over 642 documents / 51 families / 506 invariant definitions / 4,538 citations, pinned to `fcc6e924d`. |

### 0.8.0 — 2026-07-31 — amended

**Author:** I. Abbott (ratifier)
**Change kind:** semantic
**Touches:** SBC-INV-16, sbc:TERM-035
**Summary:** **Escalation-authority amendment.** §9 adopts **`SBC-INV-21`**: a change to an object's *binding status* requires ratification by the object's owning authority and a §15 amendment carrying semantic force, and MUST NOT be recorded as `editorial` even when meaning is preserved.

#### Rationale

SBC-INV-16 made normativity a measured property but left unstated *who may change it*. In the MCAD SBC-INV-15 conversion, `INV-MCAD-11` acquired its first capitalised keyword — moving from binding nothing to binding every conformance claim against it — inside a wave classified `editorial`, while a scope reversal in the same wave was escalated to the owner. Both calls were defensible; neither followed a written rule. The asymmetry was decided in a dispatch prompt, which means the next one is decided by whichever agent is holding it. Corpus evidence at `6d045949c`: 174 keywordless invariants, of which MCAD alone holds four (`INV-MCAD-1`, `-4`, `-8`, `-12`; `mcad:ERRATA-013`) — so the population this rule governs is large and currently ungoverned.

Considered and rejected: (a) *a new `ChangeKind` value for binding-status changes* — rejected because `ChangeKind` is a frozen enum under Standards Action and `semantic` ("an invariant's obligation changes") already covers going from no obligation to an obligation; a new value would buy nothing and cost a frozen-enum amendment. (b) *Keying the rule on process* ("a cleanup wave MUST NOT…") — rejected as evadable by renaming the wave; the invariant keys on **what the change does**, not what the process is called. (c) *Advisory `SHOULD`* — rejected because per-case judgement is precisely the failure being corrected.

What deliberately did not change: SBC-INV-16's text and meaning (this governs who may change binding status, not what binding means); the `ChangeKind` enum and its registration policy; the obligations of SBC-INV-1…20, none of which are altered; and the separate question of whether keywordless invariants MUST be fixed — this invariant governs the *authority* for such a change, not a deadline for making it.

### 0.9.0 — 2026-07-31 — amended

**Author:** I. Abbott (ratifier)
**Change kind:** clarification
**Touches:** SBC-INV-15
**Summary:** **Citation-form clarification.** §9's `SBC-INV-15` gains the syntactic recognition rule it was always enforced by, and the positive authoring form. **Change kind:** `clarification` — the prior text already prohibited a bolded id at the head of a list item, table cell, or heading; what it did not say is that the prohibition is **positional and unconditional**, so a citation using one of the §3 phrasings *still* registers as a definition site if it is bolded at the head. No previously-conforming document becomes non-conforming. **Touches:** SBC-INV-15 (clarified). **Motivation, measured:** rule and checker had drifted, and the gap cost four separate authors. Three independent agents converting the MCAD family each hit it and each independently switched to inline code; the survey document cataloguing the violations contained two of its own; and the errata entry documenting *that* introduced two more, written one commit after the convention was first recorded — corpus F3 rose 37→39 and was traced back to it. A rule that its own author violates while writing it down is under-specified, not under-obeyed. **Considered and rejected:** (a) *teach the parser citation-form detection*, so a well-worded bold citation is not counted — rejected as more machinery and more fragile than fixing the authoring form, and it would leave the metric's meaning ambiguous. (b) *Leave it as a per-family convention note* — rejected because it binds one document and is read by nobody authoring the next; that is where it sat when it caught its fourth author. (c) *A new invariant* — rejected because it would split one rule across two ids and re-create the multiple-definition-site problem in the doc defining it. **What deliberately did not change:** the §3 citation phrasings; SBC-INV-15's semantic requirement of one definition site per object; the duplicate-definition report as its verification surface. This amendment makes the metric and the rule agree by construction — `F3` is a formatting measure, and the invariant now says so rather than implying a semantic one.

### 0.10.0 — 2026-07-31 — amended

**Author:** I. Abbott (ratifier)
**Change kind:** clarification
**Touches:** SBC-INV-20, SBC-INV-18
**Summary:** **Diff-reading boundary clarification.** §9's `SBC-INV-20` states that reading a recorded diff is not a parser replay and is permitted. **Change kind:** `clarification` — no obligation changes; the sentence disambiguates a scope that was already implied. **Touches:** SBC-INV-20 (clarified), SBC-INV-18 (cited, unchanged). **Motivation:** scoping a `ChangeKind` backfill surfaced that INV-20's second sentence, read literally, appeared to forbid the one method that could type historical amendments at scale, and an implementer could reasonably have stopped there. The two readings were never actually in tension: **`SBC-INV-18` already lists version-control history among the permitted derivation inputs**, so the prohibition cannot have meant "do not read git" — it means do not *synthesise* what a past revision said by running today's parser over it. The distinction is between reading a record and manufacturing one. **Considered and rejected:** (a) *leaving it to the implementer* — rejected because the ambiguity had already blocked a scoping recommendation, and an unstated boundary is decided by whoever hits it first; (b) *amending INV-18 instead* — rejected because INV-18 was never ambiguous; the imprecision was INV-20's. **What deliberately did not change:** the no-op regeneration requirement; the prohibition on parser replay itself; INV-18's derivability rule; and the separate question of whether a diff-derived `ChangeKind` is reliable enough to record, which is an evidentiary matter for the backfill, not a licence granted here.

### 0.11.0 — 2026-08-07 — amended

**Author:** I. Abbott (ratifier)
**Change kind:** semantic
**Touches:** SECTION-002, SBC-INV-15
**Summary:** **Open-question identity and definition-site amendment.** §8 now makes PCDN and EOQ recognition full-handle and exact, with the entire registered phase token consumed before the final three-digit decision number. `SBC-INV-15` registers the existing first-cell decision-table row as the `open_question` definition shape; later occurrences remain citations and duplicate rows remain violations.

#### Rationale

The existing prefix parser collapsed `PCDN-SIDX-00-…`, `PCDN-SIDX-06-…`, and `PCDN-SIDX-06A-…` into fabricated shorter identities, while the corpus's decision rows used code-formatted handles that the default bold-head rule could not recognize.

Considered and rejected: path- or line-derived ids, first-match-wins, and retaining a parser-only exception; each would make identity depend on location, hide duplicate authority, or place normative vocabulary in tooling.

What deliberately did not change: invariant canonicalization, family prefix allocation, PCDN/EOQ stability across resolution, other object definition shapes, or the one-definition-site obligation.

### 0.12.0 — 2026-08-23 — ratified stable-term Standards Action

**Author:** Ira Abbott (owner and ratifier)
**Change kind:** semantic
**Touches:** sbc:TERM-001, sbc:TERM-002, sbc:TERM-003, sbc:TERM-004, sbc:TERM-005, sbc:TERM-006, sbc:TERM-007, sbc:TERM-008, sbc:TERM-009, sbc:TERM-010, sbc:TERM-011, sbc:TERM-012, sbc:TERM-013, sbc:TERM-014, sbc:TERM-015, sbc:TERM-016, sbc:TERM-017, sbc:TERM-018, sbc:TERM-019, sbc:TERM-020, sbc:TERM-044, sbc:TERM-045, sbc:TERM-046, sbc:TERM-047, sbc:TERM-048, sbc:TERM-049, sbc:TERM-050, sbc:TERM-051, sbc:TERM-052, sbc:TERM-053, sbc:TERM-054, sbc:TERM-055, sbc:TERM-056, sbc:TERM-057, sbc:TERM-058, sbc:TERM-059, sbc:TERM-060, sbc:ERRATA-007
**Summary:** Owner ratification registers exact authored `TERM-NNN` handles, family-scoped allocation without reuse, the four-column §3 definition row, and canonical compiled identity `<family-key>:TERM-NNN`. The initial allocation covers the sixty pre-existing compiled SBC term objects; numbering records identity only.

#### Rationale

Sixty positional term definitions caused sixty unresolved dependency targets and six unresolved dependency sources. Stable authored handles close that measured population without changing any definition or relationship text. The parent amendment owns the twenty current-concepts terms and the seventeen superseded-predecessor terms; ADDENDUM-C records its twenty-three terms separately.

The identifier-grammar paragraph and predecessor annotation have no pre-existing stable object target. This entry deliberately does not substitute their containing documents; their positional carriers remain explicit in the summary and source diff.

Considered and rejected: lowercased term text, path/line identity, content hashes, document-scoped ids, first-match collision repair, and implicit identity for unmodified legacy rows.

What deliberately did not change: term definition or relationship text; `ObjectKind`, `EdgeType`, `ChangeKind`, term equivalence, document lifecycle, retained historical projection bytes, or the positional status of gates, non-goals, enum values, authority rows, sections, and legacy amendments.

### 0.13.0 — 2026-08-23 — amended

**Author:** Ira Abbott (owner and ratifier)
**Change kind:** semantic
**Touches:** SBC-00-CONCEPTS#amendment:0.9.0, SBC-00-CONCEPTS#amendment:0.10.0, sbc:ERRATA-008
**Summary:** Owner acceptance of `EOQ-001-ERRATA-008` migrates only the evidence-complete 0.9.0 and 0.10.0 legacy amendments to frozen block identities. Their normative prose is unchanged, and the other twenty-one legacy amendments remain unchanged.

#### Rationale

Both migrated rows already authored exact revision, date, author, amendment status, `clarification` change kind, globally resolvable invariant targets, and their complete summaries. Keeping them positional would preserve five known identity diagnostics and withhold three authored `amends` relations despite complete evidence.

The owner accepted this exact two-row measure through `EOQ-001-ERRATA-008`. No other legacy amendment inherits that acceptance.

Considered and rejected: migrating every legacy amendment, which would fabricate missing fields or silently reinterpret positional and textual targets; and retaining these two rows solely for formatting consistency, which would discard their already-authored stable evidence.

What deliberately did not change: the amendments' normative prose, classification, targets, authorship, dates, or summaries; any invariant obligation; the other twenty-one legacy amendments; gates, non-goals, or sections; and the separate problems owned by ERRATA-005 and ERRATA-006.

### 0.14.0 — 2026-08-23 — ratified stable-gate Standards Action

**Author:** Ira Abbott (owner and ratifier)
**Change kind:** semantic
**Touches:** sbc:GATE-001, sbc:GATE-002, sbc:GATE-003, sbc:GATE-004, sbc:GATE-005, sbc:GATE-006, sbc:GATE-007, sbc:GATE-008, sbc:GATE-009, sbc:GATE-010, sbc:GATE-011, sbc:GATE-012, sbc:ERRATA-009
**Summary:** Owner acceptance of `EOQ-001-ERRATA-009` registers exact authored `GATE-NNN` handles, family-scoped allocation without reuse, the §12 checklist definition shape, and canonical compiled identity `<family-key>:GATE-NNN`. The accepted allocation assigns `GATE-001` through `GATE-012` to this document's existing gates in authored source order.

#### Rationale

The accepted 31-row SBC gate frontier closes the measured positional identity gap without changing gate text or checked state. This parent amendment owns the twelve current-concepts allocations; ADDENDUM-C owns `GATE-013` through `GATE-023`, and the superseded predecessor receives `GATE-024` through `GATE-031` as an identity annotation only.

The first committed projection containing the explicit handles is an additive object-schema-v3 compatibility frontier. Retained historical bytes are neither reinterpreted nor backfilled, and producer, store, query, and consumer support deploy atomically.

Considered and rejected: document-scoped, path/line, content-hash, invariant-derived, prose-label, and first-match identity; silent promotion of malformed or unmodified checklist rows; and deriving `blocks` or `verifies` from checked state or checklist text.

What deliberately did not change: gate text or checked state; invariant meaning; the closed `ObjectKind`, `EdgeType`, or `ChangeKind` enums; the absence of a checking source kind for `verifies`; retained projection bytes; ERRATA-006's ambiguous invariant targets; or the positional status of non-goals, sections, enum values, authority rows, and the other twenty-one legacy amendments.

### EVENT-001 — 2026-09-01 — project event

**Author:** Ira Abbott (owner); OpenAI Codex (evidence review)
**Summary:** The owner accepted `SBC-ERRATA-013 PRECONDITION`. A controlled, unpublished projection review showed that allocating the next SBC erratum while the 0.8.0 amendment remains positional adds one `dependency_source_unresolved` record; explicit family qualification of the MCAD erratum alone leaves the same invalid-source class. A candidate frozen-block migration that maps the authored `ChangeKind` token to the registered term titled “Change kind” and splits the already-authored rationale removes six invalid-source and one invalid-target records, but it would add stable amendment and rationale identities plus graph edges. No erratum identifier, target mapping, migration, scanner change, baseline change, clearing act, commit, ingest, or deployment is authorized or performed by this event.

### 0.15.0 — 2026-08-23 — ratified stable-non-goal Standards Action

**Author:** Ira Abbott (owner and ratifier)
**Change kind:** semantic
**Touches:** sbc:NONGOAL-001, sbc:NONGOAL-002, sbc:NONGOAL-003, sbc:NONGOAL-004, sbc:NONGOAL-005, sbc:NONGOAL-006, sbc:ERRATA-010
**Summary:** Owner acceptance of `EOQ-001-ERRATA-010` registers exact authored `NONGOAL-NNN` handles, family-scoped allocation without reuse, the §11 ordered-list definition shape, and canonical compiled identity `<family-key>:NONGOAL-NNN`. The accepted allocation assigns `NONGOAL-001` through `NONGOAL-006` to this document's existing non-goals in authored source order.

#### Rationale

The accepted 16-row SBC non-goal frontier closes the measured positional identity gap without changing non-goal text. This parent amendment owns the six current-concepts allocations; ADDENDUM-C owns `NONGOAL-007` through `NONGOAL-012`, and the superseded predecessor receives `NONGOAL-013` through `NONGOAL-016` as identity annotations only.

The first committed projection containing the explicit handles is an additive object-schema-v3 compatibility frontier. Retained historical bytes are neither reinterpreted nor backfilled, and producer, store, query, and consumer support deploy atomically.

Considered and rejected: document-scoped, path/line, content-hash, title-derived, bare ordered-list, and first-match identity; silent promotion of malformed or unmodified items; and inferred equivalence or target disambiguation.

What deliberately did not change: non-goal text; invariant meaning; the closed `ObjectKind`, `EdgeType`, or `ChangeKind` enums; the inference registry; retained projection bytes; ERRATA-006's ambiguous invariant targets; ERRATA-005; or the positional status of sections, enum values, authority rows, and the other twenty-one legacy amendments.

---

*End of SBC-00-CONCEPTS*

### 0.16.0 — 2026-09-05 — ratified ERRATA-015 amendment

**Author:** Ira Abbott (ratifier); OpenAI Codex (drafting and recording)
**Change kind:** semantic
**Touches:** SBC-00-CONCEPTS
**Summary:** Assign assessment/disposition ownership and explicitly retain trusted human authority inputs in derivability. The owner ratified this exact coordinated packet in task `01a06eee-bae3-7911-9198-adfae97256f1` on September 5, 2026. Accepted patch SHA-256: `220d77faff10b8132768a2d0a19ec7e099decf605ad72dd7f57a174f40e69de1`. This records specification ratification, not implementation, clearance, or deployment.

#### Rationale

The owner accepted decision-packet version 1 and subsequently ratified this exact
amendment packet on September 5, 2026. This amendment supplies the reserved contract. Treating every old
missing process field as a present violation, equating acceptance with repair,
and hiding diagnostics by client arithmetic were considered and rejected.
The native repair lifecycle, retained historical evidence, C6 clearings, and
C11/C12 response meanings deliberately do not change. This ratification authorizes deriving implementation from the coordinated
amendment after the specification commit boundary.

### 0.17.0 — 2026-09-13 — ratified condition-verification amendment

**Author:** Ira Abbott (ratifier); OpenAI Codex (drafting and recording)
**Change kind:** semantic
**Touches:** SBC-00-CONCEPTS, SBC-INV-18
**Summary:** Specify §4.2's part of recorded condition verification under
SBC ERRATA-015. The owner ratified this exact packet and its linked digest
manifest on September 13, 2026 in task `01a06eee-bae3-7911-9198-adfae97256f1`.
Accepted packet commit: `7645b24614f181b64ac254b7028367b9f26b6842`.
Accepted patch SHA-256: `8d61a050dd6ed81ee8ec41cdf3829f020185b4e132d1419dbad12df88fb1cb39`.
Accepted manifest SHA-256: `fbb41f409f5445b8d7b53a09dc35fb657520e3c275adc94d1b6624831a8832fb`.
This ratifies the specification; no concrete verification record, approval pin,
native-state change, implementation, or deployment is asserted.

#### Rationale

Independent condition binding does not admit later verification or establish a
before/after completion transition. The ratified coordinated amendment supplies those
contracts while preserving approved obligation changes as a distinct action.
Automatic interpretation of arbitrary test logs, reuse of exception authority,
editing approved condition evidence, and inference from absence were rejected.
The initial profile records human-confirmed evidence; machine-execution profiles
remain unregistered. Exact-text ratification precedes implementation.
