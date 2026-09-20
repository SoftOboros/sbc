# SBC Supporting Tools — prerelease implementation

This separate local repository begins the approved portable implementation.
Its current implemented surface is the standard-library-only SBCT cursor
codec and transactional SQLite publication store. Indexing, query extraction,
full bundle validation, Django/MCP OAuth and dashboard
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
The storage tests use a synthetic exact-byte validator, not SIDX validation.
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
