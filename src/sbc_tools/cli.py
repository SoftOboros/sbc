"""Strict CLI boundary with explicitly injected trusted host composition.

The default executable offers help/version and fails closed for operations until
a trusted host loader is supplied. Config files never name executable plugins.
"""
import argparse
from dataclasses import dataclass
import sys

from . import __version__
from .cli_results import CommandFailure, execute_check, failure_envelope, render_envelope
from .git_reader import GitUnavailableError
from .provenance import CommittedProvenanceVerifier


class _Parser(argparse.ArgumentParser):
    def error(self, message):
        raise CommandFailure('invalid_invocation')


class _Once(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        seen = getattr(namespace, '_seen', set())
        if self.dest in seen:
            parser.error('Repeated option')
        setattr(namespace, '_seen', seen | {self.dest})
        setattr(namespace, self.dest, values)


@dataclass(frozen=True)
class Invocation:
    command: str
    config: str
    format: str


def parse_invocation(argv):
    parser = _Parser(prog='sbc-tools', add_help=False, allow_abbrev=False)
    parser.add_argument('command', choices=('scan','check'))
    parser.add_argument('--config', required=True, action=_Once)
    parser.add_argument('--format', choices=('text','json'), default='text', action=_Once)
    result = parser.parse_args(argv)
    if not result.config:
        raise CommandFailure('invalid_invocation')
    return Invocation(result.command,result.config,result.format)


@dataclass(frozen=True)
class CommittedCheckHost:
    """Host loader owns config validation, approval pins and reader lifetimes."""
    verifier: CommittedProvenanceVerifier
    document_families: object
    archive_families: object

    def execute(self, invocation):
        if invocation.command != 'check':
            raise CommandFailure('invalid_configuration')
        if not self.verifier.supports('check'):
            raise CommandFailure('invalid_configuration')
        return execute_check(self.verifier,document_families=self.document_families,
                             archive_families=self.archive_families)


def _json_requested(argv):
    return '--format=json' in argv or any(a == '--format' and b == 'json' for a,b in zip(argv,argv[1:]))


def main(argv=None, *, load_host=None, stdout=None):
    """Return an exit code; stdout receives bytes, without progress or exceptions.

    load_host(config_path) is trusted application code returning a context manager
    for CommittedCheckHost. No ambient loader, plugin import or approval discovery
    is performed. The loader must validate exactly the requested configuration.
    """
    args = list(sys.argv[1:] if argv is None else argv)
    output = sys.stdout.buffer if stdout is None else stdout
    if args in (['--help'],['check','--help'],['scan','--help']):
        output.write(b'Usage: sbc-tools {scan,check} --config PATH [--format text|json]\n'
                     b'Options: --help, --version\n'
                     b'Prerelease: check requires an explicit trusted host; scan is not implemented.\n')
        return 0
    if args == ['--version']:
        output.write(('sbc-tools '+__version__+'\n').encode('utf-8'))
        return 0
    invocation, completed = None, None
    def failed(code):
        result = failure_envelope(code,command=invocation.command if invocation else None,
                                  mode=completed['mode'] if completed else None)
        if completed is not None:
            result['selection'] = completed['selection']
            result['findings'] = completed['findings']
        return result
    try:
        invocation = parse_invocation(args)
        if load_host is None:
            raise CommandFailure('invalid_configuration')
        with load_host(invocation.config) as host:
            if not isinstance(host,CommittedCheckHost):
                raise CommandFailure('invalid_configuration')
            completed = host.execute(invocation)
        envelope = completed
    except CommandFailure as exc:
        envelope = failed(exc.code)
    except GitUnavailableError:
        envelope = failed('evidence_unavailable')
    except OSError:
        envelope = failed('io_failure')
    except Exception:
        envelope = failed('internal_failure')
    format = invocation.format if invocation else ('json' if _json_requested(args) else 'text')
    output.write(render_envelope(envelope,format=format))
    return envelope['exit_code']
