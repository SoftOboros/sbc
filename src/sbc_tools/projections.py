"""Pure object and diagnostic projections over explicitly routed documents."""
from . import _producer_parser as producer
from .documents import _validate_context


def build_document_projections(sources, *, registered_prefixes):
    """Return exact object/diagnostic wire bytes for ordered (path, family, bytes).

    The caller selects and orders the corpus and supplies family policy. No
    locations, provenance, snapshot validation or publication is performed here.
    Duplicate paths are rejected rather than silently replacing source context.
    """
    prefixes = _validate_context(b"", "context.md", "context", registered_prefixes)
    prepared = []
    seen = set()
    for path, family, data in sources:
        _validate_context(data, path, family, prefixes)
        if path in seen:
            raise ValueError("Duplicate document path")
        seen.add(path)
        prepared.append((path, family, data.decode("utf-8", errors="replace")))
    scanned = producer.scan(prepared, prefixes)
    objects, diagnostics, _expectations = producer.build_projection_bundle_with_expectations(
        scanned, admitted_documents=frozenset(seen))
    return {
        kind + "/" + name + ".json": render(payload).encode("utf-8")
        for kind, payloads, render in (
            ("index", objects, producer._render),
            ("diagnostics", diagnostics, producer._diagnostic_render),
        )
        for name, payload in payloads.items()
    }
