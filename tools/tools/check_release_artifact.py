"""Validate a tested wheel before forwarding it to the isolated publisher job."""
import argparse
import ast
from email.parser import BytesParser
import hashlib
import json
from pathlib import Path
import zipfile

from check_installed_distribution import verify_wheel


def source_version():
    source = Path(__file__).resolve().parents[1]/'src/sbc_tools/__init__.py'
    module = ast.parse(source.read_text(encoding='utf-8'))
    for node in module.body:
        if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id == '__version__' for t in node.targets):
            return ast.literal_eval(node.value)
    raise ValueError('Source version missing')


def validate(directory, *, version, source_sha, tag):
    if not source_sha or tag != 'tools-v'+version or version != source_version():
        raise ValueError('Tag, requested version and source version must match')
    matrix = json.loads((directory/'matrix.json').read_bytes())
    installed = json.loads((directory/'installed.json').read_bytes())
    if matrix['status'] != 'passed' or matrix['source_sha'] != source_sha:
        raise ValueError('Artifact is not verified at the publishing revision')
    if set(matrix['checks']) != {'core','packaging','provider','installed'} or any(
            result['exit_code'] != 0 for result in matrix['checks'].values()):
        raise ValueError('Required matrix checks did not pass')
    members = list((directory/'dist').iterdir())
    expected = f'softoboros_sbc-{version}-py3-none-any.whl'
    if len(members) != 1 or members[0].name != expected or not members[0].is_file():
        raise ValueError('Expected exactly the named universal distribution wheel')
    wheel = members[0]
    if installed['distribution'] != 'softoboros-sbc' or installed['wheel'] != expected:
        raise ValueError('Installed witness distribution does not match')
    verify_wheel(wheel,installed['sha256'])
    with zipfile.ZipFile(wheel) as archive:
        metadata_paths = [p for p in archive.namelist() if p.endswith('.dist-info/METADATA')]
        wheel_paths = [p for p in archive.namelist() if p.endswith('.dist-info/WHEEL')]
        if len(metadata_paths) != 1 or len(wheel_paths) != 1:
            raise ValueError('Ambiguous wheel metadata')
        metadata = BytesParser().parsebytes(archive.read(metadata_paths[0]))
        wheel_metadata = BytesParser().parsebytes(archive.read(wheel_paths[0]))
        if metadata['Name'] != 'softoboros-sbc' or metadata['Version'] != version:
            raise ValueError('Wheel name/version does not match release')
        if wheel_metadata.get_all('Tag') != ['py3-none-any'] or wheel_metadata['Root-Is-Purelib'] != 'true':
            raise ValueError('Distribution is not the approved pure wheel shape')
    return {'distribution':'softoboros-sbc','version':version,'source_sha':source_sha,
            'wheel':expected,'sha256':hashlib.sha256(wheel.read_bytes()).hexdigest()}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--artifact-dir', type=Path, required=True)
    parser.add_argument('--version', required=True)
    parser.add_argument('--source-sha', required=True)
    parser.add_argument('--tag', required=True)
    args = parser.parse_args()
    print(json.dumps(validate(args.artifact_dir,version=args.version,source_sha=args.source_sha,tag=args.tag),indent=2))
