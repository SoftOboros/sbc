# SBC-00-ADDENDUM-C — Spec Object Model

**Document ID:** SBC-00-ADDENDUM-C
**Status:** RATIFIED (amended 2026-08-09)
**Revision:** 0.6.0
**Date:** 2026-08-09
**Author:** Ira Abbott / SoftOboros Inc.
**Parent:** `docs/SBC-00-CONCEPTS.md`
**Canonical path:** `docs/SBC-00-ADDENDUM-C.md`
**See also:** `SBC-00-ADDENDUM-A.md` (operational injection), `SBC-00-ADDENDUM-B.md` (`ErrataStatus`, ERRATA shape)
**Blocks:** any tooling family that compiles, indexes, locates, or queries an SBC corpus.
**Coordinates with:** `TODO-SIDX-00-CONCEPTS.md` (delivery contract), `TODO-SIDX-06E-C6-OBJECT-GRAPH-AND-ACKNOWLEDGMENT.md` rev 0.4.0 (ratified correction Standards Action record), and `docs/ops/doc-handoff.md` (location-declaration ritual).

---

## §0 Purpose and Authority

SBC-00-CONCEPTS specifies the *discipline*: what a concepts doc contains, which enums are frozen, which invariants bind. It says nothing about what an SBC corpus **is** as a data structure. Every consumer that has needed that structure so far — a reviewer grepping for an id, an agent reading a family cold, the doc-handoff ritual, a RAG chunker — has inferred it independently from Markdown layout. Those inferences disagree, and §2 measures the disagreement.

This addendum owns the **spec object model**: the machine-readable projection of an SBC corpus, its identifier grammar, its attribute schema, its edge types, and the rules by which history and suspicion are derived. It is the contract between the authored corpus and any tool that reads it.

### §0.1 The compilation rule [Normative]

> **Markdown is source. The store is a cache.**
> Any fact in a compiled store that is not reconstructible from the authored corpus plus a declared parser plus git history is a violation of this addendum.

This is the load-bearing rule of the entire model, and it is stated first because every subsequent design decision defers to it. A tool MAY build any store it likes — relational, graph, vector, columnar, several at once — provided the store is *derived*. The moment a store holds an authored fact, the corpus has two authorities, `SBC-00-CONCEPTS.md` §4's one-owner-per-concept guarantee is void, and the failure is undetectable by review because the second authority is invisible in the diff.

There is exactly one class of fact that this rule does not cover — suspicion clearing, which is genuinely new information not present in any document. §8.3 resolves it without weakening the rule.

### §0.2 Authority relationship to SBC-00 [Normative]

This addendum stands to `SBC-00-CONCEPTS.md` as `AuthorityRelationship = extend` (§6 of the parent): it adds named structure on an unchanged upstream grammar. It **MUST NOT** redefine any parent term, enum value, or invariant. Where the object model needs a concept the parent lacks, the concept lands in the parent by amendment and is referenced here — never defined here and mirrored upward.

Tooling families that consume this model (a spec-index service, a metrics dashboard, a CI check) stand to this addendum as `derive`: they interpret and evaluate against the grammar without owning it. Their outputs are local; their inputs are upstream. A tooling family **MUST NOT** introduce spec vocabulary; a gap in the model is filed against this addendum.

---

## §1 The Three Axes [Normative]

Requirements systems conventionally answer one question: *what is true?* An SBC corpus is authored to answer three, and the object model **MUST** preserve all three as first-class, independently queryable axes.

| Axis | Question | Where it lives today | Retrievable? |
|---|---|---|---|
| **State** | What is true now? | Current text of a `-NN-CONCEPTS.md` | ✅ by grep |
| **Trajectory** | How did we get here? | §15 change logs, git history, ERRATA transitions | ⚠️ prose, two formats, append-ordered |
| **Intent** | Why did we move? | §15 rationale essays, PCDN resolutions, ERRATA root-cause fields | ❌ unaddressable |

The third axis is the one traditional requirements management omits — DOORS carries rationale only as an untyped text attribute — and it is where engineering judgment actually lives. This corpus already authors it at high quality (`TODO-MCAD-00-CONCEPTS.md` rev 0.3.0 and 0.5.0 are sustained design arguments), and stores it in the least retrievable location available: the tail of a table cell in an append-only log.

**INV-C-3 (proposed)** binds Intent as an object class rather than a formatting convention.

---

## §2 Problem Statement [Informative]

Evidence gathered by `scripts/specidx/scan.py`, a read-only parser over `docs/todo/`, `docs/closedclaw/`, and `docs/spec-before-code/docs/`, pinned to commit `fcc6e924d` (2026-07-31). 642 documents, 56 concepts docs, 51 families, 3,512 extracted objects, 4,538 citations.

| # | Finding | Measured | Consequence |
|---|---|---|---|
| F1 | §15 change-log shape has forked | 27 bullet · 5 table · 16 unparsed · 8 absent | The Trajectory axis is not machine-readable for 89% of concepts docs |
| F10 | Invariant *definition* has ≥2 renderings | 422 bullet · 84 table | "Which line defines this id" is a heuristic, not a fact |
| F2 | Invariants with no declared verification surface | **429 / 506 (84.8%)** | SBC-00 §9's "names a verification surface" holds only in the table shape |
| F6 | Invariant statements with no RFC 2119 keyword | **217 / 506 (42.9%)** | Under the parent's own capitalisation gate, 43% of "invariants" are advisory prose |
| F7 | Acceptance gates citing an invariant id | **63 / 1,326 (4.8%)** | §12 conformance and §9 invariants are structurally disconnected |
| F3 | Ids with >1 definition site | 54 | e.g. `INV-SHARE-4` in SHARE-00 §9 *and* SHARE-01; `ECA-INV-1/2/5` in ECA-00 *and* ECA-01 |
| F4 | Ids cited but never defined | 52 | e.g. `INV-CTD-02` cited 10×, defined nowhere |
| F5 | Cross-family term collisions | 30 | `executor` ×5, `boundary condition` ×4, `net` ×4 — none labelled |
| F8 | Citation fan-out of the most-cited invariant | `INV-MCAD-9` at 56 sites | Blast radius of one amendment, currently uncomputed |
| F9 | Concepts docs missing a load-bearing section | 8 | SBC-INV-9 unenforced |
| F12 | Id grammar has eroded *within* a family | `INV-CTD-01/02/03` alongside `INV-CTD-1/10/11/12` | No tool can decide whether `INV-CTD-1` and `INV-CTD-01` are one object |

Three of these deserve naming as classes rather than counts.

**F3 is silent restatement of invariants.** SBC-INV-2 prohibits silent restatement of *glossary terms* and gives three citation phrasings. No equivalent rule covers invariants, so phase docs restate parent invariants inline and the copies drift independently. This is the parent's own named failure mode operating in a surface the parent does not guard.

**F6 is a normativity gap.** SBC-00 §1 adopts the RFC 8174 capitalisation gate: keywords bind *only* in capitals. An invariant reading "Identity preservation. Audit row carries `actual_user_id` distinct from `corpus_owner_id`" contains no keyword, therefore binds nothing, yet sits in a section titled *Frozen Invariants*. The discipline is self-consistent; the corpus is not conformant to it, and nothing measures the gap.

**F12 is grammar erosion without an allocation authority.** SBC-00 §8 freezes id *shapes* but names no owner for the family-prefix namespace and no canonicalisation rule for numeric parts. Two zero-padding conventions coexist inside one family. This will worsen: two families spun up in parallel can claim the same prefix with nothing to stop them.

---

## §3 Canonical Glossary [Normative]

Per SBC-INV-2, each entry cites its source and marks the relationship.

| Term | Definition | Relationship |
|---|---|---|
| **Spec object** | An individually addressable, individually citable unit of spec content, carrying a stable id, a kind, and a typed attribute set. | Owned by SBC-00-ADDENDUM-C. |
| **Definition site** | The single authored location that constitutes a spec object's existence. Every other occurrence of its id is a citation. | Owned by this addendum. |
| **Citation** | An occurrence of a spec object's id outside its definition site, in a document, commit message, test, or code comment. | Owned by this addendum. |
| **Edge** | A typed, directional relationship between two spec objects. | Owned by this addendum §5. |
| **Compiled store** | Any derived representation of the corpus built by a parser. Never authoritative (§0.1). | Owned by this addendum. |
| **Snapshot** | The committed object index at one commit — the corpus's state as a data structure at that point. | Owned by this addendum §7. |
| **Baseline** | A named, frozen snapshot spanning a whole family, produced at a ratification or handoff event. | Owned by this addendum §7; composes the DOORS notion. |
| **Suspicion** | The derived condition of an object whose upstream dependency changed after the object last acknowledged it. | Owned by this addendum §8; adapted from DOORS suspect links: `<delta>` = typed by change kind, cleared in git rather than in a tool. |
| **Dependency edge** | A typed edge whose registered orientation says one globally identified object depends on another for C6. | Owned by this addendum §5.1. |
| **Pair state** | Derived state for one `(upstream global object id, dependent global object id, edge type)` relationship generation. | Owned by this addendum §8.3. |
| **Introduction frontier** | The sorted Git antichain of minimal commits that introduce one continuous pair generation. | Owned by this addendum §8.3. |
| **Acknowledged-through frontier** | The sorted antichain of maximal upstream change events explicitly accepted by a completed initial or clearing act. | Owned by this addendum §8.3. |
| **Open cycle** | The interval from the first propagating event after acknowledgment through one valid atomic clearing. | Owned by this addendum §8.3. |
| **Rationale object** | An addressable record of why a change was made — what was considered, what was rejected, and what deliberately did not change. | Owned by this addendum §1/§4; does not exist upstream. |
| **Change kind** | The classification of an amendment's semantic force, governing whether it propagates suspicion (§8.2). | Owned by this addendum. |
| **Allocation authority** | The named owner of an identifier namespace, responsible for preventing collision. | Owned by this addendum §4.3. |
| **Location record** | A versioned, integrity-bound locator for one governed document at one repository, archive, Memory Alpha, or pointer location. A document may have several concurrent records. | Owned by this addendum §4.4. |
| **Document lifecycle state** | The declared authority/workflow state of a governed document, kept orthogonal to every storage location. | Owned by this addendum §4.5. |
| **Normative keyword** | MUST / MUST NOT / SHALL / SHOULD / SHOULD NOT / MAY / RECOMMENDED, binding only when capitalised. | As defined in RFC 2119 / RFC 8174; used without modification. |
| **Registration policy** | Standards Action / Specification Required / Expert Review. | As defined in `SBC-00-CONCEPTS.md` §5; used without modification. |
| **AuthorityRelationship** | mirror / adapt / extend / compose / own / derive / represent. | As defined in `SBC-00-CONCEPTS.md` §6; used without modification. |
| **ErrataStatus** | 🟢 / 🟡 / 🔴 / ⚪ lifecycle values. | As defined in `SBC-00-ADDENDUM-B.md` §1; used without modification. |
| **OpenQuestionStatus** | The native lifecycle of a PCDN or EOQ definition: `open`, `pending_ratification`, `resolved`, or `unknown`. | Owned by this addendum §4.6. |

---

## §4 Object Model [Normative]

### §4.1 Frozen enum — `ObjectKind`

Every spec object has exactly one kind. The set is closed.

| Value | Definition site shape | Axis |
|---|---|---|
| `document` | A governed `.md` file's header block | State |
| `section` | A numbered heading within a document | State |
| `invariant` | A bold id at the head of a table cell, list item, or heading (§6.1) | State |
| `term` | A bold term at the head of a §3 glossary row | State |
| `gate` | A checklist item in §12 Acceptance | State |
| `nongoal` | A numbered bold item in §11 Non-Goals | State |
| `enum_value` | A row in a frozen-enum table | State |
| `authority_row` | A row in a §6/§10 authority matrix | State |
| `errata` | An `## ERRATA-NNN` entry | State + Intent |
| `open_question` | The complete PCDN or EOQ handle in the first cell of a Markdown table row under an explicitly titled Open Questions, Open Decisions, Decisions, or Resolved Decisions heading; later occurrences are citations | Intent |
| `amendment` | One §15 change-log entry | Trajectory |
| `rationale` | An addressable record of why a change was made (§1) | Intent |

**Registration policy: Standards Action.**

`nongoal` is deliberately a first-class kind with lifecycle status. Non-goals evolve — `TODO-MCAD-00-CONCEPTS.md` rev 0.5.0 *withdraws* a §11 exclusion and takes ownership of thermal, structural, and flow analysis — and a withdrawn non-goal is exactly as consequential as an amended invariant. DOORS has no equivalent; this is an extension, not a port.

### §4.2 Attribute schema

Adopting ReqIF's genuinely good idea — a declared type system for objects and attributes — without its serialisation. Each `ObjectKind` declares an attribute set; attributes are typed and each carries a *provenance*, reusing the shape MCAD-00 §6.6 already proved.

Every object carries this common set:

| Attribute | Type | Notes |
|---|---|---|
| `id` | string | Canonical form per §4.3 |
| `kind` | `ObjectKind` | §4.1 |
| `family` | string | Family key |
| `document`, `line`, `anchor` | locator | Position — mutable, never identity |
| `status` | enum (kind-specific) | e.g. `ErrataStatus` for `errata`; `OpenQuestionStatus` for `open_question` |
| `normative` | bool | Derived: is this in a section §12 binds? |
| `text` | string | The authored statement |
| `attr_provenance` | `declared` \| `inferred` | Per-attribute; see below |
| `first_seen`, `last_changed` | commit SHA | Derived from git (§7) |

A `document` object additionally carries `lifecycle_state` and resolves to zero
or more `locations` keyed by its document id in a derived location projection.
These attributes use the frozen grammar in §4.4/§4.5. Other objects resolve
locations through their containing `document`; a consumer **MUST NOT** copy
location records onto every contained object and thereby create independently
drifting locators.

An attribute is `declared` when authored explicitly and `inferred` when the parser derived it from layout. **Inference is permitted; silent inference is not.** A store **MUST** carry the provenance of every attribute it holds, so a consumer can distinguish "the author said this invariant is verified by X" from "the parser guessed from column position." F2's 84.8% is exactly what unmarked inference looks like from the outside.

### §4.3 Identifier grammar and allocation authority

SBC-00 §8 freezes id shapes. This addendum adds what §8 omits: canonicalisation and an owner.

**Canonical form.** An invariant id canonicalises to `INV-<FAMILY>-<N>` with `<N>` unpadded decimal. `INV-CTD-01`, `INV-CTD-1`, and `CTD-INV-1` are the same object and **MUST** resolve identically. Both authored orderings (`INV-<FAMILY>-<N>` and `<FAMILY>-INV-<N>`) remain valid input; a parser normalises. Zero-padding in authored text is **NOT RECOMMENDED** and **MUST NOT** create a distinct object.

**Allocation authority.** Each family prefix is an owned object in a registry, with a named owner and a claim date. Claiming a prefix is **Expert Review**; reassigning or retiring one is **Standards Action**. Without this, two families spun up in parallel collide silently — the exact fan-out scenario the operational context's parallel-agent workflow makes routine.

**Global resolvability.** An SBC id resolves globally, independent of location. This is a deliberate improvement over DOORS, whose Absolute Numbers are module-scoped and re-bind on relocation. `INV-SSV-7` **MUST** resolve identically whether its document is in-repo, inside `docs/archived/*.zip`, or handed off to a RAG notebook. This property is what makes the archive tier safe to expand, and it is purchased with the allocation authority above.

#### §4.3.1 `GlobalObjectIdV1` and edge eligibility [Normative]

The initial C6 endpoint profile is `GlobalObjectIdV1`: an NFC string of at
most 512 UTF-8 bytes, with no surrogate, control character, backtick,
leading/trailing whitespace, `/`, `\`, or invariant prefix in the exact
reserved set `{FOO, BAR, BAZ, EXAMPLE}`. After global resolution, the object
kind **MUST** own the matching registered grammar below:

| Kind | Edge-eligible canonical id |
|---|---|
| `document` | `^[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+$`, at most 128 bytes, copied from the exact declared `Document ID` |
| `invariant` | `^INV-[A-Z]{2,8}-[1-9][0-9]*$`, with the captured prefix registered; authored `<PREFIX>-INV-<N>` and padded aliases normalize before schema-v3 emission |
| PCDN `open_question` | `^PCDN-(?:[A-Z0-9]+-)+[0-9]{3}$`, at most 128 bytes, with the complete handle allocated by its existing registry |
| EOQ `open_question` | `<family-key>:EOQ-<NNN>-ERRATA-<NNN>` |
| `errata` | `<family-key>:ERRATA-<NNN>` |
| block/compact `amendment` | `<document-id>#amendment:<revision>`, where revision matches `^(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)$` |
| its linked `rationale` | `<amendment-id>#rationale` |

`<family-key>` is one registry-owned, case-preserving
`^[A-Za-z][A-Za-z0-9-]{0,63}$` token; every `<NNN>` is exactly three ASCII
decimal digits. Existing PCDN, EOQ, ERRATA, document, and prefix allocation
authorities continue to own uniqueness; this profile creates no second
registry. A syntactically valid canonical value with zero or multiple global
definitions is unresolved. Family, kind, document, and locator **MUST NOT**
break that collision. Invalid declared document ids remain coverage defects;
the parser **MUST NOT** strip presentation markup or guess a replacement.

Legacy amendments without a revision and current `section`, `term`, `gate`,
`nongoal`, `enum_value`, and `authority_row` path-, line-, or text-derived ids
remain readable object rows but are not edge endpoints or valid `Touches`
targets. They make applicable C5/C6 coverage incomplete until another
Standards Action registers stable authored handles. The provider **MUST NOT**
compare semantic fingerprints across commits for those positional identities.
Instead, every required commit containing one or more such objects contributes
exactly one history-gap unit
`[commit, "object", "edge_ineligible_semantic_identity"]`. No positional id
enters that counter identity. In particular, `gate.checked` remains valid
per-snapshot data, but neither its cross-commit change nor an amendment that
tries to `Touches` that gate becomes resolvable under this profile.

**Registration policy:** changing the common predicate, an eligible-kind row,
an id grammar, a reserved prefix, or the positional-history-gap rule requires
Standards Action and a new compatibility frontier. An implementation-local
slug, content hash, path/line identity, first-match rule, or silent cleanup is
not registration.

### §4.4 Location records

`LocationKind` is a frozen enum:

| Value | Stable target |
|---|---|
| `repository` | Repository-relative path; the containing committed snapshot supplies the commit SHA and a separate preview envelope supplies any dirty working-tree fingerprint |
| `archive` | Repository-relative ZIP path and member path, with both archive and member SHA-256 |
| `memalpha` | Corpus/notebook identity, opaque document or artifact id, and baseline; never a signed URL |
| `pointer` | Repository-relative pointer document and its named replacement authority |

**Registration policy: Standards Action.** A new storage system does not
become a `LocationKind` because a consumer happens to support it; the stable
resolution and integrity contract lands here first.

Each location record carries:

| Attribute | Type | Notes |
|---|---|---|
| `location_kind` | `LocationKind` | Frozen above |
| `target` | typed locator | The stable fields required by the selected kind |
| `baseline` | string or null | Named frozen snapshot when one exists |
| `integrity` | map or null | SHA-256 evidence where content is addressable |
| `recorded_at` | commit SHA | First commit carrying the underlying authored or derived record; supplied by version-control history rather than self-embedded by a current-state projection |
| `retired_at` | commit SHA or null | Ends this record without erasing history |
| `attr_provenance` | map of attribute → `declared` \| `inferred` | Repository/archive facts may be derived; handoff identities and lifecycle decisions are declared |

Location records are versioned and one-to-many. Replacing a locator **MUST**
retire the old record rather than mutate it out of history. Absolute workstation
paths, credentials, expiring signed URLs, private handles unrelated to stable
resolution, and model payloads **MUST NOT** enter a committed location record.

A committed current-state projection **MUST NOT** embed a claim that it is
contained by its own not-yet-created commit. Its snapshot commit is supplied by
the version-control context in which it is read. `recorded_at` is a logical
history attribute derived from the first commit carrying the underlying source
record; schema-v1 current-state files MAY omit it until a history projection is
implemented. If serialized, it refers to an already-existing source commit,
never to the commit that is in the act of being created. A dirty preview is not
a snapshot and carries its fingerprint in a separate, noncommitted envelope.

### §4.5 Frozen enum — `DocumentLifecycleState`

| Value | Meaning |
|---|---|
| `draft` | Authoring is open and owner ratification has not been recorded |
| `ratified` | The document's decisions are owner-accepted; execution is not implied |
| `executing` | Governed implementation or conformance work is underway |
| `execution_complete` | The document's execution acceptance gates are satisfied |
| `handoff_eligible` | Live authority has been absorbed forward and the handoff ritual may run |
| `handed_off` | The handoff ritual and stable-location verification completed |
| `superseded` | A named replacement authority governs instead |
| `abandoned` | Work intentionally closed without execution or replacement |
| `unknown` | Authored evidence is insufficient to select another value |

**Registration policy: Standards Action.** Lifecycle is an authority/workflow
axis, not a storage tier. A parser **MUST NOT** infer `ratified`, `handed_off`,
or `superseded` merely from a path, ZIP member, notebook record, or pointer.
Every non-`unknown` lifecycle value carries declared provenance or cites the
authored transition from which it was deterministically derived.

### §4.6 Frozen enum — `OpenQuestionStatus`

| Value | Meaning |
|---|---|
| `open` | An authored question has no accepted resolution or ratified recommendation. |
| `pending_ratification` | A recommendation or proposed resolution is authored, but owner acceptance is not recorded. |
| `resolved` | Owner acceptance is recorded in the definition row or its governing resolved/decisions section. |
| `unknown` | The authored definition exists but its native state cannot be selected without interpretation. |

**Registration policy: Standards Action.** Status is derived only from the
definition row and its governing heading/document authority. Later citations,
directory names, and implementation state **MUST NOT** change it. The parser
records whether the status was declared in a row or deterministically inferred
from the governing authored section.

---

## §5 Frozen Enum — `EdgeType` [Normative]

Directional, typed relationships between spec objects. Every edge carries `kind_provenance ∈ {declared, inferred}` (§4.2).

| Value | Meaning | Reciprocal |
|---|---|---|
| `defines` | Document/section → the object defined in it | `defined-in` |
| `cites` | Any object → an object it references | `cited-by` |
| `refines` | A phase-level object → the family-level object it narrows | `refined-by` |
| `verifies` | A registered checking `SpecObject` → the object it checks | `verified-by` |
| `evidences` | An errata or measurement → the claim it supports | `evidenced-by` |
| `amends` | An amendment → the object whose text it changed | `amended-by` |
| `supersedes` | A replacement → what it retires | `superseded-by` |
| `blocks` | A gate → what cannot proceed until it closes | `blocked-by` |
| `motivates` | A rationale object → the change it explains | `motivated-by` |
| `same-as` | Two ids declared to denote one concept | symmetric |
| `homonym-of` | Two ids declared to share a name and **not** a concept | symmetric |

**Registration policy: Standards Action.**

`same-as` and `homonym-of` exist because **term collisions are not defects — unlabelled ones are.** F5's 30 collisions (`executor` across five families) are mostly legitimate domain separation. Without a way to declare that, every collision sits as a permanent open finding and the report trains its readers to ignore it. With it, a collision is either resolved to one concept or explicitly declared distinct, and the residue is the real signal.

The enum registration survives the initial endpoint boundary, but current
text-derived `term` ids are not `GlobalObjectIdV1`-eligible. A term
`same-as`/`homonym-of` declaration therefore remains unavailable until another
Standards Action registers stable term handles; the motivating semantic is not
permission for an implementation-local exception.

**Reciprocity.** Every edge has a reverse; a store **MUST** materialise both directions. SBC-INV-13 already mandates this for one pair (ERRATA ↔ §15); this generalises it.

**Authoring cost.** Edge *existence* remains free for the four closed inference
contexts in §5.2. Every other kind is authored through the exact `Spec Edge`
field. A prose verb, table heading, nearby object, file order, or object kind
never silently upgrades a citation to a stronger relationship.

### §5.1 Global edge identity and C6 orientation

Every C6-eligible edge **MUST** identify two canonical `object_id` values that
each resolve to exactly one definition globally in the same snapshot. Family,
document, line, and definition locator are validation evidence, never identity
qualifiers. A collision in another family or document remains a collision;
first-match and path-shaped object identities are prohibited.

For a non-definition citation, its source is the unique object defined on the
citation line, otherwise the unique `document` object defined by the citation
file, otherwise unresolved. Multiline prose belongs to that document object;
an implementation **MUST NOT** guess a containing object span. A definition
edge is owned by the unique containing document object. Unowned, ambiguous,
or unresolved endpoints produce coverage evidence and no edge.

The dependency orientation and propagation registry is closed:

| Edge type | C6 dependency orientation | `clarification` | `semantic` / `scope` / `retirement` |
|---|---|---|---|
| `defines` | none; structural ownership | no | no |
| `cites` | source depends on target | no | yes |
| `refines` | source depends on target | yes | yes |
| `verifies` | source depends on target | no | yes |
| `evidences` | source depends on target | no | yes |
| `amends` | none; supplies a change event | no | no |
| `supersedes` | none; required retirement evidence | no | no |
| `blocks` | target depends on source | no | yes |
| `motivates` | none; rationale trace | no | no |
| `same-as` | symmetric dependency | no | yes |
| `homonym-of` | none; declares distinct meanings | no | no |

`editorial` never propagates. Unknown types, orientations, or change kinds fail
closed. C6 reads canonical forward edges only; a reciprocal store row never
re-enters propagation. A `same-as` forward edge orders endpoints by ascending
UTF-8 global id and expands exactly once into the two directed dependency
pairs. Separate citation locators remain separate edge evidence but collapse
to one exact pair generation for C6.

The ratified `TODO-SIDX-06E-C6-OBJECT-GRAPH-AND-ACKNOWLEDGMENT.md` rev 0.4.0
§§3–7 and §10.1 is the coordinated Standards Action record for the exact
canonical-byte, pair, change-event, DAG, clearing, diagnostic, and metric
profile adopted here. It cannot amend this addendum independently; any
semantic change requires another Standards Action coordinated in both
documents.

### §5.2 Declared edge grammar and closed inference [Normative]

One non-inferred edge is authored by this repeatable, standalone, single-line
Markdown field outside fenced examples:

```text
**Spec Edge:** <source-object-id> -> <target-object-id> ; type=<edge-type>
```

The angle-bracket terms above are grammar metavariables, not authored
characters. Actual ids and type are ASCII tokens without whitespace. The bold
label, one ASCII space after the colon, ASCII `->`, spaces around the arrow,
space-semicolon-space, and lowercase frozen `EdgeType` token are exact. The
field has no prose suffix, wrapping, paths, wildcards, edge keys, family
qualifiers, or extra members. Every additional edge uses another complete
line.

The field's repository-relative document and positive line number are the
citation locator; its document family is the citation-envelope family. Both
endpoints **MUST** satisfy `GlobalObjectIdV1` and resolve globally and uniquely
in the same snapshot. A valid field emits `kind_provenance: declared` and
suppresses generic citation extraction for every token on that line. `defines`
cannot be authored because it remains structural. The exact declared allowlist
is `{cites, refines, verifies, evidences, amends, supersedes, blocks,
motivates, same-as, homonym-of}`, further constrained by §5.3. `same-as`
accepts either authored order, after which the producer sorts emitted
endpoints by ascending UTF-8 id. Every other accepted type preserves authored
source-to-target order.

The complete inference registry is:

| Context | Emitted type | Provenance |
|---|---|---|
| Unique document owns one definition site | `defines` | `inferred` |
| Ordinary non-definition mention with a unique source and target | `cites` | `inferred` |
| Valid amendment `Touches` target | `amends` | `inferred` |
| Linked rationale object to every valid id in its amendment's `Touches` | `motivates` | `inferred` |

No other inference is conforming. A recognized field with zero `type=` clauses
is a missing edge-kind candidate; one nonempty token outside the permitted set,
including authored `defines` or a profile-ineligible `verifies`, is
unsupported; two or more type clauses on one candidate are ambiguous.
Distinct valid fields and distinct valid edge types are never ambiguity.
Endpoint defects remain separate from the kind defect and share the candidate
identity fixed by the diagnostic owner cited in §10.

**Registration policy:** changing the field bytes, declared allowlist,
inference registry, provenance, ordering, or failure classification requires
Standards Action. Generic `Relationship:` fields, unbounded prose inference,
nearest-object selection, first-valid-token parsing, and implicit
`supersedes`/`verifies` are prohibited.

### §5.3 Object-only `verifies` [Normative]

Schema-v3 edges remain object-to-object. A `verifies` edge is eligible only
when both endpoints are globally valid `SpecObject` rows and the source kind is
registered as a checking object. `GlobalObjectIdV1` registers no checking
source kind because current gates are positional; consequently this initial
profile has no live positive `verifies` edge. A declared `verifies` field with
a locator, nonobject, or ineligible source is unsupported and emits no edge.

Existing tests, commits, and evidence strings remain locator evidence in
`verified_by`/`has_verification`; they never become placeholder objects or edge
endpoints. Registering a stable gate handle or a test/evidence `ObjectKind`
belongs to the reserved multi-producer phase and requires another Standards
Action and compatibility frontier. Historical schema-v3 bytes **MUST NOT** be
reinterpreted.

---

## §6 Definition and Normativity Rules [Normative]

### §6.1 One definition site

**INV-C-1 (proposed).** Every spec object has exactly one definition site. Restating an object's id in bold at the head of a list item, table cell, or heading in a second document constitutes a second definition site and is prohibited. A phase doc that needs to reference a family-level invariant **MUST** cite it, using one of the three SBC-INV-2 phrasings, extended from terms to all object kinds.

This closes F3 (54 ids with multiple definition sites) by extending the parent's existing anti-restatement rule to the surface where it was missing.

### §6.2 Normativity is measured, not asserted

**INV-C-2 (proposed).** An object in a section bound by §12 Acceptance **MUST** contain at least one capitalised RFC 2119 keyword in its statement. An object failing this is reported as `normative: false` regardless of the section it occupies.

This does not change what any existing invariant means. It makes F6's 42.9% *visible* rather than silently advisory. Remediation is per-family and out of scope here; measurement is the deliverable.

### §6.3 Gates bind invariants

Acceptance gates SHOULD cite the invariant ids they discharge. F7 measures 4.8%; the gap means conformance cannot be traced to the constraints it claims to enforce. This is a SHOULD, not a MUST, because retrofitting 1,326 gates is a per-family decision with real cost and no forcing deadline.

---

## §7 Snapshots, Baselines, and History [Normative]

**INV-C-4 (proposed).** The object index is **committed, not recomputed.** A snapshot is generated by the declared parser and lands in the repository alongside the corpus. CI verifies that regenerating the index at `HEAD` is a no-op.

The alternative — replaying today's parser across 585 historical commits to reconstruct history on demand — is unsound. Any change to a parsing heuristic silently rewrites the past, and every historical diff becomes a statement about the current parser rather than about the corpus. Committed indexes make parser changes visible as diffs, which is the same property that would have surfaced `INITIATIVE-MAP.md`'s staleness a month before a human noticed it.

**History** is the sequence of committed snapshots; git is its authority. An object's history is the diff of its entry across snapshots — no separate history store, and no authored history record that could disagree with git.

**A baseline** is a named, frozen snapshot spanning a family, produced at ratification or at doc-handoff. The handoff ritual already produces frozen content and a commit SHA; a baseline names the set and makes it diffable. Every object emitted to RAG **MUST** carry its baseline id, so a retrieved fragment declares itself as *correct as of baseline N* rather than being merely suspect — which converts the measured stale-RAG failure (0.69 with stale context vs 0.82 without) from a discard signal into a navigable one via `supersedes` edges.

---

## §8 Suspicion [Normative]

### §8.1 Definition

An object is **suspect** when an object it depends on changed after the dependent last acknowledged it. Suspicion is *derived* — it is a function of the edge graph and the snapshot sequence, never an authored fact.

### §8.2 Change events and typed propagation

**INV-C-5 (proposed).** An amendment declares a `ChangeKind`, and suspicion propagates only for kinds that carry semantic force and edge orientations registered in §5.1.

| `ChangeKind` | Propagates? | Example |
|---|---|---|
| `editorial` | No | Typo, formatting, link repair |
| `clarification` | To `refines` edges only | "INV-MCAD-4 clarified to bind only extracted dimensional values" |
| `semantic` | Yes, all edge types | An invariant's obligation changes |
| `scope` | Yes | A non-goal withdrawn; a phase's boundary moves |
| `retirement` | Yes, plus mandatory `supersedes` edge | An object retired or replaced |

A change event exists only when one committed projection first contains an
`amendment` with a valid `ChangeKind`, one or more declared `Touches` values,
and every touched global id resolving uniquely in that snapshot. The only
exception is a retirement target absent from the current projection: it must
resolve uniquely in every eligible parent where present, be absent currently,
carry `ChangeKind: retirement`, and have the same valid `supersedes` evidence
in every last-present parent. Missing or ambiguous evidence makes coverage
incomplete; it never authorizes a guessed event.

Object retirement is evaluated once per distinct retired `Touches` member
under `(current_commit, amendment_id, retired_object_id)`. Exactly one newly
introduced, globally unique amendment with declared `ChangeKind: retirement`
must touch that id. When the retired target resolves in the current projection,
valid successor evidence is a declared forward `supersedes` edge
`successor -> retired`. Zero distinct successor ids is missing, more than one
is ambiguous, and exactly one is a mechanically eligible current candidate;
multiple locators for the same successor do not create multiple successors.
This producer check does not prove a future or completed removal.

A canonical retirement target absent from the current projection enters only
the parent-resolved exception. The producer emits neither
`touches_unresolved/unknown` nor `retirement_supersedes_missing` for that
member; it preserves the canonical `Touches` value and retirement
`ChangeKind` as provider input. Every direct parent projection must be eligible;
the retired id must resolve once in every parent where present; each such
parent must carry exactly one distinct declared successor; every parent must
name the same successor; and that successor must resolve globally and uniquely
in the current snapshot. The amendment touches the retired change target,
while the `supersedes` edge alone binds the unchanged successor. Missing or
incompatible parents, collision, no successor, multiple successors, parent
disagreement, absence from every parent, or multiple qualifying amendments
leave the event unresolved. No first, newest, family-local, or current-only
successor may be selected.

Producer validation owns only current-projection graph/diagnostic agreement.
Git-DAG validation, per-parent eligibility, the exact history/identity/unlogged
counter accumulation, and public incomplete-reason precedence belong to the
provider contract in SIDX-06E rev 0.4.0 §10.1.4/§10.1.6. An ingestion of one
snapshot **MUST NOT** claim that parent-DAG proof.

Every non-amendment, non-rationale object has a versioned semantic fingerprint
over `kind`, `text`, common `normative`/`status`, and these additional fields:
`document.lifecycle_state`, `invariant.title`, `term.term`/`relationship`,
`gate.checked`, and `open_question.resolution`. Locator, family, provenance,
derived parser attributes, and citation lists are excluded. Within one
compatible extractor frontier, a fingerprint change or disappearance of an
edge-eligible object without a matching amendment in the same commit is an
unlogged change and makes C6 coverage incomplete. Positional objects use the
§4.3.1 history-gap rule instead of cross-commit comparison. Merge comparison
uses Git ancestry: equality with any eligible parent is inherited, not
merge-introduced.

Removing the last edge for one dependency pair additionally requires this
repeatable ASCII amendment field:

```text
Retires-Dependency: <upstream-id> -> <dependent-id> ; type=<edge-type>
```

The amendment first appears in the removal commit, uses `semantic`, `scope`,
or `retirement`, and includes the directed dependent in valid `Touches`. For
`same-as`, ids are written in ascending UTF-8 order, both endpoint ids appear
in `Touches`, and one declaration retires both derived directions. Otherwise
the removal remains unresolved and coverage is incomplete.

Each valid field is serialized on its amendment in one closed member:

```json
{
  "upstream_object_id": "INV-AAA-1",
  "dependent_object_id": "INV-BBB-2",
  "edge_type": "cites"
}
```

The member has exactly those three keys. `retired_dependencies` sorts by
ascending UTF-8 `(upstream_object_id, dependent_object_id, edge_type)` and
collapses exact duplicates; different edge types remain distinct. A member
contains no locator, family, edge key, direction, commit, parent, or
per-member provenance. A nonempty array requires exactly
`attrs.attr_provenance.retired_dependencies: declared`; both the array and its
provenance member are omitted when no valid declaration exists.

Only `{cites, refines, verifies, evidences, blocks, same-as}` are valid here.
Stored orientation is C6 upstream-to-dependent, not projected
source-to-target: `blocks` uses projected source as upstream, whereas `cites`,
`refines`, `verifies`, and `evidences` use projected target as upstream.
`same-as` stores ascending ids and one member authorizes both derived
directions. The parser checks canonical ids, a containing `ChangeKind` in
`{semantic, scope, retirement}`, and required `Touches` membership: the
directed dependent for a nonsymmetric type, or both endpoints for `same-as`.
The provider alone checks ancestry, pair existence, and actual last-edge
removal. Malformed or unrepresentable retirement fields fail generation
without echoing unsafe content until a separately registered diagnostic
exists; they never become `SpecEdge` rows or successor evidence.

**Registration policy: Standards Action.**

This exists because untyped suspicion is how DOORS suspect links fail in practice: real programs hit alarm volumes they cannot service, then bulk-clear or disable the mechanism. `INV-MCAD-9` has 56 citation sites (F8); a clarification that flagged all 56 would train its readers to clear without reading within one cycle. A mechanism that produces ignored alarms is worse than no mechanism, because it also certifies.

### §8.3 Clearing happens in git

**INV-C-6 (proposed).** A suspicion is cleared only by this exact typed ASCII
commit trailer:

```text
Clears-Suspect: <upstream-document>#<upstream-id>@<40-hex-trigger-commit> -> <dependent-document>#<dependent-id> ; type=<edge-type>
```

Both ids resolve globally and uniquely. Both repository-relative POSIX paths
must match their unique definition evidence; paths validate identity but never
disambiguate it. The trigger commit carries the propagating upstream event,
the clearing commit descends from it, the exact typed pair exists in both
projections, and abbreviated revisions, Unicode arrows, wildcards, omitted
types, path-only targets, or extra payload are invalid. A multi-type relation
requires one trailer per exact type; each `same-as` direction clears
independently.

One pair generation begins at its introduction frontier. V1 derives state only
for a singleton introduction frontier; incomparable independent introductions
remain incomplete rather than selecting a branch. The initial
acknowledged-through frontier contains the maximal propagating events reachable
at introduction. Later events form a trigger-frontier antichain. One clearing
commit closes a cycle only when it descends from every trigger and repeats one
valid trailer for every frontier member. Earlier partial trailers do not
advance acknowledged-through state.

At a merge, an open lineage dominates a closed lineage. Incomparable complete
clearings remain an unresolved ambiguity until one descendant reconciliation
commit descends from all of them and repeats the complete typed trailer set.
Only that reconciliation closes the cycle; later linear duplicates do not
create another clearing. A later propagating event opens a new cycle in the
same continuous pair generation.

Clearings **MUST NOT** be stored as authored state in a compiled store. A
clearing is a human assertion that the dependent was reviewed against exact
upstream events. Git supplies review and ancestry; the store remains a derived
cache of those facts rather than a second authority.

### §8.4 Metrics are diagnostics, not targets

Suspicion metrics **MUST** be reported as a triple: open count, **median clear latency**, and **re-suspect rate**. A bare "suspects cleared" count is trivially gamed by bulk-clearing, and any dashboard that elevates it will be. These figures are named non-targets: they exist to detect that the mechanism is failing, not to be optimized.

Open count is the number of safely resolved open dependency-pair generations
at the response snapshot. Clear latency is elapsed UTC seconds from the minimum
committer timestamp across a cycle's minimal opening antichain to its one
atomic clearing commit. Re-suspect rate is the fraction of eligible closed
cycles followed by a later cycle in the same continuous pair generation; only
closed cycles with a complete later observation window enter the denominator.

Each metric carries its eligible population and confidence. Complete evidence
with nonzero eligibility is measured. Zero eligibility is vacuous with a null
value. Incomplete evidence is uncomputable with a null total and may expose a
separately labeled observed value over the independently safe subset. Missing
history, invalid timestamps, ambiguous ancestry, or truncated evidence never
becomes zero.

---

## §9 Capability Contract [Normative]

The model is conformant when it can answer these deterministically. **Surfaces are out of scope here** (§11) — this table is the phase-level tool manifest, one named query per row. Generic query-by-SQL is expressly not the shape: named questions are testable, cacheable, agent-legible, and each row is a phase gate with its acceptance criterion already written.

| # | Question | Depends on |
|---|---|---|
| C1 | What does `<id>` say now? | §4 |
| C2 | What did `<id>` say at baseline `<b>`? | §7 |
| C3 | Why is `<id>` phrased this way? | §1, §4.1 `rationale` |
| C4 | What changed in `<family>` since `<baseline>`? | §7 |
| C5 | What depends on `<id>`, by edge type? | §5 |
| C6 | What is suspect after amending `<id>`? | §8 |
| C7 | Is this fragment current or superseded? | §7 baselines, `supersedes` |
| C8 | Which invariants lack a verification surface? | §4.2, §6.3 |
| C9 | Which terms collide, and which are declared distinct? | §5 `same-as`/`homonym-of` |
| C10 | What is this family's drift/coverage/normativity profile? | §6.2, §8.4 |
| C11 | What governed work currently needs attention? | §4.1 object kinds/status, §4.2 provenance |
| C12 | Where does this document or object live across its lifecycle? | §4.4, §4.5, §7 |

C1 is answerable today by grep. C2–C12 require a conforming derived surface.

---

## §10 Reconciliation — Adjacent Primitives [Normative]

| # | Primitive | Decision |
|---|---|---|
| 1 | **`SBC-00-CONCEPTS.md`** | `extend` (§0.2). Structure added on an unchanged grammar; parent terms never redefined. |
| 2 | **IBM/Telelogic DOORS** | `compose` + `adapt`. Five primitives adopted — object identity, typed attributes, typed links, suspicion, baselines. Deliberately rejected: atomisation into isolated shall-statements (destroys the narrative an agent onboards from), per-object editing UI, module locking, module-scoped ids (§4.3), module-level ACLs (SBC §4 is a better instrument). **DOORS is a live trademark**; it names a design influence here and **MUST NOT** be used as a product or family name. |
| 3 | **ReqIF** | `adapt`. The type system (`SpecObjectType`, `AttributeDefinition`) is adopted as §4.2; the XML serialisation is not. |
| 4 | **git** | `compose`. Authority for history (§7) and for suspicion clearing (§8.3). Semantics unmodified. |
| 5 | **Memory Alpha / RAG tier** | `derive`. Consumes compiled objects; every emitted object carries id + baseline (§7). RAG is never an authority — the parent's trust ordering (code wins over stale RAG) is unchanged and now navigable rather than merely cautionary. |
| 6 | **`docs/ops/doc-handoff.md`** | `compose`. A handoff produces a baseline (§7), declares opaque Memory Alpha and archive locators (§4.4), and records the lifecycle transition (§4.5). The runbook owns the ritual; this addendum owns the record grammar. |
| 7 | **`SBC-00-ADDENDUM-B.md`** | `compose`. `ErrataStatus` is `errata` object status; unmodified. |
| 8 | **Parallel-agent execution workflow** | Out of scope, but note the coupling: §4.3's allocation authority exists because concurrent fan-out makes prefix collision reachable. |
| 9 | **SIDX-06A/06B/06D/06E** | `compose` + `derive`. This addendum owns edge declaration, edge-eligible identity, object-only `verifies`, and retirement/`supersedes` meaning. SIDX-06E rev 0.4.0 §10.1.6 owns the exact diagnostic-v3 record units, reasons, facts, locators, and provider counter mapping; SIDX-06A owns producer serialization/profile validation; SIDX-06B owns shared-query compatibility; SIDX-06D diagnostic v1 remains immutable. None may extend this object vocabulary or reinterpret provider truth locally. |

---

## §11 Non-Goals

1. **Not a storage topology.** Relational vs. graph vs. vector vs. columnar, and how many stores — phase-level decisions for a consuming tooling family. This doc constrains only that they be derived (§0.1).
2. **Not an API surface.** MCP tool names, REST routes, auth scope, and role gating belong to the consuming family's phase docs. §9 is the manifest they implement.
3. **Not a multi-producer graph — yet.** Commits, PRs, issue trackers, ADRs, meeting transcripts, CI evidence, and external standards could all emit into this model, and the object/edge design is deliberately producer-agnostic to keep that open. Admitting a second producer now would make the first unbuildable. Revisit once the Markdown producer is conformant end to end.
4. **Not a remediation mandate.** F2/F6/F7 measure real gaps in the existing corpus. This doc makes them visible and does not schedule their repair; that is each family's call, at each family's cost.
5. **Not a replacement for reading the spec.** The model serves navigation, impact analysis, and metrics. Narrative sections remain the primary onboarding artifact — the compiled projection deliberately does not shred them, because prose context is what an agent's cold start actually consumes.
6. **Not a change to any existing invariant's meaning.** Six invariants are *proposed* here; none amends a parent invariant's obligation.

---

## §12 Acceptance [Normative]

### §12.1 This document is ratified when

- [x] Every term in §3 carries a citation and an SBC-INV-2 relationship marker.
- [x] `ObjectKind` (§4.1), `LocationKind` (§4.4), `DocumentLifecycleState` (§4.5), `OpenQuestionStatus` (§4.6), `EdgeType` (§5), and `ChangeKind` (§8.2) are closed and each declares a registration policy.
- [x] The compilation rule (§0.1) is stated normatively and §8.3 resolves its one exception without weakening it.
- [x] The identifier grammar (§4.3) names a canonical form **and** an allocation authority.
- [x] Six proposed invariants appear with verification surfaces (§12.3).
- [x] Every adjacency in §10 carries a decision with an `AuthorityRelationship`.
- [x] Each non-goal in §11 names the owner of the excluded surface or the reason it is out of scope.
- [x] Load-bearing sections §0, §3/§4, §10, §12, §15 are present (SBC-INV-9).
- [x] All PCDNs in §12.4 are resolved.
- [x] The ratified C6 Standards Action fixes global dependency identity,
  change-event authority, typed DAG clearing, and diagnostic metrics without
  transferring semantic ownership to a delivery handler.
- [x] The rev 0.6.0 correction registers exact declared/inferred edge
  authoring, `GlobalObjectIdV1`, positional history gaps, object-only
  `verifies`, and per-target retirement authority while keeping diagnostic and
  provider serialization in the coordinated SIDX owners.

### §12.2 Parent amendments this document requires — ✅ landed 2026-07-31

These were listed rather than performed because an addendum does not edit its parent silently. All four landed as `SBC-00-CONCEPTS.md` **rev 0.7.0**, a revision distinct from the **0.6.0** ratification, so the record separates what the corpus was governed by before this date from what changed on it.

| Parent section | Required change | Landed |
|---|---|---|
| §4 source-of-truth map | Add rows: object model, identifier canonicalisation, edge types, suspicion → owner `SBC-00-ADDENDUM-C` | ✅ 0.7.0 (five rows, incl. ADDENDUM-D) |
| §8 identifier grammars | Add canonical-form rule and allocation authority; cite §4.3 | ✅ 0.7.0 |
| §9 invariants | Adopt the six §12.3 invariants as `SBC-INV-15`…`SBC-INV-20` | ✅ 0.7.0 |
| §13 files cited | Add `SBC-00-ADDENDUM-C.md` | ✅ 0.7.0 (+ ADDENDUM-D) |

The recommendation was to land these **after** SBC-00 ratified, notwithstanding that amending a DRAFT is cheaper. That is what happened: SBC-00 ratified at 0.6.0 (existing content, no change) and these landed at 0.7.0. The object model is the highest-value structural change this corpus will make, and landing it with no amendment trace — because the trace was expensive — would have encoded exactly the wrong precedent in the record it is meant to improve. See `SBC-ERRATA.md` ERRATA-004 for why the root was unratified in the first place.

The 0.3.0 location/lifecycle amendment is coordinated downstream rather than
mirrored silently. `TODO-SIDX-00-CONCEPTS.md` rev 0.3.0 adopts C11/C12 and the
associated delivery invariants; `TODO-SIDX-06-WORKSPACE-DASHBOARD.md` rev 0.2.0
ratifies the work-item and dashboard projection; and `docs/ops/doc-handoff.md`
now requires stable opaque identities, baselines, integrity evidence, and a
declared lifecycle transition. None of those consumers owns or may widen the
§4.4/§4.5 grammar.

The 0.5.0 C6 amendment is the upstream Standards Action required by ratified
SIDX-06E rev 0.3.0. The 0.6.0 correction coordinates owner-accepted SIDX-06E
rev 0.4.0 PCDN-SIDX-06E-011 through PCDN-SIDX-06E-016 without reopening the
0.5.0 pair, event, clearing, or metric meaning. This document owns the §4.3,
§5, and §8 object/edge semantics. Coordinated SIDX phases own only exact
serialization, diagnostic/provider evidence, query compatibility, and
transport parity; none may reinterpret the adopted meaning.

### §12.3 Proposed invariants

| Proposed id | Statement | Verified by |
|---|---|---|
| **INV-C-1** | Every spec object **MUST** have exactly one definition site; restatement in a second document is a citation, using an SBC-INV-2 phrasing. | Parser: duplicate-definition report (F3 → 0) |
| **INV-C-2** | An object in a §12-bound section **MUST** carry a capitalised RFC 2119 keyword, or be reported `normative: false`. | Parser: normativity report (F6) |
| **INV-C-3** | An amendment with `ChangeKind ∈ {semantic, scope, retirement}` **MUST** carry a linked rationale object. | Parser: amendments lacking a `motivates` edge |
| **INV-C-4** | The object index **MUST** be committed; regeneration at `HEAD` **MUST** be a no-op. | CI: regenerate-and-diff |
| **INV-C-5** | Suspicion **MUST** propagate per `ChangeKind` (§8.2); untyped blanket propagation is prohibited. | Review of suspicion reports; re-suspect rate (§8.4) |
| **INV-C-6** | Suspicion clearings **MUST** be recorded as git commit trailers and **MUST NOT** be authored into a compiled store. | Store audit: no un-derivable rows |

### §12.4 Open questions — all resolved 2026-07-31

| Id | Question | Resolution |
|---|---|---|
| `PCDN-SBC-00-C-001` | Does the model cover submodule corpora (SOS, disco-analyzer, rlvgl, scjson), which own their own repos and ERRATA? | **Parent repo first.** Submodules opt in per-repo. Cross-repo id resolution gets its own phase; until then a submodule corpus is out of the compiled index and its ids are unresolvable from the parent — recorded as a known limitation, not a silent gap. |
| `PCDN-SBC-00-C-002` | Do `rationale` objects get authored inline (a §15 sub-shape) or as separate linked files? | **Inline sub-shape**, owned by `SBC-00-ADDENDUM-D`. A separate file class adds an unspecified surface that would fork exactly as §15 did. |
| `PCDN-SBC-00-C-003` | Is the §15 shape frozen now, or after the 27 bullet-form logs are read for content they carry that the table shape cannot? | **After.** Audit performed 2026-07-31 (`scan.py --changelog-audit`); shape frozen in `SBC-00-ADDENDUM-D` against measured content. Both authored forms remain valid input during transition. |
| `PCDN-SBC-00-C-004` | Who holds the §4.3 allocation authority — this addendum, or a registry file with a named human owner? | **Registry file with a named human owner**, in the consuming repo. The authority is operational, not normative. Seeded at `docs/spec-index/PREFIX-REGISTRY.md`. |
| `PCDN-SBC-00-C-005` | Does `ObjectKind` admit `test` and `commit` as objects now, or does that wait for the §11.3 multi-producer phase? | **Wait.** Tests and commits remain locator evidence until the multi-producer phase opens. **Rev 0.6.0 clarification:** locator evidence is not a schema-v3 `verifies` endpoint; §5.3 now requires two globally valid objects and registers no initial checking source kind. |

---

## §13 Files Cited

| File | Role |
|---|---|
| `docs/SBC-00-CONCEPTS.md` | Parent normative document; §12.2 lists required amendments |
| `docs/SBC-00-ADDENDUM-A.md` | Operational injection template (unmodified) |
| `docs/SBC-00-ADDENDUM-B.md` | `ErrataStatus`, ERRATA boundary + template (composed, §10 row 7) |
| `docs/SBC-00-ADDENDUM-C.md` | This document |
| `docs/todo/spec-index/TODO-SIDX-06E-C6-OBJECT-GRAPH-AND-ACKNOWLEDGMENT.md` | Ratified C6 Standards Action and rev 0.4.0 correction record; exact diagnostic/provider execution profile |
| `scripts/specidx/scan.py` | Read-only evidence parser producing §2 (consuming repo) |
| `docs/ops/doc-handoff.md` | Baseline-producing ritual (§10 row 6, consuming repo) |
| RFC 2119, RFC 8174 | Normative-keyword grammar |
| OMG ReqIF | Type-system influence, §10 row 3 |

---

## §14 Unblocks

- **A consuming tooling family** MAY now be specced against a frozen object model, with §9 as its capability manifest and §11.1/§11.2 marking what it owns rather than inherits.
- **The doc-handoff ritual** gains a name for what it freezes (§7 baselines) and a per-object stamp for what it emits to RAG.
- **Location-aware tooling** MAY derive a one-to-many location projection and
  answer C12 without treating storage placement as document authority.
- **Existing families** MAY use the exact §5.2 `Spec Edge` field to declare relationships that today are untyped prose, and MAY resolve eligible collisions as `homonym-of` rather than leaving them as standing findings.
- **A conforming C6 producer/provider** MAY implement the globally identified
  dependency graph and Git-derived acknowledgment rules only through the
  coordinated SIDX-06A/06B/06E contracts.
- **`SBC-00-CONCEPTS.md`** has an enumerated amendment list (§12.2) rather than an implicit obligation.

---

## §15 Change Log

| Rev | Date | Author | Status | Summary |
|---|---|---|---|---|
| 0.1.0 | 2026-07-31 | I. Abbott | DRAFT | Initial draft. Owns the spec object model: compilation rule (§0.1), State/Trajectory/Intent axes (§1), evidence base measured at `fcc6e924d` (§2), `ObjectKind` + attribute schema + identifier canonicalisation and allocation authority (§4), `EdgeType` with `same-as`/`homonym-of` (§5), one-definition-site and measured-normativity rules (§6), committed-snapshot history and baselines (§7), `ChangeKind`-typed suspicion cleared via git trailers (§8), ten-question capability contract (§9). Six invariants proposed for parent adoption as `SBC-INV-15`…`SBC-INV-20` (§12.2, §12.3). Five PCDNs open. Storage topology, API surface, and multi-producer ingestion explicitly out of scope (§11). |
| 0.2.0 | 2026-07-31 | I. Abbott (ratifier) | **Ratified** | All five PCDNs resolved in one session; §12.1 acceptance closed. **001** → parent repo only; submodule corpora are a declared limitation with their own future phase, not a silent gap. **002** → `rationale` is an inline §15 sub-shape, owned by the new `SBC-00-ADDENDUM-D`. **003** → §15 shape frozen *after* the audit, which ran this session over all 56 concepts docs; both authored forms stay valid input during transition. **004** → allocation authority is a registry file with a named human owner at `docs/spec-index/PREFIX-REGISTRY.md` in the consuming repo; operational, not normative. **005** → `test`/`commit` stay locators until the multi-producer phase opens. No normative section changed; resolutions were adopted as recommended. **Ordering note:** this addendum is ratified while its parent `SBC-00-CONCEPTS.md` remains DRAFT at 0.5.0. The §12.2 parent amendments are therefore *pending*, not overdue — they land as a single `SBC-00` §15 amendment once the parent ratifies. Recorded here so the inversion is visible rather than discovered later. Unblocks `SBC-00-ADDENDUM-D`. |
| 0.3.0 | 2026-08-07 | I. Abbott (ratifier) | **Ratified amendment** | Standards Action adopts versioned one-to-many `LocationRecord` values, frozen `LocationKind` and `DocumentLifecycleState` enums, and C11/C12. Lifecycle remains orthogonal to location; opaque Memory Alpha ids and integrity-bound archive locators replace expiring or workstation-local references. `ObjectKind` and all existing C1–C10 meanings remain unchanged. Coordinates the reciprocal SIDX-00, SIDX-06, and doc-handoff amendments. |
| 0.4.0 | 2026-08-07 | I. Abbott (ratifier) | **Ratified amendment** | Standards Action registers the decision-table row as the `open_question` definition shape and adds frozen `OpenQuestionStatus` values `open`, `pending_ratification`, `resolved`, and `unknown`. It also closes the location-snapshot self-reference gap: a repository target is repo-relative, its clean commit comes from the containing snapshot context, dirty fingerprints live only in a separate preview envelope, and `recorded_at` is derived from existing history rather than guessed before a commit exists. **Change kind:** `semantic`. **Touches:** §4.1, §4.2, §4.4, new §4.6, and §12.1. **Motivation:** SIDX-06A requires deterministic object state and a no-op committed projection; neither can be implemented from an unspecified question state nor by embedding the SHA of a commit that does not exist yet. **Considered and rejected:** a tooling-local status enum, first-match question identity, placeholder commit ids, and absolute working-tree locators. **What deliberately did not change:** `ObjectKind`, `LocationKind`, `DocumentLifecycleState`, the Markdown/git authority rule, or any store/API/frontend contract. |
| 0.5.0 | 2026-08-08 | I. Abbott (ratifier) | **Ratified amendment** | Standards Action adopts SIDX-06E rev 0.3.0: C6 edges resolve global object ids; citation ownership and dependency orientation are closed in §5.1; change events require amendment authority and fingerprint audit; typed Git trailers clear exact pair/frontier members through DAG-aware atomic acts; pair retirement and re-suspicion remain explicit; and the metric triple preserves measured, vacuous, and uncomputable truth. **Change kind:** `semantic`. **Touches:** §3, §5, §8, §12, §13, and §14. **Motivation:** path-source edges and edit-based clearing cannot answer C6 deterministically or equally for human and agent consumers. **Considered and rejected:** family-qualified ids, first-match ownership, blanket propagation, edit-based clearing, arbitrary merge selection, database-authored acknowledgments, and handler-local C6 rules. **What deliberately did not change:** canonical Markdown/Git authority, the closed `EdgeType`/`ChangeKind` values, retained historical snapshots, storage/API ownership, dashboard permission, deployment, or release authority. |
| 0.6.0 | 2026-08-09 | I. Abbott (owner and ratifier) | **Ratified correction amendment — Standards Action** | Owner ratification adopts SIDX-06E rev 0.4.0 PCDN-SIDX-06E-011 through PCDN-SIDX-06E-016 as written and closes the implementation-audit carrier gaps without weakening rev 0.5.0. It registers the exact standalone `**Spec Edge:**` grammar, declared allowlist, four-row inference registry, provenance and failure classifications (§5.2); freezes `GlobalObjectIdV1`, its eligible-kind table, canonical amendment/rationale identities, and the one-unit positional-history-gap boundary (§4.3.1); makes schema-v3 `verifies` object-only and leaves its positive control deferred until a checking-object kind has a stable registered id (§5.3); evaluates retirement once per amendment/retired target, requires one consistent declared `successor -> retired` edge across every eligible last-present parent, and forbids first/newest/family-local successor choice (§8.2); and freezes the sorted, deduplicated three-key `retired_dependencies` member with array-level declared provenance (§8.2). **Change kind:** `semantic`. **Touches:** §0 metadata; §4.3; §5/§5.1 and new §5.2/§5.3; §8.2; §10; §12.1/§12.2/§12.4; §13; §15. **Authority/provenance:** Ira Abbott explicitly accepted PCDN-SIDX-06E-011 through -016 as written on 2026-08-09; this row is the coordinated upstream Standards Action required by SIDX-06E §10.1. **Diagnostic/provider ownership:** diagnostic-v3 record identity/facts/locators and provider counter precedence remain owned by SIDX-06E rev 0.4.0, producer serialization/profile by SIDX-06A, shared-query compatibility by SIDX-06B, and diagnostic-v1 history by SIDX-06D; none becomes new object-model vocabulary. **Migration boundary:** retained object schema v2 and diagnostic schemas v1/v2 remain immutable/readable; no path/line identity is legitimized, no historical schema-v3 byte is reinterpreted, and no current positional kind is silently promoted. **Considered and rejected:** prose-verb inference, `Relationship:`/JSON/YAML alternatives, nearest/first/family-local resolution, every nonempty id, path/line/hash ids, silent header cleanup, locator-shaped `verifies`, test/commit pseudoobjects, aggregate or first-successor retirement, raw retirement strings, per-member provenance, and reusing diagnostic schema 2 with changed record identity. **What deliberately did not change:** the closed `ObjectKind`, `EdgeType`, `ChangeKind`, `LocationKind`, lifecycle, or open-question enums; Markdown/git authority; rev 0.5.0 pair orientation, fingerprint, DAG clearing, removal/reintroduction, and metric semantics; retained snapshot bytes; C11/C12 public literal ownership; dashboard, deployment, legal, qualification, governance, or release authority. |

---

*End of SBC-00-ADDENDUM-C*
