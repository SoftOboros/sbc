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

---

## How to add an entry

1. Assign the next `ERRATA-NNN` id.
2. If the entry is a deviation from ratified spec (⚪), file a §15 amendment in the affected
   phase doc in the same commit and cite `ERRATA-NNN` in the commit subject.
3. If the entry is a stealth revert (SBC-INV-7), the errata commit MUST land before the
   reverting fix commit.
4. Add a row to the Index and, if ⚪ or 🔴, a row to Open Questions with a stable
   `EOQ-NNN-ERRATA-NNN` handle.
5. On resolution: update status to 🟢, record the resolving commit and verification evidence.
   Do not delete the entry.
