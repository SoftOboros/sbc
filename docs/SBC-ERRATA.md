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

- **EOQ-001-ERRATA-005** — ADDENDUM-D makes `Change kind:` mandatory in the
  frozen block form (§2.1) while §2.4 forbids assigning a `ChangeKind` to a §15
  entry that records a project event. A project event therefore cannot be
  authored in the frozen shape. Which gives: a `project-event` status that
  exempts the field, an explicit `Change kind: none`, or a rule that project
  events stay in the legacy bullet form permanently? See
  [ERRATA-005](#errata-005--a-project-event-cannot-be-authored-in-the-frozen-block-form).

---

## Index

| Id | Title | Status | Phase | First seen |
|---|---|---|---|---|
| ERRATA-001 | `ErrataStatus` enum ownership misrepresented in v0.3.0 changelog | 🟢 | SBC-00 v0.3.0 | 2026-05-31 |
| ERRATA-002 | §4 source-of-truth map collapsed entire errata surface to one row | 🟢 | SBC-00 v0.3.0 | 2026-05-31 |
| ERRATA-003 | Two coexisting concepts docs; `SBC-INV-N` handles rebound; conformance-target invariant dropped; folder layout did not match documented structure | 🟢 | SBC-00 v0.5.0 | 2026-05-31 |
| ERRATA-004 | Family operated for two months on an unratified normative root; every governed family inherited advisory-only coverage | 🟢 | SBC-00 v0.5.0 | 2026-07-31 |
| ERRATA-005 | A project event cannot be authored in the frozen block form — mandatory `Change kind:` contradicts §2.4's prohibition | 🔴 | ADDENDUM-D v0.2.0 | 2026-07-31 |

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

**Status:** 🔴 open, first seen 2026-07-31. Found while authoring a §15 entry in
a consuming family (`CCPS-02`), not by review of ADDENDUM-D itself.

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

### Fix prescription

Owner decision required (`EOQ-001-ERRATA-005`). Three candidates, none adopted:

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

(3) is the smallest change and (1) is the most complete; the author of this entry
has no view strong enough to recommend one, which is why it is an open question
rather than a proposal.

### Verification

Not yet applicable — no fix landed. When one does: author a project-event §15
entry in the chosen shape and confirm `scripts/specidx/scan.py` parses it without
inferring a `ChangeKind` that no one declared.

### Tracking

Encountered in `docs/todo/streamz/cooperative-charger/TODO-CCPS-02-MIXED-FIDELITY-EVIDENCE.md`
§15, where the SIM-039 project-event entry stays in bullet form and the adjacent
INV-MFE-9 amendment uses the block form — the two shapes sitting side by side in
one change log is the symptom made visible. That document's §15 form note cites
this entry.

No normative SBC text is changed by filing this; the resolution will edit
ADDENDUM-D §2.1, §2.4, or §3, at which point that document's §15 becomes the
canonical record (SBC-INV-13) and this entry cites it.

---

## How to add an entry

1. Assign the next `ERRATA-NNN` id (currently: next is `ERRATA-006`).
2. If the entry is a deviation from ratified spec (⚪), file a §15 amendment in the affected
   phase doc in the same commit and cite `ERRATA-NNN` in the commit subject.
3. If the entry is a stealth revert (SBC-INV-7), the errata commit MUST land before the
   reverting fix commit.
4. Add a row to the Index and, if status is ⚪ or 🔴, a row to Open Questions with a stable
   `EOQ-NNN-ERRATA-NNN` handle.
5. Entries are permanent.  On resolution: update status to 🟢, record the resolving commit and
   verification evidence.  Do not delete the entry.
