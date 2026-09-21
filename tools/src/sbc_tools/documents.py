"""Document parsing over supplied bytes; no filesystem or repository traversal."""
import re
from ._producer_parser import EXAMPLE_PREFIXES, parse_document as _parse_document
from .identity import copy_files


def parse_document(data, *, path, family, registered_prefixes):
    """Parse one explicitly routed source using pinned document semantics.

    The host supplies an already validated family assignment. This operation
    does not infer family policy, authorize a source, scan siblings or emit a
    complete corpus projection. Invalid UTF-8 follows the pinned replacement rule.
    """
    prefixes = _validate_context(data, path, family, registered_prefixes)
    return _parse_document(data.decode("utf-8",errors="replace"),path,family,prefixes)


def _validate_context(data, path, family, registered_prefixes):
    copy_files({path:data})
    copy_files({family:b""})
    if "/" in family:
        raise ValueError("Family must be one path component")
    if isinstance(registered_prefixes,(str,bytes)):
        raise ValueError("Explicit registered prefixes required")
    prefixes = frozenset(registered_prefixes)
    if any(not isinstance(p,str) or not re.fullmatch(r"[A-Z]{2,8}",p)
           or p in EXAMPLE_PREFIXES or p == "PHASE" for p in prefixes):
        raise ValueError("Invalid registered invariant prefix")
    return prefixes
