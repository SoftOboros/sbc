"""Reproduce the pure document parser closure from exact approved source blobs."""
import argparse
import ast
import copy
import hashlib
from pathlib import Path

PINS = {"scan":"551c0ab7d70f82ad9e6fdfd99ef57a1ff78aeabb",
        "locations":"31217a012c99785cd0bda3cae3a3d9feb3cf33d5"}


def bindings(node):
    if isinstance(node,(ast.FunctionDef,ast.ClassDef)):
        return {node.name}
    if isinstance(node,(ast.Import,ast.ImportFrom)):
        return {a.asname or a.name.split(".")[0] for a in node.names}
    if isinstance(node,(ast.Assign,ast.AnnAssign)):
        targets = node.targets if isinstance(node,ast.Assign) else [node.target]
        return {n.id for t in targets for n in ast.walk(t) if isinstance(n,ast.Name)}
    return set()


def extract(source):
    trees = {}
    for name,pin in PINS.items():
        raw = (source/(name+".py")).read_bytes()
        if hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest() != pin:
            raise ValueError("Unapproved parser source")
        trees[name] = ast.parse(raw)
    parser = next(n for n in trees["scan"].body if isinstance(n,ast.FunctionDef) and n.name == "parse_document")
    parser.args = ast.parse("def parse_document(text, relative_path, family, registered_prefixes): pass").body[0].args
    # Replace filesystem admission/read and contextual family routing only.
    prefix = ast.parse('''
rel = pathlib.PurePosixPath(relative_path)
doc = Document(path=str(rel), family=family, is_concepts="CONCEPTS" in rel.name.upper())
objects: list[SpecObject] = []
citations: list[Citation] = []
raw_lines = text.splitlines()
''').body
    parser.body = prefix + parser.body[6:]
    class ExplicitRegistry(ast.NodeTransformer):
        def visit_Name(self,node):
            if node.id == "repo_root":
                node.id = "registered_prefixes"
            return node
    ExplicitRegistry().visit(parser)
    historical = next(n for n in trees["scan"].body if isinstance(n,ast.FunctionDef) and n.name == "_historical_definition_ids")
    for arg in historical.args.args:
        if arg.arg == "repo_root":
            arg.arg, arg.annotation = "registered_prefixes", None
    historical.body = [n for n in historical.body if not (
        isinstance(n,ast.Assign) and isinstance(n.value,ast.Call)
        and isinstance(n.value.func,ast.Name) and n.value.func.id == "_registered_invariant_prefixes")]
    lookup = {module:{name:node for node in tree.body for name in bindings(node)} for module,tree in trees.items()}
    needed = {"scan":{"parse_document"},"locations":set()}
    visited = {"scan":set(),"locations":set()}
    while any(needed[m]-visited[m] for m in needed):
        for module in needed:
            for name in list(needed[module]-visited[module]):
                visited[module].add(name)
                node = lookup[module][name]
                for child in ast.walk(node):
                    if isinstance(child,ast.Name) and isinstance(child.ctx,ast.Load) and child.id in lookup[module]:
                        needed[module].add(child.id)
                    if (module == "scan" and isinstance(child,ast.Attribute)
                            and isinstance(child.value,ast.Name) and child.value.id == "locations"):
                        needed["locations"].add(child.attr)
    output = {}
    for module,tree in trees.items():
        body = []
        for node in tree.body:
            if isinstance(node,ast.ImportFrom) and node.module == "__future__":
                body.append(copy.deepcopy(node))
            elif bindings(node) & needed[module]:
                if isinstance(node,ast.Import) and any(a.name == "locations" for a in node.names):
                    body.append(ast.parse("from . import _producer_locations as locations").body[0])
                else:
                    body.append(copy.deepcopy(node))
        rendered = ast.unparse(ast.fix_missing_locations(ast.Module(body=body,type_ignores=[])))
        forbidden = {"os","subprocess","tempfile","shutil","socket"}
        imports = {a.name.split(".")[0] for n in body if isinstance(n,ast.Import) for a in n.names}
        if imports & forbidden:
            raise ValueError(f"Parser extraction reached nonportable dependencies: {module}: {imports & forbidden}; closure={needed}")
        header = '"""Pinned pure parser extraction. Reproduce with tools/extract_document_parser.py.\nSource blob: '+PINS[module]+'.\n"""\n'
        output["_producer_parser.py" if module == "scan" else "_producer_locations.py"] = (header+rendered+"\n").encode()
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("source",type=Path)
    parser.add_argument("--check",action="store_true")
    args = parser.parse_args()
    output = extract(args.source)
    for name,raw in output.items():
        path = Path(__file__).resolve().parents[1]/"src/sbc_tools"/name
        if args.check:
            assert path.read_bytes() == raw,"Parser extraction drift"
        else:
            path.write_bytes(raw)
    print("Pure parser closure reproduced from verified blobs.")
