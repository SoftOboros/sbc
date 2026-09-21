"""Shared immutable-input copying and publication identity checks."""
import hashlib
import re
import unicodedata
from .canonical import canonical_json as _canonical
_FIELDS = {"repository_id", "snapshot_id", "source_commit", "projection_commit",
           "tracked_branch", "authority_manifest_sha256", "publication_id"}
_HEX64 = re.compile(r"[0-9a-f]{64}\Z")
_HEX40 = re.compile(r"[0-9a-f]{40}\Z")

def copy_publication(value):
    value = dict(value)
    if set(value) != _FIELDS:
        raise ValueError("Invalid publication")
    for key, item in value.items():
        if not isinstance(item, str) or unicodedata.normalize("NFC", item) != item:
            raise ValueError("Invalid publication field")
        if key in {"repository_id", "tracked_branch"}:
            if not 1 <= len(item) <= 256:
                raise ValueError("Invalid identifier")
        elif not (_HEX40 if key.endswith("commit") else _HEX64).fullmatch(item):
            raise ValueError("Invalid digest")
    identity = dict(value)
    identity.pop("publication_id")
    if hashlib.sha256(_canonical(identity)).hexdigest() != value["publication_id"]:
        raise ValueError("Publication identity mismatch")
    return value

def copy_files(value):
    copied = dict(value)
    if not copied:
        raise ValueError("Empty bundle")
    for path, data in copied.items():
        if (not isinstance(path, str) or not path or "\\" in path or ":" in path
                or path.startswith("/") or any(p in {"", ".", ".."} for p in path.split("/"))
                or unicodedata.normalize("NFC", path) != path
                or any(ord(c) < 32 for c in path) or not isinstance(data, bytes)):
            raise ValueError("Invalid bundle member")
    return copied
