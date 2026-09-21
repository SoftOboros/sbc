# SBC Supporting Tools — prerelease implementation

This separate local repository begins the approved portable implementation.
Its current implemented surface is the standard-library-only SBCT cursor
codec, transactional SQLite publication store, extracted document parser and projection validators
and offline committed Git verification for registered source repositories.
Indexing, query extraction, Django/MCP OAuth and dashboard
integration are not yet implemented here.

The governing SBCT documents remain in their existing authoring home until
their migration and portable authority-reference layout are recorded.
The cursor codec implements SBCT-CONTRACT-02 revision 0.1.1, approved under
GATE-206 on 2026-09-20. It does not authorize requests: hosts must validate
access before decoding and again before delivering results.

## Development

Python 3.11 or later is required. The implemented codec has no third-party
runtime dependencies. SQLite is the interpreter's standard-library module.
From this repository:

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests -v
```

Only synthetic test keys are present. Hosts provide signing keys and trusted
clock values. The codec supports at most 16 verification keys, key rotation
through new instances, and verification-only instances. Invalid trusted
composition inputs raise ValueError; untrusted invalid tokens return the
contract's safe cursor failure codes.

This checkout has no remote or release tag. First-party licensing is
BSD-3-Clause; future dependencies retain their own notices.

## Publication storage

SQLiteSnapshotStore requires an explicitly supplied BundleValidator. There is
no permissive default: the host's validator must verify the approved complete
bundle, content identity, authority/profile and committed-publication binding.
Storage tests cover both a synthetic validator and extracted SIDX semantics.
This storage slice is not yet a runnable ingest/query product.

Publication and replay keys are scoped by repository. BEGIN IMMEDIATE serializes
writers; expected generations prevent lost updates. Failed writes roll back.
Idempotent replay returns its original receipt without resetting newer current
state. Explicit retained-publication lookup returns its first recorded generation;
current lookup returns the current selection generation.

Views pin an eager immutable byte copy and need no database connection after
opening. close releases those bytes. This first implementation does not delete
retained publications or implement projection reset/garbage collection.
It only creates and writes sbct-prefixed tables; unrelated identity tables are
outside its operations. Filesystem power-loss durability and full Django/store
parity remain acceptance work.

## Projection validation

BundleValidator checks the c6-v3 object/location/diagnostic triple using 46
helpers extracted from the approved ingest Git blob
`d77b462102367d143a4d1d204df3df7dd586d193`. The extraction script verifies the
source blob and reproduces the module; corpus roots are explicit per instance.
Validation reads only supplied bytes and requires a trusted host provenance
verifier for committed bytes, approved authority/profile and corpus identity.
There is no default verifier. Tests cover both synthetic provenance and real
Git-backed integrity composition with synthetic approval fixtures.
Production-history acceptance remains outstanding.

The five historical golden vectors stored pretty-printed diagnostic JSON, which
the pinned ingest validator rejects. Reproduction with the exact pinned producer
emitters confirms that the producer emits the required compact bytes and the
recorded family hashes already match. The mismatch was in golden serialization,
not producer behavior. Tests retain the historical rejection cases and use
`projection-wire-vectors.json` for successful semantic/store integration.
`tools/reproduce_wire_vectors.py` verifies producer blobs and reproduces these
bytes from the historical semantic payloads; it does not perform a full rescan.
This correction supersedes the compatibility diagnosis in commit 892438e.

## Offline Git evidence

GitCommitReader inventories an exact SHA-1 commit, reads regular committed files
and verifies complete projection subtree membership and bytes. It ignores dirty
working files, rejects missing or corrupt objects and never follows symlinks or
submodule entries. Gitlinks remain explicit inventory entries for later relation
handling. No Git executable, hooks or network acquisition are used.

The optional reader requires the audited pure Python provider. Install it with
`python -m pip install -r requirements-git.txt`; the pinned hashes select only
the approved universal wheels. Do not substitute an unconstrained installation
or native wheel. Core validation and storage still have no third-party runtime
dependencies. To test existing audited wheel files without installation:

```powershell
python -I -S tools/check_git_provider.py C:/path/to/audited-wheels
```

Provider tests reject process/network operations and exercise real local
Git objects. Packed/shallow and submodule repository coverage remain pending.
This reader is a provenance primitive, not the BundleValidator's complete
trusted provenance verifier. Runtime gates remain open.

## Authority and corpus inputs

`verify_authority_inputs` checks exact manifest bytes against a trusted
host-supplied approval digest, the closed role inventory, canonical ordering,
committed file identities and reviewed-patch hash. It returns immutable base
file bytes. Matching hashes do not establish approval: the expected manifest
digest must come from the owner's approved baseline. Patch application and
resulting support-file identities are separate checks described below; the intermediate
result cannot satisfy BundleValidator's provenance interface.

`inventory_committed_corpus` includes every nonexcluded file under explicit
source roots plus required configuration, authority, registry and evidence
files. Missing inputs, overlapping roots and selected symlink/gitlink members
fail. `corpus_digest` implements the approved sorted repository/path/hash
identity. Configuration validation must still establish that required inputs
and registered child mounts are complete before full provenance composition.
There are now 84 core tests and 94 Git/provenance tests; these are bounded
implementation evidence, not end-to-end acceptance.

`verify_support_patch` applies the approved support-only unified patch entirely
in memory, with exact context and hunk positions, no fuzzy matching, and trusted
result hashes. It rejects renames, duplicate file sections, missing support roles
and changes outside AGENTS.md, CLAUDE.md and README.md. The recorded operational
patch reproduced all three staged reconciliation files exactly in a local probe;
the live SBC submodule was not modified.

`validate_configuration` parses the closed TOML key set, checks host-registered
repository identity, local path containment and input/output separation, and
validates reference syntax and explicit capabilities/mount mappings. It returns
an immutable configuration. These checks do not authorize a request or ratify
a baseline.

`GitCommitReader.resolve_commit` resolves an allowed ref once and peels checked
annotated tags to an exact SHA-1 commit. Missing refs/objects raise
GitUnavailableError, separately from invalid syntax or wrong object types.
`pin_child_mounts` validates explicitly included child gitlinks through their
immediate registered parent's pinned tree, retaining parent and child identities.
Included unregistered children fail; unrelated children are not opened.
Literal exclusions now remove child mounts from selection and required child
availability checks; exclusions that hide an explicit source root are rejected.
Committed relationship pins alone do not establish a clean scan.

`observe_checkout` checks HEAD against the pin, the complete index against the
committed tree, and working files against committed bytes. It catches staged,
unstaged, missing and untracked files without ambient filters or fsmonitor
commands. The result is a conservative byte-exact observation, not general Git
status: ignored files also prevent a clean result, line-ending normalization is
not applied, and symlinks and unverifiable executable modes fail closed.
Gitlinks require completed child observations bound to both their committed pin
and physical checkout location.
This does not lock the filesystem or prove absence of concurrent changes.
`observe_checkout_tree` revalidates committed mount pins and checks children
before parents. Dirty or revision-mismatched children prevent clean parent
results. A reader of identical history at a different physical checkout is
rejected. Excluded children are not opened or assumed clean, so their presence
prevents a whole-repository clean result until a separately defined scoped
policy applies. Acceptance of additional checkout forms remains pending.

## Committed provenance composition

`CommittedProvenanceVerifier` composes authority input checks, reviewed support
patch application, configured corpus inventory and exact committed projection
membership/bytes. Trusted host construction fixes the repository, configuration,
branch, profile, authority approval digest and support-result hashes. The
`bundle_validator()` factory uses those same roots and profile for semantic
validation. SQLite revalidates candidates, including ones fabricated by callers.

This composition supports explicit child source mounts and separate pinned
authority repositories. It requires an explicit branch and host-registered
readers. `inventory_mounted_corpus` selects files by parent-relative paths but
hashes them under their owning repository ID and repository-relative path.
Nested children use the immediate parent's committed gitlink. Exclusions do not
hide required evidence, and missing history fails without current-HEAD fallback.
Single-repository inventory delegates to the same implementation. Required
evidence paths are host-supplied; a production profile must register its complete
evidence inventory. Producer regeneration remains unfinished.

Retained verification reads exact source/projection commits and does not depend
on current HEAD or dirty working files. This proves committed integrity, not that
a new scan ran from a clean checkout. Use the separate checkout observations for
that admission decision; no runtime gate or access authorization is implied.

`CommittedProvenanceVerifier.admit_source()` now resolves the configured branch,
checks the pinned root and included child checkouts, verifies committed source
provenance, and repeats checkout/branch checks before returning an immutable
AdmittedSource. Dirty checkouts, changed profile evidence or an observed edit
during verification reject admission. This operation neither generates files nor
publishes a snapshot. Its result is a bounded scan-start observation, not a lock,
authorization grant or renewable lease; producer execution must read the pinned
committed bytes. Retained verification deliberately does not perform admission.

## Producer extraction reference

`tools/regenerate_reference_vectors.py` builds fixture Git commits from the five
original source cases, reads those bytes through GitCommitReader, and runs the
exact pinned producer's scan, object/diagnostic build, location build and bundle
validation. Every emitted byte matches the corrected wire vectors, including
malformed-gate and duplicate-invariant cases. Run it with:

```powershell
python -I -S tools/regenerate_reference_vectors.py C:/path/to/pinned/scripts/specidx C:/path/to/audited-wheels
```

The harness verifies source blobs and pure-wheel hashes and blocks process and
network calls. It writes only temporary fixture repositories and materialized
inputs. This is a full-regeneration reference witness, not the extracted portable
producer or the scan CLI. Archive coverage, configurable producer scopes and
admitted-source-to-producer wiring remain extraction work.

`sbc_tools.documents.parse_document` is the first runtime producer extraction.
It consumes document bytes plus an explicit relative path, family and registered
prefix set. Filesystem admission, family routing and registry loading remain
outside this pure function. The pinned parsing/lifecycle/historical-definition
rules are preserved; invalid UTF-8 follows the source's replacement behavior.
It returns document, object and citation records, not complete projections.

`tools/extract_document_parser.py` reproduces the dependency closure from two
verified source blobs. Six document cases match complete pinned-parser outputs,
including a superseded historical-definition case. An isolated probe parsed all
six with file, process and network audit events rejected.

`sbc_tools.projections.build_document_projections` accepts an ordered collection
of `(path, family, bytes)` sources and explicit registered prefixes. It resolves
corpus-wide citations and emits the pinned object and diagnostic wire bytes.
Diagnostic locators must belong to the exact supplied document set, replacing
the reference consumer's hardcoded source directories. Duplicate paths reject;
no mutable global corpus context is used.

The five original wire cases match byte for byte. Run
`tools/check_projection_extraction.py C:/path/to/pinned/scripts/specidx` under
`python -I -S` for nine full-triple reference comparisons, including cross-family
citations, historical definitions, archives and declared location/lifecycle
merging, with file/process/network access blocked during pure builds. An
additional standalone-layout probe passes.

`build_projection_files` extends the same corpus pass with location generation
and returns `(files, location_diagnostics)`. Supply archive ZIP bytes by relative
path and a family mapping keyed by `(archive_path, member_path)` for every
Markdown member. The original member count, byte and compression-ratio limits
apply without extraction to disk. Declared archive identity and hashes must
match the supplied archive; headerless members retain their diagnostics.

Generated bytes alone are not a validated snapshot or publication candidate.

`CommittedProvenanceVerifier.generate_source` now admits the configured source,
retains bytes from the verified root/child inventory, derives prefixes from the
committed registry files, generates the triple and runs semantic preflight. The
host supplies explicit document and archive-member family mappings; document
routing must cover every selected Markdown source exactly. Configuration root
order and sorted paths define document order. All selected ZIPs are inspected.

The immutable result contains admission evidence, exact generated files, the
snapshot identity and serialized location diagnostics. It does not write files,
create commits or publish a selection. After a host commits those exact outputs,
the existing bundle validator verifies committed bytes and provenance before
SQLite publication. Tests exercise that complete bounded path, child inclusion,
registry-derived wire parity and changes after admission. Admission remains an
observation, not a lock: generation reads only pinned Git bytes. Host family
policy, CLI orchestration and runtime acceptance gates remain open.

`CommittedProvenanceVerifier.check_source` regenerates from admitted inputs and
compares the full union of payload paths against the complete committed reference
at that same selected commit. It validates the reference before comparison:
absent, incomplete or corrupt references raise `ReferenceUnavailableError`,
preserving the generated candidate for later error-envelope reporting. Valid
byte/path differences return a sorted `differing_paths` tuple. `projection_commit`
identifies the reference; candidate files and snapshot identity remain separate.

The check performs no persistent writes and does not reread a moved branch.
Equality does not clear source diagnostics or approve acceptance. This is the
committed comparison operation behind the host-backed CLI boundary; working-tree
comparison remains unimplemented.

`cli_results.execute_check` maps the committed operation to the ratified command
envelope: exit 0 for equal/no findings, 1 for drift or source findings, 3 for
unavailable references or I/O failures, and 4 for unclassified/internal failures.
Hosts can classify known invocation/configuration/authority failures using the
closed `CommandFailure` vocabulary (exit 2). Unknown exception text never enters
an error message. Unavailable references preserve generated source findings but
have a null result, as required by the ratified schema.

`render_envelope` returns text or one UTF-8 JSON object with a final newline;
it does not write streams or terminate the process. The developer-only
`tools/check_cli_envelopes.py` checks sample outcomes against a supplied ratified
schema using jsonschema; this is not a runtime dependency.

`python -m sbc_tools` and the packaged `sbc-tools` entry point now provide strict
argument parsing, help/version and host-backed committed scan/check dispatch.
Unknown/abbreviated/repeated flags and conflicting invocations return exit 2.
Help/version do not load a repository. Package version comes from `__version__`.

An embedding application calls `cli.main(argv, load_host=loader)`; its trusted
loader receives the explicit configuration path and returns a context manager
for `CommittedCheckHost(verifier, document_families, archive_families)`. The loader
owns validation of that configuration, approval pins and reader cleanup. The
verifier's configured command capability must be enabled. Neither TOML nor CLI
arguments can select Python plugins or turn manifest hashes into approvals.

The default console requires explicit `--host PATH` for repository operations.
The binding loader checks the approved version-1 structure, reads no unregistered
configuration, and verifies the exact configured digest before constructing the
existing host. Missing host selection and simultaneous in-process/console loaders
are invocation errors. No settings, approval pins or repositories are discovered.
Working-tree execution and full runtime conformance remain open. JSON output is
written once after host cleanup; cleanup failure retains available findings.

`DirectoryProjectionStore` supplies the local complete-bundle publication
primitive. A host provides an output directory and a semantic validator; explicit
creation checks existing ancestors before creating missing directory components.
Publication validates the candidate, writes a uniquely named bundle, flushes its
files, rereads and revalidates every byte, then uses `os.replace` to switch
`current.json`. It never overwrites a prior bundle. Readers load one pointer and
return immutable copied bytes after integrity and semantic checks.

Nine tests cover pinned views, visibility before/after the switch, interrupted
writes, failed replacement, invalid/tampered/unlisted members and pointer traversal.
They exercise this Windows filesystem only. Trusted local directory ownership is
required; this is neither an OS sandbox nor a power-loss durability guarantee.
Concurrent writers use last-switch-wins semantics; this store is distinct from
the transactional snapshot store's generation checks. Failed staging directories
are retained and never selected; cleanup is not implemented.

`scan_source` now publishes at the configured output root, and the host CLI reports
the candidate identity with a null projection commit. The operation creates no
Git commit. Commit the selected directory and pointer before committed `check`:
clean admission deliberately rejects uncommitted generated output. After a
commit, comparison and retained snapshot validation read the selected payloads
through the same pointer/manifest decoder used for local reads. Retained bundle
directories do not enter the selected payload identity.

Existing flat committed triples remain readable. A mixed flat/selected layout is
rejected, and scan requires explicit migration of flat output instead of silently
overwriting it. Corrupt selection metadata never falls back to another bundle.
Five integration tests cover scan/commit/check/SQLite publication, failed switch,
corrupt pointers, ambiguous layouts and retained bundles. No release or
cross-platform runtime acceptance is claimed.

`HostRegistration` and `RegisteredHostLoader` now provide explicit host loading
without extending the ratified TOML schema. Register the root and authority
repository paths, exact configuration bytes, approval/profile pins, support
hashes, evidence paths and family mappings in trusted application code. The
registration copies mutable mappings. A requested config path must match one
registration before it is read, must not resolve through a different path, and
must still contain the registered bytes. Unknown or changed configurations fail.

The loader opens only registered offline Git readers and owns their cleanup with
an exit stack, including partial-open and construction failures. It supplies the
same verifier/host used by the CLI:

```python
from sbc_tools.cli import main
from sbc_tools.host import RegisteredHostLoader

# registrations are HostRegistration objects supplied by the trusted application.
raise SystemExit(main(load_host=RegisteredHostLoader(registrations)))
```

This is an explicit in-process API, not a new settings file, environment-variable
protocol or Python plugin selected by repository content. It does not establish
that a supplied digest was approved. The approved default-console channel is explicit `--host PATH`; no selection
means an invocation error. The binding file is JSON with repository mappings,
config/profile/approval digests and explicit family assignments, converted to
this same registration API. Relative repository directories are anchored to the
binding file's directory. Duplicate keys, unsupported fields/versions, linked
binding/config inputs, digest mismatches and conflicting selectors reject.

```text
sbc-tools scan --config /path/to/repository/sbc.toml --host /path/to/host.json
sbc-tools check --config /path/to/repository/sbc.toml --host /path/to/host.json --format json
```

Owner approval of this mechanism does not approve a supplied binding or digest.
Authority validation failures report `invalid_authority`; the loader never fills
in or repairs approval pins. Console integration tests use synthetic authority
fixtures and preserve snapshot identity after moving the checkout.
