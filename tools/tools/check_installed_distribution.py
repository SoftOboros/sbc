"""Build/install/execute a disposable distribution offline after wheel acquisition.

Preparation may start Python/pip processes. Installed command executions reject
process and network operations through a sitecustomize audit hook. No source or
runtime environment in the checkout is installed into or modified.
"""
import argparse
import hashlib
import inspect
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import venv
import zipfile

sys.path.insert(0,str(Path(__file__).resolve().parent))
from check_git_provider import PINS, load_verified_wheels, reject_process_and_network

BUILD_PINS = {
    'setuptools-84.0.0-py3-none-any.whl':'51a52592b3b99e102b609654876bd65f19f999935166d1352678931132b0c670',
    'wheel-0.48.0-py3-none-any.whl':'3217dcc807155e45db462d7ef2431f5ddda0d7273b700d05a67b271ceb1287ab',
    'packaging-26.3-py3-none-any.whl':'d7193f7c8e4e93f444fde0262bf90af30e16fa0ad0ad44cb553c87339b23cd1c',
}


def verify_wheel(path, digest, *, build_tool=False):
    if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
        raise ValueError('Unexpected wheel: '+path.name)
    with zipfile.ZipFile(path) as archive:
        forbidden = {'.pyd','.so','.dll','.dylib','.a','.lib'}
        if not build_tool:
            forbidden.add('.exe')
        # Build tools may carry installer launcher resources; runtime wheels may not.
        if any(Path(p).suffix.lower() in forbidden
               for p in archive.namelist()):
            raise ValueError('Native member in '+path.name)


def verify(build_wheels, provider_wheels):
    root = Path(__file__).resolve().parents[1]
    for name,digest in BUILD_PINS.items(): verify_wheel(build_wheels/name,digest,build_tool=True)
    for name,digest in PINS.items(): verify_wheel(provider_wheels/name,digest)
    with tempfile.TemporaryDirectory(prefix='sbct-installed-') as temp:
        work = Path(temp)
        def python_at(env): return env/('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
        def environment(env):
            value = {k:os.environ[k] for k in ('SYSTEMROOT','WINDIR','TEMP','TMP') if k in os.environ}
            value.update(PATH=str(python_at(env).parent),PYTHONNOUSERSITE='1',
                         PIP_CONFIG_FILE=os.devnull,PIP_DISABLE_PIP_VERSION_CHECK='1')
            return value
        def run(args, env, expected=0):
            result = subprocess.run([str(a) for a in args],cwd=work,env=environment(env),
                                    capture_output=True,text=True,encoding='utf-8')
            if result.returncode != expected:
                raise RuntimeError(f'Process exit {result.returncode}, expected {expected}: {result.stderr[-1600:]} {result.stdout[-600:]}')
            return result.stdout
        build_env, runtime = work/'builder',work/'runtime'
        for env in (build_env,runtime): venv.EnvBuilder(with_pip=True).create(env)
        run([python_at(build_env),'-m','pip','install','--no-index','--no-deps',
             *[build_wheels/p for p in BUILD_PINS]],build_env)
        source = work/'source'
        source.mkdir()
        for name in ('pyproject.toml','README.md','LICENSE'):
            shutil.copyfile(root/name,source/name)
        shutil.copytree(root/'src',source/'src',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
        dist = work/'dist'
        run([python_at(build_env),'-m','pip','wheel','--no-index','--no-deps','--no-build-isolation',
             '--wheel-dir',dist,source],build_env)
        wheels = list(dist.glob('*.whl'))
        if len(wheels) != 1 or not wheels[0].name.endswith('-py3-none-any.whl'):
            raise ValueError('Expected one pure distribution wheel')
        wheel = wheels[0]
        wheel_sha = hashlib.sha256(wheel.read_bytes()).hexdigest()
        verify_wheel(wheel,wheel_sha)
        with zipfile.ZipFile(wheel) as archive:
            names = archive.namelist()
            entry = next(n for n in names if n.endswith('.dist-info/entry_points.txt'))
            if 'sbc-tools = sbc_tools.cli:main' not in archive.read(entry).decode():
                raise ValueError('Missing console entry point')
        run([python_at(runtime),'-m','pip','install','--no-index','--no-deps',wheel,
             *[provider_wheels/p for p in PINS]],runtime)
        run([python_at(runtime),'-m','pip','check'],runtime)
        packages = json.loads(run([python_at(runtime),'-m','pip','list','--format=json'],runtime))
        if any(p['name'].lower() in {'django','setuptools','wheel','packaging'} for p in packages):
            raise ValueError('Runtime contains undeclared framework/build tooling')
        site = Path(run([python_at(runtime),'-I','-c',
                         'import sysconfig; print(sysconfig.get_path("purelib"))'],runtime).strip())
        (site/'sitecustomize.py').write_bytes(('import sys\n'+inspect.getsource(reject_process_and_network)
                                              +'\nsys.addaudithook(reject_process_and_network)\n').encode())
        origin = run([python_at(runtime),'-I','-c','import sbc_tools; print(sbc_tools.__file__)'],runtime).strip()
        if not Path(origin).is_relative_to(runtime): raise ValueError('Source checkout shadowed installation')
        negative = """import subprocess, socket
for action in (lambda: subprocess.run(['unavailable-command']), lambda: socket.getaddrinfo('example.invalid',443)):
    try: action()
    except RuntimeError: pass
    else: raise AssertionError('Audit control missing')
print('blocked')
"""
        run([python_at(runtime),'-I','-c',negative],runtime)
        command = python_at(runtime).parent/('sbc-tools.exe' if os.name == 'nt' else 'sbc-tools')
        version = run([command,'--version'],runtime).strip()
        run([command,'--help'],runtime)
        invocation = json.loads(run([command,'check','--config','unused.toml','--format=json'],runtime,2))
        assert invocation['error']['code'] == 'invalid_invocation'
        # Fixture preparation uses source test helpers; child processes use only the installation.
        load_verified_wheels(provider_wheels)
        sys.path[:0] = [str(root/'src'),str(root/'tests_git')]
        from test_console_host import ConsoleHostTests
        fixture = ConsoleHostTests()
        try:
            fixture.setUp()
            args = ['--config',fixture.registration.configuration_file,'--host',fixture.host_path,'--format=json']
            scan = json.loads(run([command,'scan',*args],runtime,1))
            assert scan['result']['publication'] == 'published'
            fixture.commit_output()
            check = json.loads(run([command,'check',*args],runtime,1))
            assert check['result']['comparison'] == 'equal'
            assert scan['selection']['snapshot_id'] == check['selection']['snapshot_id']
            module = json.loads(run([python_at(runtime),'-I','-m','sbc_tools','check',*args],runtime,1))
            assert module == check
            working_config = fixture.config.replace(b'mode = "committed"',b'mode = "working-tree"')
            fixture.registration.configuration_file.write_bytes(working_config)
            fixture.binding['config_sha256'] = hashlib.sha256(working_config).hexdigest()
            fixture.write()
            observed_scan = json.loads(run([command,'scan',*args],runtime,1))
            observed_check = json.loads(run([command,'check',*args],runtime,1))
            for observed in (observed_scan,observed_check):
                assert observed['mode'] == 'working-tree'
                assert observed['selection']['source_commit'] is None
                assert observed['selection']['projection_commit'] is None
            assert observed_scan['result']['publication'] == 'published'
            assert observed_check['result']['comparison'] == 'equal'
            fixture.binding['approved_authority_sha256'] = '0'*64
            fixture.write()
            rejected = json.loads(run([command,'scan',*args],runtime,2))
            assert rejected['error']['code'] == 'invalid_authority'
        finally:
            fixture.doCleanups()
        return {'wheel':wheel.name,'sha256':wheel_sha,'version':version,
                'runtime_packages':packages,'build_wheels':BUILD_PINS,'provider_wheels':PINS,
                'checks':['pure wheel and console metadata','offline installation and pip check',
                          'installed import origin','process/network audit negative controls',
                          'actual console launcher help/version/invocation error',
                          'console scan/commit/check','module and launcher envelope parity',
                          'wrong authority pin rejection','working-tree console scan/check with null commit IDs'],
                'scope':'Local disposable environment; fixture approvals only; no release or gate closure'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('build_wheels',type=Path)
    parser.add_argument('provider_wheels',type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(args.build_wheels.resolve(),args.provider_wheels.resolve()),indent=2))
