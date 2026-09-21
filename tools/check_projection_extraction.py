"""Compare pure corpus projection with pinned cross-document reference cases."""
import argparse
import json
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
from reproduce_wire_vectors import load_pinned_scanner


def check(source):
    package = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(package / "src"))
    from sbc_tools.projections import build_document_projections
    scanner = load_pinned_scanner(source)
    cases = json.loads((package / "tests/fixtures/producer-source-vectors.json").read_bytes())["cases"]
    stable = dict(next(c["inputs"] for c in cases if c["name"] == "stable"))
    linked = dict(stable)
    linked["docs/todo/consumer/CONS-00.md"] = (
        "# Consumer\n\n**Document ID:** CONS-00\n**Status:** DRAFT\n\n"
        "References VECT-00 and INV-VECT-1 and vectors:TERM-001.\n")
    cases.append({"name": "cross_family", "inputs": linked})
    historical = dict(linked)
    historical["docs/todo/vectors/VECT-00.md"] = historical["docs/todo/vectors/VECT-00.md"].replace(
        "**Status:** DRAFT", "**Status:** SUPERSEDED\n**Document lifecycle state:** superseded\n"
        "**Historical definitions:** INV-VECT-1")
    cases.append({"name": "historical_cross_family", "inputs": historical})
    prepared = []
    for case in cases:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for path, text in case["inputs"].items():
                target = root / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(text.encode())
            data = scanner.scan(root)
            objects, diagnostics, _ = scanner.build_projection_bundle_with_expectations(data)
            expected = {kind + "/" + name + ".json": render(payload).encode()
                        for kind, payloads, render in (("index", objects, scanner._render),
                            ("diagnostics", diagnostics, scanner._diagnostic_render))
                        for name, payload in payloads.items()}
            documents = [(d.path, d.family, case["inputs"][d.path].encode()) for d in data["docs"]]
            prepared.append((case["name"], documents, data["registered_prefixes"], expected))
    def reject_io(event, args):
        if event == "open" or event.startswith(("subprocess.", "socket.", "os.system", "os.spawn", "os.exec")):
            raise RuntimeError("Pure projection attempted I/O: " + event)
    sys.addaudithook(reject_io)
    for name, documents, prefixes, expected in prepared:
        actual = build_document_projections(documents, registered_prefixes=prefixes)
        assert actual == expected, name + ": projection drift"
    # Public layout is independent of the pinned consumer directory rules.
    result = build_document_projections([("specs/EX-00.md", "example", b"# Missing document ID\n")], registered_prefixes=[])
    assert b"specs/EX-00.md" in result["diagnostics/example.json"]
    print(json.dumps({"exact_reference_cases": [item[0] for item in prepared],
                      "audit": "File, process and network access blocked during all pure builds",
                      "standalone_layout": "passed"}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    check(parser.parse_args().source)
