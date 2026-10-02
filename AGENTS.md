# AGENTS.md — sbc (Spec Before Code)

**Semantic state variable.**  Read this before any authoring turn.  Update this when phase
status changes.  This file is the answer to "where are we?" — not a README.

---

## Current state

| Item | Value |
|---|---|
| Family | `sbc` |
| Active phase | `SBC-00` (Concepts) |
| Phase status | RATIFIED; ERRATA-015 implementation and closure remain outstanding |
| Canonical concepts doc | `docs/SBC-00-CONCEPTS.md` rev 0.17.0 |
| Ratification evidence | Owner exact-packet ratifications on September 5 and September 13, 2026 in task `01a06eee-bae3-7911-9198-adfae97256f1`; each owner records its amendment |
| Open errata | ERRATA-015; ERRATA-001 through 014 remain resolved |
| Next action | Implement the ratified ERRATA-015 contracts in SIDX, then collect complete parity and browser closure evidence |

## Artifact inventory

| Artifact | Rev | Status |
|---|---|---|
| `docs/SBC-00-CONCEPTS.md` | 0.17.0 | RATIFIED |
| `docs/SBC-00-ADDENDUM-A.md` | 0.4.0 | RATIFIED |
| `docs/SBC-00-ADDENDUM-B.md` | 0.4.0 | RATIFIED |
| `docs/SBC-00-ADDENDUM-C.md` | 0.15.0 | RATIFIED |
| `docs/SBC-00-ADDENDUM-D.md` | 0.8.0 | RATIFIED |
| `docs/SBC-ERRATA.md` | living log | 15 entries; 015 remains open |
| `templates/ERRATA.md` | extracted form | Mirrors the new assessment section pointer in ADDENDUM-B |

## Ratification and execution boundary

The former draft-0.5 context and its checklist were stale. The actual dated
owner amendments govern; this context update does not check acceptance gates
or infer that operational process was absent before formal ratification.
Review the current owner acceptance sections and ERRATA-015 closure criteria.
A ratified policy does not approve an individual exception population, install
an approval pin, clear suspicion, or prove implementation or deployment.
The September 13 condition-verification extension is ratified; companion
projection, independent verification admission, transitions, and C13 version 2
remain implementation work. Its exact receipt is retained in
[original receipt](https://github.com/iraabbott/softoboros.com/blob/2808f9bd1c9a85f6ea049a1cd7675ab7d79778e2/docs/plans/sbc-dashboard-review-2026-09-05/condition-completion-ratification.md).

---

## Agent instructions

**Authoring turns.**  Load `docs/SBC-00-CONCEPTS.md` as primary context.  Output MUST be
reviewed against the concepts doc before committing.  Any discrepancy is resolved at the spec
layer — revise the spec or reject the output (SBC-INV-12).

**Ratification turns.**  Work through the current owning document acceptance checklist line by line.  Each checked item
is a commit.  PCDNs are resolved with the human as the serialisation point — do not ratify
unilaterally.

**Errata turns.**  New errata entries go to `docs/SBC-ERRATA.md`.  If the entry is a deviation
(⚪), the §15 amendment in the affected phase doc lands in the same commit.  Commit subject
cites `ERRATA-NNN` (SBC-INV-7).

**Supporting tools.** Owner-approved consolidation on 2026-09-21 places supporting
code in `tools/` and its governing SBCT family in `docs/sbc-tools/`. Read that
family before tooling work; its approvals and acceptance gates remain separate.
Generated tooling modules must be changed through their generators. Discipline
reconciliation does not update SBCT authority pins or authorize unfinished tooling.

The September 16 exact C14 retained-source packet is ratified. ADDENDUM-C
registers source inspection; SIDX owns delivery and implementation. Receipt:
[original receipt](https://github.com/iraabbott/softoboros.com/blob/2808f9bd1c9a85f6ea049a1cd7675ab7d79778e2/docs/plans/sbc-dashboard-review-2026-09-05/retained-source-navigation-ratification.json).
This adds no repair, exception, verification, deployment, or native checklist completion.

## October 2 source reconciliation

The [reconciliation record](docs/reconciliation/2026-10-02/README.md) imports
existing ratified discipline and historical metadata from the pinned dashboard
source. It changes no native acceptance state, SBCT approval hash, runtime
approval pin, or deployment status. Preserve original source-relative links in
transported documents; use the record for standalone navigation. SBCT state
continues to be owned by [its context](docs/sbc-tools/AGENTS.md).
