# GitHub verification and PyPI publication setup

**Date:** 2026-09-26
**Status:** Owner-directed workflow preparation; no release or gate approval.

The owner requested GitHub workflow verification of the matrix and PyPI
publication setup as `softoboros-sbc`. This authorizes the bounded automation
and package-name preparation below. SBCT-06 remains a draft; no overall phase
ratification, release tag, published package or completed conformance profile is
inferred. This public SBC automation does not change downstream application CI/CD.

## Correction and ownership

SBCT-01 §5 assigns the final supported-version matrix to release acceptance.
The [gate packet](SBCT-01-GATE-DECISION-PACKET.md) recommends acceptance of its
executed runtime witnesses separately. A green GitHub matrix contributes evidence;
it cannot ratify specifications, check acceptance boxes or authorize production.

The selected PyPI distribution name is `softoboros-sbc`. Preserve Python imports
as `sbc_tools` and the existing CLI as `sbc-tools`; this is a packaging identity
change, not a semantic/API rename. The current version remains `0.1.0.dev34`.
Earlier evidence under the `sbc-tools` distribution remains historical.

## Candidate verification matrix

`.github/workflows/verify.yml` runs on pull requests, pushes to main, manual
dispatch, and calls from the publishing workflow. The initial candidate is
Python 3.11, 3.12, 3.13 and 3.14 on `windows-2025`, `ubuntu-24.04` and `macos-14`.
Runner labels and minor Python selections resolve to actual versions recorded
in each result; they are not an approved support promise for all patch releases.

Each cell acquires hash-pinned pure provider/build wheels separately from runtime
execution, runs core/provider tests and the installed-distribution verifier, and
retains logs, exact interpreter/platform identity, source SHA and tested wheel.
Applicable native-link tests must execute; a Windows-only junction skip on POSIX
is permitted and reported. Windows runner setup enables Developer Mode for test
fixture creation. Hosted runner privileges are recorded, not treated as proof
of ordinary-user installation; the earlier ordinary-user witnesses remain separate.

Schema validation packages are developer-only dependencies and may include
compiled wheels. Installed runtime inventories must contain only SBC, pip and
the approved pure-Python provider dependencies. Matrix jobs have read-only
repository access, no publishing environment and no OIDC permission. Actions
are pinned to immutable revisions; checkouts do not persist Git credentials.

## Publication sequence

`.github/workflows/publish.yml` supports manual dispatch only. It requires an
existing `tools-v<VERSION>` tag matching both the requested version and source
package version, the canonical `SoftOboros/sbc` repository, and the repository
activation variable `SBCT_PYPI_PUBLISH_ENABLED=true`. No tag is created here.

The same tagged revision runs the complete candidate matrix. A separate
read-only job verifies the Ubuntu/Python 3.12 artifact's source SHA, package
name/version, universal-wheel metadata and recorded digest. Only that exact
tested wheel is forwarded for publication; it is not rebuilt in the publishing
job. This initial setup publishes a universal wheel only. Source-distribution
publication remains an explicit follow-up rather than an untested extra artifact.

The publisher job runs on Linux in the `pypi` GitHub environment and alone has
`id-token: write`. It uses PyPI Trusted Publishing, with no stored API token.
The PyPI action checks the artifact and creates attestations. Normal pushes and
verification dispatches cannot publish. Activation does not itself ratify SBCT-06
or authorize any particular version; release review and a deliberate tag/manual
dispatch remain owner actions.

## Account setup still required

The [local execution record](evidence/github-workflow-local-execution.json)
records Windows/Python 3.14.6 passing 111 core, 7 packaging and 165 provider tests
without skips, plus installation of the renamed universal wheel and nine mounted
CLI schema envelopes. All 30 runtime module hashes match the earlier audit.
Both workflows pass actionlint 1.7.12 (ShellCheck was not enabled). These are local
preparation checks; the receipt has no GitHub source SHA or run ID. No hosted
matrix execution or account configuration is established by this evidence.

1. Create the GitHub `pypi` environment, require an owner/release reviewer, prevent
   self-review where available, and restrict deployment refs to `tools-v*` tags.
   Verify those protections before enabling the repository activation variable.
   Merely naming an environment in YAML does not establish its protections.
2. In the owning PyPI account, register a pending Trusted Publisher for the new
   project with these exact values:

   | Field | Value |
   |---|---|
   | Project | `softoboros-sbc` |
   | Owner | `SoftOboros` |
   | Repository | `sbc` |
   | Workflow filename | `publish.yml` |
   | Environment | `pypi` |

3. Completed for candidate verification: the setup and fixture correction were
   pushed, and all 12 hosted jobs passed at the revision recorded below. Release
   publication will rerun the matrix for its explicitly selected tag.
4. Complete the applicable release review, choose a unique version, enable the
   activation variable, create its reviewed tag, and dispatch publication for
   that tag/version. Review the protected-environment approval before upload.

The PyPI project endpoint returned HTTP 404 during preparation; this neither
reserves the name nor proves the account may publish it. Pending publisher
registration, environment protections, hosted runs and actual publication must
be verified independently. No package has been uploaded by this preparation.

## Hosted verification follow-up

The first [hosted matrix run](https://github.com/SoftOboros/sbc/actions/runs/36261797170)
at `fe7d8128c03e003bf7ca969ca2fc1d661fa49e02` passed all four Ubuntu cells.
Windows and macOS exposed fixture-path alias assumptions: mocked paths were
compared before resolving the temporary root, while runtime paths were already
resolved. macOS publication fixtures also supplied the linked `/var` ancestor,
which the existing runtime correctly rejects. A local aliased-temp reproduction
produced the same 12 failures and nine errors as macOS.

Fixture setup now resolves its owned temporary roots before constructing targets,
including relocated checkouts and installed-package work directories. Runtime
path validation and link rejection remain unchanged. This correction requires a
new hosted run; the first run remains failed historical evidence.

The [correction receipt](evidence/github-temp-alias-correction.json) records
111 core, 7 packaging and 165 provider tests plus installed-package verification
passing through an intentionally aliased temporary directory on local Windows.

The corrected [hosted run](https://github.com/SoftOboros/sbc/actions/runs/36262268799)
passed all 12 cells at `805a59154cba9de0d0cc940e24475c38bd054fe6`.
The [matrix receipt](evidence/github-matrix-execution.json) preserves each cell's
actual Python/platform identity, test counts, permitted skips and GitHub artifact
digest. Each cell passed 111 core and seven packaging tests, applicable provider
tests and installed-distribution verification. POSIX skipped only the Windows
junction witness; Windows skipped none. Hosted Windows used an administrator
token, so earlier ordinary-user local installation evidence remains separate.

Account setup remains incomplete: the signed-in GitHub settings page showed no
environments, and its New environment control did not open a form after a reload.
PyPI requires sign-in. No publishing activation, release tag or upload occurred.

## Sources

The design follows [PyPI Trusted Publishing](https://docs.pypi.org/trusted-publishers/using-a-publisher/),
[pending publishers](https://docs.pypi.org/trusted-publishers/creating-a-project-through-oidc/),
and the [official publish action](https://github.com/pypa/gh-action-pypi-publish).
The publishing job stays outside the reusable verification workflow, as required
by the publish action's documented trusted-publisher boundary.
