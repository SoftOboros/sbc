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
    registry = next(n for n in trees['scan'].body if isinstance(n,ast.FunctionDef) and n.name == '_registered_invariant_prefixes')
    registry.args = ast.parse('def _registered_invariant_prefixes(text): pass').body[0].args
    prefix_start = next(i for i,n in enumerate(registry.body) if isinstance(n,ast.Assign)
                        and any(isinstance(t,ast.Name) and t.id == 'prefixes' for t in n.targets))
    registry.body = registry.body[prefix_start:]
    scan = next(n for n in trees["scan"].body if isinstance(n,ast.FunctionDef) and n.name == "scan")
    scan.args = ast.parse("def scan(sources, registered_prefixes): pass").body[0].args
    # Preserve the corpus-wide resolution pass after replacing traversal and reads.
    start = next(i for i,n in enumerate(scan.body) if isinstance(n,ast.Assign)
                 and any(isinstance(t,ast.Name) and t.id == "projected" for t in n.targets))
    scan.body = ast.parse('''
docs = []
objects = []
citations = []
texts = {}
registered_prefixes = sorted(registered_prefixes)
for relative_path, family, text in sources:
    d, o, c = parse_document(text, relative_path, family, registered_prefixes)
    docs.append(d)
    objects.extend(o)
    citations.extend(c)
    texts[relative_path] = text
''').body + scan.body[start:]
    resolution = next(n for n in scan.body if isinstance(n,ast.For)
                      and isinstance(n.target,ast.Tuple) and isinstance(n.body[0],ast.Try))
    assert isinstance(resolution.body[0],ast.Try)
    resolution.body[0:1] = ast.parse("lines = texts[path].splitlines()").body
    # Locator admission uses this invocation's exact source membership, not a
    # consumer-specific global directory list. Thread context through callers.
    locator = next(n for n in trees["scan"].body if isinstance(n,ast.FunctionDef) and n.name == "_safe_locator")
    membership = next(n for n in locator.body if isinstance(n,ast.If)
                      and any(isinstance(c,ast.Name) and c.id == "SCAN_DIRS" for c in ast.walk(n)))
    membership.test = ast.parse("document not in admitted_documents",mode="eval").body
    contextual = {"_safe_locator"}
    functions = [n for n in trees["scan"].body if isinstance(n,ast.FunctionDef)]
    while True:
        callers = {n.name for n in functions if any(isinstance(c,ast.Call)
                   and isinstance(c.func,ast.Name) and c.func.id in contextual for c in ast.walk(n))}
        if callers <= contextual:
            break
        contextual |= callers
    for function in functions:
        if function.name not in contextual:
            continue
        function.args.kwonlyargs.append(ast.arg(arg="admitted_documents"))
        function.args.kw_defaults.append(None)
        for call in ast.walk(function):
            if isinstance(call,ast.Call) and isinstance(call.func,ast.Name) and call.func.id in contextual:
                call.keywords.append(ast.keyword(arg="admitted_documents", value=ast.Name(id="admitted_documents",ctx=ast.Load())))
    location_functions = {n.name:n for n in trees['locations'].body if isinstance(n,ast.FunctionDef)}
    declarations = location_functions['parse_declarations']
    declarations.args = ast.parse('def parse_declarations(text, source_path, family): pass').body[0].args
    declarations.body[1:4] = ast.parse('lines = text.splitlines()').body
    archives = location_functions['scan_archives']
    archives.args = ast.parse('def scan_archives(archive_sources, family_for_path, limits): pass').body[0].args
    archive_loop = next(n for n in archives.body if isinstance(n,ast.For))
    begin = next(i for i,n in enumerate(archives.body) if isinstance(n,ast.Assign)
                 and any(isinstance(t,ast.Name) and t.id == 'archive_dir' for t in n.targets))
    archives.body[begin:archives.body.index(archive_loop)] = []
    archive_loop.target = ast.parse('relative_archive, archive_bytes',mode='eval').body
    for n in ast.walk(archive_loop.target):
        if hasattr(n,'ctx'): n.ctx = ast.Store()
    archive_loop.iter = ast.parse('sorted(archive_sources.items())',mode='eval').body
    archive_loop.body[:4] = ast.parse('''
coverage['archives_scanned'] += 1
archive_sha = hashlib.sha256(archive_bytes).hexdigest()
''').body
    for n in ast.walk(archive_loop):
        if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr == 'ZipFile':
            n.args = [ast.parse('io.BytesIO(archive_bytes)',mode='eval').body]
        if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id == 'family_for_path':
            n.args = [ast.Name(id='relative_archive',ctx=ast.Load()),ast.Name(id='member_path',ctx=ast.Load())]
    future_index = next(i for i,n in enumerate(trees['locations'].body)
                        if isinstance(n,ast.ImportFrom) and n.module == '__future__')
    trees['locations'].body.insert(future_index + 1,ast.parse('import io').body[0])
    builder = location_functions['build_location_index']
    builder.args = ast.parse('def build_location_index(texts, documents, archive_sources, family_for_path, *, archive_limits=None): pass').body[0].args
    del builder.body[1]  # filesystem root resolution
    document_loop = next(n for n in builder.body if isinstance(n,ast.For))
    source_start = next(i for i,n in enumerate(document_loop.body) if isinstance(n,ast.Assign)
                        and any(isinstance(t,ast.Name) and t.id == 'source' for t in n.targets))
    document_loop.body[source_start:] = ast.parse('''
locs, lifecycles, declaration_diagnostics = parse_declarations(texts[document.path], document.path, document.family)
declared_locations.extend(locs)
declared_lifecycles.extend(lifecycles)
diagnostics.extend(declaration_diagnostics)
''').body
    for n in ast.walk(builder):
        if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id == 'scan_archives':
            n.args[0] = ast.Name(id='archive_sources',ctx=ast.Load())
    lookup = {module:{name:node for node in tree.body for name in bindings(node)} for module,tree in trees.items()}
    needed = {"scan":{"parse_document", "scan", "_registered_invariant_prefixes", "build_projection_bundle_with_expectations", "_render", "_diagnostic_render"},"locations":{"build_location_index", "render"}}
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
