"""Exact, in-memory application of the approved support-only unified patch."""
import hashlib
import re
from types import MappingProxyType

from .authority import PATCH_ROLES, VerifiedAuthorityInputs

_HUNK = re.compile(rb"@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@(?: [^\r\n]*)?\n\Z")


def verify_support_patch(inputs, patch_bytes, *, approved_result_sha256):
    """Require exact base context, patch hash and trusted resulting file hashes.

    No fuzzy matching, filesystem writes, executable patch tools, renames or
    normative/code changes. Unsupported patch syntax fails closed.
    """
    if (not isinstance(inputs, VerifiedAuthorityInputs) or not isinstance(patch_bytes, bytes)
            or hashlib.sha256(patch_bytes).hexdigest() != inputs.patch_sha256
            or set(approved_result_sha256) != PATCH_ROLES):
        raise ValueError("Unapproved support patch inputs")
    lines = patch_bytes.splitlines(keepends=True)
    results, i = {}, 0
    while i < len(lines):
        old_header = lines[i]
        if not old_header.startswith(b"--- a/") or not old_header.endswith(b"\n"):
            raise ValueError("Unsupported patch file header")
        try:
            role = old_header[len(b"--- a/"):-1].decode("ascii")
        except UnicodeError as exc:
            raise ValueError("Invalid patch role") from exc
        if role not in PATCH_ROLES or role in results:
            raise ValueError("Patch changes an unapproved or duplicate role")
        i += 1
        if i >= len(lines) or lines[i] != b"+++ b/" + role.encode() + b"\n":
            raise ValueError("Patch renames or invalid new header are forbidden")
        i += 1
        original = inputs.base_files_by_role[role].splitlines(keepends=True)
        output, cursor, hunks = [], 0, 0
        while i < len(lines) and lines[i].startswith(b"@@"):
            match = _HUNK.fullmatch(lines[i])
            if match is None:
                raise ValueError("Unsupported hunk header")
            old_start, old_count, new_start, new_count = (
                int(value) if value is not None else 1 for value in match.groups())
            start = old_start - 1 if old_count else old_start
            target = new_start - 1 if new_count else new_start
            if start < cursor or start > len(original):
                raise ValueError("Overlapping or out-of-range hunk")
            output.extend(original[cursor:start])
            cursor = start
            if target != len(output):
                raise ValueError("Incorrect new hunk position")
            i += 1
            removed = added = 0
            while removed < old_count or added < new_count:
                if i >= len(lines) or not lines[i].endswith(b"\n"):
                    raise ValueError("Truncated patch hunk")
                marker, content = lines[i][:1], lines[i][1:]
                if marker not in {b" ", b"-", b"+"}:
                    raise ValueError("Unsupported patch body")
                if marker in {b" ", b"-"}:
                    if cursor >= len(original) or original[cursor] != content:
                        raise ValueError("Patch base context mismatch")
                    cursor += 1
                    removed += 1
                if marker in {b" ", b"+"}:
                    output.append(content)
                    added += 1
                if removed > old_count or added > new_count:
                    raise ValueError("Patch hunk count mismatch")
                i += 1
            hunks += 1
        if not hunks:
            raise ValueError("Empty patch file section")
        output.extend(original[cursor:])
        result = b"".join(output)
        if hashlib.sha256(result).hexdigest() != approved_result_sha256[role]:
            raise ValueError("Patched support identity mismatch")
        results[role] = result
    if set(results) != PATCH_ROLES:
        raise ValueError("Incomplete support patch")
    return MappingProxyType(results)
