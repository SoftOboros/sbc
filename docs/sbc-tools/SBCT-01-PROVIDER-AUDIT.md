# SBCT-01 pure-Python provider audit

**Document ID:** SBCT-PROVIDER-AUDIT
**Status:** Informative dependency evidence; not implementation acceptance.
**Date:** 2026-09-19

SBCT-01 §8 owns the proposed provider selection. This audit does not authorize
extraction or ratify a phase. Public metadata and wheel archives were fetched
from PyPI; the artifact digest was checked against its published SHA-256.
No package was installed in the workspace environment.

| Package | Version | Universal wheel SHA-256 |
|---|---|---|
| dulwich | 1.2.15 | `5c863992962bab0fc5f75be132399a16f670f2a9283faf9aaeb953fd8891db83` |
| urllib3 | 2.8.0 | `0cf3cae568d36aa9576b28dfb35f11328f1cb974ca7647d9475ebb86c75ac6e3` |
| typing_extensions | 4.16.0 | `481caa481374e813c1b176ada14e97f1f67a4539ce9cfeb3f350d78d6370c2e8` |

All three archives use `py3-none-any` tags. Archive inspection found no `.pyd`,
`.so`, `.dll`, `.dylib`, `.exe`, `.a` or `.lib` members. Without extras, Dulwich
requires urllib3 and conditional typing_extensions; urllib3 has only optional
extra dependencies and typing_extensions has none. Metadata/native-file review
is bounded evidence, not a security audit of all source behavior.

An isolated Python 3.14.6 invocation (`-I -S`) imported directly from these wheel
archives with subprocess/process and socket-connect audit events rejected. It
read two local repositories' commit/tree objects, followed the child gitdir
indirection, and read a staged gitlink (mode 160000). The staged pin was reported
as staged evidence, not as a committed parent relationship. No hooks, network
acquisition, package installation or repository mutations were performed.

The actual core installation matrix, packed/shallow history, SHA-256 repositories,
Windows path cases, malformed/missing children, dirty detection and golden
semantic parity remain unproven. Release recipes must constrain hashes for every
runtime dependency and disable extras; native wheels of the same version are
not interchangeable. Explicit dependency acquisition is separate from offline
scan/query execution.

Sources: [Dulwich installation documentation](https://www.dulwich.io/getting-started/),
[Dulwich 1.2.15 metadata](https://pypi.org/pypi/dulwich/1.2.15/json),
[urllib3 2.8.0 metadata](https://pypi.org/pypi/urllib3/2.8.0/json),
[typing_extensions 4.16.0 metadata](https://pypi.org/pypi/typing_extensions/4.16.0/json).
