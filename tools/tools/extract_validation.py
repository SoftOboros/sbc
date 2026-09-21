"""Reproduce the mechanical extraction from the approved exact source blob.

Developer tool only. Semantic ownership moves to the extracted module; this
script records that initial extraction, not a second runtime implementation.
"""
import argparse
import ast
import copy
import hashlib
from pathlib import Path

SOURCE_BLOB = "d77b462102367d143a4d1d204df3df7dd586d193"


def extract(raw):
    digest = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    if digest != SOURCE_BLOB:
        raise ValueError("Source is not the approved ingest blob")
    tree = ast.parse(raw)
    static_helpers = {"_canonical_json", "_validate_nfc"}
    methods = [n for n in tree.body if isinstance(n, ast.FunctionDef)
               and n.name not in {"ingest", "prune"} | static_helpers]
    names = {n.name for n in methods}
    class Qualify(ast.NodeTransformer):
        def visit_Name(self, node):
            if isinstance(node.ctx, ast.Load):
                if node.id in names:
                    return ast.copy_location(ast.Attribute(ast.Name("self", ast.Load()), node.id, ast.Load()), node)
                if node.id == "_CORPUS_ROOTS":
                    return ast.copy_location(ast.Attribute(ast.Name("self", ast.Load()), "corpus_roots", ast.Load()), node)
            return node
    transformed = []
    for method in methods:
        clone = copy.deepcopy(method)
        clone.args.args.insert(0, ast.arg(arg="self"))
        transformed.append(Qualify().visit(clone))
    retained = []
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and (node.module == "django.db" or node.module == "models"):
            continue
        if isinstance(node, ast.FunctionDef) and node.name in static_helpers:
            retained.append(copy.deepcopy(node))
            continue
        if isinstance(node, ast.FunctionDef) or isinstance(node, ast.Expr):
            continue
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "_CORPUS_ROOTS" for t in node.targets):
            continue
        retained.append(copy.deepcopy(node))
    constructor = ast.parse("""
def __init__(self, corpus_roots):
    if isinstance(corpus_roots, (str, bytes)):
        raise ValueError("Corpus roots must be a sequence of paths")
    roots = tuple(corpus_roots)
    if not roots or not all(isinstance(root, str) and root for root in roots):
        raise ValueError("Explicit corpus roots are required")
    for root in roots:
        self._safe_document(root, "corpus root")
    self.corpus_roots = roots
""").body[0]
    ingest = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "ingest")
    begin = next(i for i,n in enumerate(ingest.body)
                 if isinstance(n, ast.Assign) and isinstance(n.value, ast.Call)
                 and isinstance(n.value.func, ast.Name) and n.value.func.id == "_load_object_index")
    end = next(i for i,n in enumerate(ingest.body) if isinstance(n, ast.With))
    validation_body = copy.deepcopy(ingest.body[begin:end])
    class InputView(ast.NodeTransformer):
        def visit_Call(self, node):
            node = self.generic_visit(node)
            if (isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name)
                    and node.func.value.id == "pathlib" and node.func.attr == "Path"
                    and len(node.args) == 1 and isinstance(node.args[0], ast.Name)
                    and node.args[0].id in {"index_dir", "location_dir", "diagnostic_dir"}):
                return node.args[0]
            return node
    entry = ast.parse("def validate_triple(self, index_dir, location_dir, diagnostic_dir): pass").body[0]
    entry.body = [Qualify().visit(InputView().visit(n)) for n in validation_body]
    cls = ast.ClassDef(name="ProjectionSemantics", bases=[], keywords=[],
                       body=[constructor, entry, *transformed], decorator_list=[])
    output = ast.fix_missing_locations(ast.Module(body=[*retained, cls], type_ignores=[]))
    header = (
        '"""Extracted SIDX validators; no ORM, settings or publication writes.\n'
        f'Approved source Git blob: {SOURCE_BLOB}.\n'
        'Mechanical changes: instance-qualified helpers and explicit corpus roots.\n'
        'Reproduce with tools/extract_validation.py.\n"""\n'
    )
    return header + ast.unparse(output) + "\n", len(methods) + len(static_helpers)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered, count = extract(args.source.read_bytes())
    target = Path(__file__).resolve().parents[1] / "src/sbc_tools/_sidx_validation.py"
    if args.check:
        assert target.read_bytes() == rendered.encode("utf-8"), "Extraction drift"
    else:
        target.write_bytes(rendered.encode("utf-8"))
    print(f"{count} validator/helper functions extracted from verified source.")
