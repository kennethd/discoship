import argparse
import importlib
import logging
from pprint import pprint

from discoship.db import dbinit, dump_config, reset_config, recreate_ingest_tables
from discoship.defs import DEFAULT_PROVIDER, DEFAULT_SERVICE, VERSION


log = logging.getLogger(__name__)


DISCOSHIP_DESC = """
    utility for creating international discogs.com shipping policies
"""
DISCOSHIP_EPILOG = """
    For help with nested subcommands, do `discoship {subcommand} --help`
"""

DiscoShipArgParser = argparse.ArgumentParser(description=DISCOSHIP_DESC,
                                             epilog=DISCOSHIP_EPILOG)
DiscoShipArgParser.add_argument('-d', '--debug', action='store_true',
                                help='increases loglevel output')
DiscoShipArgParser.add_argument('--version', action='version', version=VERSION,
                                help='show version and exit')
actions = DiscoShipArgParser.add_subparsers(dest='action', help='subcommands')

IngestArgParser = actions.add_parser('ingest', help='ingest external data sources')
providers = IngestArgParser.add_subparsers(dest='provider', help='data source')

UspsArgParser = providers.add_parser('usps', help='US Postal Service')
UspsArgParser.add_argument('--service', default=DEFAULT_SERVICE,
                           help=f'Shipping service (default {DEFAULT_SERVICE})')
UspsArgParser.add_argument('--all', action='store_true',
                           help='Ingest all data')
UspsArgParser.add_argument('--cpg', action='store_true',
                           help='Country Price Group')
UspsArgParser.add_argument('--rates', action='store_true',
                           help='Rates for Price Group by Weight')

# not as useful as expected; no shipping policy stuff is exposed via API
DiscogsArgParser = providers.add_parser('discogs', help='ingest data from discogs API')
DiscogsArgParser.add_argument('--destinations', action='store_true',
                              help='Ingest Discogs Destination Countries')

InitArgParser = actions.add_parser('init', help='initialize resources')
InitArgParser.add_argument('--db', action='store_true',
                           help='recreate entire db from scratch [WARNING: DESTROYS ALL DATA]')
InitArgParser.add_argument('--reset-ingest-tables', action='store_true',
                           help='drop & recreate ingest tables; you will have to re-run ingest commands')
InitArgParser.add_argument('--api', action='store_true',
                           help='configure access to discogs.com API')

ConfigArgParser = actions.add_parser('config', help='manage config')
ConfigArgParser.add_argument('--dump', action='store_true',
                             help='display current config')
ConfigArgParser.add_argument('--reset', action='store_true',
                             help='reset config to defaults')


def func_importer(func_path):
    """func_path is string of python import name ending with function name to import"""
    log.info(f'loading func_path {func_path}')
    path, funcname = func_path.rsplit('.', 1)
    mod = importlib.import_module(path)
    func = getattr(mod, funcname)
    log.debug(f'loaded da func {func}')
    return func


def delegate_args(args):
    log.debug(f'delegate_args: {args}')
    if args.action == 'config':
        if args.reset:
            print("For reference, this was your config before reset:")
            pprint(dump_config())
            reset_config()
        elif args.dump:
            pprint(dump_config())
    elif args.action == 'init':
        if args.db:
            dbinit()
        elif args.reset_ingest_tables:
            recreate_ingest_tables()
    elif args.action == 'ingest':
        func_path = f'discoship.{args.provider.lower()}.fetch.fetch'
        func = func_importer(func_path)
        if args.provider == 'discogs':
            func()
        elif args.provider == 'usps':
            func(fetchall=args.all, cpg=args.cpg, rates=args.rates, service=args.service)

