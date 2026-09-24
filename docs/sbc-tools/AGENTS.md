# AGENTS.md — SBC Supporting Tools

**Document ID:** SBCT-AGENTS
**Owner:** Ira Abbott
**Current state:** 2026-09-24, informative implementation record.

| State | Value |
|---|---|
| Family/prefix | `sbc-tools` / `SBCT` |
| Authoring home | `docs/sbc-tools/` in `SoftOboros/sbc`; package in `tools/` |
| Ratified artifacts | SBCT-00 0.4.2, SBCT-01 0.9.0, SBCT-02 0.6.2 |
| Approved specification gates | GATE-106 and GATE-206; explicit console `--host PATH` |
| Draft phases | SBCT-03 through SBCT-06 |
| Implemented | Committed-source indexing and single-repository working-tree CLI, validation, provenance, atomic publication, SQLite snapshots and cursor codec |
| Latest execution | 105 core tests and 118 Git/provenance tests; prior 15 schema envelopes and installed console proof |
| Next work | Integrate observed relationship collector with physical ownership, local dirty-state observation and aggregate capture, then version-2 CLI |
| Acceptance | GATE-101–105 and GATE-201–205 remain open |
| Publication | Unified prerelease on `main`; no release tag |

Read [README](README.md), [SBCT-00](SBCT-00-CONCEPTS.md), and the owning phase
before implementation. The [acceptance review](SBCT-01-ACCEPTANCE-REVIEW.md)
maps evidence and gaps. [Consolidation execution](evidence/repository-consolidation-execution.json)
records the latest relocated test run. Older execution records remain historical.

The owner approved one repository and adoption submodule in the
[consolidation amendment](REPOSITORY-CONSOLIDATION.md). Preserve discipline and
SBCT semantic ownership within that repository. Do not modify normative SBC
rules simply to accommodate tooling. Preserve unrelated consumer workspace work.
Generated modules must be changed through their generators.

Keep specification ratification, runtime acceptance, publication and production
adoption separate. Hashes and supplied host bindings do not infer approval.
Do not mark gates complete from test counts alone. SBCT-03/04/05/06 remain drafts.

The public backend scope is a bounded example with standard Django human auth
and minimal MCP OAuth. Production identity, policy, credentials and deployment
remain downstream. Shared semantic behavior must not be forked by a host.
First-party licensing is BSD-3-Clause. Example maintenance and eventual support
status remain explicit release decisions.


The owner approved the first-version submodule observation boundaries. The exact
[draft contract](SBCT-01-SUBMODULE-OBSERVATIONS.md) proposes nested context and wire
versioning; it is not a ratified extension or completed runtime implementation.
Current runtime still rejects submodule observations.


The nested observation context review point was accepted on 2026-09-23. Pin
mismatch is a known work-in-progress condition to be exposed by future indexing
helpers, preserving recorded pin and observed HEAD. See the owner disposition in
[the observation contract](SBCT-01-SUBMODULE-OBSERVATIONS.md).

[Observation wire approval packet](SBCT-01-OBSERVATION-WIRE-REVIEW.md) is ready for owner review; no wire approval or runtime acceptance is inferred.

Observation wire packet 0.1.2 is approved by the owner and incorporated in SBCT-01 0.9.0. Earlier pending-review notes are historical. Runtime acceptance remains open.

The dev30 relationship collector implements explicit topology, recorded pins,
observed HEAD context and unavailable/blocked participants. This is an internal
context layer, not a complete observation set or multi-repository CLI support.
