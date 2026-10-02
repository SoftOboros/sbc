# SBC-00-ADDENDUM-D — Change Log Shape and the Amendment Object

**Document ID:** SBC-00-ADDENDUM-D
**Status:** RATIFIED AMENDMENT — exact ERRATA-015 packet accepted 2026-09-05; implementation evidence remains outstanding
**Revision:** 0.8.0
**Date:** 2026-09-05
**Author:** Ira Abbott / SoftOboros Inc.
**Parent:** `docs/SBC-00-CONCEPTS.md`
**Depends on:** `SBC-00-ADDENDUM-C.md` (`ObjectKind`, `ChangeKind`, attribute provenance, §1 axes)
**Canonical path:** `docs/SBC-00-ADDENDUM-D.md`
**Resolves:** `PCDN-SBC-00-C-002` (rationale is an inline sub-shape), `PCDN-SBC-00-C-003` (freeze after audit)

---

## §0 Purpose

`SBC-00-CONCEPTS.md` SBC-INV-9 requires a §15 change log in every phase doc. It never specified the log's *shape*. This addendum freezes it.

The relationship to `SBC-00-ADDENDUM-B.md` is exact: B owns the `ERRATA.md` shape, D owns the §15 shape. Both instantiate parent rules into a copyable artifact. Together they cover the corpus's two Trajectory-and-Intent surfaces.

**Authority relationship: `extend`** on `SBC-00-CONCEPTS.md` §15; `compose` on `SBC-00-ADDENDUM-C.md` (`amendment` and `rationale` are C's `ObjectKind` values; D specifies how they are authored, not what they mean).

---

## §1 Evidence [Informative]

Audit of all 148 §15 entries across 32 concepts docs, via `scripts/specidx/scan.py --changelog-audit`, pinned to `fcc6e924d`.

| Property | Table shape (18 entries / 5 docs) | Bullet shape (130 entries / 27 docs) |
|---|---|---|
| Carries a revision | 100% | **0%** |
| Carries an author | 100% | **0%** |
| Names any object id | 55.6% | **24.6%** |
| Names a commit SHA | 5.6% | 4.6% |
| Entry ≥ 800 chars | 33.3% | 13.1% |
| Length median / p90 / max | 391 / 2,147 / 2,804 | 337 / 934 / 2,787 |

Additional: **6 documents carry entries out of chronological order** (position ≠ chronology). **13 distinct status strings** are in use — an unfrozen enum operating in the wild.

Five conclusions, each of which a frozen field closes:

1. **The delta list is usually absent.** Only 55.6% / 24.6% of entries name a single object id. "Which objects did this amendment touch" — the question SBC-INV-4's amendment-first rule exists to make answerable — is unanswerable for most of the corpus. → `Touches:`
2. **The implementation link is almost always absent.** ~5% name a commit SHA, so an amendment rarely connects to the code that realised it. → `Commits:`
3. **The bullet shape cannot be versioned.** Zero entries carry a revision or an author. Trajectory queries ("what did this say at rev 0.3.0") are structurally impossible for 27 of 32 docs. → `Rev:`, `Author:`
4. **Both shapes are carrying reasoning they have no room for.** p90 of 2,147 characters in a table cell is a design essay in a spreadsheet field. This is the Intent axis (ADDENDUM-C §1) with nowhere to live. → `#### Rationale`
5. **Status is an unfrozen enum.** 13 spellings of roughly five states. → §3 `AmendmentStatus`

Note on instrument: a lexical "rationale marker" heuristic was tried and **rejected** — it scored a 2,147-character sustained design argument (`TODO-MCAD-00-CONCEPTS.md` rev 0.4.0) at zero. Entry length is used instead because it is instrument-independent. Per ADDENDUM-C §4.2 the derived attribute is marked `inferred`, not `declared`.

---

## §2 Frozen Shape — the Amendment Entry [Normative]

A §15 entry is an `amendment` object (ADDENDUM-C §4.1). Two authored forms
are valid; both compile to the same object. Under the schema-v3 identity
frontier, a block/compact entry whose containing document and revision satisfy
the ratified global-id rules compiles to exactly
`<document-id>#amendment:<revision>`. The identifier is derived from authored
stable fields, never a repository path or line number.

### §2.1 Block form (the frozen shape)

```markdown
### 0.6.0 — 2026-08-04 — ratified

**Author:** I. Abbott
**Change kind:** semantic
**Touches:** INV-MCAD-4, INV-MCAD-5, §7.2
**Commits:** a1b2c3d, e4f5a6b
**Summary:** Scoped INV-MCAD-4 to extracted dimensional values.

#### Rationale

Five phases had each invented a vocabulary for one concept. Patching them
pairwise produced four collisions; lifting the concept to family level
dissolved all four at the root. Considered and rejected: per-phase adapters,
which preserve the collisions and add a translation surface per pair.

What did not change is the finding worth recording — the epistemic machinery
generalised unmodified; only the physical model was missing.
```

Field rules:

| Field | Required | Notes |
|---|---|---|
| Revision (heading) | **MUST** | Monotone within the document; an edge-eligible revision matches `^(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)$` |
| Date (heading) | **MUST** | ISO 8601; ordering is by this field, never by file position |
| Status (heading) | **MUST** | §3 enum |
| `Author:` | **MUST** | Free text; identity, not role |
| `Change kind:` | **MUST** | `ChangeKind`, ADDENDUM-C §8.2 — drives suspicion propagation |
| `Touches:` | **MUST** | Exactly one comma-delimited field; `none` is valid and explicit. Legacy section/path values remain readable, but only ratified `GlobalObjectIdV1` members authorize C6 events. A duplicate field fails generation. |
| `Commits:` | SHOULD | Required when status is `execution` |
| `Summary:` | **MUST** | One line |
| `#### Rationale` | Conditional | **MUST** be present when `Change kind ∈ {semantic, scope, retirement}` (ADDENDUM-C INV-C-3) |

### §2.2 Compact form

A single table row remains valid for entries that carry **no rationale** and touch **no objects** — editorial and clarification changes:

```markdown
| Rev | Date | Author | Status | Change kind | Touches | Summary |
|---|---|---|---|---|---|---|
| 0.5.1 | 2026-08-01 | I. Abbott | amended | editorial | none | Fixed two broken links in §13. |
```

The compact form **MUST NOT** be used when a rationale is required. An entry that outgrows one line is a block-form entry that was authored in the wrong shape.

### §2.3 Migration [Normative]

Existing bullet-form and legacy-table entries **remain valid input**. A parser accepts all three shapes and marks fields absent from the authored form as `inferred` or missing — never fabricated.

**No family is required to rewrite history.** Retrofitting 148 entries would substitute one unevidenced shape for another and destroy the authorship record in the process. The rule binds **new** entries from the ratification date. A family MAY backfill, and SHOULD backfill `Touches:` for entries whose amendments are still propagating suspicion.

Retained schema-v2 amendment/rationale ids remain byte-for-byte readable.
Schema-v3 emission uses the stable identities above only when the containing
declared document id, revision, and object kind are eligible. Nonconforming or
legacy entries remain object rows but cannot become edge endpoints or valid C6
`Touches` targets. Their presence contributes the exact per-required-commit
`[commit, "object", "edge_ineligible_semantic_identity"]` provider history-gap
unit defined by ADDENDUM-C §4.3.1 and SIDX-06E §10.1.2; the producer emits a
diagnostic only when such an identity is actually used by one of the
source/target/`Touches` cases registered in SIDX-06E §10.1.6. Neither layer
derives a replacement id from a path.

---

### §2.3.1 Assessment of retained legacy input [Normative]

The legacy-input permission in §2.3 remains binding. Historical applicability
and current obligations are assessed under ADDENDUM-B §1.1, with continuity
under ADDENDUM-C §7.1. A disposition neither fills a missing legacy field nor
retroactively amends the governing rule. Retained missing-field evidence and
endpoint/history limitations MUST remain inspectable.

A disposition record is neither an amendment nor a §2.5 project event. It stays
inside its owning erratum and MUST NOT generate `ChangeKind`, `Touches`, or a
suspicion input. §2.4's explicit owner classification still governs conversion
of old event-shaped entries. No keyword classifier or blanket value substitution
is authorized by acceptance of historical non-applicability.

---

## §3 Frozen Enum — `AmendmentStatus` [Normative]

Replaces the 13 status spellings measured in §1.

| Value | Meaning |
|---|---|
| `drafted` | Content added; not yet binding |
| `ratified` | Reviewer accepted; the doc's gates are closed |
| `amended` | A ratified doc's text changed |
| `execution` | Implementation landed against ratified content; `Commits:` required |
| `superseded` | This document is no longer the authority; a `supersedes` edge MUST name the replacement |

**Registration policy: Standards Action.**

`ratified` and `amended` are distinct because the first closes §12 and the second modifies text already binding — they propagate suspicion differently and collapsing them loses that.

---

## §4 The Rationale Sub-Block [Normative]

Resolves `PCDN-SBC-00-C-002` to the inline form. A separate rationale file class would be a new unspecified surface, and §1 measures what happens to those.

A rationale is a `rationale` object (ADDENDUM-C §4.1). For one eligible
amendment it is addressable exactly as `<amendment-id>#rationale`, so its
identity survives document relocation and line movement. It carries one
inferred `motivates` edge to every distinct globally valid, uniquely resolved
id in the amendment's single `Touches:` field. Invalid, ambiguous, or
edge-ineligible members produce the ratified diagnostic and no edge; a
canonical retirement target absent from the current projection instead follows
the parent-resolved exception, produces neither `touches_unresolved` nor
`retirement_supersedes_missing`, and remains provider input. The producer never
substitutes the amendment or containing document as target. An absent or empty
authored `Touches:` field remains invalid under §2.

Content SHOULD cover three things, because these are what the corpus's best existing entries already cover and what its weakest omit:

1. **What was considered and rejected**, with the reason — not merely what was chosen.
2. **What the failure mode was** if the change had not been made.
3. **What deliberately did not change**, where that is itself the finding.

The third is the one most often lost, and the most valuable on re-read: an explicit "this generalised without modification" is a load-bearing claim about the design's stability, and it is unrecoverable from a diff.

A rationale **MUST NOT** restate the amendment's normative text. It explains; the spec states. Restatement here is the SBC-INV-2 failure in a new surface.

---

## §5 Reconciliation [Normative]

| # | Primitive | Decision |
|---|---|---|
| 1 | `SBC-00-CONCEPTS.md` §15 | `extend`. Adds shape to an existing required section; changes no rule about when a §15 entry is required. |
| 2 | `SBC-00-ADDENDUM-B.md` | `compose`. Same instantiation pattern (B: ERRATA shape; D: §15 shape). SBC-INV-13's ERRATA↔§15 boundary is unchanged; `Touches:` makes the §15 side machine-readable. |
| 3 | `SBC-00-ADDENDUM-C.md` | `compose`. `amendment`, `rationale`, and `ChangeKind` are C's; D specifies authoring only. |
| 4 | git | `compose`. `Commits:` cites SHAs; git remains history's authority (C §7). D adds the amendment→implementation edge git cannot infer. |
| 5 | Semantic Versioning | `derive`, not `mirror`. Revisions look like semver and are **not** semver — there is no public API and no compatibility contract. Monotonicity is the only guaranteed property. |

---

## §6 Non-Goals

1. **Not a mandate to rewrite existing logs** (§2.3). The rule binds new entries.
2. **Not a versioning policy.** When to bump minor vs. patch is each family's call; only monotonicity binds (§5 row 5).
3. **Not a replacement for ERRATA.** SBC-INV-13's boundary stands: §15 records the spec change, ERRATA records the evidence that motivated it.
4. **Not a commit-message format.** `Commits:` cites SHAs; commit subjects stay owned by the operational context, except the `Clears-Suspect:` trailer owned by ADDENDUM-C §8.3.

---

## §7 Acceptance [Normative]

### §7.1 Document acceptance

This document is ratified when:

- [x] Every field in §2.1 is either MUST, SHOULD, or conditional, with the condition named.
- [x] `AmendmentStatus` (§3) is closed and declares a registration policy.
- [x] The rationale sub-block is addressable and carries a `motivates` edge (§4).
- [x] Schema-v3 amendment/rationale identities derive only from a declared
  document id and exact revision, never from path or line.
- [x] `motivates` targets every valid `Touches` member and cannot fall back to
  an amendment/document object for an invalid member.
- [x] Migration (§2.3) states explicitly that no family must rewrite history.
- [x] Every adjacency in §5 carries an `AuthorityRelationship`.
- [x] `PCDN-SBC-00-C-002` and `-003` are recorded as resolved here and in ADDENDUM-C §12.4.

### §7.2 `SECTION-001` — Consumer conformance

Obligations on tools that read the corpus. These are **not** gates on this document — a spec is
not unratified because no implementation exists yet — and they are tracked by the consuming
family, not here.

| # | Obligation | Status at ratification |
|---|---|---|
| D-C1 | A parser MUST accept all three authored shapes (block §2.1, compact §2.2, legacy bullet/table §2.3). | ✅ **Met** 2026-07-31 (`270bec444`). |
| D-C2 | Fields absent from an authored form MUST be marked `inferred` or omitted — never fabricated (ADDENDUM-C §4.2). | ✅ Met; mutation-checked. |
| D-C3 | Entry ordering MUST derive from the declared date field, never from file position. | ✅ **Met** 2026-07-31. Amendments carry a date-derived `chronological_rank`; 32 documents corpus-wide are flagged where file position diverges from declared date. |

Status is a snapshot; the consuming family holds the live record.

---

## §8 Files Cited

| File | Role |
|---|---|
| `docs/SBC-00-CONCEPTS.md` | Parent; §15 requirement |
| `docs/SBC-00-ADDENDUM-B.md` | Sibling instantiation (ERRATA shape) |
| `docs/SBC-00-ADDENDUM-C.md` | Object model; `ChangeKind`; INV-C-3 |
| `docs/SBC-00-ADDENDUM-D.md` | This document |
| `docs/todo/spec-index/TODO-SIDX-06E-C6-OBJECT-GRAPH-AND-ACKNOWLEDGMENT.md` | Owner-ratified stable identity and `motivates` decision record |
| `docs/todo/spec-index/TODO-SIDX-06A-CORPUS-AND-LOCATION-PROJECTION.md` | Consuming schema-v3 producer and diagnostic authority |
| `scripts/specidx/scan.py` | `--changelog-audit`, producing §1 (consuming repo) |

---

## §9 Change Log

### 0.1.0 — 2026-07-31 — drafted

**Author:** I. Abbott
**Change kind:** scope
**Touches:** SBC-00-ADDENDUM-D
**Summary:** Freezes the §15 change-log shape and the `amendment` object's authored form, after the audit `PCDN-SBC-00-C-003` required.

#### Rationale

The shape was frozen *after* measuring all 148 existing entries rather than before, because the obvious move — mandate the table shape, since 5 docs already use it — would have been wrong. The table shape carries revision and author (which bullets lose entirely) but has no room for rationale, and its p90 entry is 2,147 characters of design argument crammed into a spreadsheet cell. Freezing it would have mandated 59 rewrites toward a shape that fails the Intent axis just as badly as the one it replaced.

Considered and rejected: a separate rationale file class. It would be a fourth unspecified surface, and §1 is a measurement of what happens to unspecified surfaces in this corpus.

What deliberately did not change: the ERRATA↔§15 boundary (SBC-INV-13), the conditions under which a §15 entry is required, and every existing entry. This addendum adds shape to a surface that had none; it does not relitigate what belongs there.

This document is authored in its own block form, so it is its own first conformance test.

### 0.2.0 — 2026-07-31 — ratified

**Author:** I. Abbott (ratifier)
**Change kind:** clarification
**Touches:** sbc:ERRATA-004
**Summary:** Ratified. §7 split into document acceptance (§7.1, closed) and consumer conformance (§7.2, two items open).

#### Rationale

Ratified as part of closing ERRATA-004. Unlike its siblings this document never operated
unratified — it was drafted hours earlier — so there is no governed period for the record to
protect, and the drafting defect below was fixed at ratification rather than deferred to a
separate amendment. Recording the distinction because it is the one case where "ratify at existing
content, amend separately" does *not* apply, and a reader should be able to see that the exception
was reasoned rather than overlooked.

The defect: §7 listed "the parser accepts all three authored shapes" as a gate on **this document**.
It is not. A specification is not unratified because no implementation exists yet — that inverts
spec-before-code, making the spec wait on the code. Conflating the two would also have forced a
choice between checking a false box and blocking ratification on unrelated tooling work.

Considered and rejected: dropping the parser obligations entirely, since they are the consuming
family's business. Rejected because dropping them loses the only written record that the block form
this document freezes is not yet readable by anything — which is precisely the kind of gap that
becomes invisible and then surprising.

What deliberately did not change: the frozen shape (§2), `AmendmentStatus` (§3), the rationale
obligation (§4), and the migration guarantee that no family rewrites history (§2.3). Only the
acceptance section's structure moved.

### 0.3.0 — 2026-07-31 — amended

**Author:** I. Abbott
**Change kind:** clarification
**Touches:** SECTION-001
**Commits:** 270bec444
**Summary:** D-C1 met; D-C2 mutation-checked. D-C3 remains open.

#### Rationale

Recorded because a conformance table that is never updated becomes a stale
assertion, which is worse than no table — it certifies. D-C1 closed when the
scanner learned the block form this document freezes; D-C2 was strengthened
from "met" to "mutation-checked" after fabricating a legacy revision and
forcing `has_rationale` each turned exactly one test red, confirming the
absence-asserting tests are not passing vacuously.

D-C3 stays open and is deliberately not softened. Six documents carry
out-of-order entries today, including this family's own parent before it was
corrected during ratification — evidence that file position and chronology
diverge under ordinary authoring, not under neglect.

What deliberately did not change: the frozen shape, `AmendmentStatus`, the
rationale obligation, and the §2.3 guarantee that no family rewrites history.
This amendment touches a status snapshot only.

### 0.4.0 — 2026-07-31 — amended

**Author:** I. Abbott
**Change kind:** clarification
**Touches:** SECTION-001
**Summary:** D-C3 met; all three consumer-conformance items now closed.

#### Rationale

Ordering is now derived rather than assumed: every amendment carries a
date-derived `chronological_rank`, so no consumer re-derives ordering and gets
it differently. The index itself stays sorted by file position, because
SBC-INV-20 needs a deterministic key and position is stable where dates are
not unique.

Scope correction worth recording: the §1 evidence table says 6 documents carry
out-of-order entries. That figure counted concepts docs only. Corpus-wide the
count is **32**. Both numbers are correct for their population and §1 is left
as authored, since it describes the audit that motivated the freeze; the wider
figure belongs here, where the obligation is stated.

Considered and rejected: sorting the index by date. It would make the index
non-deterministic wherever two entries share a date, breaking SBC-INV-20 to
fix a presentation concern that an attribute already solves.

What deliberately did not change: no document was reordered. §2.3's guarantee
that no family rewrites history covers ordering too — the divergence is
reported, not silently corrected.

### §2.4 An amendment's text MUST be sufficient to classify it

**INV-D-4.** An amendment's prose SHOULD state what changed in terms that
determine its `ChangeKind` without recourse to version-control history. Where it
does not, the `Change kind:` field is a judgement made by whoever fills it in
rather than a transcription of what the author recorded, and the two are not the
same fact.

**An entry that records a project event rather than a change to spec text is not
an amendment and MUST NOT be assigned a `ChangeKind`.** Execution completions,
drafting notices, wave landings, and commit rosters commonly share the §15 entry
shape; typing them produces metadata about something that never changed. Measured
at `38e4ea8b6`: 312 of 1195 amendment-shaped lines across the corpus are project
events, and a further 238 bundle an event with a change.

**One entry carries at most one `ChangeKind`.** An entry describing several
changes of different kinds MUST be split before it can be typed, or left
untyped. It MUST NOT be assigned the kind of its largest change.

**`undeclared` and `editorial` are different facts and MUST remain
distinguishable.** `editorial` asserts that someone determined the change
carried no semantic force; absence asserts only that nobody has looked. A store
that cannot express the second will report the first, and its coverage metrics
will read as clean precisely where they are empty.

### §2.5 Project-event record [Normative]

A project event records that work happened without asserting that spec text
changed. It uses this exact forward-only form inside a change log:

```markdown
### EVENT-001 — 2026-08-28 — project event

**Author:** I. Abbott
**Commits:** a1b2c3d, e4f5a6b
**Summary:** The implementation wave completed.
```

The heading contains exactly `EVENT-NNN`, space-em-dash-space, an ISO 8601
date, and the lowercase literal `project event`. `NNN` is three ASCII digits
from `001` through `999`; the handle is stable and unique within the containing
document. It is a local record handle only. It is not an `ObjectKind`, a
`GlobalObjectIdV1`, a change event under ADDENDUM-C §8.2, or an edge endpoint.

`Author` and `Summary` each appear exactly once, are nonempty, and remain free
text. `Commits` is optional, appears at most once, and is nonempty when present.
The field order is `Author`, optional `Commits`, then `Summary`. No other field,
body prose, or rationale is valid in this form. In particular a project-event
record MUST NOT carry `Change kind`, `Touches`, `Retires-Dependency`, or any
relationship field and MUST NOT compile to an `amendment`, `rationale`, edge,
or suspicion input.

A producer recognizes a project-event candidate only from an `EVENT-` heading
inside a change log. A malformed candidate is a fail-closed producer
conformance diagnostic and prevents publication; it is not reinterpreted as an
amendment or added to the frozen diagnostic-v3 wire profile. Legacy bullet and
table entries remain readable and unchanged. No prose, keyword, status, date,
or commit heuristic may reclassify one. An entry that bundles an event with a
spec change remains untyped until an owner splits it explicitly.

### 0.5.0 — 2026-08-09 — ratified amendment

**Author:** Ira Abbott (ratifier); OpenAI Codex (drafting and reconciliation)
**Change kind:** semantic
**Touches:** SBC-00-ADDENDUM-D
**Summary:** Adopts the SIDX-06E rev 0.4.0 stable amendment/rationale identity and exact rationale-to-`Touches` motivation mapping.

#### Rationale

Schema-v2 compiled amendment and rationale ids use repository paths. That is
useful navigation evidence but cannot satisfy the ratified requirement that a
C6 endpoint survive relocation. The owner accepted the correction packet as
written, so schema-v3 now derives an amendment from the declared document id
and exact revision and derives its rationale from that amendment id.

The rationale continues to motivate every valid object named by `Touches`.
It does not motivate the amendment merely because the rationale is nested
under it, and an invalid positional member does not silently fall back to the
document. This preserves ADDENDUM-D's authored meaning while giving the
producer one deterministic identity and failure path.

Considered and rejected: retaining path-shaped v3 ids; hashing prose or
locators into ids; treating a rationale as motivation for only the first
`Touches` member; replacing invalid members with the containing document; and
rewriting retained schema-v2 bytes.

What deliberately did not change: the two authored amendment forms, closed
`AmendmentStatus`, rationale-content guidance, legacy readability, the
guarantee that no family rewrites history, Git history authority, change-kind
propagation, deployment authority, or release authority.

### 0.6.0 — 2026-08-28 — ratified project-event form

**Author:** Ira Abbott (owner and ratifier); OpenAI Codex (drafting and reconciliation)
**Change kind:** semantic
**Touches:** SBC-00-ADDENDUM-D, sbc:ERRATA-005
**Summary:** Owner acceptance of `EOQ-001-ERRATA-005` adds the exact
forward-only `EVENT-NNN` project-event record without adding an object, change
kind, dependency, or historical classifier.

#### Rationale

Project events are a measured quarter of the legacy change-log population, but
the amendment block requires a `ChangeKind` that §2.4 correctly prohibits for
events. A separate explicit record makes new events attributable and stable
without asserting that spec text changed or enlarging the object and provider
contracts.

Considered and rejected: an `AmendmentStatus` value that mixes kind and status;
`Change kind: none`, which collapses declared no-force and undeclared evidence;
permanent legacy bullets; a new `ObjectKind`; and keyword, status, commit, or
prose inference over historical entries.

What deliberately did not change: the amendment block and compact forms;
`AmendmentStatus`, `ObjectKind`, `ChangeKind`, `GlobalObjectIdV1`, edge or
suspicion semantics; legacy source rows; retained projections; mixed-entry
classification; diagnostic-v3; deployment; or release authority.

### EVENT-001 — 2026-08-28 — project event

**Author:** Ira Abbott
**Summary:** The owner accepted `EOQ-001-ERRATA-005` as proposed.

### 0.7.0 — 2026-08-29 — ratified stable-section allocation

**Author:** Ira Abbott (owner and ratifier); OpenAI Codex (drafting and reconciliation)
**Change kind:** semantic
**Touches:** SECTION-001
**Summary:** The owner's accepted decision allocates only §7.2 as `SECTION-001` and backfills only the 0.3.0 and 0.4.0 `Touches` fields to that stable local handle.

#### Rationale

The two earlier amendments explicitly change the consumer-conformance status
snapshot, so a stable section target preserves their authored scope without
substituting this document or distributing the changes among the three D-C
rows.

This amendment begins the coordinated additive object-schema-v3 frontier. It
does not reinterpret retained projections, alias an ordinal, or allocate any
other section. The §7.2 title, body, D-C1/D-C2/D-C3 labels, obligations, and
recorded statuses remain unchanged.

Considered and rejected: promoting the D-C row labels into objects;
document-, ordinal-, title-, path-, line-, or content-hash identity;
first-match repair; and new `cites`, `refines`, `blocks`, `verifies`,
`supersedes`, or checking-source semantics.

### 0.8.0 — 2026-09-05 — ratified ERRATA-015 amendment

**Author:** Ira Abbott (ratifier); OpenAI Codex (drafting and recording)
**Change kind:** semantic
**Touches:** SBC-00-ADDENDUM-D
**Summary:** Reconcile legacy validity and event/amendment boundaries with the separate assessment owner. The owner ratified this exact coordinated packet in task `01a06eee-bae3-7911-9198-adfae97256f1` on September 5, 2026. Accepted patch SHA-256: `220d77faff10b8132768a2d0a19ec7e099decf605ad72dd7f57a174f40e69de1`. This records specification ratification, not implementation, clearance, or deployment.

#### Rationale

The owner accepted decision-packet version 1 and subsequently ratified this exact
amendment packet on September 5, 2026. This amendment supplies the reserved contract. Treating every old
missing process field as a present violation, equating acceptance with repair,
and hiding diagnostics by client arithmetic were considered and rejected.
The native repair lifecycle, retained historical evidence, C6 clearings, and
C11/C12 response meanings deliberately do not change. This ratification authorizes deriving implementation from the coordinated
amendment after the specification commit boundary.
