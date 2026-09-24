import copy
import json
import unittest

from sbc_tools.observation_sets import build_observation_set, observation_set_bytes


def participant(name,head):
    return dict(repository_id=name,availability='available',observed_head=head*40,
                checkout_state='dirty',corpus_sha256='a'*64)


def relation(parent,child,context,pin):
    return dict(parent_repository_id=parent,path='vendor/'+child,repository_id=child,
                parent_commit=context*40,recorded_child_commit=pin*40,pin_state='mismatch')


class ObservationSetTests(unittest.TestCase):
    def setUp(self):
        self.args = dict(root_repository_id='root',complete=True,
            participants=[participant('root','1'),participant('child','2'),participant('leaf','3')],
            relations=[relation('root','child','1','4'),relation('child','leaf','2','5')])

    def build(self): return build_observation_set(**self.args)

    def test_nested_mismatch_uses_observed_parent_and_stable_sorted_identity(self):
        first = self.build()
        self.args['participants'].reverse()
        self.args['relations'].reverse()
        self.assertEqual(first,self.build())
        self.assertEqual(first,observation_set_bytes(json.loads(first)))
        self.args['participants'][0]['checkout_state'] = 'clean'
        self.assertNotEqual(first,self.build())
        self.assertEqual('dirty',json.loads(first)['participants'][1]['checkout_state'])

    def test_false_match_wrong_nested_context_and_unsafe_path_reject(self):
        original = copy.deepcopy(self.args)
        for field,value in (('pin_state','match'),('parent_commit','4'*40),('path','../outside')):
            self.args = copy.deepcopy(original)
            self.args['relations'][1][field] = value
            with self.subTest(field=field),self.assertRaises(ValueError): self.build()

    def test_duplicates_missing_parent_and_cycle_reject(self):
        original = copy.deepcopy(self.args)
        self.args['participants'].append(participant('child','2'))
        with self.assertRaises(ValueError): self.build()
        self.args = copy.deepcopy(original)
        self.args['relations'].pop()
        with self.assertRaises(ValueError): self.build()
        self.args = copy.deepcopy(original)
        self.args['relations'][0] = relation('leaf','child','3','4')
        with self.assertRaisesRegex(ValueError,'cycle'): self.build()

    def test_missing_ancestor_blocks_descendants_without_fabricated_values(self):
        self.args['complete'] = False
        self.args['participants'][1].update(availability='missing_checkout',observed_head=None,
                                            checkout_state='unknown',corpus_sha256=None)
        self.args['participants'][2].update(availability='blocked_by_ancestor',observed_head=None,
                                            checkout_state='unknown',corpus_sha256=None)
        self.args['relations'][0]['pin_state'] = 'unavailable'
        self.args['relations'][1].update(pin_state='unavailable',parent_commit=None,recorded_child_commit=None)
        result = json.loads(self.build())
        self.assertIsNone(result['selection_sha256'])
        self.args['participants'][2]['availability'] = 'missing_checkout'
        with self.assertRaisesRegex(ValueError,'ancestor'): self.build()

    def test_complete_cannot_include_unavailable_relation(self):
        self.args['relations'][0]['pin_state'] = 'unavailable'
        with self.assertRaises(ValueError): self.build()

    def test_digest_tampering_unknown_fields_and_boolean_version_reject(self):
        original = json.loads(self.build())
        for update in ({'selection_sha256':'0'*64},{'extra':True},{'schema_version':True}):
            with self.subTest(update=update),self.assertRaises(ValueError):
                observation_set_bytes(dict(original,**update))

    def test_unavailable_state_cannot_claim_observed_head(self):
        self.args['complete'] = False
        self.args['participants'][1]['availability'] = 'unavailable_history'
        with self.assertRaises(ValueError): self.build()
