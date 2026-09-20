"""Structural configuration and local path validation; no ref resolution."""
from dataclasses import dataclass
from pathlib import Path
import re
from types import MappingProxyType
import tomllib
import unicodedata

from .identity import copy_files

_KEYS = {"schema_version", "repository_id", "repository_root", "source_roots", "exclude",
         "registry_paths", "output_root", "tracked_ref", "mode", "capabilities",
         "authority_manifest", "submodules"}


def _path(value):
    copy_files({value: b""})
    if any(part.lower() == ".git" for part in value.split("/")):
        raise ValueError("Git administrative paths are not corpus inputs")
    return value


def _paths(value):
    if not isinstance(value, list) or any(not isinstance(p, str) for p in value):
        raise ValueError("Expected path array")
    if len(set(value)) != len(value):
        raise ValueError("Duplicate configured path")
    return tuple(_path(p) for p in value)


def _overlap(a, b):
    return a == b or a.startswith(b + "/") or b.startswith(a + "/")


def _ref(value):
    if not isinstance(value, str):
        raise ValueError("Invalid tracked reference")
    if value == "HEAD" or re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", value):
        return value
    if (not value.startswith(("refs/heads/", "refs/tags/"))
            or any(ord(c) < 33 or ord(c) == 127 or c in "~^:?*[\\" for c in value)
            or ".." in value or "@{" in value
            or any(not p or p.startswith(".") or p.endswith((".", ".lock")) for p in value.split("/"))):
        raise ValueError("Unsupported tracked reference syntax")
    return value


@dataclass(frozen=True)
class ResolvedConfiguration:
    repository_root: Path
    values: object


def validate_configuration(raw, *, config_directory, registered_repositories):
    """Validate explicit TOML and containment against host repository mappings.

    This does not resolve refs, establish Git tracking, validate child gitlinks
    or check dirty state. Those are separate committed-provider obligations.
    """
    value = tomllib.loads(raw.decode("utf-8"))
    if set(value) != _KEYS or type(value["schema_version"]) is not int or value["schema_version"] != 1:
        raise ValueError("Unsupported configuration keys or version")
    repository_id = value["repository_id"]
    if (not isinstance(repository_id, str) or not repository_id
            or unicodedata.normalize("NFC", repository_id) != repository_id
            or repository_id not in registered_repositories):
        raise ValueError("Unregistered repository identity")
    location = value["repository_root"]
    if not isinstance(location, str) or not location:
        raise ValueError("Invalid repository root")
    root = (Path(config_directory)/location).resolve(strict=True)
    if not root.is_dir() or root != Path(registered_repositories[repository_id]).resolve(strict=True):
        raise ValueError("Repository root does not match registered identity")
    roots, excluded, registry = (_paths(value[k]) for k in ("source_roots", "exclude", "registry_paths"))
    output, authority = _path(value["output_root"]), _path(value["authority_manifest"])
    if not roots or any(_overlap(a, b) for a in roots for b in roots if a != b):
        raise ValueError("Source roots must be nonempty and nonoverlapping")
    if any(_overlap(output, p) for p in (*roots, *registry, authority)):
        raise ValueError("Output overlaps authoritative input")
    if any(p == e or p.startswith(e + "/") for p in (*roots, *registry, authority) for e in excluded):
        raise ValueError("Exclusion hides required input")
    for path in (*roots, *excluded, *registry, output, authority):
        resolved = (root/path).resolve()
        if not resolved.is_relative_to(root):
            raise ValueError("Configured path escapes repository")
        if path in roots and not resolved.is_dir():
            raise ValueError("Missing source directory")
        if path in (*registry, authority) and not resolved.is_file():
            raise ValueError("Missing required input file")
    resolved_output = (root/output).resolve()
    if resolved_output.exists() and not resolved_output.is_dir():
        raise ValueError("Output destination is not a directory")
    for path in (*roots, *registry, authority):
        resolved_input = (root/path).resolve()
        if resolved_output.is_relative_to(resolved_input) or resolved_input.is_relative_to(resolved_output):
            raise ValueError("Resolved output overlaps authoritative input")
    if value["mode"] not in {"committed", "working-tree"}:
        raise ValueError("Unsupported mode")
    capabilities = value["capabilities"]
    if (not isinstance(capabilities, list) or not capabilities
            or any(c not in ("scan", "check") for c in capabilities)
            or len(set(capabilities)) != len(capabilities)):
        raise ValueError("Unsupported capabilities")
    mounts = value["submodules"]
    if not isinstance(mounts, list):
        raise ValueError("Expected submodule array")
    seen_paths, seen_ids, normalized = set(), {repository_id}, []
    for mount in mounts:
        if not isinstance(mount, dict) or set(mount) != {"path", "repository_id"}:
            raise ValueError("Invalid submodule mapping")
        path, child_id = _path(mount["path"]), mount["repository_id"]
        if not isinstance(child_id, str) or child_id not in registered_repositories or child_id in seen_ids or path in seen_paths:
            raise ValueError("Duplicate, cyclic or unregistered child mapping")
        seen_paths.add(path)
        seen_ids.add(child_id)
        normalized.append((path, child_id))
    result = dict(value, source_roots=roots, exclude=excluded, registry_paths=registry,
                  tracked_ref=_ref(value["tracked_ref"]), capabilities=tuple(capabilities),
                  submodules=tuple(sorted(normalized)))
    return ResolvedConfiguration(root, MappingProxyType(result))
