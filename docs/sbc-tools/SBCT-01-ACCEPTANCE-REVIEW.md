# SBCT-01 implementation acceptance review

**Date:** 2026-09-22
**Status:** Informative review; runtime gates remain open.
**Reviewed revision:** `3317d112bdd44a7b7f127c61fb639104ba049e9c`.

## Recommendation

Continue implementation and focused acceptance work. Do not mark SBCT-01 fully
accepted yet. Specification approval (GATE-106 and the explicit console-host
amendment) is complete; implementation acceptance is a separate determination.
This review maps existing evidence, not a fresh execution of every witness.

## Gate evidence and remaining work

| Gate | Existing evidence | Remaining acceptance work |
|---|---|---|
| GATE-101 | [Consolidation execution](evidence/repository-consolidation-execution.json): 84 core and 94 Git/provenance tests; installed wheel, actual console scan/commit/check, module parity, wrong authority rejection; isolated runtime without Django, application credentials or Git on PATH | Review the complete import/dependency boundary and supported Python/platform matrix. Current installed proof is Windows/Python 3.14.6 with synthetic approvals. |
| GATE-102 | Configuration rejects malformed fields and escaping/overlapping paths; host binding rejects linked inputs; archive and directory readers reject unsafe selections | Add a complete command-level empty-existing-root/missing-root matrix, with explicit out-of-scope-read and source-mutation assertions. Component tests alone do not establish the complete witness. |
| GATE-103 | Immutable generation, exact reference comparison, nonwriting equal check, interrupted publication and failed pointer-switch tests | Add the direct sequence: publish baseline, commit a source change, run check, observe drift and unchanged output bytes. Repeat emission and compare all emitted payload bytes. A deliberately different reference is useful but not this exact source-change sequence. |
| GATE-104 | Child history uses parent gitlinks; missing child objects, dirty descendants and mismatched checkouts reject; generation uses parent-pinned child bytes | Assemble these tests into the named witness mapping. Working-tree observation mode remains unimplemented, so its positive witness is not satisfied. |
| GATE-105 | [Location/archive extraction](evidence/sbct-01-location-archive-execution.json): nine exact full-triple reference cases; [producer regeneration](evidence/sbct-01-producer-regeneration-execution.json): five full pinned-producer cases | Retain bounded fixture claims, reconcile the final selected profile and document every intentional difference. Historical malformed golden serialization remains a rejection witness, not a producer change. |
| GATE-106 | Owner-approved specification, source baseline and CLI binding | Complete as specification approval; no new approval inferred. |

## Named witness gaps

- W-101: the installed-package proof is local. The pure-Python runtime dependency
  claim excludes build-tool launcher resources and the pip-generated console
  executable; no third-party compiled runtime extensions or compiler were used.
- W-102: committed identity and dirty rejection are covered. The positive dirty
  observation report is absent: the verifier currently accepts committed mode only.
- W-103: parent-pinned child history and missing-child rejection have component
  and integration coverage; retain repository ownership in the consolidated evidence.

## Next implementation order

1. Complete the missing root and source-change end-to-end witnesses; fix any
   exposed behavior under the existing SBCT-01 contract.
2. Implement the ratified working-tree observation behavior, preserving its
   distinction from committed evidence; obtain clarification only if the contract
   leaves an authority decision unresolved.
3. Reconcile gate evidence and prepare the bounded acceptance recommendation.
4. Continue SBCT-02 shared queries/providers. Django, dashboard and distribution
   phase implementation still require their respective draft ratifications.

## Evidence handling

Historical execution JSON remains unchanged. Its earlier pending-work statements
refer to the execution date, not the current state. The consolidation test run
proves the relocated package; no runtime suite was rerun for this documentation-only
review. External SIDX source accessibility and public release acceptance remain open.


## Follow-up execution — 2026-09-23

Four added console integration cases execute committed source-change drift with
unchanged source/output bytes, repeated full projection payload equality, a
configured root without Markdown documents, and missing-root rejection without
source/output writes. See [execution evidence](evidence/sbct-01-end-to-end-execution.json).
The root-without-documents case uses a tracked `.keep` file: it is not proof for
a literally empty filesystem directory absent from the committed Git tree.

These cases address the direct source-change/repeat-emission gap in GATE-103
and part of GATE-102. Root escape/symlink out-of-scope-read witnesses and literal
empty-directory semantics still need reconciliation; working-tree observation
mode remains absent. The earlier review table records the state at its review
revision. No gate is closed by this follow-up.


## Configured path boundary repair — 2026-09-23

Configuration now rejects symlink/reparse components before path resolution or
inspection of their descendants. Ten metadata-injected negative cases cover
source roots, nested roots, registry files, authority files and output paths for
both link types. These are deterministic boundary controls, not proof against
concurrent filesystem replacement or native Windows junction creation.

A literal empty existing directory passes configuration validation. Committed
corpus admission still requires the root to appear in committed file ancestry;
an empty directory absent from Git history therefore remains an acceptance gap.
Do not infer GATE-102 closure from the configuration-level positive test.
See [boundary execution](evidence/sbct-01-path-boundary-execution.json).


## Empty-root implementation — 2026-09-23

The registered committed host now accepts a configured existing directory with
zero committed source members. Configuration existence and linked-path checks
run before and after admission. The corpus inventory still reads only committed
files; it does not synthesize directory records or ingest checkout bytes.
The standalone inventory primitive remains strict by default; the host explicitly
enables empty selections after configuration validation. Committed file, symlink
or unmounted gitlink ancestors cannot be treated as empty directories.

Console scan/commit/check succeeds for a literally empty directory without a
marker file. A root removed after host construction rejects, and a committed file
ancestor remains invalid under the empty-root option. This resolves the prior
literal-empty-root implementation gap. It does not close GATE-102 or establish
filesystem race isolation. Working-tree observation mode remains outstanding.
See [execution evidence](evidence/sbct-01-empty-root-execution.json).


## Observation comparison component — 2026-09-23

`tools/src/sbc_tools/observations.py` compares supplied validated candidate and
reference bytes as a single-repository observation. Both commit IDs remain null;
its value type does not carry committed admission or invoke a provenance verifier.
Candidate identity is independent of comparison outcome. Missing/corrupt reference
bytes report unavailable while retaining candidate findings. It performs no file
reads or publication. Five tests and the ratified envelope schema cover this
boundary; see [execution evidence](evidence/sbct-01-observation-comparison-execution.json).

This is a building block, not completed working-tree mode. Safe complete capture,
authority verification, submodule observations, scan publication and CLI host
integration remain required. The default console still rejects working-tree mode.


## Working-tree capture component — 2026-09-23

`capture_working_tree` accepts explicit validated working-tree configuration,
captures source roots and required inputs, and includes authority/registry files.
It rejects configured mounts and nested repositories in this single-repository
slice. Linked components and special files reject before content reads. Open-file
identity is compared with path metadata before reading, and handle metadata is
checked afterward. Two captures must produce identical path/byte mappings.
Windows path/handle change-time differences are handled without dropping identity,
size or modification-time checks. Results contain immutable bytes and corpus
records, with no committed identities or approval claim.

Seven focused tests pass within 98 core tests. See
[capture execution](evidence/sbct-01-working-tree-capture-execution.json).
This is not an atomic snapshot or hostile-filesystem sandbox. Authority verification,
producer composition, submodule observations, publication and CLI integration
remain outstanding; working-tree console mode remains disabled.


## Verified observation generation — 2026-09-23

`generate_working_tree` now composes captured single-repository bytes with exact
registered configuration/profile checks, offline pinned authority verification,
and approved support-patch verification. Generation uses the same configured
producer helper as committed generation; both paths apply complete bundle
semantic validation. The observation result has no committed admission or source
commit. Its validator uses an explicitly rejecting committed-proof provider.

Tests cover dirty-source output and immutable captures, wrong authority pin
rejection before producer invocation, configuration/profile/patch tampering, and
refusal to supply committed proof. No projection is published by generation.
See [execution evidence](evidence/sbct-01-working-generation-execution.json).
CLI integration, observation publication and submodule observations remain open.


## Single-repository observation CLI — 2026-09-23

The explicit host loader now selects working-tree behavior only from registered
configuration. It supports scan publication and comparison to a selected committed
reference using the same validated reference reader and directory publication
primitive as committed mode. Observation results retain null commit IDs. Missing
references retain the observation selection/findings and return unavailable;
failed pointer switches retain prior published selection. Capabilities remain
explicit and authority-pin failures do not publish output.

Five console integration tests cover these behaviors. Submodule observations are
not implemented: configured mounts and nested repositories reject. Working-tree
capture is a bounded two-pass observation, not atomic filesystem isolation.
Historical pending-CLI statements above are superseded for this supported subset.
See [CLI execution evidence](evidence/sbct-01-working-cli-execution.json).
Runtime acceptance gates remain open for final witness reconciliation.


## Approved observation-set validation — 2026-09-23

The owner approved the wire review recommendation, incorporated by SBCT-01 0.9.0.
`observation_sets.py` now builds canonical observation-set bytes and validates
closed fields, identities, sorted ownership, rooted acyclic relations, pin matches,
immediate-parent observed-HEAD context, blocked descendants and selection digests.
Seven new tests pass within 105 core tests; the runtime validator also accepts
the complete and unavailable contract examples. See
[execution evidence](evidence/sbct-01-observation-set-execution.json).

Validation operates on supplied metadata; Git truth, capture stability and host
authorization remain separate obligations. Multi-repository capture and version-2
CLI emission are not yet implemented. No runtime gate is closed.

## Observed relationship collector — 2026-09-24

`observed_mounts.py` implements the approved relationship-context slice using
host-supplied readers and explicit mount/source selections. It retains the root
reference baseline separately from observed HEAD, follows immediate-parent
observed HEAD for nested relations, and preserves outer pin mismatches. Missing
checkouts and unavailable required pinned history block descendants without
accessing their readers. Unregistered included gitlinks and invalid mappings
reject; excluded participants are not inspected.

Eight new real-Git tests cover ordering, divergence, unavailable evidence,
baseline separation, invalid registration and excluded readers. This collector
does not establish physical mount ownership, checkout dirtiness, captured bytes,
aggregate stability or publication. Those remain host/capture integration work;
the CLI still rejects multi-repository observations. No runtime gate is closed.

## Physical ownership and local checkout observation — 2026-09-25

`local_checkout.py` verifies an explicitly supplied checkout location, inspecting
path components before resolving them or reading child HEADs. Identical Git
objects in another checkout do not establish mount ownership. Symlinks/reparse
points, missing boundary evidence and unsupported local evidence yield unknown.

Local checkout checks compare index membership/modes/objects and whole-checkout
file bytes against observed HEAD. Registered child mounts are traversal boundaries:
child HEAD mismatch makes the immediate parent dirty, but dirty child interiors
do not propagate. Untracked files (including ignored files), deletions and staged
changes conservatively count as dirty. Two equal passes retain an internal
evidence digest over local files, index and HEAD context; detected changes reject
the observation even when both passes would independently report dirty.

Eleven new provider tests pass within 129 Git/provenance tests; 105 core tests
also pass. The provider run uses the audited pure wheels and rejects process and
network calls. Tests cover parent/child dirtiness boundaries, wrong physical
ownership, simulated reparse components, unregistered nested checkouts and
content/ref/index changes. Existing committed recursive-clean behavior remains
unchanged. This is bounded change detection, not filesystem isolation.

These internal primitives still require integration with explicit host
registration, relationship collection, aggregate corpus capture and version-2
CLI emission. Their internal evidence digest is not a corpus/selection identity.
No runtime acceptance gate is closed and no release or installed-console proof
is claimed for dev31.

## Mounted aggregate capture — 2026-09-25

Dev32 combines explicit mount context, physical ownership checks and local
checkout observations with repeated source/required-input capture. Root context
is pinned for the operation; the configured reference is checked again before
returning. Nested relations retain immediate-parent observed-HEAD semantics.
Local checkout evidence brackets two captures; changed refs, relationship context,
index/content evidence or captured bytes reject the aggregate.

Successful results contain immutable root-relative files, owning-repository
corpus records and validated complete observation-set bytes. Empty participant
corpora receive the canonical empty-corpus hash. Dirty and mismatched participants
remain valid when stable. Missing participants retain their unavailable/blocked
relationship context in an exception and return no corpus or partial projection.
Filesystem/configuration failures also return no corpus. No publication occurs.

Twelve aggregate tests run within 141 provider tests; 105 core tests also pass.
Coverage includes nested divergence, stable dirty content, owner-relative records,
immutable captures, excluded files and required inputs, unavailable and blocked
participants, wrong physical ownership, ref/content change detection and ordering.
Identical bytes with different HEAD context preserve the corpus hash while changing
the observation-set identity. Provider tests use the audited pure wheels with
process/network audit rejection; they do not prove atomic filesystem isolation.

Authority verification, generation, host registration and version-2 CLI integration
remain pending for mounted observations. The unavailable exception is an internal
context carrier, not yet a complete unavailable wire envelope. Whole-checkout
unknown state remains fail-closed, including additional gitlinks for which no child
evidence is supplied. This record does not close runtime acceptance gates.
