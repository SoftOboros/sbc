"""Verify closed-profile authority input pins against a trusted approval digest.

This proves base input and patch integrity, not patch application or approval.
The expected digest is supplied by trusted host composition, never a request.
"""
from dataclasses import dataclass
import hashlib
import json
import re
from types import MappingProxyType
import unicodedata

from .identity import copy_files

ROLES = MappingProxyType({
    "authority_inputs": frozenset({"SBC-00-CONCEPTS.md", "SBC-00-ADDENDUM-A.md",
        "SBC-00-ADDENDUM-B.md", "SBC-00-ADDENDUM-C.md", "SBC-00-ADDENDUM-D.md",
        "TODO-SIDX-00-CONCEPTS.md", "TODO-SIDX-06A-CORPUS-AND-LOCATION-PROJECTION.md",
        "SBC-ERRATA.md", "SPEC-BEFORE-CODE-CONCEPTS.md"}),
    "producer_inputs": frozenset({"scan.py", "locations.py", "suspect.py"}),
    "support_inputs": frozenset({"AGENTS.md", "CLAUDE.md", "README.md", "LICENSE"}),
})
PATCH_ROLES = frozenset({"AGENTS.md", "CLAUDE.md", "README.md"})


def _exact(value, keys):
    if not isinstance(value, dict) or set(value) != set(keys):
        raise ValueError("Invalid authority shape")


def _unique(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError("Duplicate authority JSON key")
        value[key] = item
    return value


def _invalid_constant(value):
    raise ValueError("Nonfinite authority JSON number")


@dataclass(frozen=True)
class VerifiedAuthorityInputs:
    manifest_sha256: str
    patch_sha256: str
    base_files_by_role: object


def verify_authority_inputs(raw, *, approved_manifest_sha256, patch_bytes, readers):
    """Check exact approved manifest bytes and every referenced committed blob.

    readers maps host-registered repository IDs to read-only Git readers.
    The returned type deliberately cannot satisfy BundleValidator provenance.
    Patch application and resulting support identities must be verified later.
    """
    if (not isinstance(raw, bytes) or not isinstance(patch_bytes, bytes)
            or not isinstance(approved_manifest_sha256, str)
            or not re.fullmatch(r"[0-9a-f]{64}", approved_manifest_sha256)
            or hashlib.sha256(raw).hexdigest() != approved_manifest_sha256):
        raise ValueError("Unapproved authority manifest bytes")
    manifest = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique,
                          parse_constant=_invalid_constant)
    _exact(manifest, {*ROLES, "schema_version", "profile", "license", "reviewed_patches", "payload_schemas"})
    if (type(manifest["schema_version"]) is not int or manifest["schema_version"] != 1
            or manifest["profile"] != "sidx-schema3-location1" or manifest["license"] != "BSD-3-Clause"):
        raise ValueError("Unsupported authority profile")
    schemas = manifest["payload_schemas"]
    _exact(schemas, {"index", "locations", "diagnostics"})
    if schemas != {"index": 3, "locations": 1, "diagnostics": 3} or any(type(v) is not int for v in schemas.values()):
        raise ValueError("Invalid payload schemas")
    patches = manifest["reviewed_patches"]
    if not isinstance(patches, list) or len(patches) != 1:
        raise ValueError("Exactly one approved operational patch is required")
    patch = patches[0]
    _exact(patch, {"role", "sha256", "applies_to"})
    if (patch["role"] != "proposed-operational-metadata-correction"
            or not isinstance(patch["applies_to"], list) or len(patch["applies_to"]) != 3
            or set(patch["applies_to"]) != PATCH_ROLES
            or patch["sha256"] != hashlib.sha256(patch_bytes).hexdigest()):
        raise ValueError("Invalid reviewed patch")
    result, seen = {}, set()
    for group, roles in ROLES.items():
        rows = manifest[group]
        if not isinstance(rows, list) or len(rows) != len(roles):
            raise ValueError("Incomplete authority role inventory")
        found, order = set(), []
        for row in rows:
            _exact(row, {"role", "repository_id", "commit", "files"})
            role, repository_id = row["role"], row["repository_id"]
            if role not in roles or role in found:
                raise ValueError("Unknown or repeated authority role")
            found.add(role)
            if (not isinstance(repository_id, str) or not repository_id
                    or unicodedata.normalize("NFC", repository_id) != repository_id
                    or repository_id not in readers):
                raise ValueError("Unregistered authority repository")
            files = row["files"]
            if not isinstance(files, list) or len(files) != 1:
                raise ValueError("Each authority role requires one file")
            item = files[0]
            _exact(item, {"path", "blob_oid", "sha256"})
            path = item["path"]
            copy_files({path: b""})
            key = (repository_id, path)
            if key in seen:
                raise ValueError("Duplicate authority path")
            seen.add(key)
            order.append(key)
            # read_blob checks exact commit type, safe path, file mode and object integrity.
            data = readers[repository_id].read_blob(row["commit"], path)
            blob_oid = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
            if item["blob_oid"] != blob_oid or item["sha256"] != hashlib.sha256(data).hexdigest():
                raise ValueError("Authority input identity mismatch")
            result[role] = data
        if order != sorted(order):
            raise ValueError("Authority inputs are not canonically ordered")
    return VerifiedAuthorityInputs(approved_manifest_sha256, patch["sha256"], MappingProxyType(result))
