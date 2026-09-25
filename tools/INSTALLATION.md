# Prerelease installation and verification

This is the repository-core development recipe governed by
[SBCT-01](../docs/sbc-tools/SBCT-01-REPOSITORY-CORE.md) §5 and §8. It does not
declare a supported release matrix or complete core/dashboard conformance.
See the [installation review](../docs/sbc-tools/SBCT-01-INSTALLATION-REVIEW.md)
for executed environments and remaining evidence.
The [portability follow-up](../docs/sbc-tools/SBCT-01-PORTABILITY-REVIEW.md)
records Python 3.11 conditional inclusion, WSL Linux execution and native-link
checks. Python/platform support remains an explicit release decision.

## Select the interpreter and environment

Use Python 3.11 or later with `venv` and `pip`. Create a writable, ordinary-user
virtual environment; no system package installation or administrator step is
part of this recipe. Run the examples from the SBC repository root. Replace
`python` in the creation command with the explicit interpreter being tested.

On Windows PowerShell:

```powershell
python -m venv .venv-sbct
$sbctPython = Join-Path $PWD '.venv-sbct/Scripts/python.exe'
& $sbctPython -m pip install -r tools/requirements-git.txt
& $sbctPython -m pip install --no-deps ./tools
& $sbctPython -m pip check
& $sbctPython -m sbc_tools --version
```

On POSIX shells, the equivalent interpreter path is `.venv-sbct/bin/python`:

```sh
python -m venv .venv-sbct
.venv-sbct/bin/python -m pip install -r tools/requirements-git.txt
.venv-sbct/bin/python -m pip install --no-deps ./tools
.venv-sbct/bin/python -m pip check
.venv-sbct/bin/python -m sbc_tools --version
```

These acquisition/build commands may access PyPI. They are separate from offline
repository operations. Source installation uses the build backend in
`pyproject.toml`; it is not the exact pinned offline build proof below. The POSIX
commands document the corresponding recipe; the offline installed variant has
WSL Linux evidence, while macOS remains unexecuted.

The package's standard-library core and optional Git provider are separate
installation steps. Installing `./tools` alone does not install the provider
needed for repository CLI operations. [requirements-git.txt](requirements-git.txt)
is the authoritative provider recipe: exact versions, universal-wheel hashes,
binary-only acquisition, no extras, and `typing_extensions` only on Python below
3.12. Keep dependency resolution enabled so missing transitive dependencies fail.
Do not replace it with an unconstrained `pip install dulwich` or a native wheel.

## Offline artifact installation

Acquire the approved provider wheels before entering the offline environment.
For the selected interpreter, `python -m pip download -r tools/requirements-git.txt
--dest PROVIDER_WHEELS` uses the recipe's hashes and conditional dependency.
This is acquisition, not scanning. A shared verification wheel directory needs
all three artifacts pinned by [the provider verifier](tools/check_git_provider.py),
including the conditional artifact even when the current interpreter omits it.

With the target virtual environment's interpreter and a locally built SBC wheel:

```text
python -m pip install --no-index --no-cache-dir --find-links PROVIDER_WHEELS -r tools/requirements-git.txt
python -m pip install --no-index --no-deps PATH_TO_SBC_WHEEL
python -m pip check
python -m sbc_tools --version
```

Substitute the actual wheel path; `PATH_TO_SBC_WHEEL` is not a published package
name. Preserve its build evidence and digest. No release artifact is supplied by
these examples. Scanning still requires authored configuration and an explicit
`--host PATH` binding with approved authority pins; installation cannot supply
those approvals.

## Reproduce the installed execution evidence

Use a developer interpreter with the schema-test dependencies available, and
wheel directories containing the exact build/provider artifacts pinned in the
existing verifier. Run from `tools/`:

```text
python tools/check_installed_distribution.py BUILD_WHEELS PROVIDER_WHEELS --python PATH_TO_TARGET_PYTHON
```

Omitting `--python` uses the invoking interpreter for the disposable builder and
runtime. The selected interpreter must already exist; the verifier does not
download Python or modify that installation. Schema validation and fixture
preparation stay in the developer process. Repository commands execute the built
distribution in the target runtime, without developer schema packages.

The verifier copies source to a temporary builder, installs exact pinned build
wheels, builds without network/build isolation, and installs the provider through
the unchanged requirements recipe in a separate temporary runtime. It checks
the exact resolved package set, `pip check`, native archive guards, and rejection
of a tampered provider wheel without package changes before running the installed
CLI witnesses. The target interpreter/platform and recipe digest are reported
with the wheel digest. Temporary environments are removed afterward.

Python 3.11 may bootstrap setuptools into its new virtual environment. The
verifier removes that build helper from the disposable runtime and records the
removal before testing the minimal dependency inventory. It loads test audit
controls through an environment-local `.pth` hook so an operating system's
`sitecustomize` does not shadow them. Schema packages are developer-only inputs;
they are not installed into the runtime under test.

Python's standard library and the pip-generated Windows console launcher remain
within the approved installation boundary. Third-party compiled runtime
extensions and native build tools do not. Audit controls on repository commands
are test witnesses, not OS isolation or production authorization.
