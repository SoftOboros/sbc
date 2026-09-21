# CLAUDE.md — sbc (Spec Before Code)

## Repository Purpose

Normative home for the Spec-Before-Code planning discipline.  This repo distributes:

- The discipline's concepts doc, frozen enums, and invariants (`SBC-INV-1`…`SBC-INV-14`).
- A portable operational-context injection template (ADDENDUM-A) for adoption in other projects.
- The `ErrataStatus` enum, ERRATA boundary rules, and `ERRATA.md` file template (ADDENDUM-B).
- The errata log for the `sbc` family itself (`docs/SBC-ERRATA.md`).

Supporting code lives in `tools/`, governed by `docs/sbc-tools/`. The owner
approved one repository and adoption submodule on 2026-09-21. Read the SBCT
family before tooling work; production integrations remain downstream.

## Structure

```
docs/SBC-00-CONCEPTS.md      normative authority for the discipline
docs/SBC-00-ADDENDUM-A.md    operational context injection template
docs/SBC-00-ADDENDUM-B.md    ErrataStatus enum; ERRATA boundary rules; ERRATA.md template
docs/SBC-ERRATA.md           errata log for this family
docs/SPEC-BEFORE-CODE-CONCEPTS.md  SUPERSEDED predecessor / input (ERRATA-003) — not normative
templates/ERRATA.md          bare ERRATA.md template for adopters
AGENTS.md                    semantic state variable — read before any authoring turn
```

## Context priming

Read `CLAUDE.md` (this file) and `AGENTS.md` first.  Then load
`docs/SBC-00-CONCEPTS.md` as primary normative context before any authoring task.
Do not derive intent from document structure alone — the concepts doc is the spec.

## Spec-Before-Code Planning Discipline

This section is the operational narrative.  The normative artifact is
[`docs/SBC-00-CONCEPTS.md`](docs/SBC-00-CONCEPTS.md).  If this section and the concepts
doc disagree, that is a bug — amend whichever was wrong and cite the other.  New vocabulary
lands in the concepts doc first via §15 amendment, then propagates here — never the reverse.

### Normative keywords (RFC 2119 / RFC 8174)

The key words **MUST**, **MUST NOT**, **SHALL**, **SHOULD**, **SHOULD NOT**, **MAY**, and
**RECOMMENDED** in all `SBC-*` docs are interpreted per RFC 2119 and RFC 8174 when, and only
when, they appear in capitals.  Lowercase uses are ordinary English.

### Normative vs. informative sections

Sections referenced by a phase doc's §12 Acceptance checklist are **normative**.  All other
sections are **informative**.  This file is informative; `docs/SBC-00-CONCEPTS.md` is normative.

### Conformance targets

A conforming adoption of SBC MUST satisfy all gates in `docs/SBC-00-CONCEPTS.md §12`.
A partial adoption (operational context injection only, without a family `-00-CONCEPTS` doc)
satisfies advisory coverage only; normative coverage requires a ratified concepts doc.
An adopting family's own acceptance list MUST name its conforming artifact (SBC-INV-14).

### Definitions — reference vs. restatement

Every term that also exists in an external standard MUST be cited using one of three phrasings
(SBC-INV-2):

- **"As defined in `<source>`; used without modification."**
- **"As defined in `<source>`; adapted: `<delta>`."**
- **"Owned by `<PHASE>`; does not exist upstream yet."**

Silent restatement is prohibited.

### Frozen enumerations — registration policy

Every frozen enum declares its registration policy.  Values from `docs/SBC-00-CONCEPTS.md §5`:
**Standards Action** / **Specification Required** / **Expert Review**.  Default to Standards
Action when in doubt.

### Phase document shape

§0 authority policy · §1 purpose · §2 problem statement · §3 canonical glossary ·
§4 source-of-truth map · §5–§9 frozen decisions · §10 reconciliation · §11 non-goals ·
§12 acceptance · §13 files cited · §14 unblocks · §15 change log.

Load-bearing sections (MUST appear in every phase): §0, §3/§4, §10, §12, §15.

Reference shape: [`docs/SBC-00-CONCEPTS.md`](docs/SBC-00-CONCEPTS.md).

### Execution discipline

Once a concepts doc is ratified (§15 dated entry, all PCDNs resolved), execution commits:

- Cite the phase as `SBC<NN><letter>` in the commit subject (e.g. `SBC00a:`).
- Name in the PR description which invariants the change touches and how each is preserved.
- A frozen enum or invariant change requires a §15 amendment **first**, in a separate commit.

### Errata log

The `sbc` family errata log lives at [`docs/SBC-ERRATA.md`](docs/SBC-ERRATA.md).
Governed by SBC-INV-7, SBC-INV-10, and `docs/SBC-00-ADDENDUM-B.md`.

Status legend: 🟢 resolved · 🟡 diagnosed · 🔴 open · ⚪ deviation-pending-ratification.

**Stealth-revert prohibition (SBC-INV-7).** Any revert of ratified-and-implemented content
MUST produce: (a) an errata entry filed first at ⚪, (b) a §15 entry in the affected phase
doc citing the errata id, (c) a commit-subject citation of the errata id.  All three required.

### Standards integration — authority boundary declarations

Each externally-authored concept crossing the repo boundary MUST declare an
`AuthorityRelationship` (values in `docs/SBC-00-CONCEPTS.md §6`):
mirror · adapt · extend · compose · own · derive · represent.

Each such concept MUST be recorded with six axes: upstream authority, local representation,
mutation rights, divergence policy, downstream consumers, conformance test owner.

Current declarations for this repo:

| Concept | Upstream | Relationship |
|---|---|---|
| Normative keywords | RFC 2119 / RFC 8174 (IETF) | compose |
| SCXML | W3C | compose |
| git commit / PR mechanics | git | compose |

### Agent context rules (SBC-INV-12)

- Load `docs/SBC-00-CONCEPTS.md` as primary context before any authoring task.
- Review output against the concepts doc before committing.
- Discrepancies MUST be resolved at the spec layer — revise the spec or reject the output.
  They MUST NOT be resolved by silently updating the doc.
- This applies even when the executor is a constrained enterprise model with limited reasoning.
  The invariants are a checklist, not a reasoning task.

### Applicability

Full discipline applies to this repo from its first commit.  There are no informal phases here;
the repo exists to distribute the discipline, so every authoring turn is a governed turn.
