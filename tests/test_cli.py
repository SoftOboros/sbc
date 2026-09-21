from contextlib import contextmanager
import io
import json
from types import SimpleNamespace
import unittest

from sbc_tools.cli import CommittedCheckHost, main, parse_invocation
from sbc_tools.cli_results import CommandFailure
from sbc_tools.provenance import CheckedProjection
from test_cli_results import candidate


class CLITests(unittest.TestCase):
    def call(self,args,loader=None):
        out = io.BytesIO()
        code = main(args,load_host=loader,stdout=out)
        return code,out.getvalue()

    def test_help_and_version_do_not_load_host(self):
        def forbidden(path): self.fail('Host loaded for help/version')
        for args in (['--help'],['check','--help'],['scan','--help'],['--version']):
            code, raw = self.call(args,forbidden)
            self.assertEqual(0,code)
            self.assertTrue(raw.endswith(b'\n'))

    def test_strict_arguments_and_conflicts_fail_before_loading(self):
        def forbidden(path): self.fail('Host loaded for invalid invocation')
        invalid = [[],['inspect'],['check'],['check','--conf','x'],
                   ['check','--config','x','--config','y'],
                   ['scan','check','--config','x'],['--version','check','--config','x'],
                   ['check','--config','x','--unknown'],
                   ['check','--config','x','--format','text','--format','json']]
        for args in invalid:
            args = args if '--format' in args else args+['--format','json']
            with self.subTest(args=args):
                code,raw = self.call(args,forbidden)
                self.assertEqual(2,code)
                value = json.loads(raw)
                self.assertEqual('invalid_invocation',value['error']['code'])
                self.assertIsNone(value['selection'])

    def test_defaults_and_options_before_command(self):
        self.assertEqual('text',parse_invocation(['check','--config','repo.toml']).format)
        parsed = parse_invocation(['--format=json','--config=repo.toml','check'])
        self.assertEqual(('check','repo.toml','json'),(parsed.command,parsed.config,parsed.format))

    def test_no_ambient_host_or_implicit_scan_success(self):
        for command in ('check','scan'):
            code,raw = self.call([command,'--config','unused.toml','--format=json'])
            self.assertEqual(2,code)
            self.assertEqual('invalid_configuration',json.loads(raw)['error']['code'])

    def test_explicit_host_dispatch_and_cleanup(self):
        events = []
        verifier = SimpleNamespace(supports=lambda c:c=='check',
            check_source=lambda **kwargs:CheckedProjection(candidate(),'6'*40,()))
        @contextmanager
        def load(path):
            events.append(path)
            try: yield CommittedCheckHost(verifier,{}, {})
            finally: events.append('closed')
        code,raw = self.call(['check','--config','chosen.toml','--format=json'],load)
        self.assertEqual(0,code)
        self.assertEqual(['chosen.toml','closed'],events)
        self.assertEqual('equal',json.loads(raw)['result']['comparison'])
        self.assertEqual(1,raw.count(b'\n'))

    def test_loader_failure_is_safe_and_preserves_exit_mapping(self):
        for error,code in ((OSError('private path'),3),(RuntimeError('private token'),4),
                           (CommandFailure('invalid_authority'),2)):
            def fail(path): raise error
            actual,raw = self.call(['check','--config','x','--format=json'],fail)
            self.assertEqual(code,actual)
            self.assertNotIn(b'private',raw)

    def test_disabled_capability_and_scan_do_not_execute(self):
        @contextmanager
        def load(path):
            def forbidden(**kwargs): self.fail('Disabled execution')
            yield CommittedCheckHost(SimpleNamespace(supports=lambda c:False,check_source=forbidden),{}, {})
        for command in ('check','scan'):
            code,raw = self.call([command,'--config','x','--format=json'],load)
            self.assertEqual(2,code)
            self.assertIsNone(json.loads(raw)['result'])

    def test_cleanup_failure_overrides_success_and_retains_findings(self):
        verifier = SimpleNamespace(supports=lambda c:True,
            check_source=lambda **kwargs:CheckedProjection(candidate(True),'6'*40,()))
        @contextmanager
        def load(path):
            yield CommittedCheckHost(verifier,{}, {})
            raise OSError('private cleanup path')
        code,raw = self.call(['check','--config','x','--format=json'],load)
        result = json.loads(raw)
        self.assertEqual(3,code)
        self.assertTrue(result['findings'])
        self.assertIsNone(result['result'])
        self.assertNotIn(b'private',raw)


if __name__ == '__main__': unittest.main()
