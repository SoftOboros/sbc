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
