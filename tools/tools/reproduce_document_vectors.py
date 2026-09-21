"""Capture the pinned per-document parser results for extraction comparison."""
import argparse
import dataclasses
import json
from pathlib import Path
import sys
import tempfile

sys.path.insert(0,str(Path(__file__).resolve().parent))
from reproduce_wire_vectors import load_pinned_scanner


def plain(value):
    if dataclasses.is_dataclass(value):
        return plain(dataclasses.asdict(value))
    if isinstance(value,dict):
        return {k:plain(v) for k,v in value.items()}
    if isinstance(value,(set,frozenset)):
        return sorted(plain(v) for v in value)
    if isinstance(value,(list,tuple)):
        return [plain(v) for v in value]
    return value


def reproduce(source):
    scanner = load_pinned_scanner(source)
    fixtures = Path(__file__).resolve().parents[1]/"tests/fixtures"
    source_vectors = json.loads((fixtures/"producer-source-vectors.json").read_bytes())
    stable = next(c for c in source_vectors["cases"] if c["name"] == "stable")
    historical = dict(stable["inputs"])
    path = next(p for p in historical if p.startswith("docs/todo/"))
    historical[path] = historical[path].replace("**Status:** DRAFT",
        "**Status:** SUPERSEDED\n**Document lifecycle state:** superseded\n**Historical definitions:** INV-VECT-1")
    source_vectors["cases"].append({"name":"historical_registered","inputs":historical})
    output = []
    for case in source_vectors["cases"]:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for path,text in case["inputs"].items():
                if any(p in {"", ".", ".."} for p in path.split("/")) or "\\" in path or ":" in path:
                    raise ValueError("Unsafe fixture path")
                target = root/path
                target.parent.mkdir(parents=True,exist_ok=True)
                target.write_bytes(text.encode())
            for path,text in case["inputs"].items():
                if not path.startswith("docs/todo/") or not path.endswith(".md"):
                    continue
                output.append({"case":case["name"],"path":path,"text":text,
                    "family":scanner.family_of(Path(path)),
                    "registered_prefixes":sorted(scanner._registered_invariant_prefixes(root)),
                    "expected":plain(scanner.parse_document(root/path,root))})
    return fixtures/"document-parser-vectors.json",(json.dumps({"source_commit":source_vectors["source_commit"],
        "cases":output},indent=2)+"\n").encode()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("source",type=Path)
    parser.add_argument("--check",action="store_true")
    args = parser.parse_args()
    target,raw = reproduce(args.source)
    if args.check:
        assert target.read_bytes() == raw,"Document reference drift"
    else:
        target.write_bytes(raw)
    print("Pinned per-document references reproduced.")
