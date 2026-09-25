# SBCT-01 consolidated gate decision packet

**Date:** 2026-09-25
**Status:** Prepared for owner decision; no acceptance recorded.
**Runtime:** `0.1.0.dev34`, revision `9d666f43efe6ffab4c478a97ba199077e611d7de`.
**Evidence checkpoint:** `c8ce3e2` (tests and evidence; runtime unchanged).
**Governing contract:** [SBCT-01](SBCT-01-REPOSITORY-CORE.md) 0.9.1 and
[observation contract](SBCT-01-SUBMODULE-OBSERVATIONS.md) 0.1.3.

**Follow-up evidence:** [Installation reconciliation](SBCT-01-INSTALLATION-REVIEW.md)
adds direct requirements-recipe execution on Windows/Python 3.12.14 and 3.14.6.
The original evidence scope below is retained; no gate recommendation or approval
state changes. The Python 3.11 branch and release environment matrix remain open.

**Latest follow-up:** [Portability and native-link review](SBCT-01-PORTABILITY-REVIEW.md)
now supplies Python 3.11 and WSL Linux execution, native Windows junctions and
native Linux directory symlinks. It adds GATE-102 to the bounded owner review
recommendation, with unexecuted native cases stated explicitly. GATE-101 retains
support-policy reconciliation. Earlier recommendations and decision wording
below describe the original packet; they are not an approval record.

## Proposed disposition

Recommend owner approval of `GATE-103`, `GATE-104` and `GATE-105` against the
identified runtime, source baseline and witnesses below. Keep `GATE-101` and
`GATE-102` open. Their missing evidence prevents full SBCT-01 acceptance even if
the three recommended gates are approved. All five remain unchecked today.

This packet maps the existing gate requirements; it does not amend them or grant
an exception. The owner may accept or return each recommendation separately.
`GATE-106` remains the previously approved specification gate.

| Gate | Recommendation | Basis and remaining limit |
|---|---|---|
| `GATE-101` | Keep open | Installed offline scan/check and import/dependency evidence exist on Windows 11 / Python 3.14.6. Supported Python/platform coverage and final distribution-recipe reconciliation remain. |
| `GATE-102` | Keep open | Empty/missing roots and command rejection are covered, including 60 injected link/reparse cases and six escaping-scope cases with guarded reads and unchanged fixture bytes. Native symlink creation failed with errno 22; native junction behavior is unproven. |
| `GATE-103` | Recommend approval | Exact repeated projection payloads, semantic source-change drift without writes, interrupted file-write preservation and failed selection-switch preservation have witnesses. Random retained directory names are outside projection payload equality; power-loss durability is not established. |
| `GATE-104` | Recommend approval | Committed reads use parent-recorded child history and reject dirty/mismatched clean admission. Observation mode separately retains recorded pins, observed HEADs, local state and incomplete evidence without claiming a clean committed snapshot. |
| `GATE-105` | Recommend approval | Exact pinned producer, wire, document and extraction comparisons pass for the selected profile. Existing portable differences are owned by SBCT-01; no new semantic difference was found in these cases. Public retrieval of authority/source pins remains release work. |

## Evidence identity and execution scope

The [boundary/profile record](evidence/sbct-01-boundary-profile-execution.json)
records 111 core passes and 164 provider tests: 163 passed, one native-symlink
case skipped. Counts include overlapping witnesses and are not separate gate
proofs. The [installed execution record](evidence/sbct-01-installed-mounted-execution.json)
records nine mounted launcher/module envelopes, actual console execution and
offline installation outside the source checkout. These were prior executions;
preparing this packet does not constitute a new runtime test run.

The installed artifact was `sbc_tools-0.1.0.dev34-py3-none-any.whl`, SHA-256
`0561e8b750dc9015b0badeb0b991a46072d957f392938c1465af008b48207996`.
The record pins build/provider wheel hashes and runtime package inventory.
Its environment had no Django, consumer application, application credentials,
Git on PATH or runtime build tooling. Python audit controls reject process and
network access with negative controls; they are not an OS sandbox.

The [import inventory](evidence/sbct-01-core-import-audit.json) hashes 30 runtime
Python modules and finds Dulwich as the only nonstandard-library import root.
This is a static first-party inventory, not a full dependency-source security
audit. Installation evidence remains Windows 11 / Python 3.14.6 with synthetic
fixture approvals, not production authority approval.

## Witness map for the recommended gates

### Deterministic output and retained publication

For `GATE-103`, [console tests](../../tools/tests_git/test_console_host.py)
include `test_repeated_scan_preserves_exact_payload_bytes` and
`test_committed_source_change_reports_drift_without_writing`. The latter
publishes a baseline, commits a semantic source change, and checks for drift
without changing source/output bytes. The installed mounted verifier adds
repetition and dirty child-document drift through the installed launcher.

[Directory publication tests](../../tools/tests/test_directory_store.py)
include `test_interrupted_file_write_never_selects_partial_bundle` and
`test_failed_switch_leaves_prior_selection_usable`.
[Mounted CLI tests](../../tools/tests_git/test_mounted_working_cli.py) add
`test_failed_switch_retains_previous_pointer_and_complete_observation`.
These exercise injected write/switch failures and retained selection, not
machine crashes or power-loss durability. Repetition compares every selected
projection payload byte, not random retention paths or observation metadata
that legitimately changes when checkout evidence changes.

### Committed child history and explicitly labeled observations

For `GATE-104` and named witnesses `W-102-P/N` and `W-103-P/N`:

| Required behavior | Concrete witness |
|---|---|
| Resolve child bytes at the recorded parent pin, retaining child ownership | [Mounted corpus tests](../../tools/tests_git/test_mounted_corpus.py): `test_nested_owner_paths_and_parent_pins_preserved`, `test_uses_pinned_history_despite_changed_child_head`; [generation tests](../../tools/tests_git/test_generation.py): `test_child_documents_generated_from_parent_pinned_bytes`. |
| Reject missing history rather than substitute a checkout HEAD | [Mounted corpus tests](../../tools/tests_git/test_mounted_corpus.py): `test_missing_child_objects_reject`; [observed relationship tests](../../tools/tests_git/test_observed_mounts.py): `test_missing_pinned_history_is_not_replaced_by_observed_head`. |
| Reject dirty or mismatched checkout evidence as clean committed admission | [Admission tests](../../tools/tests_git/test_admission.py), [checkout tests](../../tools/tests_git/test_checkout.py), and [nested checkout tests](../../tools/tests_git/test_checkout_tree.py). |
| Preserve dirty observed bytes without inventing committed identity | [Mounted generation tests](../../tools/tests_git/test_mounted_working_generation.py): `test_dirty_child_generates_v2_comparison_without_commit_claims_or_publication`; installed mounted scan/check envelopes. |
| Distinguish local dirty state, pin mismatch and unavailable descendants | [Local checkout tests](../../tools/tests_git/test_local_checkout.py), [observation-set tests](../../tools/tests/test_observation_sets.py), and [mounted CLI tests](../../tools/tests_git/test_mounted_working_cli.py): missing checkout, unavailable history and blocked descendants. |

Committed corpus reads and clean-checkout admission are distinct operations:
reading valid pinned history does not assert the checkout is clean. Observation
mode uses the configured root ref and each immediate parent's observed HEAD for
nested context, retaining outer pin mismatches. It never substitutes this context
for committed provenance. The approved incomplete-evidence amendment permits
known HEAD with unknown local state/null corpus only in an incomplete result;
missing required evidence produces no partial publication.

### Selected producer profile and owned differences

For `GATE-105`, the selected source commit is
`751ffe62027a3030bc989d22f5c2f759234064dc`. The
[profile reconciliation](SBCT-01-BOUNDARY-AND-PROFILE-REVIEW.md) identifies all
four source blobs and maps the authority role profile `sidx-schema3-location1`
to new projection validation `c6-v3` (object/diagnostic schema 3, location schema 1).

Its execution record reports nine exact full-triple comparisons, five complete
committed reference-source regenerations, five wire fixtures, six document
fixtures, exact parser/location extraction and all 46 validator/helper functions.
These are overlapping checks of bounded fixtures, not exhaustive language proof.
No generated runtime modules or golden fixtures changed during reconciliation.

SBCT-01 owns explicit source routing and repository ownership, mechanical
extraction boundaries, and the approved observation wrapper. Historical malformed
`projection-vectors.json` serialization remains rejection evidence; exact pinned
emitter output in `projection-wire-vectors.json` remains the accepted wire fixture.
That fixture correction does not relax runtime validation or introduce an
alternate semantic parser. New differences require their owning specification
disposition. Query-profile and retained-profile acceptance are separate.

## Work remaining after the proposed decisions

1. For `GATE-101` / `W-101-P/N`, reconcile the Python 3.11 floor and supported
   environments with an explicit execution matrix. Exercise the ordinary-user
   install recipe with hash-selected universal provider wheels, including the
   Python-version conditional dependency path. Package metadata alone does not
   establish CLI provider installation; the explicit requirements recipe matters.
2. For `GATE-102`, run actual native symlink/junction command witnesses in an
   environment that supports their creation, retaining read guards and exact
   no-mutation comparisons. Preserve the current skipped result as historical
   evidence. Do not treat injected metadata as native filesystem proof.
3. Continue the authorized SBCT-02 engine work. `GATE-201` needs identical
   file/Django request-result fixtures; `GATE-202` needs Python/REST/MCP error
   distinctions; `GATE-203` needs projection-only rebuild with auth preservation;
   `GATE-204` needs the full snapshot/filter/cursor/authorization matrix;
   `GATE-205` needs query-core audit and exact historical production-profile
   validation. Existing stores, cursor tests and SBCT-01 fixtures are partial
   evidence and do not close these gates. `GATE-206` remains approved.
4. Follow the [first-release work order](FIRST-RELEASE.md): ratify the exact
   Django/OAuth and dashboard contracts before deriving their implementation,
   then complete the selected release profile. Public source/authority retrieval,
   notices, supported environments and release authorization remain explicit
   release work. SBCT-03 through SBCT-06 remain drafts; optional Interlock remains
   outside the minimum first release.

## Decision text for owner review

Proposed wording, **not an approval record**:

> Approve GATE-103, GATE-104 and GATE-105 for runtime 0.1.0.dev34 at
> 9d666f43efe6ffab4c478a97ba199077e611d7de using this packet's witness map and
> identified source/profile baseline. Keep GATE-101 and GATE-102 open for their
> remaining evidence. This does not approve full SBCT-01 acceptance, SBCT-02
> runtime gates, untested platforms, a release/tag or production adoption.

After an explicit owner decision, record the disposition in SBCT-01 and the
acceptance log with this packet as evidence. Until then, leave normative gate
checkboxes and ratification states unchanged. The next independent work is the
remaining installation-recipe and environment-matrix reconciliation.
