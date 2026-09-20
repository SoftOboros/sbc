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

Eight provider tests reject process/network operations and exercise real local
Git objects. Full authority-manifest validation, complete authoritative corpus
inventory, packed/shallow and submodule repository coverage remain pending.
This reader is a provenance primitive, not the BundleValidator's complete
trusted provenance verifier. Runtime gates remain open.
