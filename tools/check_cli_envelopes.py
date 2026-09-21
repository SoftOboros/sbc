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

raw = args.schema.read_bytes()
validator = jsonschema.Draft202012Validator(json.loads(raw))
envelopes = sample_envelopes()
for envelope in envelopes:
    validator.validate(envelope)
print(json.dumps({'schema_sha256':hashlib.sha256(raw).hexdigest(),
                  'valid_envelopes':len(envelopes)},indent=2))
