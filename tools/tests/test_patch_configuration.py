import difflib
import hashlib
from pathlib import Path
import tempfile
import unittest

from sbc_tools.authority import PATCH_ROLES, VerifiedAuthorityInputs
from sbc_tools.configuration import validate_configuration
from sbc_tools.patches import verify_support_patch


class PatchTests(unittest.TestCase):
    def setUp(self):
        self.base = {role:b"before\ncontext\n" for role in PATCH_ROLES}
        self.result = {role:b"after\ncontext\n" for role in PATCH_ROLES}
        self.patch = "".join("".join(difflib.unified_diff(
            self.base[r].decode().splitlines(True), self.result[r].decode().splitlines(True),
            fromfile="a/"+r, tofile="b/"+r)) for r in sorted(PATCH_ROLES)).encode()
        self.pins = {r:hashlib.sha256(b).hexdigest() for r,b in self.result.items()}

    def verify(self, patch=None, base=None, pins=None, digest=None):
        patch = self.patch if patch is None else patch
        inputs = VerifiedAuthorityInputs("0"*64, digest or hashlib.sha256(patch).hexdigest(), self.base if base is None else base)
        return verify_support_patch(inputs, patch, approved_result_sha256=self.pins if pins is None else pins)

    def test_exact_support_patch_and_immutable_result(self):
        result = self.verify()
        self.assertEqual(self.result, dict(result))
        with self.assertRaises(TypeError): result["README.md"] = b"x"
        self.assertEqual(b"before\ncontext\n", self.base["README.md"])

    def test_wrong_patch_or_result_hash(self):
        with self.assertRaises(ValueError): self.verify(digest="0"*64)
        pins = dict(self.pins, **{"README.md":"0"*64})
        with self.assertRaises(ValueError): self.verify(pins=pins)

    def test_wrong_context_and_hunk_positions(self):
        base = dict(self.base, **{"README.md":b"different\ncontext\n"})
        with self.assertRaises(ValueError): self.verify(base=base)
        for patch in (self.patch.replace(b"@@ -1,2 +1,2 @@", b"@@ -9,2 +1,2 @@"),
                      self.patch.replace(b"@@ -1,2 +1,2 @@", b"@@ -1,2 +2,2 @@"), self.patch[:-5]):
            with self.subTest(patch=patch[:30]), self.assertRaises(ValueError): self.verify(patch)

    def test_forbidden_role_rename_duplicate_and_missing(self):
        first = self.patch.split(b"--- a/CLAUDE.md")[0]
        for patch in (self.patch.replace(b"AGENTS.md",b"scan.py"),
                      self.patch.replace(b"+++ b/AGENTS.md",b"+++ b/README.md"),
                      self.patch + first, first):
            with self.subTest(patch=patch[:30]), self.assertRaises(ValueError): self.verify(patch)


class ConfigurationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root/"docs").mkdir()
        (self.root/"docs/nested").mkdir()
        (self.root/"authority.json").write_bytes(b"{}")
        (self.root/"registry.md").write_bytes(b"registry")
        self.raw = '''schema_version = 1
repository_id = "fixture"
repository_root = "."
source_roots = ["docs"]
exclude = []
registry_paths = ["registry.md"]
output_root = "output"
tracked_ref = "HEAD"
mode = "committed"
capabilities = ["scan", "check"]
authority_manifest = "authority.json"
submodules = []
'''

    def verify(self, raw=None, mapping=None):
        return validate_configuration((raw or self.raw).encode(), config_directory=self.root,
            registered_repositories={"fixture":self.root} if mapping is None else mapping)

    def test_valid_configuration_is_immutable(self):
        result = self.verify()
        self.assertEqual(self.root.resolve(),result.repository_root)
        self.assertEqual(("docs",),result.values["source_roots"])
        with self.assertRaises(TypeError): result.values["mode"] = "other"

    def test_missing_unknown_duplicate_and_boolean_keys(self):
        for raw in (self.raw.replace('mode = "committed"\n',''), self.raw+'extra = 1\n',
                    self.raw+'mode = "committed"\n', self.raw.replace('schema_version = 1','schema_version = true')):
            with self.subTest(raw=raw[-20:]), self.assertRaises(ValueError): self.verify(raw)

    def test_invalid_paths_overlap_missing_and_exclusions(self):
        replacements = [('source_roots = ["docs"]','source_roots = ["../escape"]'),
            ('source_roots = ["docs"]','source_roots = ["absent"]'),
            ('source_roots = ["docs"]','source_roots = ["docs", "docs/nested"]'),
            ('output_root = "output"','output_root = "docs/generated"'),
            ('authority_manifest = "authority.json"','authority_manifest = "missing.json"'),
            ('exclude = []','exclude = ["registry.md"]'),
            ('exclude = []','exclude = [".git"]')]
        for old,new in replacements:
            with self.subTest(new=new), self.assertRaises(ValueError): self.verify(self.raw.replace(old,new))

    def test_registered_identity_required(self):
        with self.assertRaises(ValueError): self.verify(mapping={})
        with self.assertRaises(ValueError): self.verify(mapping={"fixture":self.root/"docs"})

    def test_ref_syntax(self):
        for ref in ("refs/heads/main", "refs/tags/v1", "a"*40, "a"*64):
            self.verify(self.raw.replace('"HEAD"', '"'+ref+'"'))
        for ref in ("main", "HEAD~1", "refs/heads/", "refs/heads/a..b", "refs/heads/a.lock", "refs/heads/a@{1}"):
            with self.subTest(ref=ref), self.assertRaises(ValueError): self.verify(self.raw.replace('"HEAD"', '"'+ref+'"'))

    def test_mount_and_capability_duplicates(self):
        for raw in (self.raw.replace('["scan", "check"]','["scan", "scan"]'),
                    self.raw.replace('submodules = []','submodules = [{path="child", repository_id="fixture"}]')):
            with self.assertRaises(ValueError): self.verify(raw)


if __name__ == "__main__": unittest.main()
