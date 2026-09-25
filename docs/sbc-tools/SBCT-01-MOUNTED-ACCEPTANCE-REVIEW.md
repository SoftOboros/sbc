# SBCT-01 mounted observation acceptance review

**Date:** 2026-09-25
**Status:** Informative implementation review; runtime gates remain open.
**Runtime reviewed:** `9d666f43efe6ffab4c478a97ba199077e611d7de`, package `0.1.0.dev34`.
**Contract:** SBCT-01 0.9.1 / observation contract 0.1.3.

## Result and recommendation

The installed mounted-observation slice has bounded local execution evidence.
Continue acceptance reconciliation; do not declare the entire repository core,
query engine or release accepted from this proof. No new runtime defect was
confirmed by this scoped review. The missing-participant schema gap was already
resolved by the owner's explicit incomplete-evidence amendment.

The extended distribution verifier builds a pure wheel, installs into a disposable
runtime, and invokes the actual console launcher outside the source checkout.
Runtime environment variables are allowlisted, Git is absent from PATH, and
process/network audit controls include negative tests. Fixture setup uses source
helpers in the parent process; installed commands import the built distribution.
The runtime has no Django, consumer application, build tooling or application
credentials. This is not an OS sandbox or proof of all provider source behavior.

See [execution evidence](evidence/sbct-01-installed-mounted-execution.json) and
[first-party import inventory](evidence/sbct-01-core-import-audit.json).

## Confirmed local witnesses

- Installed mounted scan, committed-reference check and module/launcher parity
  produce version-2 results with null committed identities.
- A semantic child-document change causes nonwriting check to report drift;
  source and output file bytes remain unchanged by the check.
- Repeated scans preserve every selected projection payload byte and source bytes.
  Retained bundle directory names and the selection pointer may change by design;
  new untracked output bundles can make the parent's own checkout dirty.
- Missing child checkout and blocked descendants return an incomplete observation
  with null selection/result, known parent HEAD, unknown parent local evidence,
  and no replacement of the existing publication pointer.
- Missing child history remains distinct from a missing checkout. Invalid authority
  returns a safe early error and preserves the previous publication.
- Installed envelopes validate against the approved version-2 schema.

The proof is Windows 11 / Python 3.14.6 with the exact approved provider wheels and
synthetic fixture approvals. It does not extend acceptance to untested platforms,
Python versions, providers, authority baselines or consumer production hosts.

## Remaining gate work

| Gate | Current evidence and next action |
|---|---|
| `GATE-101` | Installed committed, single-source and mounted execution; pure-wheel archive checks; runtime import origin and package inventory; static first-party import inventory. Reconcile the supported Python/platform matrix and final distribution recipe before broad acceptance. |
| `GATE-102` | Prior empty-existing/missing-root CLI cases, metadata-injected link/reparse cases, wrong-location rejection and lazy blocked-reader tests. Complete a command-level path-boundary matrix with explicit no-out-of-scope-read/no-source-mutation assertions; native junction/symlink coverage remains unproven. |
| `GATE-103` | Prior committed drift/interrupted-publication tests plus installed mounted drift and selected-payload repetition. Assemble the named final witness set; directory retention and atomic pointer switching are not crash/power-loss durability proof. |
| `GATE-104` | Prior committed parent-pin and dirty/mismatch rejection tests plus mounted observation ownership, nested observed-parent context and unavailable/blocked handling. Preserve the distinction between committed clean admission and dirty working-tree observation when signing off the witness map. |
| `GATE-105` | Prior pinned producer/location/archive parity fixtures remain evidence. Reconcile the final selected profile, authority/source accessibility and every intentional difference before acceptance; this run did not regenerate golden vectors. |

SBCT-02 runtime acceptance also remains open. In particular, identical Django-store,
REST and MCP request/result witnesses are not supplied by these filesystem/CLI
tests. SBCT-03 through SBCT-06 retain their draft status and separate approvals.

## Review observations

The first drift fixture changed an ordinary heading, which changed captured bytes
without changing the semantic projection. The corrected witness adds a recognized
document ID. The repeat witness compares selected payloads, not randomly named
retained publication directories. Both corrections concern the verifier's expected
results; no runtime source behavior changed during this review.

The next bounded action is the command-level path-boundary witness matrix, followed
by final profile/golden reconciliation and an explicit gate recommendation. No
approval, public release, tag or deployment is inferred from this record.
