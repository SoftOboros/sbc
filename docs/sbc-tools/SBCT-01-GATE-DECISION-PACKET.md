# SBCT-01 consolidated gate decision packet

**Date:** 2026-09-25
**Status:** Prepared for owner decision; no acceptance recorded.
**Runtime:** `0.1.0.dev34`, revision `9d666f43efe6ffab4c478a97ba199077e611d7de`.
**Evidence checkpoint:** `4def3c6` (latest Windows execution; runtime unchanged).
**Governing contract:** [SBCT-01](SBCT-01-REPOSITORY-CORE.md) 0.9.1 and
[observation contract](SBCT-01-SUBMODULE-OBSERVATIONS.md) 0.1.3.

**Review scope:** Consolidated requirement-to-witness review of the existing
records and selected test/runtime paths. No fresh runtime suite or independent
subagent review is claimed. Historical execution records remain unchanged.

## Proposed disposition

Recommend owner approval of `GATE-101` through `GATE-105` against the identified
runtime, source baseline and witnesses below. All five remain unchecked until
the owner explicitly decides. No new blocking runtime defect was identified in
this limited review; that is not an exhaustive implementation or security audit.

Two review findings are resolved in this informative packet: its main table and
decision text had retained blockers already superseded by later execution; and
its `GATE-101` recommendation conflated the offline installation witness with
the final release support policy. SBCT-01 §5 explicitly assigns the final
supported-version matrix to a release gate. The now-executed ordinary-user
installation/scan/check and dependency boundary support phase acceptance without
asserting support for every platform or every version above the metadata floor.

This packet maps the existing gate requirements; it does not amend them or grant
an exception. The owner may accept or return each recommendation separately.
`GATE-106` remains the previously approved specification gate.

| Gate | Recommendation | Basis and remaining limit |
|---|---|---|
| `GATE-101` | Recommend approval | Exact requirements-recipe installation and offline committed/single/mounted CLI witnesses pass on Windows/Python 3.11.9 and 3.14.6 and WSL Linux/Python 3.12.3; earlier Windows 3.12.14 evidence also exists. Real 3.11 conditional dependency inclusion, pure-wheel guards, exact runtime inventory and the 30-module import audit are recorded. Release support policy remains separate. |
| `GATE-102` | Recommend approval | Literal empty roots, missing roots, malformed configuration and escaping paths have witnesses. Windows now passes all 165 provider tests, including 26 native directory-symlink and 26 junction command cases; Linux directory symlinks also pass. Guards and exact fixture snapshots establish bounded no-read/no-mutation rejection. A separate native file-symlink matrix and hostile concurrent replacement are not proven. |
| `GATE-103` | Recommend approval | Exact repeated projection payloads, semantic source-change drift without writes, interrupted file-write preservation and failed selection-switch preservation have witnesses. Random retained directory names are outside projection payload equality; power-loss durability is not established. |
| `GATE-104` | Recommend approval | Committed reads use parent-recorded child history and reject dirty/mismatched clean admission. Observation mode separately retains recorded pins, observed HEADs, local state and incomplete evidence without claiming a clean committed snapshot. |
| `GATE-105` | Recommend approval | Exact pinned producer, wire, document and extraction comparisons pass for the selected profile. Existing portable differences are owned by SBCT-01; no new semantic difference was found in these cases. Public retrieval of authority/source pins remains release work. |

## Evidence identity and execution scope

| Record | Accepted review input; not owner acceptance |
|---|---|
| [Original boundary/profile execution](evidence/sbct-01-boundary-profile-execution.json) | 111 core passes, earlier provider matrix and exact golden regeneration. Its original symlink skip remains historical. |
| [Recipe execution](evidence/sbct-01-installation-recipe-execution.json) | Direct requirements resolver and installed CLI on Windows/Python 3.12.14 and 3.14.6. |
| [Portability execution](evidence/sbct-01-portability-native-execution.json) | Windows 3.11.9 and WSL Linux 3.12.3 each pass 111 core tests and 164 of 165 provider tests, with one platform-specific skip. Three installed proofs include nine mounted envelopes each and exact artifact/dependency hashes. |
| [Windows native execution](evidence/sbct-01-windows-native-execution.json) | Windows 3.14.6 passes all 165 provider tests after owner-authorized Developer Mode enablement; execution itself uses the ordinary token. |

These counts overlap and are not separate gate proofs. The installed records
identify each `sbc_tools-0.1.0.dev34-py3-none-any.whl` artifact by digest, with
build/provider hashes and exact runtime inventory. Those runtime environments
contain no Django, consumer application, application credentials, Git on PATH or
build tooling. Python audit controls reject process/network access with negative
controls; they are not an OS sandbox. Developer schema tooling remains outside
the installed runtime. The earlier verifier findings and their repairs are
recorded in the [portability review](SBCT-01-PORTABILITY-REVIEW.md).

The [import inventory](evidence/sbct-01-core-import-audit.json) hashes 30 runtime
Python modules and finds Dulwich as the only nonstandard-library import root.
This is a static first-party inventory, not a full dependency-source security
audit. All installed proofs use synthetic fixture approvals, not production
authority approval. Review rechecks confirm these 30 runtime files match the
recorded baseline; documentation and verifier changes did not alter the runtime.

## Witness map for the recommended gates

### Installation and path boundaries

For `GATE-101` / `W-101-P/N`, the
[installed verifier](../../tools/tools/check_installed_distribution.py) builds
and installs outside the source checkout, exercises the actual requirements
recipe and launcher, checks import origin and exact package inventory, and
rejects tampered provider wheels and matching-digest native archive sentinels.
Its ordinary-token Windows and UID-1000 Linux executions provide the positive
runtime witnesses. Python 3.11's bootstrap setuptools is removed from the
disposable runtime, and its required `typing_extensions` is included. Native
schema-test dependencies belong only to the developer process.

For `GATE-102`, [console tests](../../tools/tests_git/test_console_host.py)
exercise literal empty roots, missing configured roots and malformed bindings.
The [command boundary matrix](../../tools/tests_git/test_cli_path_boundaries.py)
guards opens, resolution and descendant metadata while comparing all fixture
file/link contents, including Git metadata and external targets. Injected
`S_IFLNK`/reparse cases include file-input roles; native matrices exercise
directory symlinks/junctions. The linked-component check uses `lstat` and rejects
the link/reparse marker before resolving or opening selected input content.
The lack of a separate native file-symlink matrix is a coverage limit, not an
exception permitting file links. Approval does not relax that rejection rule.

Developer Mode was authorized to create native Windows test fixtures. It is not
required by the SBC runtime, nor does enabling it satisfy an acceptance gate by
itself. The subsequent non-administrator execution provides the witness.

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

1. Record the owner's explicit phase-gate dispositions. No acceptance is inferred
   from this review or from authorization to continue implementation.
2. Under release planning, select the supported interpreter/platform matrix and
   obtain any additional witnesses that selection requires. Executed versions
   are evidence points, not a security/support recommendation. macOS, Python 3.13,
   other architectures and native Linux beyond the tested WSL environment remain
   unexecuted. Preserve native file-symlink coverage as an explicit follow-up;
   do not characterize existing evidence as exhaustive filesystem isolation.
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

> Approve GATE-101 through GATE-105 for runtime 0.1.0.dev34 at
> 9d666f43efe6ffab4c478a97ba199077e611d7de using this packet's witness map and
> identified source/profile baseline. This accepts the reviewed SBCT-01 runtime
> witnesses; it does not approve SBCT-02 runtime gates, a general platform/version
> support policy, a release/tag or production adoption. The stated evidence
> limits do not create exceptions to the ratified contract.

After an explicit owner decision, record the disposition in SBCT-01 and the
acceptance log with this packet as evidence. Until then, leave normative gate
checkboxes and ratification states unchanged. The next implementation work is
the already authorized SBCT-02 engine; final support-policy and release decisions
remain separately reviewable.
