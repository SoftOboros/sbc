"""Publication boundary tests; no network or upload is performed."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

from check_release_artifact import source_version, validate


class ReleaseArtifactTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        (self.root/'dist').mkdir()
        self.version = source_version()
        self.wheel = self.root/'dist'/f'softoboros_sbc-{self.version}-py3-none-any.whl'
        self.matrix = {'status':'passed','source_sha':'a'*40,
                       'checks':{key:{'exit_code':0} for key in ('core','packaging','provider','installed')}}
        self.write_wheel()
        self.write_matrix()

    def write_matrix(self):
        (self.root/'matrix.json').write_text(json.dumps(self.matrix),encoding='utf-8')

    def write_wheel(self, *, name='softoboros-sbc', tag='py3-none-any', native=False):
        prefix = f'softoboros_sbc-{self.version}.dist-info/'
        with zipfile.ZipFile(self.wheel,'w') as archive:
            archive.writestr(prefix+'METADATA',f'Metadata-Version: 2.4\nName: {name}\nVersion: {self.version}\n')
            archive.writestr(prefix+'WHEEL',f'Wheel-Version: 1.0\nRoot-Is-Purelib: true\nTag: {tag}\n')
            if native: archive.writestr('fixture.pyd',b'non-executable sentinel')
        installed = {'distribution':'softoboros-sbc','wheel':self.wheel.name,
                     'sha256':hashlib.sha256(self.wheel.read_bytes()).hexdigest()}
        (self.root/'installed.json').write_text(json.dumps(installed),encoding='utf-8')

    def verify(self, **changes):
        args = dict(version=self.version,source_sha='a'*40,tag='tools-v'+self.version)
        args.update(changes)
        return validate(self.root,**args)

    def test_accepts_exact_tested_artifact(self):
        self.assertEqual(hashlib.sha256(self.wheel.read_bytes()).hexdigest(),self.verify()['sha256'])

    def test_tag_version_and_revision_mismatches_reject(self):
        for changes in ({'tag':'main'},{'version':'9.9.9'},{'source_sha':'b'*40},{'source_sha':''}):
            with self.subTest(changes=changes), self.assertRaises(ValueError): self.verify(**changes)

    def test_failed_or_incomplete_checks_reject(self):
        self.matrix['checks']['provider']['exit_code'] = 1
        self.write_matrix()
        with self.assertRaises(ValueError): self.verify()
        del self.matrix['checks']['provider']
        self.write_matrix()
        with self.assertRaises(ValueError): self.verify()

    def test_unpassed_matrix_rejects(self):
        self.matrix['status'] = 'failed'
        self.write_matrix()
        with self.assertRaises(ValueError): self.verify()

    def test_tampered_wheel_rejects(self):
        self.wheel.write_bytes(self.wheel.read_bytes()+b'changed')
        with self.assertRaises(ValueError): self.verify()

    def test_extra_distribution_rejects(self):
        (self.root/'dist/extra.whl').write_bytes(b'extra')
        with self.assertRaises(ValueError): self.verify()

    def test_wrong_metadata_or_native_archive_rejects_even_with_matching_hash(self):
        for changes in ({'name':'other-package'},{'tag':'cp314-cp314-win_amd64'},{'native':True}):
            with self.subTest(changes=changes):
                self.write_wheel(**changes)
                with self.assertRaises(ValueError): self.verify()
