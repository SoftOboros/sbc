"""Build/install/execute a disposable distribution offline after wheel acquisition.

Preparation may start Python/pip processes. Installed command executions reject
process and network operations through a virtual-environment audit hook. No source or
runtime environment in the checkout is installed into or modified.
"""
import argparse
from dataclasses import replace
import hashlib
import inspect
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
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


def verify(build_wheels, provider_wheels, *, python=None):
    root = Path(__file__).resolve().parents[1]
    interpreter = Path(python or sys.executable).resolve()
    recipe = root/'requirements-git.txt'
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
        def run(args, env, expected=0, *, include_stderr=False):
            result = subprocess.run([str(a) for a in args],cwd=work,env=environment(env),
                                    capture_output=True,text=True,encoding='utf-8')
            expected_codes = (expected,) if isinstance(expected, int) else expected
            if result.returncode not in expected_codes:
                raise RuntimeError(f'Process exit {result.returncode}, expected {expected}: {result.stderr[-1600:]} {result.stdout[-600:]}')
            return result.stdout + result.stderr if include_stderr else result.stdout
        build_env, runtime = work/'builder',work/'runtime'
        for env in (build_env,runtime):
            run([interpreter,'-I','-m','venv',env],env)
        runtime_identity = json.loads(run([python_at(runtime),'-I','-c',
            'import json,platform,sys; print(json.dumps({"platform":platform.platform(),'
            '"python":platform.python_version(),"version_info":list(sys.version_info[:3])}))'],runtime))
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
        # Exercise the documented recipe through pip's dependency resolver,
        # including its interpreter marker, rather than installing all pins.
        recipe_bytes = recipe.read_bytes()
        local_recipe = work/'requirements-git.txt'
        local_recipe.write_bytes(recipe_bytes)
        before = json.loads(run([python_at(runtime),'-m','pip','list','--format=json'],runtime))
        # Python 3.11 ensurepip bootstraps setuptools into new environments.
        # Remove that build helper to prove the installed runtime does not need it.
        bootstrap_removed = [p['name'] for p in before if p['name'].lower() == 'setuptools']
        if bootstrap_removed:
            run([python_at(runtime),'-m','pip','uninstall','--yes',*bootstrap_removed],runtime)
            before = json.loads(run([python_at(runtime),'-m','pip','list','--format=json'],runtime))
        tampered = work/'tampered-provider-wheels'
        tampered.mkdir()
        for name in PINS:
            shutil.copyfile(provider_wheels/name,tampered/name)
        changed = tampered/next(name for name in PINS if name.startswith('dulwich-'))
        changed.write_bytes(changed.read_bytes()+b'\n')
        rejection = run([python_at(runtime),'-m','pip','install','--no-index','--no-cache-dir',
                         '--find-links',tampered,'-r',local_recipe],runtime,1,include_stderr=True)
        if 'DO NOT MATCH THE HASHES' not in rejection:
            raise ValueError('Tampered wheel did not fail the requirements hash check')
        if json.loads(run([python_at(runtime),'-m','pip','list','--format=json'],runtime)) != before:
            raise ValueError('Rejected provider installation changed runtime packages')
        # Validate the archive guard independently of digest rejection.
        for suffix in ('.pyd','.so'):
            native = work/('native-'+suffix[1:]+'.whl')
            with zipfile.ZipFile(native,'w') as archive:
                archive.writestr('fixture/native'+suffix,b'non-executable test sentinel')
            try:
                verify_wheel(native,hashlib.sha256(native.read_bytes()).hexdigest())
            except ValueError as exc:
                if 'Native member' not in str(exc): raise
            else:
                raise ValueError('Native archive guard did not reject '+suffix)
        run([python_at(runtime),'-m','pip','install','--no-index','--no-cache-dir',
             '--find-links',provider_wheels,'-r',local_recipe],runtime)
        run([python_at(runtime),'-m','pip','install','--no-index','--no-deps',wheel],runtime)
        run([python_at(runtime),'-m','pip','check'],runtime)
        packages = json.loads(run([python_at(runtime),'-m','pip','list','--format=json'],runtime))
        installed = {p['name'].lower().replace('_','-'):p['version'] for p in packages}
        expected = {name.split('-')[0].lower().replace('_','-'):name.split('-')[1] for name in PINS}
        if runtime_identity['version_info'][:2] >= [3,12]:
            expected.pop('typing-extensions')
        if set(installed) != set(expected) | {'pip','sbc-tools'}:
            raise ValueError('Runtime package inventory differs from the selected recipe')
        if any(installed[name] != version for name,version in expected.items()):
            raise ValueError('Runtime dependency version differs from the audited pin')
        site = Path(run([python_at(runtime),'-I','-c',
                         'import sysconfig; print(sysconfig.get_path("purelib"))'],runtime).strip())
        # A distribution's standard-library sitecustomize can precede this
        # environment on sys.path. A dedicated .pth hook avoids that shadowing.
        (site/'sbct_installed_audit.py').write_bytes(('import sys\n'+inspect.getsource(reject_process_and_network)
                                                   +'\nsys.addaudithook(reject_process_and_network)\n').encode())
        (site/'sbct_installed_audit.pth').write_bytes(b'import sbct_installed_audit\n')
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
        # Mounted scenarios run through the installed launcher, not mocked source
        # call sites. Only fixture preparation imports the checkout's helpers.
        from test_mounted_working_cli import MountedWorkingCLITests
        from test_admission import checkout
        from test_provenance_inputs import commit_files
        mounted = MountedWorkingCLITests()
        mounted_results = []
        try:
            mounted.setUp()
            args = ['--config',mounted.registration.configuration_file,
                    '--host',mounted.host_path,'--format=json']
            def invoke(action, expected):
                result = json.loads(run([command,action,*args],runtime,expected))
                assert result['schema_version'] == 2
                assert result['mode'] == 'working-tree'
                if result['selection'] is not None:
                    assert result['selection']['source_commit'] is None
                    assert result['selection']['projection_commit'] is None
                    assert result['selection']['dependencies'] == []
                mounted_results.append(result)
                return result
            missing_reference = invoke('check',3)
            assert missing_reference['observation']['complete']
            scan = invoke('scan',(0,1))
            assert scan['result']['publication'] == 'published'
            files = dict(mounted.source_files,**{'sbc.toml':mounted.registration.config_bytes})
            files.update({p.relative_to(mounted.source_root).as_posix():p.read_bytes()
                          for p in (mounted.source_root/'projection').rglob('*') if p.is_file()})
            child_head = mounted.child_reader.resolve_commit('HEAD')
            committed = commit_files(mounted.source_repo,files,{'docs/todo/child':child_head})
            checkout(mounted.source_repo,mounted.source_root,committed)
            checked = invoke('check',(0,1))
            assert checked['result']['comparison'] == 'equal'
            assert scan['selection']['snapshot_id'] == checked['selection']['snapshot_id']
            module = json.loads(run([python_at(runtime),'-I','-m','sbc_tools','check',*args],runtime,(0,1)))
            assert module == checked
            mounted_results.append(module)
            def checkout_bytes():
                return {p.relative_to(mounted.source_root).as_posix():p.read_bytes()
                        for p in mounted.source_root.rglob('*') if p.is_file()
                        and '.git' not in p.relative_to(mounted.source_root).parts}
            def selected_payload():
                output = mounted.source_root/'projection'
                selected = json.loads((output/'current.json').read_bytes())['bundle']
                files = output/selected/'files'
                return {p.relative_to(files).as_posix():p.read_bytes()
                        for p in files.rglob('*') if p.is_file()}
            before_repeat = checkout_bytes()
            before_payload = selected_payload()
            repeated = invoke('scan',(0,1))
            assert repeated['selection']['snapshot_id'] == scan['selection']['snapshot_id']
            assert selected_payload() == before_payload
            assert {p:b for p,b in checkout_bytes().items() if not p.startswith('projection/')} == {
                p:b for p,b in before_repeat.items() if not p.startswith('projection/')}
            (mounted.child_root/'note.md').write_bytes(
                b'# Installed dirty child\n\n**Document ID:** CHILD-00\n')
            before_check = checkout_bytes()
            dirty = invoke('check',1)
            assert dirty['result']['comparison'] == 'different'
            assert checkout_bytes() == before_check
            states = {p['repository_id']:p['checkout_state'] for p in dirty['observation']['participants']}
            # Repeat publication added an untracked retained output bundle in the
            # parent. That is its own dirty state, separate from child contents.
            assert states == {'source':'dirty','child':'dirty'}
            pointer = mounted.source_root/'projection/current.json'
            original_pointer = pointer.read_bytes()
            # A missing ancestor must prevent opening its registered descendant.
            config = mounted.registration.config_bytes.replace(b'repository_id = "child"}]',
                b'repository_id = "child"}, {path = "docs/todo/child/nested", repository_id = "nested"}]')
            original_registration = mounted.registration
            mounted.registration = replace(mounted.registration,config_bytes=config,
                source_repositories=dict(mounted.registration.source_repositories,
                                         nested=mounted.child_root/'nested'))
            mounted.registration.configuration_file.write_bytes(config)
            mounted.write_binding()
            parked = mounted.root/'parked-installed-child'
            mounted.child_root.rename(parked)
            try:
                missing = invoke('scan',3)
            finally:
                parked.rename(mounted.child_root)
                mounted.registration = original_registration
                mounted.registration.configuration_file.write_bytes(original_registration.config_bytes)
                mounted.write_binding()
            assert missing['selection'] is None and missing['result'] is None
            assert not missing['observation']['complete']
            participants = {p['repository_id']:p for p in missing['observation']['participants']}
            assert participants['child']['availability'] == 'missing_checkout'
            assert participants['nested']['availability'] == 'blocked_by_ancestor'
            assert participants['source']['observed_head'] == committed
            assert participants['source']['checkout_state'] == 'unknown'
            assert participants['source']['corpus_sha256'] is None
            assert pointer.read_bytes() == original_pointer
            mounted.child_repo.refs[b'HEAD'] = b'0'*40
            try:
                unavailable = invoke('scan',3)
            finally:
                mounted.child_repo.refs[b'HEAD'] = child_head.encode()
            assert unavailable['observation']['participants'][0]['availability'] == 'unavailable_history'
            assert pointer.read_bytes() == original_pointer
            mounted.registration = replace(mounted.registration,approved_authority_sha256='0'*64)
            mounted.write_binding()
            rejected = invoke('scan',2)
            assert rejected['error']['code'] == 'invalid_authority'
            assert rejected['observation'] is None
            assert pointer.read_bytes() == original_pointer
            # Schema tooling is a developer dependency in this parent process;
            # it is deliberately absent from the installed runtime environment.
            import jsonschema
            from referencing import Registry, Resource
            contracts = root.parent/'docs/sbc-tools/contracts'
            schema = json.loads((contracts/'observation-set.schema.json').read_bytes())
            registry = Registry().with_resource(schema['$id'],Resource.from_contents(schema))
            validator = jsonschema.Draft202012Validator(
                json.loads((contracts/'cli-observation-envelope.schema.json').read_bytes()),registry=registry)
            for result in mounted_results:
                validator.validate(result)
        finally:
            mounted.doCleanups()
        return {'wheel':wheel.name,'sha256':wheel_sha,'version':version,
                'platform':runtime_identity['platform'],'python':runtime_identity['python'],
                'mounted_cli_schema_envelopes':len(mounted_results),
                'runtime_packages':packages,'build_wheels':BUILD_PINS,'provider_wheels':PINS,
                'provider_recipe':{'path':'tools/requirements-git.txt',
                                   'sha256':hashlib.sha256(recipe_bytes).hexdigest(),
                                   'resolver_dependencies':expected,
                                   'typing_extensions_required':runtime_identity['version_info'][:2] < [3,12],
                                   'bootstrap_packages_removed':bootstrap_removed,
                                   'tampered_wheel_rejected_without_package_changes':True,
                                   'native_archive_guard_rejections':['.pyd','.so']},
                'checks':['pure wheel and console metadata','offline installation and pip check',
                          'hash-constrained requirements resolver and exact package inventory',
                          'tampered provider hash rejection without package changes',
                          'native archive guards with matching digest negative controls',
                          'installed import origin','process/network audit negative controls',
                          'actual console launcher help/version/invocation error',
                          'console scan/commit/check','module and launcher envelope parity',
                          'wrong authority pin rejection','working-tree console scan/check with null commit IDs',
                          'installed mounted scan/commit/check and module parity',
                          'installed mounted repeat emission byte equality without source changes',
                          'installed mounted dirty child nonwriting drift',
                          'installed missing child and blocked descendant with retained pointer',
                          'installed missing history versus checkout and bad authority rejection',
                          'installed mounted envelopes validate against approved schema'],
                'scope':'Local disposable environment; fixture approvals only; no release or gate closure'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('build_wheels',type=Path)
    parser.add_argument('provider_wheels',type=Path)
    parser.add_argument('--python',type=Path,help='Explicit interpreter for disposable build/runtime environments')
    args = parser.parse_args()
    print(json.dumps(verify(args.build_wheels.resolve(),args.provider_wheels.resolve(),python=args.python),indent=2))
