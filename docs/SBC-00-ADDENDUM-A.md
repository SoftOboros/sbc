# SBC-00-ADDENDUM-A — Operational Context Injection Template

**Document ID:** SBC-00-ADDENDUM-A
**Status:** RATIFIED (2026-07-31)
**Revision:** 0.3.0
**Date:** 2026-07-31
**Parent:** `docs/SBC-00-CONCEPTS.md`
**Canonical path:** `docs/SBC-00-ADDENDUM-A.md`

---

## §0 Purpose

This addendum is a **prompt injection template**: the verbatim text to paste into a project's
operational context document (`CLAUDE.md` or equivalent) to activate SBC governance for that
project.  It is the informative complement to the normative `SBC-00-CONCEPTS.md`; where the
concepts doc defines *what the rules are*, this addendum defines *how to load them into an
agent session*.

**How to use.**  Copy the fenced block below into your project's operational context document.
Replace every `<PLACEHOLDER>` with project-specific values.  Delete placeholder lines whose
features you are not activating.  The injected text is informative in the operational context
(narrative); `SBC-00-CONCEPTS.md` is the normative artifact.  If the two ever diverge, that
is a bug — file it and amend whichever was wrong.

**What this is not.**  This is not a substitute for `SBC-00-CONCEPTS.md`.  Agents that load
only the operational context have advisory coverage; agents that also load `SBC-00-CONCEPTS.md`
have normative coverage with stable `SBC-INV-N` handles.

---

## §1 Injectable Text

Paste everything between the `<!-- SBC-INJECT-BEGIN -->` and `<!-- SBC-INJECT-END -->` markers
into the operational context document.  The markers themselves are optional; include them if you
want a machine-parseable boundary.

---

<!-- SBC-INJECT-BEGIN -->

## Spec-Before-Code Planning Discipline

Multi-phase initiatives under `<INITIATIVE_DOCS_ROOT>/` follow a standards-body-style planning
cycle: every behaviour change is preceded by a ratified *concepts* doc.  Vocabulary drift and
invariant erosion are the dominant failure modes once a plan crosses ~3 phases; the cycle exists
to prevent silent forks, not as ceremony.

The normative artifact for this discipline is
[`docs/SBC-00-CONCEPTS.md`](docs/SBC-00-CONCEPTS.md).  This section is the informative
narrative.  If this section and `SBC-00-CONCEPTS.md` disagree, that is a bug — amend whichever
was wrong and cite the other.

### Normative keywords (RFC 2119 / RFC 8174)

The key words **MUST**, **MUST NOT**, **SHALL**, **SHOULD**, **SHOULD NOT**, **MAY**, and
**RECOMMENDED** in all initiative-family TODO docs and per-phase concepts docs are interpreted
per RFC 2119 and RFC 8174.  Use capitals when invoking the keyword; lowercase for ordinary
English.  Plain narrative without capitalised keywords is advisory, not binding.

### Normative vs. informative sections

In a per-phase `<PREFIX>-NN-CONCEPTS.md`:

- Sections referenced by the phase's **Acceptance** checklist are **normative** — binding on
  implementers.
- All other sections (problem statement, narrative, non-goals, change log) are **informative**.
- The initiative README entry for a phase is **informative**; the per-phase doc is the normative
  artifact.

Do not re-derive normative rules in README narrative — cite the per-phase doc and section number.

### Conformance targets

Initiative-level acceptance lists in each initiative README MUST name the conforming artifact
(e.g. "a conforming `<INITIATIVE>` deployment MUST satisfy gates (a)–(d)").  Optional phases
yield a second conformance level ("a conforming deployment without `<INITIATIVE>-<NN>` satisfies
gates (a)–(c)").  This lets reviewers reason about partial deployments without re-arguing scope.

### Definitions — reference vs. restatement

For every term that also exists in this project or an external standard, the glossary entry MUST
cite the authoritative source and mark the relationship using exactly one of these three phrasings:

- **"As defined in `<source>`; used without modification."** — source is canonical; this doc
  references it.
- **"As defined in `<source>`; adapted: `<delta>`."** — source is canonical; this doc extends or
  narrows it with a named delta.
- **"Owned by `<PHASE>`; does not exist upstream yet."** — this doc is canonical; upstream will
  mirror once the phase lands.

Silent restatement of an existing definition is how forks form.  Do not do it.

### Frozen enumerations — registration policy

Every frozen enum (claim class, mode, budget disposition, etc.) declares its registration policy
in the concepts doc, using values from `SBC-00-CONCEPTS.md §5`:

- **Standards Action** — adding a value requires a §15 amendment to the `-00-CONCEPTS` doc and a
  ratification session.  Use for enums encoding invariants or cross-phase contracts.
- **Specification Required** — adding a value requires a phase-owner walkthrough update; no
  CONCEPTS amendment.  Use for enums local to one phase's contract surface.
- **Expert Review** — phase owner MAY add a value with a PR-level note.  Use for internal enums
  with no cross-phase coupling.

Default to Standards Action when in doubt; demote later if churn justifies.

### Phase document shape

A per-phase concepts doc follows this section layout:

§0 authority policy · §1 purpose · §2 problem statement (evidence, pinned to artifacts) ·
§3 canonical glossary · §4 source-of-truth map (one owner per concept) · §5–§9 frozen decisions
(enums, invariants) · §10 reconciliation decisions vs. adjacent primitives · §11 non-goals ·
§12 acceptance checklist · §13 files cited · §14 unblocks · §15 change log.

Phases beyond `-00` MAY omit sections that do not apply; §0, §3/§4, §10, §12, §15 are
load-bearing and MUST appear in every phase.

See `<REFERENCE_FAMILY_00_CONCEPTS_PATH>` as the reference shape.

### Execution discipline

Once a concepts doc is ratified (§15 dated entry, all PCDNs resolved), execution commits:

- Cite the phase as `<INITIATIVE><NN><letter>` in the commit subject
  (e.g. `<FOO>02a:`, `<BAR>03b:`).
- Name in the PR description which invariants (from §9 of the concepts doc) the change touches,
  and how each is preserved.
- Touching a frozen enum value or an invariant requires a §15 amendment **first**, in a separate
  commit.  No behaviour commit rides on an unamended invariant.

### Errata logs

Every spec family running this discipline MUST maintain a living `ERRATA.md`:

- **Location**: alongside the family's phase docs (`<INITIATIVE_DOCS_ROOT>/<FAMILY>/ERRATA.md`).
- **Shape**: status legend (🟢 resolved / 🟡 diagnosed / 🔴 open / ⚪ deviation-pending-ratification),
  Open Questions section with stable `EOQ-NNN-<ERRATA-id>` handles, index table, per-entry
  sections (Symptom / Root cause / Fix / Verification / Tracking).  Entries are permanent —
  resolved entries stay in the log as institutional memory.
- **When to add an entry**: known issues, execution deviations from ratified spec, pre-existing
  bugs surfaced during a phase, and **stealth reverts** (see below).

**Stealth-revert prohibition (SBC-INV-7).**  A behaviour change that undoes ratified-and-implemented
phase content while landing under an unrelated commit's scope is a stealth revert and is
prohibited.  If a revert is structurally necessary: (a) file an `ERRATA` entry first, in a
separate commit, with status ⚪; (b) land the unrelated fix citing the `ERRATA-NNN` id in the
commit subject; (c) add a dated §15 entry in the affected phase doc pointing at the errata id.
All three parts are required.  This makes stealth reverts impossible by construction — every
revert produces an errata entry, a §15 entry, and a commit-subject citation.

### Standards integration — authority boundary declarations

When a phase doc integrates an externally-authored grammar (IETF, ISO, W3C, SMPTE, IEEE, vendor
APIs that act as de-facto standards), citing the spec is not enough.  Each externally-authored
concept that crosses the project boundary MUST declare an `AuthorityRelationship` (values from
`SBC-00-CONCEPTS.md §6`):

| Value | Meaning |
|---|---|
| **mirror** | Copy verbatim; no local divergence. |
| **adapt** | Copy verbatim; add named local affordances that MUST NOT leak across the upstream wire boundary. |
| **extend** | Add named local fields/values on an unchanged upstream grammar, in a declared namespace. |
| **compose** | Use upstream terms as components of a higher-level construct this project owns. |
| **own** | This project authors the grammar; full mutation rights gated by this discipline. |
| **derive** | Interpret/evaluate against upstream without owning it; outputs local, inputs upstream. |
| **represent** | Visualise the upstream grammar; display semantics local, payload round-trip preserves upstream names. |

Each external-grammar concept MUST be recorded as a row with six axes: **upstream authority**,
**local representation**, **mutation rights**, **divergence policy**, **downstream consumers**,
**conformance test owner**.  An undeclared local mirror reads as `mirror` with no mutation rights
— never silently as `own`.  Promoting a row to `own` requires an explicit §15 amendment.

The failure mode this prevents: *"we copied it into our schema, therefore we own it."*

### Agent context rules

When an AI agent participates in any SBC phase (SBC-INV-12):

- The agent MUST receive the ratified spec as primary context, not the existing code.
- Agent output MUST be reviewed against the spec before committing.
- Discrepancies between agent output and spec MUST be resolved at the spec layer — revise the
  spec or reject the output.  They MUST NOT be resolved by silently updating the code.

### Identifier hygiene

Every family prefix MUST be registered with a named owner before use and MUST be globally
unique across the corpus (`SBC-00-CONCEPTS.md` §8).  An id MUST resolve identically whether its
document is in-repo, archived, or handed off to a retrieval tier — so a prefix scoped to a single
*document* rather than a *family* is a conformance failure, not a shorthand.  Ids canonicalise
with an unpadded number: `INV-FOO-01`, `INV-FOO-1`, and `FOO-INV-1` are one object.

Every spec object has exactly one definition site (SBC-INV-15).  Restating an id in bold at the
head of a table cell, list item, or heading in a second document creates a second definition site
and is prohibited — cite it instead, using one of the three phrasings above.

An invariant that contains no capitalised RFC 2119 keyword binds nothing, whatever section it sits
in (SBC-INV-16).  Write **MUST**, not "must".

### Change logs and rationale

The §15 change-log shape is frozen in `SBC-00-ADDENDUM-D.md`.  Each entry declares a revision,
date, author, status, **change kind**, and the object ids it **touches**.  Amendments whose change
kind is `semantic`, `scope`, or `retirement` MUST carry a rationale block recording what was
considered and rejected, what the failure mode would have been, and what deliberately did not
change (SBC-INV-17).

The last of those is the one most often lost and the most valuable on re-read: "this generalised
without modification" is a load-bearing claim about the design's stability, and it is unrecoverable
from a diff.

### Tooling that reads the corpus

Any compiled store built over the corpus — index, database, graph, embedding set — MUST be
derivable from the authored documents plus a declared parser plus version-control history
(SBC-INV-18).  **Markdown is source; the store is a cache.**  The single class of fact that is not
derivable — a human clearing a suspicion — is recorded as a version-control commit trailer, not as
a row in the store.  Details: `SBC-00-ADDENDUM-C.md`.

### Applicability

This discipline applies to any initiative family that produces a `-NN-CONCEPTS` gate.
Single-doc TODOs and phase-1 prototypes MAY use informal form; the moment a family produces
a `-00-CONCEPTS` doc, the full discipline applies to that family.

<!-- SBC-INJECT-END -->

---

## §2 Customisation Reference

| Placeholder | Replace with | Notes |
|---|---|---|
| `<INITIATIVE_DOCS_ROOT>` | Path to initiative docs (e.g. `docs/todo`) | |
| `<FAMILY>` | Initiative family name (e.g. `semantic-servo`) | |
| `<INITIATIVE>` | Short initiative identifier (e.g. `SSV`, `FOO`) | Used in phase codes |
| `<PREFIX>` | Phase doc filename prefix (e.g. `TODO-FOO`) | |
| `<NN>` | Two-digit phase index | |
| `<REFERENCE_FAMILY_00_CONCEPTS_PATH>` | Path to an existing ratified `-00-CONCEPTS` as reference shape | Omit line if none yet exists |
| `<FOO>`, `<BAR>` | Concrete phase code examples for your project | e.g. `SSV02a`, `SE03b` |

Lines referencing features not yet activated (errata logs, parallel-agent workflow, bench
authorisation) MAY be omitted from the initial injection and added via a §15 amendment to
this addendum when the feature is activated.

---

## §3 Files Cited

| File | Role |
|---|---|
| `docs/SBC-00-CONCEPTS.md` | Parent normative document |
| `docs/SBC-00-ADDENDUM-A.md` | This document |

---

## §4 Change Log

| Rev | Date | Author | Status | Summary |
|---|---|---|---|---|
| 0.1.0 | 2026-05-31 | I. Abbott | DRAFT | Initial draft; anonymised from project operational context; all family/path references parameterised |
| 0.2.0 | 2026-07-31 | I. Abbott (ratifier) | **Ratified** | Ratification only — no content change. Closes the gap recorded in ERRATA-004, where this addendum sat DRAFT while the discipline it injects was in continuous force. Ratified at existing content; the material accumulated since lands separately at 0.3.0. |
| 0.3.0 | 2026-07-31 | I. Abbott (ratifier) | **Ratified (amendment)** | **Injection-template amendment** propagating `SBC-00-CONCEPTS.md` 0.7.0 into the injectable block, per §0's rule that new vocabulary lands in the concepts doc first and propagates here — never the reverse. Adds three subsections: *Identifier hygiene* (global prefix uniqueness with a named owner, unpadded canonicalisation, one definition site per object, and the capitalisation gate — SBC-INV-15/16); *Change logs and rationale* (frozen §15 shape, `Touches:`, and the rationale obligation — SBC-INV-17); *Tooling that reads the corpus* (the compilation rule and the commit-trailer carve-out — SBC-INV-18). Each cites its owning document rather than restating it, per SBC-INV-2 — this addendum is informative narrative and must not become a second normative surface. Adopting projects re-paste the block to pick these up; the `<!-- SBC-INJECT-* -->` markers make the boundary machine-findable for a diff. |
