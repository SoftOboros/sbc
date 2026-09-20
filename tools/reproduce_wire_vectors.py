"""Reproduce emitted bytes from historical payloads using the pinned producer."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile

PINS = {"scan.py": "551c0ab7d70f82ad9e6fdfd99ef57a1ff78aeabb",
        "locations.py": "31217a012c99785cd0bda3cae3a3d9feb3cf33d5",
        "suspect.py": "d4da35b954285f757e03add62c5087765a754b88"}

def reproduce(source):
    for name, expected in PINS.items():
        raw = (source/name).read_bytes()
        actual = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        if actual != expected:
            raise ValueError("Unapproved producer source: " + name)
    sys.path.insert(0, str(source))
    spec = importlib.util.spec_from_file_location("pinned_scanner", source/"scan.py")
    scanner = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = scanner
    spec.loader.exec_module(scanner)
    fixtures = Path(__file__).resolve().parents[1]/"tests/fixtures"
    historical = json.loads((fixtures/"projection-vectors.json").read_bytes())
    cases = []
    for case in historical["cases"]:
        files = {}
        with tempfile.TemporaryDirectory() as temp:
            for kind in ("index", "locations", "diagnostics"):
                payloads = {Path(p).stem: json.loads(s) for p,s in case["files"].items()
                            if p.startswith(kind + "/")}
                emit = scanner.emit_diagnostic_index if kind == "diagnostics" else scanner.emit_index
                target = Path(temp)/kind
                emit(payloads, target)
                for path in sorted(target.glob("*.json")):
                    files[kind + "/" + path.name] = path.read_bytes().decode("utf-8")
        # Emission alone must match the already recorded diagnostic hashes.
        manifest = json.loads(files["diagnostics/_manifest.json"])
        for descriptor in manifest["families"]:
            assert hashlib.sha256(files["diagnostics/" + descriptor["filename"]].encode()).hexdigest() == descriptor["sha256"]
        cases.append({"name": case["name"], "files": files})
    return fixtures/"projection-wire-vectors.json", (json.dumps({
        "source_commit": historical["source_commit"], "producer_blobs": PINS,
        "scope": "Pinned emit functions over historical semantic payloads; not a full rescan",
        "cases": cases}, indent=2) + "\n").encode()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    path, raw = reproduce(args.source)
    if args.check:
        assert path.read_bytes() == raw, "Wire vector drift"
    else:
        path.write_bytes(raw)
    print("Five wire vectors reproduced with exact pinned emitters.")
