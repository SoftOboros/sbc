"""SBCT-CONTRACT-02 0.1.1 signed cursor framing.

No authentication decisions, query semantics, framework imports, or implicit
keys. Hosts must authorize before decode and supply the expected binding.
"""
from __future__ import annotations

import base64
import binascii
import hashlib
import hmac
import json
import re
import unicodedata
from collections.abc import Mapping

_HEX64 = re.compile(r"[0-9a-f]{64}\Z")
_HEX40 = re.compile(r"[0-9a-f]{40}\Z")
_KID = re.compile(r"[A-Za-z0-9_-]{1,32}\Z")
_B64 = re.compile(r"[A-Za-z0-9_-]+\Z")
_DIGESTS = frozenset({
    "snapshot_id", "publication_id", "capability_profile_sha256",
    "evidence_identity_sha256", "inherited_provider_identity",
    "access_context_sha256", "filter_digest",
})
_BINDING = _DIGESTS | {"repository_id", "projection_commit", "capability", "limit"}
_CLAIMS = _BINDING | {"version", "last", "issued_at", "expires_at"}
MAX_TOKEN_BYTES = 8192
TTL_SECONDS = 900


def _canonical(value: dict) -> bytes:
    return (json.dumps(value, sort_keys=True, ensure_ascii=False,
                       allow_nan=False, separators=(",", ":")) + "\n").encode("utf-8")


def _b64(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def _unb64(value: str) -> bytes:
    if not _B64.fullmatch(value):
        raise ValueError("Invalid base64url")
    raw = base64.b64decode(value + "=" * (-len(value) % 4),
                          altchars=b"-_", validate=True)
    if _b64(raw) != value:
        raise ValueError("Noncanonical base64url")
    return raw


def _unique_object(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key")
        result[key] = value
    return result


def _text(value: object) -> bool:
    return isinstance(value, str) and unicodedata.normalize("NFC", value) == value


def _valid_binding(value: object) -> bool:
    if not isinstance(value, dict) or set(value) != _BINDING:
        return False
    if not all(isinstance(value[k], str) and _HEX64.fullmatch(value[k]) for k in _DIGESTS):
        return False
    return (
        _text(value["repository_id"]) and 1 <= len(value["repository_id"]) <= 256
        and isinstance(value["projection_commit"], str)
        and bool(_HEX40.fullmatch(value["projection_commit"]))
        and value["capability"] == "C11"
        and type(value["limit"]) is int and 1 <= value["limit"] <= 200
    )


def _valid_claims(value: object) -> bool:
    if not isinstance(value, dict) or set(value) != _CLAIMS:
        return False
    if not _valid_binding({k: value[k] for k in _BINDING}):
        return False
    last = value["last"]
    return (
        type(value["version"]) is int and value["version"] == 1
        and type(value["issued_at"]) is int and value["issued_at"] >= 0
        and type(value["expires_at"]) is int
        and value["expires_at"] == value["issued_at"] + TTL_SECONDS
        and isinstance(last, list) and len(last) == 5
        and all(_text(last[i]) for i in (0, 2, 3))
        and (last[1] is None or _text(last[1]))
        and type(last[4]) is int and last[4] >= 1
    )


def _signer_failure() -> dict:
    return {"code": "signer_unavailable", "message": "Cursor signer unavailable.",
            "retryable": True}


class HMACCursorCodec:
    """Fixed HMAC-SHA256 codec with a host-owned, bounded verification ring.

    Construct a fresh codec after key changes; key bytes are copied at startup.
    Verification-only instances use active_key_id=None. Never log key material.
    Malformed encode inputs raise ValueError (trusted composition error).
    """

    def __init__(self, keys: Mapping[str, bytes], active_key_id: str | None):
        if len(keys) > 16:
            raise ValueError("Verification ring exceeds 16 keys")
        copied = {}
        for kid, secret in keys.items():
            if not isinstance(kid, str) or not _KID.fullmatch(kid):
                raise ValueError("Invalid key identifier")
            if not isinstance(secret, bytes) or len(secret) < 32:
                raise ValueError("Keys require at least 32 bytes")
            copied[kid] = bytes(secret)
        if active_key_id is not None and active_key_id not in copied:
            raise ValueError("Active key missing from verification ring")
        self._keys = copied
        self._active = active_key_id

    def encode(self, claims: Mapping) -> str | dict:
        try:
            # Materialize an independent JSON value and accept Python tuples.
            value = json.loads(_canonical(dict(claims)))
        except (TypeError, ValueError, UnicodeError, RecursionError) as exc:
            raise ValueError("Invalid cursor claims") from exc
        if not _valid_claims(value):
            raise ValueError("Invalid cursor claims")
        if self._active is None:
            return _signer_failure()
        prefix = f"sbct1.{self._active}.{_b64(_canonical(value))}"
        signature = hmac.new(self._keys[self._active], prefix.encode("ascii"),
                             hashlib.sha256).digest()
        token = f"{prefix}.{_b64(signature)}"
        if len(token) > MAX_TOKEN_BYTES:
            return _signer_failure()
        return token

    def decode(self, token: str, expected: Mapping, now: int) -> dict:
        invalid = {"code": "invalid_cursor"}
        if type(now) is not int or now < 0:
            raise ValueError("Clock must provide nonnegative Unix seconds")
        expected_value = dict(expected)
        if not _valid_binding(expected_value):
            raise ValueError("Invalid expected binding")
        if not isinstance(token, str) or len(token) > MAX_TOKEN_BYTES or not token.isascii():
            return invalid
        try:
            version, kid, payload, signature = token.split(".")
            if version != "sbct1" or not _KID.fullmatch(kid) or kid not in self._keys:
                return invalid
            raw = _unb64(payload)
            supplied = _unb64(signature)
            signed = f"{version}.{kid}.{payload}".encode("ascii")
            wanted = hmac.new(self._keys[kid], signed, hashlib.sha256).digest()
            if not hmac.compare_digest(supplied, wanted):
                return invalid
            value = json.loads(raw, object_pairs_hook=_unique_object)
            if not _valid_claims(value) or _canonical(value) != raw:
                return invalid
        except (ValueError, TypeError, UnicodeError, binascii.Error, RecursionError):
            return invalid
        if now < value["issued_at"] or now >= value["expires_at"]:
            return invalid
        if any(value[k] != expected_value[k] for k in _BINDING):
            return {"code": "cursor_snapshot_mismatch"}
        return value
