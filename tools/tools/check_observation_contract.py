"""Offline structural checks for draft schemas; no runtime conformance claim."""
import argparse
import copy
import json
import hashlib
import unicodedata
from pathlib import Path
import jsonschema
from referencing import Registry, Resource

parser = argparse.ArgumentParser()
parser.add_argument('contracts',type=Path)
args = parser.parse_args()
def read(name): return json.loads((args.contracts/name).read_bytes())
observation = read('observation-set.schema.json')
envelope = read('cli-observation-envelope.schema.json')
for schema in (observation,envelope): jsonschema.Draft202012Validator.check_schema(schema)
registry = Registry().with_resource(observation['$id'],Resource.from_contents(observation))
validator = jsonschema.Draft202012Validator(envelope,registry=registry)
complete = read('cli-observation-envelope.example.json')
unavailable = copy.deepcopy(complete)
unavailable.update(status='error',exit_code=3,selection=None,result=None,
                   error={'code':'evidence_unavailable','message':'Required evidence is unavailable.'})
unavailable['observation'].update(complete=False,selection_sha256=None)
unavailable['observation']['participants'][0].update(availability='missing_checkout',
    observed_head=None,checkout_state='unknown',corpus_sha256=None)
unavailable['observation']['relations'][0]['pin_state'] = 'unavailable'
early = copy.deepcopy(unavailable)
early.update(exit_code=2,observation=None,error={'code':'invalid_configuration','message':'Invalid repository configuration.'})
for value in (complete,unavailable,early): validator.validate(value)
negative = []
def changed(path,value,base=complete):
    item = copy.deepcopy(base)
    target = item
    for key in path[:-1]: target = target[key]
    target[path[-1]] = value
    negative.append(item)
changed(['schema_version'],1)
changed(['mode'],'committed')
changed(['selection','source_commit'],'1'*40)
changed(['selection','dependencies'],[complete['observation']['relations'][0]])
changed(['observation','extra'],True)
changed(['observation','participants',0,'availability'],'missing_checkout')
changed(['observation','participants',0,'checkout_state'],'unknown')
changed(['observation','relations',0,'recorded_child_commit'],None)
for path in ('../escape','a//b','a/./b','C:/outside','.git/objects','/absolute'):
    changed(['observation','relations',0,'path'],path)
changed(['observation','complete'],False)
changed(['observation','selection_sha256'],'a'*64,unavailable)
changed(['selection'],complete['selection'],unavailable)
changed(['observation'],None)
for number,item in enumerate(negative):
    if validator.is_valid(item): raise AssertionError(f'Negative case accepted: {number}')
def digest(value):
    payload = {k:v for k,v in value.items() if k != 'selection_sha256'}
    return hashlib.sha256((json.dumps(payload,sort_keys=True,separators=(',',':'),
                                     ensure_ascii=False)+'\n').encode()).hexdigest()


def check_complete_semantics(value):
    # Developer review witness only: this is not the runtime observation validator.
    rows, edges = value['participants'], value['relations']
    ids = [r['repository_id'] for r in rows]
    assert ids == sorted(set(ids))
    assert all(unicodedata.normalize('NFC',x) == x for x in ids)
    root = value['root_repository_id']
    assert root in ids
    by_id = {r['repository_id']:r for r in rows}
    keys = [(e['parent_repository_id'],e['path']) for e in edges]
    assert keys == sorted(set(keys))
    parents = {}
    for edge in edges:
        parent,child = edge['parent_repository_id'],edge['repository_id']
        assert parent in by_id and child in by_id and child != root and child not in parents
        parents[child] = parent
        expected = 'match' if edge['recorded_child_commit'] == by_id[child]['observed_head'] else 'mismatch'
        assert edge['pin_state'] == expected
        if parent != root:
            assert edge['parent_commit'] == by_id[parent]['observed_head']
    assert set(parents) == set(ids)-{root}
    for child in parents:
        seen = set()
        while child != root:
            assert child not in seen and child in parents
            seen.add(child)
            child = parents[child]
    assert value['selection_sha256'] == digest(value)

check_complete_semantics(complete['observation'])
semantic_negative = []
for mutation in ('digest','false_match','missing_root','duplicate_id','missing_edge','unknown_parent','duplicate_edge','unsorted'):
    item = copy.deepcopy(complete['observation'])
    if mutation == 'digest': item['selection_sha256'] = '0'*64
    elif mutation == 'false_match': item['relations'][0]['pin_state'] = 'match'
    elif mutation == 'missing_root': item['root_repository_id'] = 'absent'
    elif mutation == 'duplicate_id': item['participants'].append(copy.deepcopy(item['participants'][0]))
    elif mutation == 'missing_edge': item['relations'] = []
    elif mutation == 'unknown_parent': item['relations'][0]['parent_repository_id'] = 'absent'
    elif mutation == 'duplicate_edge': item['relations'].append(copy.deepcopy(item['relations'][0]))
    elif mutation == 'unsorted': item['participants'].reverse()
    if mutation != 'digest': item['selection_sha256'] = digest(item)
    semantic_negative.append(item)
for item in semantic_negative:
    try: check_complete_semantics(item)
    except AssertionError: pass
    else: raise AssertionError('Semantic negative accepted')
print(json.dumps({'draft_schema_positive_cases':3,'draft_schema_negative_cases':len(negative),
    'complete_semantic_positive_cases':1,'complete_semantic_negative_cases':len(semantic_negative),
    'scope':'Developer contract checks; filesystem capture, temporal stability and runtime cases not executed'},indent=2))
