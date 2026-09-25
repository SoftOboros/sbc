# SBCT-01 installation recipe and environment reconciliation

**Date:** 2026-09-25
**Status:** Informative execution evidence; acceptance gates remain open.
**Runtime:** `0.1.0.dev34`, revision `9d666f43efe6ffab4c478a97ba199077e611d7de`.
**Contract:** SBCT-01 0.9.1 §5/§8 and named witnesses `W-101-P/N`.

**Follow-up:** The [portability review](SBCT-01-PORTABILITY-REVIEW.md) adds actual
Python 3.11 and WSL Linux execution and native directory-link witnesses. The
ledger below retains its earlier scope; consult that review for current evidence.

## Result

The documented hash-constrained provider recipe now has installed CLI evidence
on Windows 11 with Python 3.12.14 and 3.14.6. Both runs passed the committed,
single-source and mounted observation witnesses, including nine mounted schema
envelopes each. See [the execution record](evidence/sbct-01-installation-recipe-execution.json)
and [installation instructions](../../tools/INSTALLATION.md).

The Python 3.12.14 core suite passed all 111 tests. Its provider suite ran 164
tests: 163 passed and the native directory-symlink witness was skipped because
creation returned errno 22. The earlier Python 3.14 core/provider results are
retained separately; only its installed recipe/CLI proof was rerun here.

The previous verifier installed every provider wheel directly with dependencies
disabled. That established execution with approved bytes, but did not exercise
the requirements file's resolver or interpreter marker. The extended verifier
installs through the unchanged `requirements-git.txt`, checks the exact resulting
package inventory, and runs `pip check`. Both tested interpreters correctly omit
`typing_extensions`; Dulwich and urllib3 remain at their approved versions.
The Python 3.11 conditional inclusion branch is not yet executed.

An explicit developer-only `--python` selects the existing interpreter for the
disposable builder and runtime. Identity in the report comes from that target
runtime. Fixture preparation and JSON Schema validation stay in the parent
developer process; installed commands use only the built distribution and
resolved runtime dependencies. The interpreter installations are not modified.

## Installation and failure witnesses

- Each run creates separate disposable builder/runtime environments, uses only
  local hash-verified build/provider wheels and builds without network access.
  Repository commands have no Git executable on PATH or application credentials.
- Before provider installation, a copied Dulwich wheel is altered while retaining
  the original requirements hash. Pip rejects it specifically for a hash mismatch;
  the runtime package inventory stays unchanged. The original wheel cache is not
  modified.
- Synthetic archives with `.pyd` and `.so` members are rejected even when their
  supplied digest matches. This proves the archive guard is independent of hash
  mismatch rejection; the sentinel members are not executable native extensions.
- The successful resolver inventory contains only pip, SBC, Dulwich and urllib3.
  Build/schema/framework packages do not enter the runtime. Process/network audit
  negative controls and the prior installed CLI witnesses still pass.

The existing import inventory hashes were checked against all 30 current runtime
modules. This change affects the verification harness and documentation only;
no runtime version bump or semantic amendment is needed. The two built wheel
digests identify the executed artifacts, not reproducible-wheel-byte acceptance.
No claim of system-wide privilege isolation follows from local virtual environments.

## Environment evidence ledger

This is an execution ledger, not an approved support policy. SBCT-01 names a
Python 3.11 floor; the final supported-version matrix remains a release decision.
An unexecuted entry is neither accepted nor silently removed from that decision.

| Python | Windows 11 | Linux | macOS |
|---|---|---|---|
| 3.11 | Not run; interpreter unavailable in the inspected local/runtime inventory | Not run | Not run |
| 3.12 | 3.12.14: recipe and installed CLI passed; core/provider suite result in execution record | Not run | Not run |
| 3.13 | Not run; interpreter unavailable in the inspected local/runtime inventory | Not run | Not run |
| 3.14 | 3.14.6: recipe and installed CLI passed; earlier core/provider evidence retained | Not run | Not run |

The new interpreter is an existing bundled CPython runtime; no Python download,
OS package, compiler or administrator installation was used. The exact Windows
build, interpreter patch versions and pip versions are in the execution record.
The ledger does not extrapolate to other architectures or future interpreters.

## Gate disposition and next work

`GATE-101` remains open. The direct recipe/resolver gap is now covered on the two
executed interpreters, but Python 3.11 conditional inclusion, the release support
matrix and non-Windows execution remain unresolved. Reusing this verifier on
explicitly selected environments is the next witness; a simulated marker result
would not substitute for execution on Python 3.11.

`GATE-102` still needs native symlink/junction evidence. Installation coverage
cannot substitute for that filesystem boundary. The
[gate decision packet](SBCT-01-GATE-DECISION-PACKET.md) continues to recommend
owner approval of `GATE-103/104/105`, with no disposition inferred from a request
to continue work. SBCT-02 runtime acceptance, draft-phase ratification, public
authority retrieval and release authorization remain separate work.
