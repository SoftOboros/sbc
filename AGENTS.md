# AGENTS.md — sbc (Spec Before Code)

**Semantic state variable.**  Read this before any authoring turn.  Update this when phase
status changes.  This file is the answer to "where are we?" — not a README.

---

## Current state

| Item | Value |
|---|---|
| Family | `sbc` |
| Active phase | `SBC-00` (Concepts) |
| Phase status | DRAFT — pending ratification |
| Canonical concepts doc | `docs/SBC-00-CONCEPTS.md` (rev 0.5.0). `docs/SPEC-BEFORE-CODE-CONCEPTS.md` is its SUPERSEDED predecessor — ERRATA-003. |
| Ratified artifacts | none yet (the predecessor's self-declared "ratified" status applied to the in-repo narrative, not this portable family) |
| Open errata | none (ERRATA-001…003 resolved) |
| Next action | Ratification review of `docs/SBC-00-CONCEPTS.md` rev 0.5.0 |

---

## Artifact inventory

| Artifact | Rev | Status |
|---|---|---|
| `docs/SBC-00-CONCEPTS.md` | 0.5.0 | DRAFT — canonical |
| `docs/SBC-00-ADDENDUM-A.md` | 0.1.0 | DRAFT |
| `docs/SBC-00-ADDENDUM-B.md` | 0.1.0 | DRAFT |
| `docs/SPEC-BEFORE-CODE-CONCEPTS.md` | — | SUPERSEDED predecessor (ERRATA-003); retained as institutional memory |
| `docs/SBC-ERRATA.md` | — | living log; 3 entries, all 🟢 |
| `templates/ERRATA.md` | — | extracted from ADDENDUM-B §3 |

---

## Ratification gate (SBC-00)

The following MUST be true before `SBC-00-CONCEPTS.md` moves to RATIFIED:

- [ ] All §12 acceptance checklist items checked
- [ ] `SBC-00-ADDENDUM-A.md` §12 acceptance checklist checked (if present — confirm)
- [ ] `SBC-00-ADDENDUM-B.md` §4 change log has ratification entry
- [x] `docs/SBC-ERRATA.md` cited in `SBC-00-CONCEPTS.md §13` files cited
- [x] `templates/ERRATA.md` extracted from ADDENDUM-B §3 and committed
- [ ] `AGENTS.md` updated to reflect RATIFIED status
- [ ] §15 change log entry in concepts doc records ratification with reviewer and date

---

## Known gaps at current rev

These are not errata (no ratified spec has been violated); they are pre-ratification work items.

| Item | Location | Notes |
|---|---|---|
| ADDENDUM-A and ADDENDUM-B have no §12 acceptance checklist | both addenda | Addenda inherit parent; confirm or add before ratification |
| `templates/ERRATA.md` is a hand-edited copy of ADDENDUM-B §3, not a literal extraction | `templates/ERRATA.md` vs ADDENDUM-B §3 | Two copies of one artifact can drift (the fork failure mode). Make one the source, or note the intentional delta. |

> Resolved since last rev: `SBC-ERRATA.md` now cited in `SBC-00-CONCEPTS.md §13`; `templates/ERRATA.md`
> extracted; folder layout (`docs/`, `templates/`) now matches the documented structure (all via ERRATA-003).

---

## Agent instructions

**Authoring turns.**  Load `docs/SBC-00-CONCEPTS.md` as primary context.  Output MUST be
reviewed against the concepts doc before committing.  Any discrepancy is resolved at the spec
layer — revise the spec or reject the output (SBC-INV-12).

**Ratification turns.**  Work through the §12 checklist above line by line.  Each checked item
is a commit.  PCDNs are resolved with the human as the serialisation point — do not ratify
unilaterally.

**Errata turns.**  New errata entries go to `docs/SBC-ERRATA.md`.  If the entry is a deviation
(⚪), the §15 amendment in the affected phase doc lands in the same commit.  Commit subject
cites `ERRATA-NNN` (SBC-INV-7).

**What this repo does not contain.**  No executable code.  No migrations.  No generated
artifacts.  If an authoring turn produces code, that is a conformance failure — stop and check
the concepts doc.
