# SBCT-01 portability and native-link review

**Date:** 2026-09-25
**Status:** Informative execution evidence; no gate approval recorded.
**Runtime:** `0.1.0.dev34`, revision `9d666f43efe6ffab4c478a97ba199077e611d7de`.
**Contract:** SBCT-01 0.9.1, `GATE-101/102`, and `W-101-P/N`.

## Result

The Python 3.11 conditional-install branch, ordinary-user Linux execution and
native directory-link rejection now have concrete witnesses. All 30 runtime
module hashes remain unchanged. Changes concern verification code, fixtures and
documentation. See [execution evidence](evidence/sbct-01-portability-native-execution.json)
for exact versions, hashes, packages and negative controls. This extends the
[installation review](SBCT-01-INSTALLATION-REVIEW.md).

| Environment exercised this review | Core suite | Provider suite | Installed recipe and CLI |
|---|---|---|---|
| Windows 11 x86_64 / Python 3.11.9 | 111 passed | 165 run: 164 passed, one native-symlink privilege skip | Passed; nine mounted envelopes; conditional `typing_extensions` included |
| Ubuntu 24.04 under WSL2, native Linux filesystem / Python 3.12.3 | 111 passed | 165 run: 164 passed, one Windows-only junction skip | Passed; nine mounted envelopes; conditional dependency omitted |
| Windows 11 x86_64 / Python 3.14.6 | Earlier suite evidence retained | Focused boundary matrix passed, with native-symlink privilege skip | Updated verifier passed; nine mounted envelopes |

Earlier Windows/Python 3.12.14 evidence remains valid at its recorded verifier
revision. This ledger does not declare support for untested interpreters,
architectures, macOS or non-WSL Linux installations. Python 3.13 and newer 3.11
patch releases have not been executed here.

## Native filesystem boundaries

Each native link matrix executes 26 command cases: scan/check across committed,
single-source observation and mounted observation modes; source, registry,
authority and output path roles; plus the mounted-child path role. All reject
with `invalid_configuration`, no selection, no guarded content open, no target
resolution or descendant metadata access, and unchanged file/link snapshots.
Snapshots include host bindings, source, Git metadata, external fixture targets
and any output. Snapshot traversal does not follow symlinks or junctions.

Windows junctions use Python's standard-library Windows helper without a shell
command, compiler or administrator step. Linux directory symlinks were tested
under `/tmp` on the native WSL filesystem, not the Windows-mounted checkout.
Code and pinned wheels were copied into disposable Linux directories first.

Windows directory-symlink creation remains unavailable in the ordinary token:
errno 22 with WinError 1314. That witness is skipped, not passed. No system
privilege or Developer Mode setting was changed. Native results remain distinct
from the 60 injected metadata and six escaping-scope cases. Native file symlinks
and hostile concurrent filesystem replacement are not established by these
directory-link matrices.

## Interpreter floor and isolated installation

Linux execution used the existing user with UID 1000. Windows Python 3.11 came
from the [Python-documented NuGet CI distribution](https://docs.python.org/3.11/using/windows.html#the-nuget-org-packages)
in a temporary directory. Its executable had a valid Python Software Foundation
Authenticode signature; the test token was not an administrator token. The URL
and observed SHA-256 are recorded. No system Python, launcher registration or
PATH setting changed. This is a 3.11.9 compatibility witness, not a release
support/security baseline recommendation. NuGet is not an SBC consumer dependency.

The unchanged requirements recipe includes `typing_extensions` on real Python
3.11 and omits it on the tested newer interpreters. The verifier removes the
setuptools helper bootstrapped by Python 3.11 from its disposable runtime before
checking the exact package inventory. All three installed runs reject tampered
provider bytes without package changes and pass matching-digest native-archive
guard controls. Repository commands execute without build tooling.

The Linux developer process needed newer JSON Schema tooling than the installed
distribution supplied. Exact dependencies were acquired from PyPI into a separate
disposable developer environment; wheel hashes are recorded. Its compiled `rpds`
dependency is absent from the installed SBC runtime, whose exact inventory is
SBC, pip and pure-Python provider packages. Developer dependency acquisition is
separate from offline builder/runtime execution.

## Findings and repairs

1. The corruption fixture tried to overwrite a read-only POSIX loose Git object.
   It now permits owner writes on its own object before deliberately corrupting
   it. Reader behavior and assertions did not change.
2. Ubuntu's standard-library `sitecustomize` shadowed the verifier's environment
   file. The process negative control failed and prevented an offline proof. A
   dedicated audit module now loads through an environment-local `.pth` file;
   negative controls pass on Windows and Linux. This remains Python audit
   evidence, not an OS sandbox.
3. An installed Linux attempt reached schema validation without the required
   `referencing` developer package. The completed proof supplies the exact schema
   dependencies separately and validates the envelopes. Earlier incomplete
   attempts are not reported as successful installed runs.

## Gate recommendation and remaining work

Native directory-link evidence supports adding `GATE-102` to the owner's bounded
review alongside `GATE-103/104/105`. It does not claim the unexecuted Windows
symlink or native file-symlink cases. If the selected support scope requires
those native cases, retain them as required witnesses rather than infer an
exemption. The gate remains unchecked pending the owner's scope and disposition.

`GATE-101` remains open for final installation/support-matrix reconciliation.
Its former Python 3.11 conditional and non-Windows execution gaps now have the
bounded evidence above; they are no longer wholly untested. The supported-version
and platform policy remains a release decision. A Python 3.11 metadata floor
does not prove every later interpreter.

Next consolidate the proposed support scope for owner review while continuing
already authorized SBCT-02 query-engine work as appropriate. No runtime gate,
draft phase, release/tag or production approval is inferred here.
