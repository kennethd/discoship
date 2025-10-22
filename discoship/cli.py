import argparse
import importlib
import logging

from discoship.defs import DEFAULT_PROVIDER, DEFAULT_SERVICE, VERSION


log = logging.getLogger(__name__)


DISCOSHIP_DESC = """
    utility for creating international discogs.com shipping policies
"""
DISCOSHIP_EPILOG = """
    For help with subcommands, do `discoship {subcommand} --help`
"""

DiscoShipArgParser = argparse.ArgumentParser(description=DISCOSHIP_DESC,
                                             epilog=DISCOSHIP_EPILOG)
DiscoShipArgParser.add_argument('-v', '--verbose', action='store_true',
                                help='increases output')
DiscoShipArgParser.add_argument('-p', '--provider', default=DEFAULT_PROVIDER,
                                help=f'Shipping provider (default {DEFAULT_PROVIDER})')
DiscoShipArgParser.add_argument('--version', action='version', version=VERSION,
                                help='show version and exit')
subparsers = DiscoShipArgParser.add_subparsers(dest='action', help='subcommands')

FetchArgParser = subparsers.add_parser('fetch', help='fetch external data sources')
FetchArgParser.add_argument('--all', action='store_true',
                            help='Fetch all data')
FetchArgParser.add_argument('--cpg', action='store_true',
                            help='Country Price Group')
FetchArgParser.add_argument('--rates', action='store_true',
                            help='Rates for Price Group by Weight')
FetchArgParser.add_argument('--service', default=DEFAULT_SERVICE,
                            help=f'Shipping service (default {DEFAULT_SERVICE})')


def func_importer(func_path):
    """func_path is string of python import name ending with function name to import"""
    path, funcname = func_path.rsplit('.', 1)
    mod = importlib.import_module(path)
    func = getattr(mod, funcname)
    return func


def delegate_args(args):
    provider = args.provider
    action = args.action
    func_path = f'discoship.{provider}.{action}.{action}'
    log.info(f'loading func_path {func_path}')
    func = func_importer(func_path)
    log.info(f'loaded da func {func}')
    if action == 'fetch':
        func(fetchall=args.all, cpg=args.cpg, rates=args.rates,
             service=args.service, verbose=args.verbose)

