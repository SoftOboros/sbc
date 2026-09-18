# SBC-00-ADDENDUM-B — ERRATA.md Schema and Injection Template

**Document ID:** SBC-00-ADDENDUM-B
**Status:** RATIFIED (2026-07-31)
**Revision:** 0.2.0
**Date:** 2026-07-31
**Parent:** `docs/SBC-00-CONCEPTS.md`
**Canonical path:** `docs/SBC-00-ADDENDUM-B.md`
**See also:** `docs/SBC-00-ADDENDUM-A.md` (operational context injection)

---

## §0 Purpose

This addendum owns two things deferred from `SBC-00-CONCEPTS.md`:

1. The **`ErrataStatus` frozen enum** — the four-value lifecycle legend for every entry in a
   family's `ERRATA.md`.  Deferred from the concepts doc because it is operational (agents read
   it in `ERRATA.md` on every session) rather than normative (no code path is gated against it
   directly).

2. The **`ERRATA.md` file template** — the verbatim shape a new initiative family copies when
   activating SBC-INV-10.  The template is the artifact; this addendum is the spec for that
   artifact.

The normative rules governing `ERRATA.md` (permanence, location, stealth-revert obligation)
live in `SBC-00-CONCEPTS.md` SBC-INV-7 and SBC-INV-10.  This addendum does not restate them;
it instantiates them into a copyable shape.

---

## §1 Frozen Enum — `ErrataStatus` [Normative]

The lifecycle legend for every entry in a family's `ERRATA.md`.

| Icon | Value | Meaning |
|---|---|---|
| 🟢 | `resolved` | Root-caused and fixed; resolving commit SHA and verification evidence recorded. |
| 🟡 | `diagnosed` | Root cause known; fix prescription clear; no longer needs user input to proceed. |
| 🔴 | `open` | Undiagnosed or unresolved; appears in the Open Questions list. |
| ⚪ | `deviation-pending-ratification` | A deviation from ratified spec (including a structurally-necessary revert) awaiting ratification; appears in the Open Questions list. |

**Lifecycle rules:**

- An entry enters at 🔴 (undiagnosed) or ⚪ (known deviation).
- ⚪ → 🟡 or 🟢 once the deviation is ratified via §15 amendment in the affected phase doc.
- 🔴 → 🟡 once root cause is known.
- 🟡 → 🟢 once the fix lands and verification evidence is recorded.
- **Entries are permanent.**  A 🟢 entry stays in the log; status transitions, the entry is
  never deleted.  The log is institutional memory, not a queue.
- A question leaves the Open Questions list when its entry reaches 🟢 or 🟡.

**Registration policy: Standards Action.**  Adding, removing, or renaming a value requires a
§4 amendment to this addendum and a ratification session.

---

## §2 ERRATA vs. Adjacent Artifacts [Normative]

Two boundaries that MUST be maintained explicitly:

**ERRATA vs. issue tracker.**  The issue tracker is the outward-facing intake surface.
Once an issue is *accepted* (root cause identified or deviation scope agreed), the canonical
record moves into the family's `ERRATA.md`.  Never-accepted reports (duplicates, won't-fix,
out-of-scope) stay in the tracker only.  The log is curated, not a mirror of every report.

**ERRATA vs. phase §15.**  A §15 amendment changes spec text.  An errata entry records the
*evidence* that motivated the amendment, or records a bug that did not require a spec amendment.
Both MAY reference each other; neither replaces the other.

- Resolution edits a normative section of a `-NN-CONCEPTS.md` → §15 entry is canonical;
  errata entry cites the §15.
- Resolution edits code / tests / non-normative docs → errata entry is canonical;
  §15 entry cites the errata id if a spec touch was incidental.

---

## §3 ERRATA.md File Template

Copy everything between the `<!-- ERRATA-TEMPLATE-BEGIN -->` and `<!-- ERRATA-TEMPLATE-END -->`
markers into `<INITIATIVE_DOCS_ROOT>/<FAMILY>/ERRATA.md`.  Replace every `<PLACEHOLDER>`.
Delete the "How to add" footer if you prefer a separate contributing guide.

---

<!-- ERRATA-TEMPLATE-BEGIN -->

# ERRATA — `<FAMILY>`

**Family:** `<FAMILY>`
**Phase docs:** `<INITIATIVE_DOCS_ROOT>/<FAMILY>/`
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

*One line per ⚪ or 🔴 entry; remove when entry reaches 🟢 or 🟡.*

| EOQ id | Errata | Ask |
|---|---|---|
| *(none)* | — | — |

---

## Index

| Id | Title | Status | Phase | First seen |
|---|---|---|---|---|
| *(none)* | — | — | — | — |

---

<!-- ============================================================ -->
<!-- ENTRY TEMPLATE — copy this block for each new entry         -->
<!-- ============================================================ -->

<!--
## ERRATA-001 — <one-line title>

**Status:** 🔴 open
**First seen:** YYYY-MM-DD
**Owning phase:** `<INITIATIVE>-<NN>` (`<phase doc path>`)
**EOQ:** `EOQ-001-ERRATA-001` — <one-line open question>

### Symptom

<What the observer sees.  Pin to artifact path and line where possible.>

### Root cause

<Mechanism.  "Unknown" until diagnosed.>

### Fix

<Proposed location and minimal change sketch.  Resolving commit SHA once landed.>

### Verification

<How to confirm the fix is correct.  Evidence recorded once resolved.>

### Tracking

<Cross-references: related phase §15 entries, related EOQ ids, related commits.>
-->

<!-- ============================================================ -->

---

## How to add an entry

1. Assign the next monotonically-increasing `ERRATA-NNN` id.
2. If the entry is a deviation from ratified spec, set status ⚪ and file a §15 amendment in
   the affected phase doc in the same commit.  Cite `ERRATA-NNN` in the commit subject.
3. If the entry is a stealth revert (SBC-INV-7), the errata commit MUST land first, before
   the reverting fix commit.
4. Add a row to the Index table and, if status is ⚪ or 🔴, a row to Open Questions with a
   stable `EOQ-NNN-<ERRATA-id>` handle.
5. Entries are permanent.  On resolution: update status to 🟢, record the resolving commit SHA
   and verification evidence in the Fix and Verification fields, remove from Open Questions.
   Do not delete the entry.

<!-- ERRATA-TEMPLATE-END -->

---

## §4 Change Log

| Rev | Date | Author | Status | Summary |
|---|---|---|---|---|
| 0.1.0 | 2026-05-31 | I. Abbott | DRAFT | Initial draft; `ErrataStatus` frozen here (deferred from SBC-00-CONCEPTS); ERRATA vs §15 / tracker boundary; copyable file template |
| 0.2.0 | 2026-07-31 | I. Abbott (ratifier) | **Ratified** | Ratification only — no content change. Closes the gap recorded in ERRATA-004, where this addendum sat DRAFT while `ErrataStatus` and the ERRATA/§15 boundary were in active use across 28 errata logs and 220 entries. Ratified at existing content. **No amendment follows:** the ERRATA↔§15 boundary (SBC-INV-13) and the four-value `ErrataStatus` lifecycle are unaffected by the `SBC-00-CONCEPTS.md` 0.7.0 object-model amendment — an `errata` is one `ObjectKind` among twelve and its lifecycle rules were already the most fully specified surface in the family. Recording that nothing changed here is itself the finding: the object model generalised over the existing errata shape without modifying it. |
