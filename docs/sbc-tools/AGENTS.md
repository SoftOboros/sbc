# AGENTS.md — SBC Supporting Tools

**Document ID:** SBCT-AGENTS
**Owner:** Ira Abbott
**Current state:** 2026-09-25, informative implementation record.

| State | Value |
|---|---|
| Family/prefix | `sbc-tools` / `SBCT` |
| Authoring home | `docs/sbc-tools/` in `SoftOboros/sbc`; package in `tools/` |
| Ratified artifacts | SBCT-00 0.4.2, SBCT-01 0.9.1, SBCT-02 0.6.2 |
| Approved specification gates | GATE-106 and GATE-206; explicit console `--host PATH` |
| Draft phases | SBCT-03 through SBCT-06 |
| Implemented | Committed-source indexing, single/mounted working-tree CLI, validation, provenance, atomic publication, SQLite snapshots and cursor codec |
| Latest execution | Windows/Python 3.14.6: all 165 provider tests pass after authorized Developer Mode enablement, including 26 native symlink and 26 junction command cases; earlier core/install/Linux evidence retained |
| Next work | Owner gate/support-scope review; remaining selected-platform witnesses and authorized SBCT-02 query-engine work |
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

Dev31 adds physical checkout-location verification and local dirty-state
observation. Dirty child interiors do not propagate to parents; child HEAD
mismatches do. Unknown evidence stays distinct from dirty state. Aggregate
capture and CLI integration remain pending; acceptance gates remain open.

Dev32 integrates the internal mounted capture path and emits validated complete
observation-set metadata with immutable captured bytes. Failures produce no
corpus and retain relationship context. Host/generation/CLI integration and
unavailable version-2 envelope framing remain pending; no gate is closed.

Dev33 adds authority-verified mounted generation through the shared producer and
data-only version-2 comparison with participant corpus-hash binding. Console host
integration and missing-participant/incomplete-observation results remain pending.

Dev34 implements mounted working-tree scan/check through explicit host bindings.
Registered source readers open lazily in relationship order; missing participants
and blocked descendants produce incomplete v2 results with no publication. The
owner approved known HEAD with unknown local evidence in incomplete observations
in [the amendment review](SBCT-01-INCOMPLETE-OBSERVATION-REVIEW.md), incorporated
by SBCT-01 0.9.1 / observation contract 0.1.3. Prior pending-CLI notes are historical.
No runtime acceptance gate or release is approved by this implementation record.

The [installed mounted acceptance review](SBCT-01-MOUNTED-ACCEPTANCE-REVIEW.md)
records successful actual-launcher execution and the remaining gate matrix.
Dev34 runtime source is unchanged by that review. Its distribution verifier now
covers mounted repeat/drift, missing/blocked evidence and retained publication.
Windows/Python 3.14.6 remains the executed installation boundary; other platform
and Python combinations are not established by this evidence.

The [boundary/profile reconciliation](SBCT-01-BOUNDARY-AND-PROFILE-REVIEW.md)
records 60 injected link/reparse and six escaping-scope command cases, exact
pinned regeneration, and the remaining native-link/platform limits. Runtime
source remains dev34. No gate, exception or new compatibility profile is approved.

The [consolidated gate decision packet](SBCT-01-GATE-DECISION-PACKET.md)
recommends owner approval of GATE-103/104/105 and retaining GATE-101/102 open.
It maps concrete witnesses and remaining work; no owner disposition is recorded.

The [installation reconciliation](SBCT-01-INSTALLATION-REVIEW.md) extends the
verifier to execute the unchanged requirements recipe and conditional dependency
resolution on two existing interpreters. Tampered-wheel and native archive guard
negative controls pass. Runtime remains dev34; GATE-101/102 remain open.

The [portability/native-link review](SBCT-01-PORTABILITY-REVIEW.md) adds actual
Python 3.11 conditional inclusion, ordinary-user WSL Linux execution, 26 native
Windows junction cases and 26 native Linux directory-symlink cases. It repairs
verification-only POSIX fixture and audit-hook issues. GATE-102 is now included
in the bounded owner review recommendation; no acceptance is recorded.

The owner authorized Windows Developer Mode; the
[Windows follow-up](evidence/sbct-01-windows-native-execution.json) now executes
the previously skipped directory-symlink matrix under a non-administrator token.
Developer Mode remains enabled. This is fixture-creation setup, not a new SBC
runtime installation requirement. Gate approvals remain unchanged.
