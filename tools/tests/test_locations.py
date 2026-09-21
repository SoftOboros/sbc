import hashlib
import io
import json
from pathlib import Path
import unittest
import warnings
import zipfile

from sbc_tools import _producer_locations as locations
from sbc_tools.projections import build_projection_files


def archive_bytes(members, compression=zipfile.ZIP_STORED):
    stream = io.BytesIO()
    with warnings.catch_warnings(), zipfile.ZipFile(stream, 'w', compression=compression) as archive:
        warnings.simplefilter('ignore', UserWarning)
        for path, data in members:
            archive.writestr(path, data)
    return stream.getvalue()


class LocationProjectionTests(unittest.TestCase):
    def test_full_original_wire_vectors(self):
        fixtures = Path(__file__).parent / 'fixtures'
        sources = json.loads((fixtures / 'producer-source-vectors.json').read_bytes())
        expected = json.loads((fixtures / 'projection-wire-vectors.json').read_bytes())
        for case in sources['cases']:
            documents = [(p, 'vectors', text.encode()) for p, text in sorted(case['inputs'].items())
                         if p.startswith('docs/todo/vectors/')]
            wanted = next(c['files'] for c in expected['cases'] if c['name'] == case['name'])
            with self.subTest(case=case['name']):
                files, _ = build_projection_files(documents, registered_prefixes=['VECT'],
                                                  archives={}, archive_families={})
                self.assertEqual({p:t.encode() for p,t in wanted.items()}, files)

    def test_unsafe_duplicate_and_invalid_archives_rejected(self):
        for raw in (b'not a zip', archive_bytes([('../escape.md', b'bad')]),
                    archive_bytes([('same.md', b'one'), ('same.md', b'two')])):
            with self.subTest(raw=raw[:20]), self.assertRaises(locations.LocationProjectionError):
                build_projection_files([], registered_prefixes=[], archives={'history/a.zip':raw},
                                       archive_families={('history/a.zip','same.md'):'example'})

    def test_pinned_archive_limits_enforced(self):
        cases = [([('a.txt', b'aa'), ('b.txt', b'bb')], locations.ArchiveLimits(max_members=1)),
                 ([('a.txt', b'aa')], locations.ArchiveLimits(max_member_bytes=1)),
                 ([('a.txt', b'aa'), ('b.txt', b'bb')], locations.ArchiveLimits(max_total_bytes=3))]
        for members, limits in cases:
            with self.subTest(limits=limits), self.assertRaises(locations.LocationProjectionError):
                locations.scan_archives({'a.zip':archive_bytes(members)}, lambda a,m:'example', limits)
        with self.assertRaises(locations.LocationProjectionError):
            locations.scan_archives({'a.zip':archive_bytes([('a.md',b'x'*10000)],zipfile.ZIP_DEFLATED)},
                                    lambda a,m:'example', locations.ArchiveLimits())

    def test_explicit_family_required_and_bound_to_each_archive(self):
        raw = archive_bytes([('document.md', b'# Example\n\n**Document ID:** EX-00\n')])
        with self.assertRaises(ValueError):
            build_projection_files([], registered_prefixes=[], archives={'a.zip':raw}, archive_families={})
        for family in ('first', 'second'):
            files, _ = build_projection_files([], registered_prefixes=[], archives={'a.zip':raw},
                                              archive_families={('a.zip','document.md'):family})
            self.assertIn('locations/'+family+'.json',files)

    def test_declared_archive_hashes_verified_and_lifecycle_merged(self):
        member = b'# Archived document\n'
        raw = archive_bytes([('document.md', member)])
        columns = locations.LOCATION_COLUMNS
        row = {'Document ID':'EX-00', 'Kind':'archive', 'Path':'history/a.zip', 'Member':'document.md',
               'Archive SHA-256':hashlib.sha256(raw).hexdigest(), 'Member SHA-256':hashlib.sha256(member).hexdigest()}
        text = ('# Declaration\n\n**Document ID:** EX-00\n\n## Location Records\n\n'
                + '| '+' | '.join(columns)+' |\n| '+' | '.join('---' for _ in columns)+' |\n'
                + '| '+' | '.join(row.get(c,'-') for c in columns)+' |\n\n'
                + '## Document Lifecycle\n\n| Document ID | State | Evidence |\n|---|---|---|\n'
                + '| EX-00 | superseded | declared |\n')
        kwargs = dict(registered_prefixes=[], archives={'history/a.zip':raw},
                      archive_families={('history/a.zip','document.md'):'example'})
        files, _ = build_projection_files([('specs/EX-00.md','example',text.encode())], **kwargs)
        self.assertIn(b'"lifecycle_state": "superseded"',files['locations/example.json'])
        self.assertIn(b'"target": "declared"',files['locations/example.json'])
        invalid = text.replace(row['Member SHA-256'], '0'*64)
        with self.assertRaises(locations.LocationProjectionError):
            build_projection_files([('specs/EX-00.md','example',invalid.encode())], **kwargs)


if __name__ == '__main__': unittest.main()
