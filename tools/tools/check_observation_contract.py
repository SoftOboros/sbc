"""Offline structural checks for draft schemas; no runtime conformance claim."""
import argparse
import copy
import json
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
print(json.dumps({'draft_schema_positive_cases':3,'draft_schema_negative_cases':len(negative),
    'scope':'Structure only; semantic graph/digest/stability checks and runtime cases not executed'},indent=2))
