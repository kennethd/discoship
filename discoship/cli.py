import argparse
import importlib
import logging
from pprint import pprint
import sys

from discoship.db import dbinit, dump_config, set_config, reset_config, \
                         recreate_ingest_tables
from discoship.defs import DEFAULT_PROVIDER, DEFAULT_SERVICE, USPS_SERVICES, VERSION
from discoship.policy.ship_countries import list_countries, list_orphans

log = logging.getLogger(__name__)


DISCOSHIP_DESC = """
    utility for creating international discogs.com shipping policies
"""
DISCOSHIP_EPILOG = """
    For help with nested subcommands, do `discoship {subcommand} --help`
"""

DiscoShipArgParser = argparse.ArgumentParser(description=DISCOSHIP_DESC,
                                             epilog=DISCOSHIP_EPILOG)
DiscoShipArgParser.add_argument('-i', '--info', action='store_true',
                                help='increases loglevel output')
DiscoShipArgParser.add_argument('-d', '--debug', action='store_true',
                                help='increases loglevel output to maximum')
DiscoShipArgParser.add_argument('--version', action='version', version=VERSION,
                                help='show version and exit')
actions = DiscoShipArgParser.add_subparsers(dest='action', help='subcommands')

IngestArgParser = actions.add_parser('ingest', help='ingest external data sources')
providers = IngestArgParser.add_subparsers(dest='provider', help='data source')

# users will almost always want to do:
# $ discoship ingest usps --all
# for devs, it is convenient to be able to ingest only data you are working on:
# $ discoship -d ingest usps --rates --pmi
UspsArgParser = providers.add_parser('usps', help='US Postal Service')
UspsArgParser.add_argument('--service', choices=USPS_SERVICES, default=DEFAULT_SERVICE,
                           help=f'Shipping service (default {DEFAULT_SERVICE})')
UspsArgParser.add_argument('--all', action='store_true',
                           help='Ingest all data for service')
UspsArgParser.add_argument('--cpg', action='store_true',
                           help='Ingest USPS Country Price Group data')
UspsArgParser.add_argument('--rates', action='store_true',
                           help='Ingest Rates for Price Group by Weight for service')

# not as useful as expected; no shipping policy stuff is exposed via API
DiscogsArgParser = providers.add_parser('discogs', help='ingest data from discogs API')
DiscogsArgParser.add_argument('--destinations', action='store_true',
                              help='Ingest Discogs Destination Countries')

CountriesArgParser = providers.add_parser('countries', help='ingest country data')
CountriesArgParser.add_argument('--iso3166', action='store_true',
                                help='Ingest ISO3166 Country Codes & official country names')

InitArgParser = actions.add_parser('init', help='initialize resources')
InitArgParser.add_argument('--db', action='store_true',
                           help='recreate entire db from scratch [WARNING: DESTROYS ALL DATA]')
InitArgParser.add_argument('--reset-ingest-tables', action='store_true',
                           help='drop & recreate ingest tables; you will have to re-run ingest commands')
#InitArgParser.add_argument('--api', action='store_true',
#                           help='configure access to discogs.com API')

PolicyArgParser = actions.add_parser('policy', help='create policy recommendation')
PolicyArgParser.add_argument('--country',
                             help='create policy for country (may specify name or country code)')
PolicyArgParser.add_argument('--price-group', action='store_true',
                             help='create policy for USPS price group')
PolicyArgParser.add_argument('--all', action='store_true',
                             help='create policy for all countries/price groups')
PolicyArgParser.add_argument('--list-countries', action='store_true',
                             help='list recognized countries & 2-letter codes')
PolicyArgParser.add_argument('--list-orphans', action='store_true',
                             help='list country names from ISO & discogs tables with no match for join')

ConfigArgParser = actions.add_parser('config', help='manage config')
ConfigArgParser.add_argument('--dump', action='store_true',
                             help='display current config')
ConfigArgParser.add_argument('--reset', action='store_true',
                             help='reset config to defaults')
ConfigArgParser.add_argument('--set', nargs=2,
                             help='requires 2 args: config key & value')


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
            print("For reference, this was your config before reset:", file=sys.stderr)
            pprint(dump_config(), stream=sys.stderr)
            reset_config()
            print("\nNew config:", file=sys.stderr)
            pprint(dump_config(), stream=sys.stderr)
        if args.set:
            rowcount = set_config(args.set[0], args.set[1])
            print("\nNew config:", file=sys.stderr)
            pprint(dump_config(), stream=sys.stderr)
        elif args.dump:
            # always STDOUT when it is output asked for; STDERR when extra info
            pprint(dump_config(), stream=sys.stdout)
    elif args.action == 'init':
        if args.db:
            dbinit()
        elif args.reset_ingest_tables:
            recreate_ingest_tables()
    elif args.action == 'policy':
        if args.list_countries:
            list_countries()
        elif args.list_orphans:
            list_orphans()
    elif args.action == 'ingest':
        func_path = f'discoship.{args.provider}.fetch.fetch'
        func = func_importer(func_path)
        if args.provider == 'usps':
            func(fetchall=args.all, cpg=args.cpg, rates=args.rates, service=args.service)
        else:
            func()

