# SBC Supporting Tools — prerelease implementation

This separate local repository begins the approved portable implementation.
Its current implemented surface is the standard-library-only SBCT cursor
codec. Indexing, query extraction, stores, Django/MCP OAuth and dashboard
integration are not yet implemented here.

The governing SBCT documents remain in their existing authoring home until
their migration and portable authority-reference layout are recorded.
The cursor codec implements SBCT-CONTRACT-02 revision 0.1.1, approved under
GATE-206 on 2026-09-20. It does not authorize requests: hosts must validate
access before decoding and again before delivering results.

## Development

Python 3.11 or later is required. The implemented codec has no third-party
runtime dependencies. From this repository:

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
