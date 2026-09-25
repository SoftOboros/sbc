"""Validate actual explicit-host mounted CLI test results against wire schemas."""
import argparse
import json
from pathlib import Path
import sys
import unittest

import jsonschema
from referencing import Registry, Resource
from check_git_provider import load_verified_wheels, reject_process_and_network


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('wheel_directory', type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    contracts = root.parent / 'docs/sbc-tools/contracts'
    observation = json.loads((contracts / 'observation-set.schema.json').read_bytes())
    envelope = json.loads((contracts / 'cli-observation-envelope.schema.json').read_bytes())
    registry = Registry().with_resource(observation['$id'], Resource.from_contents(observation))
    validator = jsonschema.Draft202012Validator(envelope, registry=registry)
    load_verified_wheels(args.wheel_directory)
    sys.path.insert(0, str(root / 'src'))
    sys.path.insert(0, str(root / 'tests_git'))
    sys.addaudithook(reject_process_and_network)
    from test_mounted_working_cli import MountedWorkingCLITests
    result = unittest.TestResult()
    envelopes = []
    for name in unittest.defaultTestLoader.getTestCaseNames(MountedWorkingCLITests):
        case = MountedWorkingCLITests(name)
        original = case.invoke
        def invoke(command='scan', original=original):
            code, value = original(command)
            validator.validate(value)
            envelopes.append(value)
            return code, value
        case.invoke = invoke
        case.run(result)
    if not result.wasSuccessful():
        for _, error in result.errors + result.failures:
            print(error, file=sys.stderr)
        return 1
    print(json.dumps(dict(tests=result.testsRun, validated_cli_envelopes=len(envelopes),
                          schema_version=2, installed_console_launcher=False), indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())
