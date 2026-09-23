# AGENTS.md — SBC Supporting Tools

**Document ID:** SBCT-AGENTS
**Owner:** Ira Abbott
**Current state:** 2026-09-22, informative implementation record.

| State | Value |
|---|---|
| Family/prefix | `sbc-tools` / `SBCT` |
| Authoring home | `docs/sbc-tools/` in `SoftOboros/sbc`; package in `tools/` |
| Ratified artifacts | SBCT-00 0.4.2, SBCT-01 0.8.0, SBCT-02 0.6.2 |
| Approved specification gates | GATE-106 and GATE-206; explicit console `--host PATH` |
| Draft phases | SBCT-03 through SBCT-06 |
| Implemented | Committed-source indexing, validation, provenance, CLI, atomic directory publication, SQLite snapshots and cursor codec |
| Latest execution | 98 core and 105 Git/provenance tests; prior 14 schema envelopes and installed-wheel proof |
| Next work | SBCT-01 working-tree observations and acceptance reconciliation; then shared query/provider engine |
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
