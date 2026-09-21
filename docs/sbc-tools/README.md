> Current repository layout: [owner-approved consolidation](REPOSITORY-CONSOLIDATION.md).
> SBC and its tools share one repository; SBCT-00 is now 0.4.2. Earlier progress entries are historical.

# SBCT — SBC Supporting Tools

**Document ID:** SBCT-README
**Status:** SBCT-00 through SBCT-02 RATIFIED 2026-09-19; SBCT-03 through SBCT-06 remain DRAFTS.
**Owner:** Ira Abbott
**Informative:** phase documents own contracts; this file owns navigation only.

This family specifies reusable indexing helpers, shared queries, an optional
Django reference backend, a dashboard, and Interlock composition. It governs
the supporting code separately from the SBC discipline and the SIDX delivery
contracts it consumes. The package/repository working name is `sbc-tools`;
the package and these documents now share the SBC repository. No package release is implied.

The owner requires standalone usability, standard Django human authentication
and minimal MCP OAuth in a bounded example, with production variants maintained
downstream around the public interfaces. Interlock means cross-repository
dependency and governance coordination. Consumer-specific reuse instructions,
source inventories and deployment gates do not belong in this portable doc set.

## Read order and phases

The [console host-binding proposal](SBCT-01-CONSOLE-HOST-PROPOSAL.md) records the approved
explicit `--host` option and data-only registration schema in SBCT-01 0.8.0.
The extension provides no implicit discovery or approval inference.

The [first-release work order](FIRST-RELEASE.md) records the owner's public
prerelease direction and the indexing/dashboard delivery sequence.
The [dashboard host contract](SBCT-04-HOST-CONTRACT.md) is prepared for
GATE-406 review; its interfaces and witnesses remain proposed.

Read [AGENTS.md](AGENTS.md), then the ratified [SBCT-00](SBCT-00-CONCEPTS.md)
revision 0.4.2. SBCT-01 is ratified with approved amendment 0.8.0; SBCT-02 is ratified 0.6.2; SBCT-06 is draft 0.6.0; other child phases are 0.5.0. §8 supplies concrete candidate
contracts and prerequisites for review. Begin with SBCT-01's exact authority/source
baseline and configuration, then SBCT-02's public interfaces. SBCT-01 GATE-106 and parent review gates are complete; implementation
acceptance remains unchecked. GATE-206 was approved 2026-09-20; the active work is SBCT-02 implementation.

| Phase | Owns | Depends on |
|---|---|---|
| [SBCT-00](SBCT-00-CONCEPTS.md) | Family boundaries, glossary, invariants, conformance profiles | SBC and SIDX pinned contracts |
| [SBCT-01](SBCT-01-REPOSITORY-CORE.md) | Configurable scanner, validator, CLI, repository/submodule provenance | SBCT-00 |
| [SBCT-02](SBCT-02-QUERIES-AND-ADAPTERS.md) | Shared queries, snapshot stores, provider interfaces | SBCT-01 |
| [SBCT-03](SBCT-03-DJANGO-REFERENCE.md) | Minimal Django adapter/example, auth and local setup | SBCT-02 |
| [SBCT-04](SBCT-04-DASHBOARD.md) | Reusable client/dashboard and host integration | SBCT-02; SBCT-03 for the local example |
| [SBCT-05](SBCT-05-INTERLOCK.md) | Cross-repository dependency/governance composition | SBCT-02; SBCT-04 for optional UI panels |
| [SBCT-06](SBCT-06-ADOPTION-AND-CONFORMANCE.md) | Standalone conformance, package compatibility, release evidence | Selected profile's phases |

## Conformance targets

SBCT-00 §5 and §12 own the targets. A core distribution uses SBCT-01/02/06;
an MCP example adds SBCT-03; a local dashboard adds SBCT-03/04; Interlock adds SBCT-05.
The Interlock profile is optional. A single-repository installation is useful
and complete without it. These are ratified SBCT profile definitions, not claims that a
partial implementation satisfies every SIDX capability or deployment gate.

## Review order

1. Apply ratified SBCT-00 and its approved decisions/deferrals.
2. Close the baseline and compatibility decisions before extraction.
3. Ratify the applicable phase before deriving supporting code from it.
4. Record evidence against each phase's acceptance gates; publication and
   production rollout are separate from specification ratification.

[ERRATA.md](ERRATA.md) is the permanent family log. Pre-ratification design
decisions remain in SBCT-00 and are not fabricated policy deviations.
Consumer reconnaissance and adoption plans are maintained outside this family.

## Authoring validation and known tooling gap

The initial source check covered all 10 documents, local Markdown links,
sections §0–§15 in all seven phases, unique document/gate IDs, 12 invariant
definitions and one prefix-registry entry. The original 44 acceptance gates remained unchecked at that review. Revision
0.2.0 adds OAuth example witnesses; no acceptance evidence is claimed.
These structural checks are not implementation or ratification evidence.

The current local scanner predates SBC's stable glossary/gate/non-goal forms:
it projects acceptance gates using document path/line identity and does not
extract this family's stable glossary/non-goal definitions. Its generated
dependency diagnostics therefore remain visible. This is part of the recorded
baseline/compatibility decision in SBCT-00 §8; no scanner code, diagnostic
baseline or upstream grammar is changed to make these drafts appear clean.

The [ratification packet](RATIFICATION.md) assembles the approved dispositions,
compatibility policy, observed authority inputs and named witness coverage.

SBCT-01 now proposes exact source candidates and a complete configuration/CLI
contract; its [provider audit](SBCT-01-PROVIDER-AUDIT.md) supplies bounded
pure-Python dependency evidence. Its §8 lists the remaining GATE-106 inputs.

The [SBCT-01 phase review](SBCT-01-REVIEW.md) includes the approved BSD-3-Clause
license choice, source reconciliation, schemas and golden reference evidence.

SBCT-02 §8 records the three accepted review directions. The owner subsequently ratified the phase explicitly; the required contract
contract details were approved under GATE-206 on 2026-09-20. Runtime gates remain open.

The approved [SBCT-02 contract package](SBCT-02-CONTRACT-PACKAGE.md) now provides
typed declarations, JSON schemas, exact query authority pins and 16 executed
reference-producer vectors. Its 28 additional runtime scenarios are specified,
not executed. Structural/digest checks and limited review are recorded in the
package's evidence links. Owner approval under GATE-206 is recorded; runtime acceptance remains outstanding.
