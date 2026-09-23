"""Developer-only check against the supplied ratified CLI JSON Schema."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import jsonschema

parser = argparse.ArgumentParser()
parser.add_argument('schema',type=Path)
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(root/'src'),str(root/'tests')]
from test_cli_results import sample_envelopes
from test_observations import observation_samples
from sbc_tools.observations import check_observation

raw = args.schema.read_bytes()
validator = jsonschema.Draft202012Validator(json.loads(raw))
args, _ = observation_samples()
envelopes = sample_envelopes() + [check_observation(**args),
    check_observation(**dict(args,reference_files=None))]
observed_scan = check_observation(**args)
observed_scan['command'] = 'scan'
observed_scan['result'].update(publication='published',comparison='not_applicable')
envelopes.append(observed_scan)
for envelope in envelopes:
    validator.validate(envelope)
print(json.dumps({'schema_sha256':hashlib.sha256(raw).hexdigest(),
                  'valid_envelopes':len(envelopes)},indent=2))
