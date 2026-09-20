# SBC Supporting Tools — prerelease implementation

This separate local repository begins the approved portable implementation.
Its current implemented surface is the standard-library-only SBCT cursor
codec, transactional SQLite publication store, extracted projection validators
and an offline committed Git reader.
Indexing, query extraction, committed-source verification, Django/MCP OAuth and dashboard
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
There is no default verifier. Tests use synthetic provenance; Git verification
and production-history acceptance are still outstanding.

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
There are now 46 core tests and 35 Git/provenance tests; these are bounded
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
not applied, and symlinks/gitlinks and unverifiable executable modes fail closed.
This does not lock the filesystem or prove absence of concurrent changes.
Recursive child checkout composition, acceptance of additional checkout forms,
and complete BundleValidator provenance integration remain pending.
