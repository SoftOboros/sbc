import base64
import hashlib
import hmac
import json
import unittest

from sbc_tools.cursors import HMACCursorCodec


class CursorTests(unittest.TestCase):
    def setUp(self):
        self.secret = b"synthetic-test-key-only-0123456789"
        self.codec = HMACCursorCodec({"test": self.secret}, "test")
        self.binding = dict(
            repository_id="repo", snapshot_id="1"*64, publication_id="2"*64,
            projection_commit="a"*40, capability_profile_sha256="3"*64,
            evidence_identity_sha256="4"*64, inherited_provider_identity="5"*64,
            access_context_sha256="6"*64, capability="C11",
            filter_digest="7"*64, limit=50)
        self.claims = dict(self.binding, version=1, issued_at=1000, expires_at=1900,
                           last=["family", None, "GATE-1", "docs/spec.md", 10])

    def signed(self, raw):
        payload = base64.urlsafe_b64encode(raw).rstrip(b"=").decode()
        prefix = f"sbct1.test.{payload}"
        sig = hmac.new(self.secret, prefix.encode(), hashlib.sha256).digest()
        return prefix + "." + base64.urlsafe_b64encode(sig).rstrip(b"=").decode()

    def test_roundtrip_and_determinism(self):
        token = self.codec.encode(self.claims)
        self.assertEqual(token, self.codec.encode(self.claims))
        self.assertEqual(self.claims, self.codec.decode(token, self.binding, 1000))
        self.assertEqual(self.claims, self.codec.decode(token, self.binding, 1899))

    def test_expiry_and_future(self):
        token = self.codec.encode(self.claims)
        for now in (999, 1900, 2000):
            with self.subTest(now=now):
                self.assertEqual({"code": "invalid_cursor"}, self.codec.decode(token, self.binding, now))

    def test_every_binding_dimension(self):
        token = self.codec.encode(self.claims)
        for field in self.binding:
            if field == "capability":
                continue  # Only C11 is valid in this profile.
            changed = dict(self.binding)
            changed[field] = 51 if field == "limit" else (
                "another-repo" if field == "repository_id" else
                "b"*40 if field == "projection_commit" else "f"*64)
            with self.subTest(field=field):
                self.assertEqual({"code": "cursor_snapshot_mismatch"},
                                 self.codec.decode(token, changed, 1100))

    def test_tampered_signature(self):
        token = self.codec.encode(self.claims)
        prefix, sig = token.rsplit(".", 1)
        sig = ("A" if sig[0] != "A" else "B") + sig[1:]
        self.assertEqual({"code": "invalid_cursor"},
                         self.codec.decode(prefix + "." + sig, self.binding, 1100))

    def test_retired_and_removed_keys(self):
        token = self.codec.encode(self.claims)
        verifier = HMACCursorCodec({"test": self.secret}, None)
        self.assertEqual(self.claims, verifier.decode(token, self.binding, 1100))
        self.assertEqual("signer_unavailable", verifier.encode(self.claims)["code"])
        self.assertEqual({"code": "invalid_cursor"},
                         HMACCursorCodec({}, None).decode(token, self.binding, 1100))

    def test_rotation_preserves_original_expiry(self):
        token = self.codec.encode(self.claims)
        rotated = HMACCursorCodec({"test": self.secret, "new": b"n"*32}, "new")
        self.assertEqual(self.claims, rotated.decode(token, self.binding, 1100))
        self.assertTrue(rotated.encode(self.claims).startswith("sbct1.new."))
        self.assertEqual({"code": "invalid_cursor"}, rotated.decode(token, self.binding, 1900))

    def test_noncanonical_and_duplicate_json(self):
        raw = json.dumps(self.claims).encode()
        duplicate = raw[:-1] + b', "version": 1}'
        for candidate in (raw, duplicate):
            self.assertEqual({"code": "invalid_cursor"},
                             self.codec.decode(self.signed(candidate), self.binding, 1100))

    def test_signed_invalid_claims(self):
        for changes in ({"expires_at": 2000}, {"version": True},
                        {"limit": True}, {"unexpected": "field"},
                        {"last": ["family", None, "id", "path", False]}):
            value = dict(self.claims, **changes)
            raw = (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()
            self.assertEqual({"code": "invalid_cursor"},
                             self.codec.decode(self.signed(raw), self.binding, 1100))

    def test_invalid_encodings_and_legacy_tokens(self):
        for token in ("a.b", "sbct2.test.a.b", "sbct1.test.@@.@@", "x"*8193, "é"):
            self.assertEqual({"code": "invalid_cursor"}, self.codec.decode(token, self.binding, 1100))

    def test_rejects_noncanonical_base64(self):
        token = self.codec.encode(self.claims)
        version, kid, payload, sig = token.split(".")
        self.assertEqual({"code": "invalid_cursor"},
                         self.codec.decode(f"{version}.{kid}.{payload}=.{sig}", self.binding, 1100))

    def test_key_configuration_is_validated_and_copied(self):
        for keys, active in (({"test": b"short"}, "test"), ({"bad.kid": b"x"*32}, None),
                             ({}, "missing")):
            with self.assertRaises(ValueError):
                HMACCursorCodec(keys, active)
        keys = {"test": self.secret}
        codec = HMACCursorCodec(keys, "test")
        keys.clear()
        self.assertEqual(self.codec.encode(self.claims), codec.encode(self.claims))

    def test_input_and_output_are_not_shared(self):
        token = self.codec.encode(self.claims)
        result = self.codec.decode(token, self.binding, 1100)
        result["last"][0] = "changed"
        self.assertEqual("family", self.codec.decode(token, self.binding, 1100)["last"][0])

    def test_bad_host_input_fails(self):
        with self.assertRaises(ValueError):
            self.codec.encode(dict(self.claims, expires_at=1901))
        with self.assertRaises(ValueError):
            self.codec.decode("invalid", {}, 1100)


if __name__ == "__main__":
    unittest.main()
