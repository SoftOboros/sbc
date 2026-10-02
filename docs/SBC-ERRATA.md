# ERRATA — `sbc` (Spec-Before-Code discipline)

**Document ID:** SBC-ERRATA
**Family:** `sbc`
**Phase docs:** `docs/SBC-00-CONCEPTS.md`, `docs/SBC-00-ADDENDUM-A.md`, `docs/SBC-00-ADDENDUM-B.md`
**Governed by:** `docs/SBC-00-CONCEPTS.md` SBC-INV-7, SBC-INV-10; `docs/SBC-00-ADDENDUM-B.md`

**Status legend**

| Icon | Meaning |
|---|---|
| 🟢 | resolved — fix landed, verification evidence recorded |
| 🟡 | diagnosed — root cause known, fix prescription clear |
| 🔴 | open — undiagnosed or unresolved |
| ⚪ | deviation-pending-ratification — awaiting §15 amendment |

---

## Open Questions

| EOQ id | Errata | Question |
|---|---|---|
| `EOQ-001-ERRATA-015` | `ERRATA-015` | **Open.** What forward-only record and lifecycle distinguish a verified repair from authorized clearance of an exception that cannot be repaired forward, without redefining `resolved` or reusing suspicion acknowledgment? |
| `EOQ-002-ERRATA-015` | `ERRATA-015` | **Open.** What exact approval scope, evidence, applicability boundary, and recurrence rules establish and maintain a clean slate without accepting unknown future defects? |
| `EOQ-003-ERRATA-015` | `ERRATA-015` | **Open.** After the process is ratified, how do shared queries and the dashboard distinguish open work, planned work, verified repairs, and approved clearances while preserving historical evidence and confidence meaning? |

---

## Resolved Decisions

| EOQ id | Errata | Resolution |
|---|---|---|
| `EOQ-001-ERRATA-005` | `ERRATA-005` | **Accepted.** Add a distinct, forward-only `EVENT-NNN` project-event record that is validated but does not compile to an object, `ChangeKind`, `Touches`, edge, or suspicion input; retain legacy and mixed entries without inference. |
| `EOQ-001-ERRATA-006` | `ERRATA-006` | **Accepted.** Use the exact declared historical-definition list and current-projection-only exclusion measured by the six-part candidate; retain the document, every unlisted object, all source bytes, and all committed history without inferring equivalence or replacement semantics. |
| `EOQ-001-ERRATA-007` | `ERRATA-007` | **Accepted.** Begin the next compatibility frontier with stable term handles for the measured 66-record wave. |
| `EOQ-001-ERRATA-008` | `ERRATA-008` | **Accepted.** Mechanically migrate only the evidence-complete 0.9.0 and 0.10.0 legacy amendments to the frozen block shape; leave every other legacy amendment unchanged. |
| `EOQ-001-ERRATA-009` | `ERRATA-009` | **Accepted.** Register the exact `GATE-NNN` authored shape and 31-row allocation as a new compatibility frontier without adding `verifies` semantics. |
| `EOQ-001-ERRATA-010` | `ERRATA-010` | **Accepted.** Register the exact `NONGOAL-NNN` authored shape and 16-row allocation as a new compatibility frontier without changing non-goal text or asserting equivalence. |
| `EOQ-001-ERRATA-012` | `ERRATA-012` | **Accepted.** Register the exact `SECTION-NNN` authored heading shape, allocate only ADDENDUM-D §7.2 as `SECTION-001`, and backfill only its two named `Touches` fields without adding D-C objects or new relationship semantics. |

---

## Index

| Id | Title | Status | Phase | First seen |
|---|---|---|---|---|
| ERRATA-001 | `ErrataStatus` enum ownership misrepresented in v0.3.0 changelog | 🟢 | SBC-00 v0.3.0 | 2026-05-31 |
| ERRATA-002 | §4 source-of-truth map collapsed entire errata surface to one row | 🟢 | SBC-00 v0.3.0 | 2026-05-31 |
| ERRATA-003 | Two coexisting concepts docs; `SBC-INV-N` handles rebound; conformance-target invariant dropped; folder layout did not match documented structure | 🟢 | SBC-00 v0.5.0 | 2026-05-31 |
| ERRATA-004 | Family operated for two months on an unratified normative root; every governed family inherited advisory-only coverage | 🟢 | SBC-00 v0.5.0 | 2026-07-31 |
| ERRATA-005 | A project event cannot be authored in the frozen block form — mandatory `Change kind:` contradicts §2.4's prohibition | 🟢 | ADDENDUM-D v0.6.0 | 2026-07-31 |
| ERRATA-006 | Superseded predecessor definitions still collide with the replacement authority in the current object graph | 🟢 | ADDENDUM-C v0.10.0 | 2026-08-22 |
| ERRATA-007 | Positional SBC objects and legacy amendments have no stable C5/C6 endpoint identity | 🟢 | ADDENDUM-C v0.7.0 | 2026-08-22 |
| ERRATA-008 | Two evidence-complete legacy amendments remain positional despite carrying explicit frozen fields | 🟢 | ADDENDUM-D v0.5.0 | 2026-08-23 |
| ERRATA-009 | SBC acceptance gates have no stable C5/C6 endpoint identity | 🟢 | ADDENDUM-C v0.8.0 | 2026-08-23 |
| ERRATA-010 | SBC non-goals have no stable C5/C6 endpoint identity | 🟢 | ADDENDUM-C v0.9.0 | 2026-08-23 |
| ERRATA-011 | Project-event ratification left two downstream §15-shape restatements stale | 🟢 | ADDENDUM-A/C clarification | 2026-08-29 |
| ERRATA-012 | Two ADDENDUM-D amendments target positional §7.2, which cannot resolve as a C6 endpoint | 🟢 | ADDENDUM-C v0.12.0 / ADDENDUM-D v0.7.0 | 2026-08-29 |
| ERRATA-013 | SBC-00 rev 0.8.0 carried complete amendment evidence but remained positionally identified | 🟢 | SBC-00 v0.8.0 | 2026-09-01 |
| ERRATA-014 | SBC-00 rev 0.11.0 carried complete amendment evidence but remained positionally identified | 🟢 | SBC-00 v0.11.0 | 2026-09-02 |
| ERRATA-015 | Historical exceptions lack a forward-only clearance contract | 🔴 | ADDENDUM-B/C/D; downstream SIDX-06 | 2026-09-03 |

---

## ERRATA-001 — `ErrataStatus` enum ownership misrepresented in v0.3.0 changelog

**Status:** 🟢 resolved
**First seen:** 2026-05-31
**Owning phase:** `SBC-00` rev 0.3.0 (`docs/SBC-00-CONCEPTS.md`)

### Symptom

The v0.3.0 §15 changelog entry read: *"`ErrataStatus` folded into SBC-INV-10"*.  No
`ErrataStatus` enum section appeared anywhere in the concepts doc.  The changelog claimed
ownership that was never exercised; the enum had no frozen definition in any artifact.

### Root cause

During synthesis, the decision to defer `ErrataStatus` to ADDENDUM-B was correct but the
changelog entry was written as if the enum had landed in the concepts doc.  The entry described
an intent, not an outcome.  ADDENDUM-B did not yet exist when the changelog was written, so
the deferral had no destination.

### Fix

`docs/SBC-00-ADDENDUM-B.md` created as the normative home for `ErrataStatus` (§1), the
ERRATA boundary rules (§2), and the `ERRATA.md` file template (§3).  `SBC-00-CONCEPTS.md`
§4 source-of-truth map updated to point `ErrataStatus` → ADDENDUM-B §1.  §15 entry v0.4.0
records the correction.

### Verification

`SBC-00-CONCEPTS.md` §4 contains no claim of ownership over `ErrataStatus`.
`SBC-00-ADDENDUM-B.md` §1 contains the frozen enum with registration policy declared.
§15 v0.4.0 in the concepts doc cites this correction.

### Tracking

Resolved by creation of `SBC-00-ADDENDUM-B.md` and `SBC-00-CONCEPTS.md` patch rev 0.4.0.

---

## ERRATA-002 — §4 source-of-truth map collapsed entire errata surface to one row

**Status:** 🟢 resolved
**First seen:** 2026-05-31
**Owning phase:** `SBC-00` rev 0.3.0 (`docs/SBC-00-CONCEPTS.md`)

### Symptom

`SBC-00-CONCEPTS.md` §4 source-of-truth map contained a single row:

> *"Errata log file shape + lifecycle — Each family's `ERRATA.md`; shape governed by SBC-INV-10"*

This single row conflated four distinct concepts — the `ErrataStatus` enum, the ERRATA vs. §15
boundary rule, the ERRATA vs. issue-tracker boundary rule, and the file shape — each of which
requires a separate owner.  The map's contract is one owner per concept; one row for four
concepts violated SBC-INV-2 (silent restatement / collapsed ownership) and left the boundary
rules without a normative home or stable identifier.

### Root cause

ADDENDUM-B did not exist when the concepts doc was written.  The map entry was a placeholder
deferral written as if a single owner covered the entire surface.  Once ADDENDUM-B was created,
the gap became visible: the map pointed nowhere useful and no invariant (SBC-INV-7, SBC-INV-10)
addressed the canonical-record decision rule.

### Fix

`SBC-00-CONCEPTS.md` §4 source-of-truth map expanded to four rows, each pointing to the
correct section of ADDENDUM-B.  `SBC-INV-13` added to §9 to give the ERRATA vs. §15
canonical-record decision rule a stable invariant handle.  §15 v0.4.0 records both changes.

### Verification

`SBC-00-CONCEPTS.md` §4 contains four errata-surface rows, each with a distinct owner.
`SBC-INV-13` exists in §9 with a verification surface.
`SBC-00-ADDENDUM-B.md` §2 contains the normative boundary rules.

### Tracking

Resolved by `SBC-00-CONCEPTS.md` patch rev 0.4.0 and `SBC-00-ADDENDUM-B.md` creation.
Motivated the creation of this errata log (SBC-INV-10 now applied to the sbc family itself).

---

## ERRATA-003 — Predecessor/successor concepts docs coexisted with rebound invariant handles

**Status:** 🟢 resolved
**First seen:** 2026-05-31
**Owning phase:** `SBC-00` rev 0.5.0 (`docs/SBC-00-CONCEPTS.md`)

### Symptom

The `sbc` folder shipped **two** concepts docs for the same subject:
`SPEC-BEFORE-CODE-CONCEPTS.md` (the softoboros-relative input, self-declared *Ratified
2026-05-31*, ten invariants `SBC-INV-1…10`) and `SBC-00-CONCEPTS.md` (the portable synthesis
Sonnet authored from it, DRAFT, thirteen invariants). Three concrete defects followed:

1. **`SBC-INV-N` handles rebound between the two docs** — the predecessor's `SBC-INV-6`
   ("maintain a living `ERRATA.md`") and `SBC-INV-10` ("acceptance list names its conforming
   artifact") map to *different* rules under the same handles in the successor. The discipline's
   own §8 promise is that an assigned id never re-binds.
2. **The conformance-target rule was dropped as an invariant** — the predecessor's `SBC-INV-10`
   survived in the successor only as §3 glossary prose, with no numbered handle a phase doc could
   cite "preserves".
3. **`AGENTS.md` contradicted a sibling doc** — it reported "Ratified artifacts: none yet" while
   `SPEC-BEFORE-CODE-CONCEPTS.md` declared itself ratified.

Compounding: every `docs/SBC-…` canonical-path header and cross-link pointed at a `docs/`
directory, but the files sat in `concepts/`, and `templates/ERRATA.md` (referenced by README
and CLAUDE.md) was actually a top-level `templates-ERRATA.md`.

### Root cause

`SBC-00-CONCEPTS.md` was synthesised from `SPEC-BEFORE-CODE-CONCEPTS.md` by a second author
(Sonnet) and the files were dropped into the repo without running the discipline's own
supersession trail: no errata entry, no §15 amendment, no SUPERSEDED marker. The renumbering of
invariants during synthesis went unrecorded, so the two docs silently forked — the exact failure
mode (handle erosion / silent fork) the discipline exists to prevent.

### Fix

- Folder layout brought into line with every doc's documented structure:
  `concepts/` → `docs/`, `templates-ERRATA.md` → `templates/ERRATA.md`. All `docs/SBC-…` links
  now resolve.
- `SBC-00-CONCEPTS.md` designated the sole canonical concepts artifact;
  `SPEC-BEFORE-CODE-CONCEPTS.md` stamped **SUPERSEDED** with a banner pointing at the successor
  and at this entry, and an explicit "do not cite this doc's `SBC-INV-N` handles" warning. Kept
  in-tree as institutional memory (SBC-INV-10), not deleted.
- Conformance-target rule re-homed as **SBC-INV-14** in `SBC-00-CONCEPTS.md §9`; §12 invariant
  count corrected (twelve → fourteen); header revision synced (0.3.0 → 0.5.0); §13 files-cited
  expanded to list `SBC-ERRATA.md` and the superseded predecessor.
- `AGENTS.md` reconciled (see Verification).

### Verification

- `find docs/spec-before-code -type f` shows a single `docs/` directory and `templates/ERRATA.md`;
  no `concepts/`, no `templates-ERRATA.md`.
- `SBC-00-CONCEPTS.md §9` carries `SBC-INV-1…14`; §12 reads "fourteen"; header reads `0.5.0`.
- `SPEC-BEFORE-CODE-CONCEPTS.md` opens with the SUPERSEDED banner.
- `AGENTS.md` names `SBC-00-CONCEPTS.md` as the sole canonical concepts doc and no longer
  contradicts the predecessor's status.

### Tracking

Resolved by `SBC-00-CONCEPTS.md` rev 0.5.0 (§15 entry cites this errata) plus the folder
restructure. Per SBC-INV-13, because the resolution edited normative §9/§12/§13 of a
`-NN-CONCEPTS.md`, the §15 entry is the canonical record and this entry cites it. The
predecessor doc's renumbered handles are recorded here so anyone who cited them pre-supersession
can remap.

---

## ERRATA-004 — Family operated for two months on an unratified normative root

**Status:** 🟢 resolved
**First seen:** 2026-07-31
**Owning phase:** `SBC-00` (`docs/SBC-00-CONCEPTS.md`)

### Symptom

`SBC-00-CONCEPTS.md` carried **Status: DRAFT — not yet ratified** from 2026-05-31 through
2026-07-31, at revision 0.5.0, with §12 Acceptance fully authored and every checkbox unchecked.
`SBC-00-ADDENDUM-A.md` and `SBC-00-ADDENDUM-B.md` were DRAFT 0.1.0 over the same window.

During that window the discipline was in continuous force across the corpus: 51 families,
56 concepts docs, 506 invariant definitions, and 585 phase-coded commits since January cited
its rules. The project operational context document had already been rewritten (2026-07-18,
DOCH Wave 3) to cite `SBC-00-CONCEPTS.md` as the normative owner and to stop restating its
content — so the *only* normative authority for the discipline was a document whose own §12
declared it unratified.

### Root cause

Ratification is an explicit act with no forcing function. SBC-INV-1 requires a ratified concepts
doc before behaviour change *in a governed family*, and every family complied against the SBC
form — but nothing in the discipline gates the discipline's own root. The failure was invisible
because the corpus behaved exactly as if the root were ratified; the DRAFT marker was load-bearing
text that no process step ever read.

Per `CLAUDE.md`'s conformance-target rule and `SBC-00-ADDENDUM-A.md` §0, agents loading only the
operational context have **advisory** coverage; normative coverage requires the ratified concepts
doc. For two months no reader could obtain normative coverage, because the artifact that confers
it did not exist in ratified form.

### Fix

Ratified 2026-07-31 by the document owner, at existing content and without editing forward:

- `SBC-00-CONCEPTS.md` 0.5.0 DRAFT → **0.6.0 RATIFIED** (ratification only; no normative change).
- `SBC-00-ADDENDUM-A.md` 0.1.0 → **0.2.0 RATIFIED**.
- `SBC-00-ADDENDUM-B.md` 0.1.0 → **0.2.0 RATIFIED**.
- `SBC-00-ADDENDUM-D.md` 0.1.0 → **0.2.0 RATIFIED**.
- `SBC-00-ADDENDUM-C.md` was ratified earlier the same day at 0.2.0.

Content changes accumulated while the root was unratified were then landed as **separate,
subsequent amendments** rather than folded into the ratification revisions — `SBC-00-CONCEPTS.md`
0.7.0 (adopting ADDENDUM-C's §12.2 parent amendments) and `SBC-00-ADDENDUM-A.md` 0.3.0. This
ordering is the point: ratify what was actually in force, then amend with a visible trace, so the
record shows what the corpus was governed by at each moment.

### Verification

- All five `sbc` documents carry **Status: RATIFIED** with a dated §15/§4/§9 entry naming the
  ratifier.
- `SBC-00-CONCEPTS.md` §12 checkboxes are checked, and §15 carries separate 0.6.0 (ratification)
  and 0.7.0 (amendment) rows — the amendment does not ride the ratification.
- `scripts/specidx/scan.py` reports no `sbc`-family document with an unparsed or absent §15.

### Evidence addendum — prepared 2026-09-13

**Recorded by:** OpenAI Codex; retained-source corroboration.

**Original resolved-report filing:** `ca0ed17edaf3fc163828fda9ddaaa919c2f9cb9a`.
**Earlier C/D ratification boundary:** `91fbbd48e50179f34c77fef9220d556c80924744`.
**Root ratification and amendment boundary:** `3eb6ab1004ec64ead547d12b7ce8d3beeccac14a`.

The filing already contains the resolved narrative while the retained concepts
root is still revision 0.5.0 DRAFT. The root-change commit moves that root to
0.7.0 RATIFIED and records both 0.6.0 ratification and 0.7.0 amendment rows in
one Git commit. Those document revisions are distinct; an independent 0.6.0
Git snapshot is not established. The commit message also records that limit.

This qualifies the original Fix and Verification wording about separate,
subsequent amendments: the retained root history does not demonstrate separate
ratification and amendment commits. Ratified resulting documents corroborate
the later state, not a ratified root at filing or compliance with that original
sequencing claim. Later ratification neither repairs the earlier ordering nor
waives it. No historical non-applicability or accepted unrepaired exception is
inferred, and the original narrative remains intact as historical evidence.

**Corroboration:** [Exact retained evidence](../../plans/sbc-dashboard-review-2026-09-05/authority-scope-evidence.json).

This addendum is available only from the commit that first includes it;
its preparation date does not backdate adoption or verification. It
records source evidence, not human-confirmed condition satisfaction, an
exception disposition, or historical non-applicability. Native state and
independent obligations remain unchanged.

### Tracking

Related: ERRATA-003 (the 0.5.0 self-conformance pass that authored §12 but did not close it).
Per SBC-INV-13 the resolution edited normative document status and §15 of `-NN-CONCEPTS` docs,
so the §15 entries are the canonical record and this entry cites them.

Institutional lesson, recorded because it generalises beyond this family: **a discipline that
gates its dependents but not itself will eventually be found unratified.** The `-00` root of any
family running SBC should be checked for ratification status by the same sweep that checks
dependents — a candidate conformance check for the spec-index tooling (`scan.py`), where it is
one query over already-extracted document headers.

---

## ERRATA-005 — A project event cannot be authored in the frozen block form

**Status:** 🟢 resolved; exact remedy accepted by the owner through
`EOQ-001-ERRATA-005` on 2026-08-28, ratified in authority commit
`c1e8ca4f56da7b37217f8e4a7531c16b68c1bd64`, implemented in
`5600d0c1c311240727d7c38d1dd54e992ec90488`, and live-verified on
2026-08-29.
First seen 2026-07-31 while authoring a §15 entry in a consuming family
(`CCPS-02`), not by review of ADDENDUM-D itself.

### Symptom

Pinned to `49323e921`. Two normative rules in `SBC-00-ADDENDUM-D` cannot both be
satisfied by a single §15 entry that records a project event:

- **§2.1 field rules** mark `Change kind:` as **MUST** for the frozen block form.
  There is no exemption and no `none` value.
- **§2.4** states that an entry recording a project event rather than a change to
  spec text "is not an amendment and **MUST NOT** be assigned a `ChangeKind`."

An author recording an execution completion, a wave landing, or — as here — a
filed defect, must therefore either violate §2.1 by omitting a mandatory field,
violate §2.4 by typing a non-amendment, or decline the frozen shape and author in
the legacy bullet form that §2.3 keeps valid.

### Root cause

§2.1 was written for amendments and §2.4 was added later to stop project events
being typed. §2.4 correctly removed the *obligation* to classify them but did not
revisit the *shape* that assumes every entry is classifiable. The frozen form and
the exemption were specified against different populations of the same section:
§2.1 against the 883 amendment-shaped lines, §2.4 against the 312 project events
it measured inside them. Nothing reconciled the two counts.

Note that §2.4's own measurement is what makes this non-theoretical: project
events are 26% of the corpus's §15 lines, so the shape that cannot express them
cannot express roughly a quarter of what families actually write.

### Accepted measure

The owner accepted a fourth candidate through `EOQ-001-ERRATA-005` on
2026-08-28. ADDENDUM-D rev 0.6.0 and coordinated SIDX-06A rev 0.9.0 ratify this
exact boundary:

1. A forward project event uses the exact heading
   `### EVENT-NNN — YYYY-MM-DD — project event`, followed in order by nonempty
   `Author`, optional nonempty `Commits`, and nonempty `Summary` fields.
2. The stable handle is unique within the containing document and is a local
   source-record handle only. It is not an `ObjectKind`, `GlobalObjectIdV1`,
   change event, or edge endpoint.
3. The form prohibits `Change kind`, `Touches`, `Retires-Dependency`, other
   fields, body prose, and rationale. It emits no amendment, rationale, edge,
   semantic fingerprint, or suspicion-provider input.
4. An explicit malformed `EVENT-` candidate fails publication with a producer
   conformance diagnostic. The immutable sixteen-code diagnostic-v3 wire
   profile does not change.
5. Legacy bullet/table entries and mixed event/change entries remain unchanged
   and unclassified. No keyword, status, date, commit, path, line, prose, or
   first-match inference is authorized.

This is intentionally not a fourth object class hidden inside tooling. Markdown
retains the project record, while the Spec Index projects only spec objects and
their declared relationships.

The three previously documented candidates remain rejected:

1. **A `project-event` value in `AmendmentStatus` (§3)** that exempts
   `Change kind:`. Keeps one authored shape. Costs a frozen-enum amendment under
   Standards Action, and overloads a status enum with a kind distinction.
2. **An explicit `Change kind: none`.** Cheapest to author and parse, but it
   re-creates precisely the collapse §2.4 warns about — `none` and `undeclared`
   would be one token away from being read as the same fact, and §2.4's closing
   rule exists to keep "someone determined this carries no semantic force"
   distinct from "nobody looked."
3. **Project events stay in bullet form permanently**, with §2.1 scoped
   explicitly to amendments. Requires no enum change and is honest about the two
   populations, but leaves a class of entries structurally unversioned and
   unattributed — which is four of the five defects §1 measured.

The adopted form preserves the completeness sought by (1) without mixing kind
and status, preserves §2.4's declared/undeclared distinction, and avoids (3)'s
permanent unattributed-bullet shape.

### Verification

Authority commit `c1e8ca4f56da7b37217f8e4a7531c16b68c1bd64` landed
ADDENDUM-D rev 0.6.0, coordinated SIDX-06A rev 0.9.0, and `EVENT-001` as the
first real source control. Implementation commit
`5600d0c1c311240727d7c38d1dd54e992ec90488` added the closed project-event
parser and validator. A valid event remains source-only: it emits no amendment,
rationale, citation, dependency edge, semantic fingerprint, public diagnostic,
or suspicion-provider input. Explicit malformed candidates fail publication,
while fenced examples and all legacy or mixed prose retain their prior behavior.

The twelve focused project-event tests passed. The portable scanner suite
passed 99 tests with the three Windows symlink-privilege cases explicitly
deselected; when included, those same three fail during fixture setup with
WinError 1314 rather than exercising scanner behavior. Python bytecode
compilation, changed-file checks, and the generated-index drift gate passed.
Two controlled negative witnesses separately removed source-line suppression
and the event parser boundary: the first leaked an `EOQ-001-ERRATA-005`
citation, and the second swallowed the event into the preceding rationale.
Restoring each mechanism returned the final suite to green.

Regeneration after the implementation was an exact no-op relative to the
authority commit. `--check-index` reported 7,027 objects, 753 location records,
8,868 diagnostics, and 60 object families. The immutable sixteen-code
diagnostic-v3 profile did not change.

The Docker VM was rebuilt from the exact implementation commit by stopping the
stack, building the backend and frontend, starting the stack, and running the
full split-database migration sequence. The live ingest reproduced 7,027
objects, 12,214 edges, 753 locations across 753 documents, 8,868 diagnostics,
and 60 families. The evidence scheduler names the same full commit, and the
migration-drift check reports all migrations applied with no model changes.

On 2026-08-29 the signed-in SBC dashboard reported `staleness_state: current`,
branch `webslinger`, commit `5600d0c`, nine eligible and nine observed-partial
rows, and `uncomputable` with provider reason
`suspicion_inputs_incomplete`. Decision, deviation, acceptance, and coverage
inputs were available and complete; suspicion was available and incomplete.
The remaining coverage gap was therefore displayed rather than converted to
zero.

### Tracking

Encountered in `docs/todo/streamz/cooperative-charger/TODO-CCPS-02-MIXED-FIDELITY-EVIDENCE.md`
§15, where the SIM-039 project-event entry stays in bullet form and the adjacent
INV-MFE-9 amendment uses the block form — the two shapes sitting side by side in
one change log is the symptom made visible. That document's §15 form note cites
this entry.

ADDENDUM-D rev 0.6.0 is the canonical Standards Action and SIDX-06A rev 0.9.0
is its coordinated producer boundary. Authority commit `c1e8ca4f5` and
implementation commit `5600d0c1c` close this entry with committed-projection,
live-ingest, current-provider, and signed-in dashboard evidence. `EVENT-001`
remains a validated source record only. Legacy and mixed entries remain
unclassified, and `suspicion_inputs_incomplete` remains visible for later
work; this resolution closes no historical classification, identity,
relationship, or global provider-coverage gap by assertion.

---

## ERRATA-006 — Superseded predecessor definitions remain current identity collisions

**Status:** 🟢 resolved; exact remedy accepted by the owner through
`EOQ-001-ERRATA-006` on 2026-08-28, ratified in authority commit
`abc768c8ed942a5c2448af5da43f6a5de3a964c1`, implemented in
`8d38ab6734a0cb8c28d9f4824e9d7ce78f1c04f7`, and live-verified on
2026-08-28.
First seen 2026-08-22 while measuring the deployed C6 provider against
projection commit `e6192bd21`; remeasured 2026-08-23 at `d4780d027` and
2026-08-28 at `a09d18f0f` and `8d38ab673`.

### Symptom

`SPEC-BEFORE-CODE-CONCEPTS` declares itself superseded, retained only as
institutional memory, and names `SBC-00-CONCEPTS` as the sole replacement
authority. The current schema-v3 projection nevertheless reads both files as
current authored input. Its syntactic definition rule therefore admits the ten
historical invariant rows from the predecessor alongside the replacement rows.

At `e6192bd21`, 94 SBC-family `dependency_target_unresolved/ambiguous`
records cite those ten colliding invariant handles. Two handles also have
unrelated duplicate definition sites outside the predecessor, so suppressing
the predecessor alone is not claimed to close every collision. It does close
the mismatch between the authored supersession record and current-snapshot
identity treatment.

At `d4780d027`, the deployed SBC projection has 177 diagnostics. Ninety-seven
are ambiguous dependency targets: 94 cite the ten predecessor handles and the
remaining three cite unrelated ECA, phase-local, and SHARE handles. The exact
measured inventory is source-excluded evidence, not new citations:

```text
predecessor: INV-SBC-1..INV-SBC-10 = 94 records
other: INV-ECA-1 = 1; INV-PHASE-1 = 1; INV-SHARE-4 = 1
```

The predecessor's live document row still reports lifecycle `unknown` with
inferred provenance because its prose banner terminates the governed header
before the later `Status:` line. A producer therefore has neither declared
lifecycle authority nor a declared member set it can safely act on.

### Root cause

ERRATA-003 resolved the human authority fork with a superseded banner and an
explicit replacement, before the global object graph existed. ADDENDUM-C later
required every current edge endpoint to resolve to exactly one definition and
correctly prohibited family, path, and first-match tie-breakers. It did not
specify whether contained definitions in a document with declared lifecycle
`superseded` remain current edge candidates, historical rows only, or leave the
active corpus entirely.

The producer therefore cannot use the banner as an exclusion rule without
inventing lifecycle semantics. Treating the replacement as the winner because
it is newer or canonical-by-path would violate the existing collision rule.

### Accepted measure

The owner's acceptance adopts the exact measured declaration below, not a
banner heuristic or a whole-document lifecycle rule:

1. A document MAY declare contiguous governed-header fields
   `Document lifecycle state: superseded` and `Historical definitions:`. The
   latter is a nonempty comma-separated list of canonical `GlobalObjectIdV1`
   values. An inferred `Status: SUPERSEDED` value is deliberately insufficient.
2. Every listed id MUST be unique and MUST identify exactly one edge-eligible
   definition owned by that same document before exclusion. Empty members,
   aliases, unregistered ids, duplicate members, absent definitions, and local
   definition collisions fail generation.
3. In the current projection only, the producer excludes exactly those listed
   definition rows and same-document citation or dependency candidates whose
   source or target is listed. It retains the document object, its location,
   every unlisted contained object, and every source byte.
4. The declaration creates no `same-as`, `homonym-of`, `supersedes`, successor,
   retirement, or replacement mapping. It does not select by path, age,
   document name, family, first match, or prose description.
5. Retained committed schema-v3 projections remain immutable and readable. The
   first committed projection implementing this declaration begins the matching
   additive compatibility frontier; it does not reset or truncate the fixed C6
   history frontier.
6. The first declaration on `SPEC-BEFORE-CODE-CONCEPTS` carries this exact
   source-excluded evidence value:

   ```text
   **Document lifecycle state:** superseded
   **Historical definitions:** INV-SBC-1, INV-SBC-2, INV-SBC-3, INV-SBC-4, INV-SBC-5, INV-SBC-6, INV-SBC-7, INV-SBC-8, INV-SBC-9, INV-SBC-10
   ```

   Its accepted stable term, gate, amendment, and other unlisted rows remain
   current projection input.

The acceptance does not authorize a general rule for all contents of a
superseded document, any inferred identity equivalence, or a C6 history reset.

The broader alternatives remain rejected for this wave. Moving the entire
predecessor out of the active corpus would also remove accepted stable term and
gate identities. Per-object supersession records would require authored
successor meanings that do not exist, and the producer MUST NOT invent them.

### Noncommitting preview evidence

An isolated preview based on `d4780d027` implemented only the candidate above,
declared the ten exact ids, regenerated all three projections, and ratcheted the
reviewed diagnostic reductions. It was not committed, published, ingested, or
deployed:

- object rows: 7,019 to 7,009; location rows remain 753;
- dependency edges: 11,979 to 12,057, adding 78 newly resolvable edges and
  removing none;
- diagnostics: 9,001 to 8,885, a reduction of 116;
- SBC diagnostics: 177 to 98; ambiguous SBC targets: 97 to 20; and
- the remaining 20 ambiguous target records are exactly:

  ```text
  INV-SBC-2 = 13; INV-SBC-4 = 4; INV-ECA-1 = 1;
  INV-PHASE-1 = 1; INV-SHARE-4 = 1
  ```

The two surviving SBC handles remain ambiguous because draft MCAD documents
contain additional definition-shaped restatements. The ECA and SHARE cases are
separate definition-shaped restatements. The phase-local handle has seven
different meanings and requires owner-assigned identity; none is folded into
this decision.

The strict preview tests prove retention of the document and unlisted
definitions, exclusion of both listed-source and listed-target candidates, and
failure on implicit lifecycle, aliases, duplicate list members, missing local
definitions, and duplicate local definitions. The runnable Windows scanner
suite reports 90 passed and 3 deselected; the three excluded cases require
symlink privilege and fail at fixture setup with WinError 1314 on this host.
After the diagnostic-baseline ratchet, `--check-index` reports a clean 7,009 /
753 / 8,885 projection.

A second noncommitting preview replayed the same rule against `a09d18f0f` on
2026-08-28. The 94 predecessor-driven ambiguous targets remained unchanged in
the source projection. The preview moved objects from 7,025 to 7,015, edges
from 12,090 to 12,169, diagnostics from 8,984 to 8,868, SBC diagnostics from
160 to 81, and ambiguous targets from 97 to 20. It retained the predecessor
document, its location, 17 terms, eight gates, four non-goals, one amendment,
and every source byte. Its two focused tests passed; both failed when the
exclusion mechanism was deliberately disabled. The runnable scanner suite
passed 95 tests with the three Windows symlink-privilege cases explicitly
deselected, and `--check-index` reported a clean 7,015 / 753 / 8,868
projection. This remains preview evidence, not implementation evidence.

This preview proves only current-projection behavior. The deployed provider at
`d4780d027` remains available but incomplete with 2,143/31 eligible/resolved
change events, 33,231/11,845 eligible/resolved dependency-edge units, 7,768
historical identity-collision units, 175 history gaps, 109 unlogged object
changes, and 19 unlogged dependency removals. Historical units remain evidence;
this candidate neither erases them nor claims that suspicion becomes
computable.

### Verification

Authority commit `abc768c8ed942a5c2448af5da43f6a5de3a964c1` landed the
ADDENDUM-C and coordinated SIDX-06A/06B/06E amendments plus the exact
predecessor declaration before producer behavior changed.
Implementation commit `8d38ab6734a0cb8c28d9f4824e9d7ce78f1c04f7` then added the
closed declaration parser and current-projection exclusion. It validates the
complete same-document definition set before excluding the listed definition
rows and listed-source or listed-target candidates. Its negative controls fail
on inferred lifecycle, aliases, duplicate members, absent definitions, and
same-document definition collisions.

The two focused implementation tests passed with 96 deselected; both failed
when the exclusion helper was deliberately disabled. The runnable scanner
matrix passed 112 tests with twelve environment-specific cases deselected:
nine Windows symlink-privilege cases and three Windows CRLF bootstrap cases.
Python bytecode compilation, changed-file checks, generated-index drift, and
the diagnostic ratchet passed.

The committed projection contains 7,023 objects, 12,198 edges, 753 locations,
and 8,868 diagnostics across 60 families. Relative to `a09d18f0f`, SBC
diagnostics fell 160 to 81 and ambiguous dependency targets fell 97 to 20. The
remaining records are exactly:

```text
INV-SBC-2 = 13; INV-SBC-4 = 4; INV-ECA-1 = 1;
INV-PHASE-1 = 1; INV-SHARE-4 = 1
```

The predecessor remains projected as one document with its location, seventeen
terms, eight gates, four non-goals, and one amendment. None of its ten listed
historical invariants remains a current definition row. No source byte or
retained projection was rewritten.

The Docker VM was rebuilt from the exact implementation commit by stopping the
stack, building the backend and frontend, starting the stack, and running the
full split-database migration sequence. The live ingest reproduced 7,023
objects, 12,198 edges, 753 locations across 753 documents, 8,868 diagnostics,
and 60 families. Its immutable evidence carrier names the same full commit;
the refreshed scheduler is healthy, and a live SBC C11 query reports
`staleness_state: current` with eight observed work items. The total remains
`uncomputable` only because suspicion coverage reports
`suspicion_inputs_incomplete`. That separately tracked partial-coverage state
is not converted to zero and is not evidence against this exact projection
repair.

### Tracking

This is a C6-era consequence of the earlier ERRATA-003 repair, not a rewrite of
that historical record. `SBC-00-ADDENDUM-C` rev 0.10.0 and coordinated
SIDX-06A/06B/06E amendments ratified the accepted rule before producer code
changed. Authority commit `abc768c8e` and implementation commit `8d38ab673`
close this entry with committed projection, live ingest, and current provider
evidence. The twenty remaining ambiguous targets and the separate
`suspicion_inputs_incomplete` coverage state remain visible for later waves;
this resolution assigns neither identity nor replacement semantics to them.

---

## ERRATA-007 — Positional SBC objects and legacy amendments lack stable endpoint identity

**Status:** 🟢 resolved, first seen 2026-08-22 while classifying the SBC-family
schema-v3 diagnostics at projection commit `e6192bd21`; term remedy ratified
2026-08-23 and implemented at
`664355fb85ccbe7f2adae841fa02a7dfb280ccb7`.

### Symptom

The SBC family carries 189 dependency diagnostics whose invalid endpoint or
owner is an object kind that ADDENDUM-C §4.3.1 deliberately leaves
edge-ineligible:

- 130 invalid targets: 60 terms, 31 gates, 16 non-goals, and 23 legacy
  amendments;
- 59 invalid sources: 6 terms, 12 gates, 1 non-goal, and 40 legacy amendments.

The two SBC `touches_unresolved/unknown` records are the same boundary seen
through amendment metadata: ADDENDUM-D revisions 0.3.0 and 0.4.0 explicitly
name `§7.2`, but a mutable section position is not a global object id. The
producer is correct to preserve the authored text and decline to guess a
target.

This gap is present in the newest C6 authority work itself. All 11 SBC
dependency diagnostics blamed to the 2026-08-08 and 2026-08-09 C6 amendments
are term, gate, or legacy-amendment identity cases. They are not missing
`ChangeKind` or `Touches` facts.

### Root cause

ADDENDUM-C §4.3.1 intentionally registers stable endpoint grammars only for
documents, invariants, open questions, errata, block/compact amendments, and
their rationales. It explicitly keeps current sections, terms, gates,
non-goals, enum values, authority rows, and legacy amendments readable but
positional and edge-ineligible until another Standards Action supplies stable
authored handles.

The limitation is therefore specified, not a parser defect. What is missing is
an owned decision about whether any of those kinds should enter a later
compatibility frontier and how authors allocate their handles.

### Adopted first measure — stable term handles

At projection commit `61825733b`, the 189 dependency diagnostics split into
four independently decidable object-kind populations:

- terms: 66 records (60 targets and 6 sources);
- legacy amendments: 63 records (23 targets and 40 sources);
- gates: 43 records (31 targets and 12 sources); and
- non-goals: 17 records (16 targets and 1 source).

The two positional `§7.2` `Touches` records remain a separate section-identity
question. Legacy amendments are also coupled to ERRATA-005's unresolved
project-event shape. Terms are therefore the largest measured single-kind wave
that is not blocked by that separate contradiction.

The owner accepted the terms-first measure on 2026-08-23. The coordinated
Standards Action in `SBC-00-CONCEPTS.md` rev 0.12.0 and
`SBC-00-ADDENDUM-C.md` rev 0.7.0 registers:

1. exact authored handles `TERM-NNN`, with `NNN` from `001` through `999`;
2. family-owner allocation in monotonically increasing order without reuse;
3. a four-column §3 definition row whose first cell is the handle and whose
   second cell begins with the bold term;
4. canonical compiled identity `<family-key>:TERM-NNN`; and
5. an additive object-schema-v3 compatibility frontier at the first committed
   projection containing explicit handles. Retained historical schema-v3 bytes
   are neither reinterpreted nor backfilled, and support deploys atomically
   across producer, store, query, and consumer layers.

The initial allocation covers exactly the 60 compiled SBC term objects in the
66-record wave: `TERM-001` through `TERM-020` in the current concepts document,
`TERM-021` through `TERM-043` in ADDENDUM-C, and `TERM-044` through `TERM-060`
in the superseded predecessor. The predecessor's visible `Concepts doc (terms
doc)` row never matched the registered legacy definition shape and is not
silently promoted in this wave.

Term numbers carry identity only. This decision does not assert equivalence,
authority, lifecycle, or replacement relationships between terms, and no
definition or relationship text changes. Unmodified legacy three-column rows
remain positional and edge-ineligible.

The remaining legacy-amendment, gate, non-goal, and section populations are
outside this resolution and require separate tracking. Substituting a
containing document or deriving an id from text, path, line, or content is
still prohibited because it would invent a different target.

### Verification

Implementation commit `664355fb85ccbe7f2adae841fa02a7dfb280ccb7`
adds the exact grammar to the producer, store endpoint validator, and C6
historical-definition eligibility path. Positive definition and local-citation,
duplicate-collision, malformed-handle, relocation, and cross-commit fingerprint
fixtures pass. The focused producer block passed 4 tests; the complete scanner
behavior suite passed 84 tests with 3 Windows symlink-privilege tests explicitly
deselected. Running those 3 without the deselection fails only at symlink
creation with Windows error 1314. The complete Spec Index ingest and suspicion
suite passed 131 tests with one Windows SQLite teardown warning. Python bytecode
compilation and `git diff --check` passed; Ruff and Black were not installed in
the configured virtual environment, so no lint or formatter result is claimed.

Reconciliation and regeneration reduced the committed diagnostic baseline from
9,115 to 9,049 records. The entire 66-record delta is in the SBC family, which
moved from 291 to 225 diagnostics: invalid targets fell by 60 and invalid
sources fell by 6. All 60 stable term objects are present, no diagnostic names a
stable term endpoint, and every non-term family count is unchanged. The
generated-index drift gate is clean at 7,003 objects, 11,757 edges, 753 location
records, and 9,049 diagnostics across 60 object families. The separately
reported 96 archive files lacking document ids are unchanged location-coverage
evidence, not term-wave failures.

### Tracking

`EOQ-001-ERRATA-007` was resolved by the owner acceptance recorded in the
coordinated Standards Action. The accepted 66-record term wave is closed by the
implementation and projection evidence above. The legacy-amendment, gate,
non-goal, and section populations are outside that resolution and MUST receive
their own owner decision and coordinated SBC/Spec Index tracking before tooling
changes. ERRATA-005 owns the separate project-event shape contradiction.

---

## ERRATA-008 — Two evidence-complete legacy amendments remain positional

**Status:** 🟢 resolved by owner acceptance on 2026-08-23 and implementation
commit `48c6530193012650efa475e64fcad3046cf3ef91`.
**First seen:** 2026-08-23 while beginning the first post-term SBC burn-down
round at projection commit `fc27ff981`.

### Symptom

The current SBC projection contains 30 amendment objects: seven use the frozen
`<document-id>#amendment:<revision>` identity and 23 retain legacy positional
identities. The legacy rows account for the 63 amendment-identity diagnostics
carried forward from ERRATA-007: 40 invalid sources and 23 invalid targets. Two
additional ambiguous invariant citations share legacy-amendment locators but
belong to the separate superseded-definition collision tracked by ERRATA-006.

Most of the 23 rows cannot be migrated without an owner decision about missing
fields or positional targets. Two rows are different. `SBC-00-CONCEPTS.md`
revisions 0.9.0 and 0.10.0 already author all evidence required for a bounded
migration:

- exact revision, date, author, and ratified-amendment status;
- exact `clarification` change kind;
- exact, globally resolvable invariant targets (`SBC-INV-15`, `SBC-INV-18`,
  and `SBC-INV-20`); and
- the complete existing summary text, including motivation, rejected
  alternatives, and what deliberately did not change.

Those two rows currently produce exactly five diagnostics: three invalid
sources and two invalid targets.

### Root cause

ADDENDUM-D §2.3 permits evidence-backed backfill but deliberately does not
rewrite history automatically. A legacy row remains positional even when its
summary happens to contain field-shaped prose. The producer is correct not to
promote it silently.

ERRATA-005 blocks a uniform migration for draft, ratification-only, and project
event rows, while several semantic amendments still name positional sections
or text terms in `Touches:`. Reformatting those entries would either fabricate
a missing field or expose a different unresolved target. Neither is part of
this candidate.

### Adopted measure

The owner accepted a mechanical migration of only revisions 0.9.0 and 0.10.0
from their five-column legacy rows to ADDENDUM-D's frozen block form:

1. preserve each revision, date, author, and entire summary-cell text exactly;
2. map the authored `Ratified (amendment)` status to the frozen `amended` value;
3. lift the already-authored `Change kind:` and `Touches:` values into their
   standalone fields, relying only on the ratified invariant alias
   normalization;
4. author no new rationale object, because `clarification` does not require one
   and the existing text remains in `Summary:`; and
5. leave the other 21 legacy amendment objects byte-for-byte unchanged.

The coordinated `SBC-00-CONCEPTS.md` 0.13.0 entry records the identity
migration as `semantic`: the normative prose is unchanged, but the compiled
objects become edge-eligible and the dependency graph changes. Its `Touches:`
field names the two resulting canonical amendment ids and
`sbc:ERRATA-008`; it does not claim that any other legacy amendment is
resolved.

### Verification

Implementation commit `48c6530193012650efa475e64fcad3046cf3ef91`
produces the two canonical objects
`SBC-00-CONCEPTS#amendment:0.9.0` and
`SBC-00-CONCEPTS#amendment:0.10.0`. Both retain their exact legacy summary,
author, and date; both declare `clarification`; and their `Touches:` values
contain only the already-authored invariant targets.

Regeneration reduced total diagnostics 9,049 → 9,044, with only `sbc`
changing 225 → 220. Invalid sources fell 53 → 50 and invalid targets fell
70 → 68; every other diagnostic bucket was unchanged. The coordinated 0.13.0
amendment and rationale increased objects 7,005 → 7,007 and the accepted
relationships increased edges 11,772 → 11,800; locations stayed at 753.

The complete scanner behavior suite passed 84 tests with the three Windows
symlink-privilege cases explicitly deselected. The Spec Index ingest and
suspicion suites passed 131 tests; one Windows SQLite teardown warning did not
fail the run. The generated-index drift gate is clean.

An isolated negative control restored revision 0.9.0 to its legacy row and
regenerated 9,047 diagnostics instead of 9,044: one invalid source, one invalid
target, and the expected unresolved 0.13.0 `Touches:` member returned. The
temporary negative-control worktree was then removed.

### Tracking

`EOQ-001-ERRATA-008` is resolved by the owner's acceptance and the
implementation and projection evidence above. ERRATA-005 still owns the
project-event shape contradiction; ERRATA-006 still owns ambiguous predecessor
definitions. Gates, non-goals, sections, and the other 21 amendments remain
outside this resolution.

---

## ERRATA-009 — SBC acceptance gates have no stable C5/C6 endpoint identity

**Status:** 🟢 resolved by owner acceptance on 2026-08-23 and implementation
commit `570d4e60ddad1f2bc301fe6439e47c2f64ffabeb`.
**First seen:** 2026-08-23 while beginning the second post-term SBC burn-down
round at projection commit `ecb0755550b14b6f6d03066c2f19102c0e93b76d`.

### Symptom

The current SBC projection contains 31 positional `gate` objects, all carrying
declared checked state but no authored identity:

| Current carrier | Gate objects | Current definition locators |
|---|---:|---|
| `SBC-00-CONCEPTS.md` | 12 | lines 293–304 |
| `SBC-00-ADDENDUM-C.md` | 11 | lines 717–726 and 729 |
| superseded `SPEC-BEFORE-CODE-CONCEPTS.md` | 8 | lines 222–229 |

Those rows account for exactly 43 invalid dependency records carried forward
from ERRATA-007: 31 invalid targets for their document-definition relations and
12 invalid sources where a gate cites an invariant. Ten additional ambiguous
target records occur at gate locators, but they are invariant-definition
collisions between the current and superseded concepts documents. ERRATA-006,
not this entry, owns those ten records.

At this baseline the complete projection contains 7,007 objects, 11,800 edges,
753 location records, and 9,044 diagnostics. SBC contributes 220 diagnostics:
97 ambiguous targets, 68 invalid targets, 50 invalid sources, three missing
targets, and two unknown `Touches` members.

### Root cause

ADDENDUM-C §4.3.1 explicitly keeps a gate's path/line-derived id readable but
ineligible for `GlobalObjectIdV1`, cross-commit semantic comparison, and C5/C6
edges until another Standards Action registers a stable authored handle.
ADDENDUM-C §5.3 separately registers no checking source kind for `verifies`.
The producer is therefore enforcing the ratified boundary rather than failing
to recognize evidence.

Neither SBC §8 nor ADDENDUM-C §4.3.1 registers a gate handle. Prose labels such
as “Gate (a)” elsewhere in the corpus are not an identifier grammar and do not
allocate unique SBC objects. The accepted `TERM-NNN` frontier is useful
precedent, but it does not authorize copying term identity semantics onto
gates.

### Adopted measure

The owner's acceptance of `EOQ-001-ERRATA-009` adopts the following exact,
coordinated Standards Action:

1. Register authored gate handles as `GATE-NNN`, where `NNN` is exactly three
   ASCII decimal digits from `001` through `999`. The family owner allocates
   monotonically within one family and never reuses a number.
2. Freeze the definition shape as a §12 checklist item whose content begins
   with an inline-code handle followed by space, em dash, space, and nonempty
   gate text: ``- [x] `GATE-001` — <gate text>``. The checklist marker continues
   to own declared checked state. A malformed or unmodified item remains a
   readable positional gate and is never silently promoted.
3. Compile a valid definition as `<family-key>:GATE-NNN`, add `gate` to the
   `GlobalObjectIdV1` eligible-kind table, and recognize the complete local
   handle only inside its owning family. The number conveys identity only.
4. Allocate the existing SBC rows in this exact order, preserving every gate's
   text and checked state:

   | Accepted range | Existing definitions | Allocation order |
   |---|---|---|
   | `GATE-001`…`GATE-012` | current `SBC-00-CONCEPTS.md` | authored source order |
   | `GATE-013`…`GATE-023` | current `SBC-00-ADDENDUM-C.md` | authored source order |
   | `GATE-024`…`GATE-031` | superseded `SPEC-BEFORE-CODE-CONCEPTS.md` | authored source order |

5. Begin an additive object-schema-v3 compatibility frontier at the first
   committed projection containing those explicit handles. Retained historical
   bytes are neither reinterpreted nor backfilled, and producer, store, query,
   and consumer support must deploy atomically.
6. Limit the migration's relationship delta to already-inferred `defines` and
   `cites` edges. It does not infer `blocks` or `verifies` from checklist text,
   invariant citations, or checked state; it does not register `gate` as a
   checking source kind for `verifies`; and it does not resolve ERRATA-006's
   ambiguous invariant targets.

Document-scoped ids, path/line or content-hash ids, invariant ids reused as gate
ids, prose labels such as “Gate (a),” and first-match collision repair remain
rejected. Each would either violate global identity or assert an unowned
relationship.

### Verification

Implementation commit `570d4e60ddad1f2bc301fe6439e47c2f64ffabeb`
adds the exact grammar to the producer, schema-v3 ingest validator, and C6
historical-definition eligibility path. Positive definition and local-citation,
duplicate-collision, malformed-handle, relocation, cross-commit fingerprint,
and family-matching fixtures pass.

Regeneration reduced total diagnostics 9,044 → 9,001, with only `sbc`
changing 220 → 177. Invalid sources fell 50 → 38 and invalid targets fell
68 → 37, accounting for the exact twelve-source and 31-target gate population.
All 97 ambiguous targets, three missing targets, and two unknown `Touches`
members are unchanged. The coordinated authority and implementation commits
increase objects 7,009 → 7,019 and edges 11,817 → 11,980; locations remain at
753.

All 31 stable objects are present as `sbc:GATE-001` through `sbc:GATE-031`, and
their text and checked-state multiset is unchanged from the positional rows.
The final gate edge census is 31 `defines`, 46 `cites`, 23 `amends`, and 23
`motivates`. The identity migration itself contributes the 31 definition edges
and two gate-originated invariant citations. The other 44 citations and the
46 amendment/rationale edges arise from explicit coordinated authority text,
not checklist inference. No `blocks` or `verifies` edge involves a gate, and a
gate remains ineligible as a checking source.

The scanner behavior block passed 88 tests with three Windows
symlink-privilege tests explicitly deselected. The supporting location and
suspicion block passed 17 tests with six Windows symlink-privilege tests
explicitly deselected. The complete Spec Index ingest and suspicion block
passed 137 tests; three Windows SQLite teardown/cache warnings did not fail the
run. Python bytecode compilation and `git diff --check` passed. Ruff and Black
were not installed in the configured virtual environment, so no lint or
formatter result is claimed. After projecting this closure prose, the
generated-index drift gate is clean at 7,019 objects, 11,979 edges, 753
location records, and 9,001 diagnostics across 60 object families. The
separately reported 96 archive files lacking document ids are unchanged
location-coverage evidence, not gate-wave failures.

### Tracking

`EOQ-001-ERRATA-009` is resolved by the owner's acceptance. Coordinated
`SBC-00-CONCEPTS.md` rev 0.14.0 and `SBC-00-ADDENDUM-C.md` rev 0.8.0 amendments
ratify the grammar, allocation, endpoint eligibility, compatibility boundary,
and explicit non-adoption of `verifies` semantics. The accepted 31-record gate
wave is closed by the implementation and committed-projection evidence above.
ERRATA-006 remains the owner of superseded-definition ambiguity. Non-goals,
sections, and the other 21 legacy amendments remain outside this resolution.

---

## ERRATA-010 — SBC non-goals have no stable C5/C6 endpoint identity

**Status:** 🟢 resolved by owner acceptance on 2026-08-23 and implementation
commit `c04187737d83b9eda144067dd97e2e51e96a05cb`.
**First seen:** 2026-08-23 while beginning the next SBC burn-down round at
projection commit `0a44fbf2051d13e8131a043d43c2808ae9333a65`.

### Symptom

At its first-seen baseline, the SBC projection contained 16 positional
`nongoal` objects with no authored identity:

| Current carrier | Non-goal objects | Current definition locators |
|---|---:|---|
| `SBC-00-CONCEPTS.md` | 6 | lines 293–298 |
| `SBC-00-ADDENDUM-C.md` | 6 | lines 717–722 |
| superseded `SPEC-BEFORE-CODE-CONCEPTS.md` | 4 | lines 213–216 |

Those rows account for exactly 17 invalid dependency records carried forward
from ERRATA-007: 16 invalid targets for their document-definition relations and
one invalid source where the second current-concepts non-goal cites this
authored token:

```text
SBC-INV-9
```

That citation also has an ambiguous target because both the replacement and
superseded concepts documents define that handle. ERRATA-006, not this entry,
owns that target collision.

At this baseline the complete projection contains 7,019 objects, 11,981 edges,
753 location records, and 9,001 diagnostics. SBC contributes 177 diagnostics:
97 ambiguous targets, 37 invalid targets, 38 invalid sources, three missing
targets, and two unknown `Touches` members.

### Root cause

ADDENDUM-C §4.3.1 explicitly keeps a non-goal's path-, line-, or text-derived
identity readable but ineligible for `GlobalObjectIdV1`, cross-commit semantic
comparison, and C5/C6 edges until another Standards Action registers a stable
authored handle. The producer is enforcing that ratified boundary rather than
failing to recognize evidence.

Neither SBC §8 nor ADDENDUM-C §4.3.1 registers a non-goal handle. Ordered-list
numbers express presentation order within one document; they are reused across
the three carriers and are not identifiers. The accepted `TERM-NNN` and
`GATE-NNN` frontiers are useful precedent, but neither authorizes copying its
identity semantics onto `nongoal`.

### Adopted measure

The owner accepted `EOQ-001-ERRATA-010` exactly as proposed. Coordinated
`SBC-00-CONCEPTS.md` rev 0.15.0 and `SBC-00-ADDENDUM-C.md` rev 0.9.0 amendments
ratify this Standards Action:

1. Register authored non-goal handles as `NONGOAL-NNN`, where `NNN` is exactly
   three ASCII decimal digits from `001` through `999`. The family owner
   allocates monotonically within one family and never reuses a number.
2. Freeze the definition shape as a §11 ordered-list item whose content begins
   with an inline-code handle followed by space, em dash, space, and the
   existing bold non-goal text: ``1. `NONGOAL-001` — **<non-goal title>.**
   <body>``. The ordered-list number remains presentation only; the handle is
   not part of `nongoal.text`. A malformed or unmodified item remains a
   readable positional non-goal and is never silently promoted.
3. Compile a valid definition as `<family-key>:NONGOAL-NNN`, add `nongoal` to
   the `GlobalObjectIdV1` eligible-kind table, and recognize the complete local
   handle only inside its owning family. The number conveys identity only.
4. Allocate the existing SBC rows in this exact order, preserving every
   non-goal's text:

   | Proposed range | Existing definitions | Allocation order |
   |---|---|---|
   | `NONGOAL-001`…`NONGOAL-006` | current `SBC-00-CONCEPTS.md` | authored source order |
   | `NONGOAL-007`…`NONGOAL-012` | current `SBC-00-ADDENDUM-C.md` | authored source order |
   | `NONGOAL-013`…`NONGOAL-016` | superseded `SPEC-BEFORE-CODE-CONCEPTS.md` | authored source order |

5. Begin an additive object-schema-v3 compatibility frontier at the first
   committed projection containing those explicit handles. Retained historical
   bytes are neither reinterpreted nor backfilled, and producer, store, query,
   and consumer support must deploy atomically.
6. Limit the migration's relationship delta to the closed inference registry.
   It permits the 16 structural `defines` edges and makes the one existing
   invariant citation source eligible, but it does not override that citation's
   still-ambiguous target, add an edge for it, infer equivalence among similar
   current and predecessor text, or infer any new edge kind.

Document-scoped, path/line, content-hash, title-derived, or bare ordered-list
identities and first-match collision repair are rejected by the adopted
measure. Each would either violate global identity or assert an unowned
relationship.

### Noncommitting preview

A disposable preview implemented only the proposed grammar and exact 16-row
allocation against `0a44fbf2051d13e8131a043d43c2808ae9333a65`. It produced:

- total diagnostics 9,001 → 8,984, with only `sbc` changing 177 → 160;
- invalid sources 38 → 37 and invalid targets 37 → 21, accounting for the exact
  one-source and 16-target non-goal population;
- all 97 ambiguous targets, three missing targets, and two unknown `Touches`
  members unchanged;
- objects unchanged at 7,019 and location records unchanged at 753; and
- edges 11,981 → 11,997: exactly 16 new `defines` edges and no new `cites` edge,
  because ERRATA-006 still leaves that cited invariant target ambiguous.

All 16 preview objects retained the exact prior text multiset under the proposed
`sbc:NONGOAL-001` through `sbc:NONGOAL-016` identities. The scanner behavior
suite passed 88 tests; the three remaining cases failed only when Windows
refused test symlink creation with error 1314 before their assertions. Python
bytecode compilation, projection validation, and `git diff --check` passed.

The preview is evidence for the measured consequence, not authorization to
publish the semantics. Its source, authored-handle, and generated changes are
not part of this tracking commit.

### Verification

Implementation commit `c04187737d83b9eda144067dd97e2e51e96a05cb` adds the
exact grammar to the producer, schema-v3 ingest validator, and C6 historical-
definition eligibility path. Positive definition and local-citation, duplicate-
collision, malformed-handle, relocation, cross-commit fingerprint, unrelated-
ordered-prose, and family-matching fixtures pass.

Regeneration reduced total diagnostics 9,001 → 8,984, with only `sbc` changing
177 → 160. Invalid sources fell 38 → 37 and invalid targets fell 37 → 21,
accounting for the exact one-source and sixteen-target non-goal population. All
97 ambiguous targets, three missing targets, and two unknown `Touches` members
are unchanged. Objects increased 7,021 → 7,025 for the two amendment/rationale
pairs; locations remain at 753.

All 16 stable non-goal objects preserve the exact prior text multiset. The
identity migration contributes exactly 16 `defines` edges; its now-eligible
invariant citation remains edge-free because ERRATA-006 still leaves the target
ambiguous. The same coordinated commit's four other `defines`, fourteen
`amends`, fourteen `motivates`, and forty-three `cites` are source-derived
ratification and amendment-history metadata. No `blocks`, `verifies`,
`same-as`, or `homonym-of` semantics were added.

The scanner behavior file passed 93 tests; three Windows symlink-privilege cases
failed with error 1314 before their assertions. The complete Spec Index ingest
and suspicion files passed 142 tests; the only other case was blocked while
reading the worktree manifest by a Windows permission error, and its exact
allowlist assertion passed when rerun directly with Django initialized. Python
bytecode compilation, changed-JSON parsing, generated-index drift, and
`git diff --check` passed. Ruff and Black were not installed in the configured
virtual environment, so no lint or formatter result is claimed.
After projecting this closure prose, the generated-index drift gate is clean at
7,025 objects, 12,090 edges, 753 location records, and 8,984 diagnostics across
60 object families. The separately reported 96 archive files lacking document
ids are unchanged location-coverage evidence, not non-goal-wave failures.

### Tracking

`EOQ-001-ERRATA-010` is resolved by the owner's acceptance. Coordinated
`SBC-00-CONCEPTS.md` rev 0.15.0 and `SBC-00-ADDENDUM-C.md` rev 0.9.0 amendments
ratify the grammar, allocation, endpoint eligibility, compatibility boundary,
preserved text, and explicit non-adoption of equivalence or target-
disambiguation semantics. The accepted 16-record wave is closed by implementation
commit `c04187737d83b9eda144067dd97e2e51e96a05cb` and the committed-projection
evidence above. ERRATA-005 still owns the project-event shape contradiction, and
ERRATA-006 still owns superseded-definition ambiguity. Sections, the other 21
legacy amendments, and the three missing SSV references remain outside this
measure.

---

## ERRATA-011 — Project-event ratification left downstream §15-shape restatements stale

**Status:** 🟢 resolved by merged-lineage clearing commit
`d9e9bad488f0bffc10349aae1a77da86e07d3206` and current live provider
evidence on 2026-08-29.

**First seen:** 2026-08-29 while reviewing the deployed SBC suspicion queue at
projection commit `f32d53be85281d04175981c9b2fda29f241f2aff`.

**Owning phases:** `SBC-00-ADDENDUM-A` rev 0.3.0 and
`SBC-00-ADDENDUM-C` rev 0.10.0, downstream of the ratified
`SBC-00-ADDENDUM-D` rev 0.6.0 project-event authority.

### Symptom

The current deployed provider reports ten active `cites` suspicions across
eight SBC work-item rows. Every finding has the same trigger frontier,
authority commit `c1e8ca4f56da7b37217f8e4a7531c16b68c1bd64`, which ratified
the separate forward-only `EVENT-NNN` project-event record.

Eight citation relationships remain historically or structurally consistent
after review. Two downstream statements cannot be acknowledged unchanged:

1. The operational injection in `SBC-00-ADDENDUM-A` says every §15 entry
   declares a change kind and touched objects. ADDENDUM-D §2.5 instead requires
   a project event to declare neither `Change kind:` nor `Touches:`.
2. `PCDN-SBC-00-C-003` says "both authored forms" remain valid input. After
   project-event ratification, that count is safe only when explicitly scoped
   to the two amendment forms; `EVENT-NNN` is a separate non-amendment form.

The suspicion provider therefore exposed real downstream drift. Clearing all
ten findings without repairing these two statements would certify review while
leaving the reviewed contradiction in the current source.

### Root cause

The authority commit correctly coordinated ADDENDUM-D, ERRATA-005, and the
SIDX-06A producer boundary, but did not propagate the newly explicit
amendment/project-event distinction into ADDENDUM-A's informative injection or
ADDENDUM-C's resolved wording for PCDN-SBC-00-C-003. The parser and provider
behaved as ratified: the semantic upstream changes opened typed suspicions on
their existing dependents rather than assuming that unchanged citations still
meant the same thing.

### Accepted measure

The owner's 2026-08-29 acceptance authorizes this exact clarification and no
broader reinterpretation:

1. Scope ADDENDUM-A's frozen-field statement to amendment entries and cite
   ADDENDUM-D §2.5 for the separate project-event form.
2. Scope PCDN-SBC-00-C-003's two-form statement to amendment forms and state
   that the forward-only project-event form is not an amendment.
3. Preserve all historical ERRATA prose and the ratified project-event grammar,
   enums, parser boundary, legacy-input treatment, and provider confidence
   semantics without change.
4. Record one exact `Clears-Suspect` trailer for each of the ten reviewed
   dependency pairs at trigger commit `c1e8ca4f56da7b37217f8e4a7531c16b68c1bd64`.
   The trailers acknowledge that review only; they do not remove relationships,
   suppress later change events, or convert incomplete coverage into zero.

The corresponding ADDENDUM-A rev 0.4.0 and ADDENDUM-C rev 0.11.0 changes are
`clarification` amendments. Under ADDENDUM-C §8.2, clarification propagates only
across `refines`; it does not silently reopen every `cites` pair repaired here.

### Verification

Before implementation, the signed-in dashboard and direct backend query both
showed projection `f32d53be8` as current with eight loaded SBC rows, ten observed
suspicion findings, and provider reason `suspicion_inputs_incomplete`. The
implementation must regenerate the source-derived index, pass the matching
drift and parser gates, publish the exact trailer-bearing commit, and repeat the
Linux evidence-provider and signed-in dashboard checks. Remaining incomplete
history or identity evidence stays `uncomputable`; this measure cannot assert it
away.

Commit `6d69d346375e0ad6aa993fb143daeffde0ecae56` implemented the accepted
clarification and carried all ten authorized trailers. It subsequently became
one parent of merge commit `25d2cd2edd633ba79bfea12d593c47a473cefd08`,
while the other parent retained the open state. At current projection
`fc6433af03fea118fe31e8b60721905ce6b3f308`, the live provider still reports the
same ten findings and `invalid_clearing_count: 0`. Provider inspection confirms
that a merge preserves an acknowledgment only when every parent that observed
the event carries one. Replaying the same authorized trailers on the merged
lineage is therefore required; it adds no review scope or semantic claim.

Commit `d9e9bad488f0bffc10349aae1a77da86e07d3206` replayed those same ten
trailers on the merged lineage. The docker-vm stack was taken down, the backend
and 8,844-page frontend export were rebuilt, the stack was restarted, and every
split-database migration lane reported no migrations to apply. Evidence refresh
then pinned the carrier head to `d9e9bad488f0bffc10349aae1a77da86e07d3206`,
and ingest produced 7,032 objects, 12,244 edges, 753 locations across 753
documents, 8,868 diagnostics, and 60 object families.

The current direct SBC query reports `staleness_state: current`, provider
availability, zero invalid clearings, zero clearing ambiguities, and no
suspicion evidence on any SBC row. The global provider finding count fell from
35 to 25; the SBC slice contains only this errata entry's deviation record.
Provider confidence correctly remains `uncomputable` with reason
`suspicion_inputs_incomplete`, because unrelated legacy history and identity
coverage gaps remain outside this measure.

### Tracking

The owner explicitly accepted `SBC-ERRATA-011` and authorized clearing the
`c1e8ca4f` review wave on 2026-08-29. No new EOQ is allocated because this
measure propagates the already-ratified ADDENDUM-D §2.5 distinction and adds no
new project-event, amendment, object, edge, or suspicion semantics. The entry is
resolved by the accepted clarification, the merged-lineage replay, and the
current live provider result above.

---

## ERRATA-012 — Two amendments target positional §7.2, which cannot resolve as a C6 endpoint

**Status:** 🟢 resolved, first seen 2026-08-29 while beginning the next SBC
evidence burn-down round at projection commit
`4833da43f6a09b886d820b045b5d0f6b2cc0545e`; the owner accepted the exact
measure and implementation landed at
`5736e95ae766ed0b19c6c9961def910d7e0805b3`.

**Owning authority:** `SBC-00-ADDENDUM-C` §4.1 and §4.3.1 for section object
identity and edge eligibility; `SBC-00-ADDENDUM-D` §2.3, §7.2, and §15 for the
two authored amendment records and their migration boundary.

### Symptom

The current source-derived SBC diagnostic projection contains exactly two
`touches_unresolved/unknown` records:

| Amendment | Authored `Touches` member | Locator | Diagnostic subject |
|---|---|---|---|
| `SBC-00-ADDENDUM-D` 0.3.0 | `§7.2` | `SBC-00-ADDENDUM-D.md:295` | `SBC-00-ADDENDUM-D#amendment:0.3.0` |
| `SBC-00-ADDENDUM-D` 0.4.0 | `§7.2` | `SBC-00-ADDENDUM-D.md:321` | `SBC-00-ADDENDUM-D#amendment:0.4.0` |

Both records have `target_token: null` and `touch_ordinal: 1`. The first
amendment records the status changes to D-C1 and D-C2 while retaining D-C3 as
open; the second records D-C3 closing. Each rationale explicitly says the
amendment touches the §7.2 consumer-conformance status snapshot.

At this baseline the complete committed projection contains 7,032 objects,
12,244 edges, 753 location records, and 8,868 diagnostics across 60 families.
SBC contributes 81 diagnostics: 35 unresolved dependency sources, 44 unresolved
dependency targets, and these two unresolved `Touches` members. The live query
is current at the same commit and returns no open SBC work-item row before this
tracking entry is added; global suspicion confidence remains independently
`uncomputable` for legacy inputs outside this slice.

### Root cause

ADDENDUM-C already registers `section` as an `ObjectKind`, but §4.3.1 keeps
current path-, line-, or text-derived section ids outside `GlobalObjectIdV1`.
They remain ineligible as edge endpoints and `Touches` targets until a Standards
Action registers a stable authored handle. The producer therefore rejects the
positional token `§7.2` rather than deriving identity from its document, ordinal,
title, path, or line.

The source provides enough evidence to identify the intended narrative section,
but not enough authority to choose a canonical object id. `D-C1`, `D-C2`, and
`D-C3` are authored row labels inside that section; they are not registered
objects or an authorization to split either amendment into three new targets.
The two diagnostics are therefore correct evidence, not parser failures.

### Accepted measure — implemented

The owner's acceptance of `EOQ-001-ERRATA-012` adopts the following exact
coordinated Standards Action:

1. Register authored section handles as `SECTION-NNN`, where `NNN` is exactly
   three ASCII decimal digits from `001` through `999`. The family owner
   allocates monotonically within one family and never reuses a number.
2. Freeze a stable definition as a numbered Markdown heading whose authored
   content is `<existing § ordinal>`, one space, an inline-code `SECTION-NNN`
   handle, space, em dash, space, and the existing nonempty title. The exact
   migrated heading is ``### §7.2 `SECTION-001` — Consumer conformance``.
   The `§7.2` ordinal remains presentation and local navigation only; the handle
   is identity and is not part of the section text.
3. Compile a valid definition as `<family-key>:SECTION-NNN`, add `section` to
   the `GlobalObjectIdV1` eligible-kind table, and recognize the complete local
   handle only inside its owning family. The number conveys identity only. An
   unmodified or malformed numbered heading remains positional and ineligible.
4. Allocate only the existing ADDENDUM-D §7.2 section as `SECTION-001`, without
   changing its title, body, D-C1/D-C2/D-C3 labels, obligations, or recorded
   statuses. No other section receives a stable handle in this wave.
5. Backfill only the 0.3.0 and 0.4.0 amendment fields from `Touches: §7.2` to
   `Touches: SECTION-001`. ADDENDUM-D §2.3 permits an explicit backfill; this
   candidate does not reinterpret retained historical projection bytes or
   automatically alias any positional `§<ordinal>` token.
6. Begin an additive object-schema-v3 compatibility frontier at the first
   committed projection containing the handle. Limit the relationship delta to
   the closed existing inference registry: the section's structural `defines`
   edge and the `amends`/`motivates` edges already prescribed for valid authored
   `Touches`. The measure adds no `cites`, `refines`, `blocks`, `verifies`,
   `supersedes`, or checking-source semantics.

Substituting the containing document id is rejected because both rationales say
the change touched only the §7.2 status snapshot. Promoting the three D-C labels
is rejected because it would invent objects and distribute amendment scope that
the authored `Touches` fields do not declare. Automatic ordinal aliases,
path/line/content-hash ids, title-derived ids, and first-match repair are also
rejected. No additional identity or relationship repair is authorized by the
acceptance.

### Verification

The implementation commit passed all 107 scanner tests on Linux. Five focused
scanner tests cover valid, malformed, duplicate, relocated/fingerprint, and
cross-family section behavior. Neutralizing stable-section emission made the
positive test fail on the absent object; restoring the implementation returned
all five to green. Six focused schema-v3 ingest and suspicion tests also passed
on Linux.

Source-derived regeneration and `--check-index` report 7,039 objects, 12,269
edges, 753 location records, and 8,866 diagnostics across 60 families. Against
the accepted baseline, the exact object delta is the section plus the two
coordinated amendment/rationale pairs. The exact edge delta is five `defines`,
four `amends`, and four `motivates`; there are no added `cites` pairs or other
edge types. The location projection is byte-identical.

SBC now contributes 79 diagnostics: the same 35 unresolved dependency sources
and 44 unresolved dependency targets, with zero unresolved `Touches` members.
Normalized diagnostic comparison removes only the two named unknown records.
The D-C1, D-C2, and D-C3 source rows are byte-identical and no D-C object was
created. The diagnostic baseline reconciles downward to 8,866 records without
growing any class.

### Tracking

`EOQ-001-ERRATA-012` is resolved by the owner's acceptance. Coordinated
ADDENDUM-C rev 0.12.0 and ADDENDUM-D rev 0.7.0 amendments ratify the handle
grammar, one-row allocation, endpoint eligibility, exact two-field backfill,
compatibility boundary, and explicit non-adoption of D-C object or new edge
semantics. The implementation commit and exact committed-projection evidence
above resolve this entry. The 79 other SBC diagnostics and all global legacy
provider gaps remain outside this measure.

---

## ERRATA-013 — SBC-00 rev 0.8.0 carried complete amendment evidence but remained positionally identified

**Status:** 🟢 resolved by the owner-authorized precondition migration at
`842d6d70fb5a54556c39cee8c2e62bfe7bb2e148`.

**First seen:** 2026-09-01 while reviewing the next SBC evidence burn-down
slice at projection commit `786b2331b0c508f8f2b392fbf7115e9018257c0a`.

**Owning authority:** `SBC-00-ADDENDUM-C` §4.3.1 for stable global identity and
edge eligibility; `SBC-00-ADDENDUM-D` §2.1–§2.3 for the frozen amendment shape
and explicit legacy migration boundary.

### Symptom

At the parent projection, SBC-00 rev 0.8.0 emitted only the positional object id
`docs/spec-before-code/docs/SBC-00-CONCEPTS.md#0.8.0`. Its legacy-table record
had inferred field provenance, a nonconforming `ratified (amendment)` status,
no declared `ChangeKind` or `Touches`, and no rationale object, even though the
authored row explicitly supplied a semantic change kind, named its targets,
and separated motivation, rejected alternatives, and deliberately unchanged
content.

That row accounted for six `dependency_source_unresolved/invalid` records and
one `dependency_target_unresolved/invalid` record. Its evidence also named
`MCAD ERRATA-013` without a family qualifier. The accepted `EVENT-001`
precondition probe showed that qualifying the cross-family target alone leaves
an invalid positional source; target repair cannot substitute for source
identity.

### Root cause

ADDENDUM-D §2.3 deliberately preserves legacy-table input, but ADDENDUM-C
§4.3.1 admits an amendment as a stable C5/C6 endpoint only when its containing
document, authored revision, and object kind satisfy the registered identity
rules. ERRATA-008 migrated only revs 0.9.0 and 0.10.0 and explicitly withheld
authority for every other legacy row.

The 0.8.0 row nevertheless carried enough authored evidence for one exact
migration. Its textual `ChangeKind` target now has the registered stable handle
`sbc:TERM-035`, and the independently existing MCAD entry resolves globally as
`mcad:ERRATA-013`. No path, line, first-match, or inferred alias is required.

### Accepted measure — implemented

The owner's exact acceptance of `SBC-ERRATA-013 PRECONDITION MIGRATION`
authorized only the following repair:

1. Migrate SBC-00 rev 0.8.0 from its legacy table row to the frozen block form,
   retaining the authored revision, date, author, `semantic` classification,
   summary, and rationale prose.
2. Declare exactly `Touches: SBC-INV-16, sbc:TERM-035`, implementing the
   accepted mapping from the authored `ChangeKind` token without changing
   either target's text or meaning.
3. Qualify only the existing cross-family reference from `MCAD ERRATA-013` to
   `mcad:ERRATA-013`.
4. Split the already-authored motivation, rejected alternatives, and
   deliberately unchanged text into the required rationale sub-block.
5. Leave every other legacy amendment, frozen enum, invariant, scanner rule,
   schema, retained snapshot, baseline class, and clearing state unchanged.

Commit `842d6d70fb5a54556c39cee8c2e62bfe7bb2e148` implements that exact source
migration and no broader legacy backfill.

### Verification

Source-derived regeneration reports 7,051 objects, 12,325 edges, 753 location
records, and 8,859 diagnostics across 60 object families. Relative to the
accepted parent, the positional amendment object is replaced by the stable
`SBC-00-CONCEPTS#amendment:0.8.0` object and its rationale, for a net increase
of one object. The 16 added edges are exactly two `defines`, ten `cites`, two
`amends`, and two `motivates`; no registered edge type is added or changed.

The diagnostic baseline tightens by exactly six invalid sources and one invalid
target, from 8,866 to 8,859 total records. The location projection is unchanged.
All 107 portable scanner tests pass; the three Windows symlink-privilege cases
remain explicitly deselected, and regeneration plus diff checks are clean.

The docker-vm store ingested the same commit atomically with all five snapshots
retained. Operator readback is ready and the shared C11 query reports
`staleness_state: current`. The newly eligible semantic change event opens
three new SBC suspicion findings, leaving four SBC work items with six finding
keys; no clearing act is inferred or performed. Provider confidence remains
`uncomputable` with `suspicion_inputs_incomplete` because unrelated history and
identity gaps remain outside this repair.

### Tracking

No new EOQ is proposed: the owner already supplied the exact migration decision,
and this entry records the defect, bounded implementation, and verification
rather than reopening the semantics. Publishing `sbc:ERRATA-013` would add only
the permanent resolved tracking object and its already-registered citation
relations. It would not authorize clearing the three new suspicion findings or
repairing another legacy amendment.

---

## ERRATA-014 — SBC-00 rev 0.11.0 carried complete amendment evidence but remained positionally identified

**Status:** 🟢 resolved by the owner-authorized precondition migration at
`0a137ea600cb8e140148e5efde2ec4c0738cc718`.

**First seen:** 2026-09-02 while reviewing the next SBC evidence burn-down
slice at projection commit `b0309bfccf3c67cc936235a7197034e24f6f6c78`.

**Owning authority:** `SBC-00-ADDENDUM-C` §4.3.1 for stable global identity and
edge eligibility; `SBC-00-ADDENDUM-D` §2.1–§2.3 for the frozen amendment shape
and explicit legacy migration boundary; the accepted `SECTION-NNN` Standards
Action for stable section allocation.

### Symptom

At the parent projection, SBC-00 rev 0.11.0 emitted only the positional object
id `docs/spec-before-code/docs/SBC-00-CONCEPTS.md#0.11.0`. Its legacy-table
record had inferred field provenance, a nonconforming `ratified (amendment)`
status, no declared `ChangeKind` or `Touches`, and no rationale object, even
though the authored row explicitly supplied a `semantic` change kind, named
§8 identifier grammar and `SBC-INV-15`, and separated motivation, rejected
alternatives, and deliberately unchanged content.

That row accounted for one `dependency_source_unresolved/invalid` record and
one `dependency_target_unresolved/invalid` record. The source was not eligible
for graph relations under its positional amendment identity, and the authored
§8 target had no stable identity of its own. Neither defect could be repaired by
deriving identity from a path, line, ordinal, title, or first match.

### Root cause

ADDENDUM-D §2.3 deliberately preserves legacy-table input, but ADDENDUM-C
§4.3.1 admits an amendment as a stable C5/C6 endpoint only when its containing
document, authored revision, and object kind satisfy the registered identity
rules. ERRATA-008 migrated only revs 0.9.0 and 0.10.0, and ERRATA-013 migrated
only rev 0.8.0; both explicitly withheld authority for every other legacy row.

The 0.11.0 row carried enough authored evidence for one exact migration once
the owner allocated `SECTION-002` to the existing §8 section and authorized the
exact target pair. No new identifier grammar, amendment meaning, relationship
type, or implicit legacy alias was required.

### Accepted measure — implemented

The owner's exact acceptance of `SBC-ERRATA-014 PRECONDITION MIGRATION`
authorized only the following repair:

1. Allocate `SECTION-002` to the existing SBC-00 §8 section without changing
   its ordinal, title, identifier grammar, body, or normative effect.
2. Migrate SBC-00 rev 0.11.0 from its legacy table row to the frozen block form,
   retaining the authored revision, date, author, `semantic` classification,
   summary, and rationale prose.
3. Declare exactly `Touches: SECTION-002, SBC-INV-15`, implementing the accepted
   stable replacement for the authored §8 target without changing either
   target's text or meaning.
4. Split the already-authored motivation, rejected alternatives, and
   deliberately unchanged text into the required rationale sub-block.
5. Leave every other legacy amendment, invariant, scanner rule, schema,
   retained snapshot, baseline class, and clearing state unchanged.

Commit `0a137ea600cb8e140148e5efde2ec4c0738cc718` implements that exact source
migration and no broader legacy backfill.

### Verification

Source-derived regeneration reports 7,054 objects, 12,349 edges, 753 location
records, and 8,857 diagnostics across 60 object families. Relative to the
accepted parent, the positional amendment object is replaced by the stable
`SBC-00-CONCEPTS#amendment:0.11.0` object and its rationale, while §8 gains
`sbc:SECTION-002`, for a net increase of two objects. The nine added edges are
exactly three `defines`, two `cites`, two `amends`, and two `motivates`; no
registered edge type is added or changed.

The diagnostic baseline tightens by exactly one invalid source and one invalid
target, from 8,859 to 8,857 total records. The location projection is
byte-identical. All 107 portable scanner tests pass; the three Windows
symlink-privilege cases remain explicitly deselected, and regeneration plus
diff checks are clean.

The docker-vm store ingested the same commit atomically with all seven snapshots
retained. Operator readback is ready and the shared C11 query reports
`staleness_state: current`. The newly eligible semantic change event opens four
new SBC suspicion findings, leaving six SBC work items with ten finding keys;
no clearing act is inferred or performed. Provider confidence remains
`uncomputable` with `suspicion_inputs_incomplete` because unrelated history and
identity gaps remain outside this repair.

### Tracking

No new EOQ is allocated: the owner already supplied the exact migration
decision, and this entry records the defect, bounded implementation, and
verification rather than reopening the semantics. The owner separately
authorized allocation of this permanent resolved `sbc:ERRATA-014` record at
the deployed migration commit. That allocation does not authorize clearing any
suspicion finding, migrating another legacy row, or changing any object or edge
semantics.

---

## ERRATA-015 — Historical exceptions lack a forward-only clearance contract

**Status:** 🔴 open. The owner agreed to the forward-only policy direction and
authorized this tracking entry; the process contract and its downstream
representation still require decisions and ratification.

**First seen:** 2026-09-03 during the convergence review at committed projection
`2982d08393ec3b8db7eb3fccad5fa43661c5f109`.

**Owning authority:** `SBC-00-ADDENDUM-B` owns errata lifecycle and record shape;
`SBC-00-ADDENDUM-C` owns the object model, baselines, and suspicion;
`SBC-00-ADDENDUM-D` owns amendment and project-event shapes. The parent's
source-of-truth map and invariants remain authoritative. SIDX consumes the
resulting process; it does not invent exception meaning in a query or UI.

### Symptom

The evidence burn-down improves current source without erasing the deficiencies
recorded in earlier snapshots. Between commits `4833da43f` and `2982d0839`,
SBC diagnostics fell from 81 to 70 and legacy amendment objects from 21 to 19
(18 table rows and one predecessor bullet remain). Corpus-wide diagnostics
fell from 8,868 to 8,857. The remaining SBC records comprise 47 invalid
legacy-amendment endpoints, 20 ambiguous targets, and three missing targets.

The 2026-09-03 docker-vm readback at the latter commit reported a current,
operational provider with `suspicion_inputs_incomplete`: six observed SBC work
items and ten uncleared finding keys. Snapshot-wide coverage still included
207 history-gap units and 8,736 commit-qualified identity-collision units.
These are historical counter units, not counts of newly broken SBC objects.

Those results are consistent with the present contract. They do not make the
observed dashboard useless or turn every legacy diagnostic into an operational
failure. However, there is no authored process by which the owner can accept
a bounded historical exception that cannot be repaired forward, retain its
evidence, and have it stop counting as unfinished work in an explicitly
approved operational scope. Treating complete historical computability as the
only finish line therefore misses the owner's intended clean-slate milestone.

### Root cause and existing boundaries

The existing mechanisms have different purposes:

- ADDENDUM-B §1 defines `resolved` as root-caused and fixed, with a resolving
  commit and verification evidence. Its permanent log does not define a
  separate outcome for an approved limitation that remains unfixed.
- ADDENDUM-C §7 defines a named frozen baseline. Naming a snapshot does not
  itself approve every exception in it or reset suspicion coverage.
- ADDENDUM-C §8.3 clears exact dependency-pair trigger frontiers. It is not a
  general disposition for a missing reference, ambiguous identity, or
  historical evidence gap.
- ADDENDUM-D §2.3 preserves legacy input without fabricating absent fields.
  Its §2.4 project events deliberately do not authorize change events or
  suspicion inputs; a narrative event is not an exception-clearance mechanism.
- SIDX-06E §8.1 counts the complete required history and requires the frozen
  defect counters to be zero for complete coverage. SIDX-06B and SIDX-06C
  consume that meaning; they cannot reinterpret it as owner approval.
- The existing source-diagnostic baseline is a no-new-debt ratchet. It is
  neither a member-level exception approval nor a historical counter reset;
  this proposal does not replace or relax that gate.

Immutable committed evidence is the reason not to repair the past in place.
Idempotent regeneration is the requirement that the same authored evidence
and forward decisions reproduce the same result. It is not a reason to avoid
recording a new, authorized disposition.

This is a process-design gap, not a newly executed deviation from ratified
policy. Filing it neither changes the four-value errata lifecycle nor makes
the currently correct provider behavior a bug.

### Agreed direction — not a ratified record grammar

The owner established the following direction in this thread:

1. SBC policy evolves forward. The dashboard records what happened and what
   is planned; it does not rewrite earlier policy or evidence.
2. Repair forward where evidence permits. Where an exception cannot be
   repaired forward, provide an explicit approval and clearance path rather
   than inventing missing semantics or keeping it perpetually unfinished.
3. Distinguish still-open exceptions, verified repairs, and approved
   clearances. Retain the evidence and disposition history for each. A planned
   repair is not completed merely because it has been scheduled.
4. Establish a clean slate within an approved scope, then keep it clean.
   Earlier acceptance is not blanket acceptance of later defects or regressions.
5. Amend the process first, derive its shared-query representation next, and
   then update the dashboard. Preserve historical limitations instead of
   presenting clearance as proof that those limitations never existed.

These are design constraints for the following work. No exception population,
baseline cutoff, machine-readable clearance field, new enum value, changed
confidence rule, or executed clearing act is accepted by this entry.

### Ratified contract boundary — September 5, 2026

The owner accepted the policy packet and then stated that the exact coordinated
amendment packet is RATIFIED in task `01a06eee-bae3-7911-9198-adfae97256f1`.
The accepted patch SHA-256 is
`220d77faff10b8132768a2d0a19ec7e099decf605ad72dd7f57a174f40e69de1`.
The permanent [ratification record](../../plans/sbc-dashboard-review-2026-09-05/ratification.md)
binds its source manifest and the clerical ratification changes.

The parent rev 0.16.0, ADDENDUM-B rev 0.3.0, C rev 0.13.0, D rev 0.8.0,
and coordinated SIDX owners now govern implementation. The three existing
EOQs retain their closure tracking while implementation and required witnesses
remain outstanding. This record approves no individual member or clearing act;
all existing repair statuses and unchecked gates remain unchanged.

### Ratified condition-verification extension — September 13, 2026

The owner ratified the exact condition-verification packet and its linked digest
manifest from commit `7645b24614f181b64ac254b7028367b9f26b6842` in the same task.
The [permanent receipt](../../plans/sbc-dashboard-review-2026-09-05/condition-completion-ratification.md)
binds the actual owner statement, approved artifacts, and resulting source hashes.
The parent rev 0.17.0, ADDENDUM-B rev 0.4.0, C rev 0.14.0, and coordinated SIDX
owners now specify independent recorded verification and supported transitions.
Implementation begins with retained companion projection and strict admission.
This erratum remains open; the ratification confirms no real condition, changes
no native gate, installs no authority pin, and claims no deployed acceptance.

### Proposed work sequence and decisions

**2026-09-05 review clarification — historical applicability.** The owner
directed the review to distinguish process requirements that did not exist or
did not apply at the time from applicable obligations that remain unfulfilled.
This belongs in the existing first two decisions, not a new parallel tracker.
ADDENDUM-D's migration rule already permits legacy forms and does not mandate
rewriting old logs. A retained coverage diagnostic is therefore not, by itself,
proof of a process violation. Conversely, an older unimplemented commitment
does not cease to be outstanding because later process requirements changed.
The review must establish both the governing authority at the relevant act and
any continuing or explicitly adopted migration obligation. An absent formal
ratification date alone does not prove that no operational rule applied.

The bounded [SBC/SIDX inventory and review packet](../../plans/sbc-dashboard-review-2026-09-05/review-and-delivery.md)
records the source population, proposed classifications, parser closure
evidence, and recommended answers to the three existing decisions. Its
candidate process terms remain unratified. No population is cleared and no
current query or confidence meaning changes through this clarification.

**First: amend the SBC process.** Resolve `EOQ-001-ERRATA-015` and
`EOQ-002-ERRATA-015` before implementing exception disposition.

- Prefer extending the existing permanent errata record over creating a
  parallel tracker. Review whether the distinction belongs in lifecycle,
  disposition evidence, or both; do not silently broaden `resolved` to mean
  unfixed-but-approved. Exact values and transitions remain undecided.
- Specify who can approve clearance, the recorded rationale and evidence,
  the exact exception or reviewed set, the applicable policy revision and
  snapshot/baseline, and the effect of that decision on present obligations.
  A bulk approval needs an auditable bounded membership, not a wildcard over
  future findings.
- Define identity and matching across later projections. Existing diagnostic
  keys and locators are evidence, not automatically stable exception handles.
  Decide how persistent accepted debt, a newly introduced defect, a regression,
  a later policy change, and a superseding or withdrawn approval differ.
  Include deterministic handling of duplicate and conflicting decisions.
- Define which inputs can be dispositioned and which still prevent a
  trustworthy evaluation. Approval does not supply an absent reference target,
  select one colliding definition, or repair an invalid evidence carrier.
- Preserve reproducibility and as-of history. The process needs recorded
  forward authority, not database-only state, parser replay over old source,
  deletion of retained diagnostics, or a silent history-frontier reset.
- Route lifecycle/template changes through ADDENDUM-B; baseline/object and
  acknowledgment boundaries through ADDENDUM-C; and any record-shape change
  through ADDENDUM-D. Review the parent source-of-truth map and affected
  invariants before those amendments. Publish only the required coordinated
  Standards Actions, with their own dated amendment and rationale records.

**Second: specify shared derivation and conformance.** After the process
decisions, resolve the representation contract in `EOQ-003-ERRATA-015` through
SIDX-06A/06D/06E for projection and evidence and SIDX-06B for Python, REST, and
MCP parity. Decide how to represent approved operational scope alongside
historical coverage, including all totals, filters, confidence, and invalid or
incomplete disposition inputs. Any change to existing public meanings needs
an explicit compatibility decision. Do not make accepted clearance a valid
historical change event, a resolved dependency edge, or a verified repair by
arithmetic subtraction from the current counters.

**Third: follow with dashboard representation.** Amend SIDX-06 and SIDX-06C
against the accepted shared contract. The intended review separates what is
still open, what is planned, what was repaired and verified, and what was
cleared by approval; it exposes approval scope and retained limitations. Exact
labels, grouping, navigation, and defaults remain design work. The client
continues to render shared meaning rather than owning approval state or
inventing completeness from hidden rows.

The three EOQs above are the tracking handles for this sequence. This entry
does not pre-allocate additional phase, object, enum, or policy identifiers.

### Verification and closure evidence still required

Before closing this process gap, the implementing work needs to demonstrate:

- A verified repair and an approved unfixed exception remain distinguishable,
  and merely proposed or planned work remains open.
- Exact authorized clearance changes only its approved operational scope;
  unlisted defects and later new or regressed problems remain actionable under
  the ratified matching rules.
- Rebuilding the cache and repeating regeneration yield the same disposition
  state, while querying a snapshot before the decision does not import a
  future approval into the past.
- Retained source and projection bytes remain unchanged. Historical gaps stay
  inspectable, and clearance does not fabricate missing identities or evidence.
- Invalid, duplicate, conflicting, revoked, or out-of-scope disposition inputs
  have the deterministic outcomes selected by the process decision, including
  failure tests that cannot pass by silently omitting the affected work.
- Shared Python, REST, and MCP answers agree; the dashboard distinguishes
  observed historical limitations from current approved-scope work and does
  not claim a clean slate when unaccepted in-scope exceptions remain.

No such implementation or acceptance test is claimed by this filing. Source
projection and no-drift checks for the tracking-only change are separate from
proof of the future process.

### Tracking and explicit exclusions

The owner's instruction to start by amending 015 authorizes this permanent
open entry and its decision questions. It is not approval of a specific
clearance record or of the proposed implementation details above.

No existing clearing act, source-diagnostic baseline, provider counter rule,
or confidence rule is modified. Database mutation and deployment are not part
of this filing. A later ingestion of the tracking projection can change the
ordinary history-counter units; that is not exception clearance, and no runtime
result after this filing is claimed here. ADDENDUM-C rev 0.6.0 and every other
legacy amendment stay outside this filing; none receives inferred targets or
fields. No existing resolved erratum is reopened, and none is reclassified as
an approved-but-unfixed exception.

---

## How to add an entry

1. Assign the next `ERRATA-NNN` id (currently: next is `ERRATA-016`).
2. If the entry is a deviation from ratified spec (⚪), file a §15 amendment in the affected
   phase doc in the same commit and cite `ERRATA-NNN` in the commit subject.
3. If the entry is a stealth revert (SBC-INV-7), the errata commit MUST land before the
   reverting fix commit.
4. Add a row to the Index and, if status is ⚪ or 🔴, a row to Open Questions with a stable
   `EOQ-NNN-ERRATA-NNN` handle.
5. Entries are permanent.  On resolution: update status to 🟢, record the resolving commit and
   verification evidence.  Do not delete the entry.
