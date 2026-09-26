"""Collect matrix evidence using the existing offline runtime witnesses."""
import argparse
import ctypes
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys
import urllib.request

from check_git_provider import PINS
from check_installed_distribution import BUILD_PINS, verify_wheel


def acquire(directory, pins, *, build_tools=False):
    directory.mkdir(parents=True, exist_ok=True)
    for filename, digest in pins.items():
        path = directory/filename
        if not path.exists():
            package, version = filename.split('-')[:2]
            request = urllib.request.Request(
                f'https://pypi.org/pypi/{package}/{version}/json',
                headers={'User-Agent':'softoboros-sbc-verification'})
            with urllib.request.urlopen(request, timeout=60) as response:
                release = json.load(response)
            candidate = next(item for item in release['urls'] if item['filename'] == filename)
            if candidate['digests']['sha256'] != digest:
                raise ValueError('PyPI artifact differs from the approved hash: '+filename)
            if not candidate['url'].startswith('https://files.pythonhosted.org/'):
                raise ValueError('Unexpected wheel download origin')
            with urllib.request.urlopen(candidate['url'], timeout=120) as response:
                raw = response.read()
            if hashlib.sha256(raw).hexdigest() != digest:
                raise ValueError('Downloaded wheel hash mismatch')
            path.write_bytes(raw)
        verify_wheel(path, digest, build_tool=build_tools)


def run(work, *, provider_wheels=None, build_wheels=None):
    root = Path(__file__).resolve().parents[1]
    work.mkdir(parents=True, exist_ok=True)
    evidence = work/'evidence'
    evidence.mkdir(exist_ok=False)
    report = {'status':'running', 'source_sha':os.environ.get('GITHUB_SHA'),
              'run_id':os.environ.get('GITHUB_RUN_ID'), 'python':platform.python_version(),
              'platform':platform.platform(), 'machine':platform.machine(),
              'administrator_token':bool(ctypes.windll.shell32.IsUserAnAdmin()) if os.name == 'nt' else None,
              'uid':os.getuid() if hasattr(os,'getuid') else None, 'checks':{}}

    def execute(name, arguments):
        completed = subprocess.run([str(item) for item in arguments], cwd=root,
                                   capture_output=True, text=True, encoding='utf-8')
        (evidence/(name+'.stdout')).write_text(completed.stdout, encoding='utf-8')
        (evidence/(name+'.stderr')).write_text(completed.stderr, encoding='utf-8')
        report['checks'][name] = {'exit_code':completed.returncode}
        if completed.returncode:
            raise RuntimeError(name+' failed:\n'+completed.stderr[-6000:])
        return completed

    try:
        provider = provider_wheels or work/'provider-wheels'
        builder = build_wheels or work/'build-wheels'
        acquire(provider, PINS)
        acquire(builder, BUILD_PINS, build_tools=True)
        core = execute('core', [sys.executable,'-I','-S','-c',
            "import sys,unittest; sys.path.insert(0,'src'); "
            "r=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.discover('tests')); "
            "sys.exit(not r.wasSuccessful())"])
        packaging = execute('packaging', [sys.executable,'-I','-S','-c',
            "import sys,unittest; sys.path.insert(0,'tools'); "
            "r=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.discover('tests_tools')); "
            "sys.exit(not r.wasSuccessful())"])
        provider_result = execute('provider', [sys.executable,'-I','-S',
                                               root/'tools/check_git_provider.py',provider])
        for name, result in [('core',core),('packaging',packaging),('provider',provider_result)]:
            count = re.search(r'Ran (\d+) tests?', result.stderr)
            if count is None:
                raise ValueError('Missing unittest execution count: '+name)
            skips = [line for line in result.stderr.splitlines() if '... skipped ' in line]
            report['checks'][name].update(tests_run=int(count[1]),skips=skips)
            if any(os.name == 'nt' or "skipped 'Windows junction witness'" not in line for line in skips):
                raise ValueError('An applicable matrix witness was skipped: '+name)
        installed = execute('installed', [sys.executable,root/'tools/check_installed_distribution.py',
                                           builder,provider,'--artifacts-directory',evidence/'dist'])
        installed_report = json.loads(installed.stdout)
        (evidence/'installed.json').write_text(json.dumps(installed_report,indent=2)+'\n',encoding='utf-8')
        report['status'] = 'passed'
        return report
    finally:
        if report['status'] != 'passed': report['status'] = 'failed'
        (evidence/'matrix.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--work-dir', type=Path, required=True)
    parser.add_argument('--provider-wheels', type=Path)
    parser.add_argument('--build-wheels', type=Path)
    args = parser.parse_args()
    print(json.dumps(run(args.work_dir.resolve(),
                         provider_wheels=args.provider_wheels.resolve() if args.provider_wheels else None,
                         build_wheels=args.build_wheels.resolve() if args.build_wheels else None),indent=2))
