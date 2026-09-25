import json
import unittest

from sbc_tools.corpus import CorpusInput, corpus_digest
from sbc_tools.observation_sets import build_observation_set
from sbc_tools.observations import check_observation
from test_observations import observation_samples


def mounted_samples():
    args, _ = observation_samples()
    records = (CorpusInput('child', 'note.md', 'b' * 64),)
    args['corpus_records'] = records
    rows = [dict(repository_id=owner, availability='available', observed_head='1' * 40,
                 checkout_state='clean', corpus_sha256=corpus_digest(r for r in records if r.repository_id == owner))
            for owner in ('fixture', 'child')]
    relations = [dict(parent_repository_id='fixture', path='child', repository_id='child',
                      parent_commit='1' * 40, recorded_child_commit='1' * 40, pin_state='match')]
    args['observation_set'] = json.loads(build_observation_set(root_repository_id='fixture',
        participants=rows, relations=relations, complete=True))
    return args


class MountedObservationTests(unittest.TestCase):
    def test_v2_complete_set_is_copied_and_committed_ids_stay_null(self):
        args = mounted_samples()
        result = check_observation(**args)
        args['observation_set']['participants'].clear()
        self.assertEqual(2, result['schema_version'])
        self.assertEqual(2, len(result['observation']['participants']))
        self.assertEqual([], result['selection']['dependencies'])
        self.assertIsNone(result['selection']['source_commit'])
        self.assertIsNone(result['selection']['projection_commit'])

    def test_unrelated_or_changed_records_reject(self):
        args = mounted_samples()
        for records in ((), (CorpusInput('foreign', 'note.md', 'b' * 64),),
                        (CorpusInput('child', 'note.md', 'c' * 64),), args['corpus_records'] * 2):
            with self.subTest(records=records), self.assertRaises(ValueError):
                check_observation(**dict(args, corpus_records=records))

    def test_wrong_root_or_incomplete_or_tampered_set_reject(self):
        args = mounted_samples()
        with self.assertRaises(ValueError): check_observation(**dict(args, repository_id='child'))
        args['observation_set']['complete'] = False
        args['observation_set']['selection_sha256'] = None
        with self.assertRaises(ValueError): check_observation(**args)
        args = mounted_samples()
        args['observation_set']['selection_sha256'] = '0' * 64
        with self.assertRaises(ValueError): check_observation(**args)

    def test_unavailable_reference_preserves_complete_observation(self):
        args = mounted_samples()
        result = check_observation(**dict(args, reference_files=None))
        self.assertEqual((2, 3), (result['schema_version'], result['exit_code']))
        self.assertTrue(result['observation']['complete'])
        self.assertIsNotNone(result['selection'])
        self.assertIsNone(result['result'])

    def test_context_identity_is_separate_from_projection_snapshot(self):
        args = mounted_samples()
        first = check_observation(**args)
        value = args['observation_set']
        value['participants'][0]['checkout_state'] = 'dirty'
        args['observation_set'] = json.loads(build_observation_set(root_repository_id='fixture',
            participants=value['participants'], relations=value['relations'], complete=True))
        second = check_observation(**args)
        self.assertEqual(first['selection']['snapshot_id'], second['selection']['snapshot_id'])
        self.assertNotEqual(first['observation']['selection_sha256'], second['observation']['selection_sha256'])
