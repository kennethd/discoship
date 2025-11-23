import argparse
import importlib
import logging
from pprint import pprint
import sys

from discoship.countries.fetch import fetch as fetch_countries_data
from discoship.db import dbinit, dump_config, set_config, reset_config, \
                         recreate_ingest_tables
from discoship.defs import DEFAULT_PROVIDER, DEFAULT_SERVICE, USPS_SERVICES, VERSION
from discoship.discogs.fetch import fetch as fetch_discogs_data
from discoship.policy.policy import create_policy
from discoship.policy.ship_countries import list_countries, list_orphans
from discoship.usps.fetch import fetch as fetch_usps_data

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
DiscoShipArgParser.add_argument('--save-fixture-data', action='store_true',
                                help='write inputs & outputs of various functions to tests/data for unit tests')
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
InitArgParser.add_argument('--all', action='store_true',
                           help='init db and run all ingest scripts [WARNING: DESTROYS ALL DATA]')
InitArgParser.add_argument('--db', action='store_true',
                           help='recreate entire db from scratch [WARNING: DESTROYS ALL DATA]')
# --reset-ingest-tables useful for schema changes during dev without losing config
InitArgParser.add_argument('--reset-ingest-tables', action='store_true',
                           help='drop & recreate ingest tables; you will have to re-run ingest commands')
#InitArgParser.add_argument('--api', action='store_true', help='configure access to discogs.com API')

PolicyArgParser = actions.add_parser('policy', help='create policy recommendation')
PolicyArgParser.add_argument('--country',
                             help='create policy for country (may specify name or country code)')
PolicyArgParser.add_argument('--service', choices=USPS_SERVICES, default=DEFAULT_SERVICE,
                             help=f'Shipping service (default {DEFAULT_SERVICE})')
# Not sure--price-group arg is useful..
#PolicyArgParser.add_argument('--price-group', action='store_true',
#                             help='create policy for USPS price group')
PolicyArgParser.add_argument('--all', action='store_true',
                             help='create policy for all countries/price groups')

ConfigArgParser = actions.add_parser('config', help='manage config')
ConfigArgParser.add_argument('--dump', action='store_true',
                             help='display current config')
ConfigArgParser.add_argument('--reset', action='store_true',
                             help='reset config to defaults')
ConfigArgParser.add_argument('--set', nargs=2,
                             help='requires 2 args: config key & value')

ListArgParser = actions.add_parser('list', help='list things in the db')
ListArgParser.add_argument('--countries', action='store_true',
                           help='list recognized countries & 2-letter codes')
ListArgParser.add_argument('--orphans', action='store_true',
                           help='list country names from ISO & discogs tables with no match for join')


def delegate_args(args):
    log.debug(f'delegate_args: {args}')
    if args.save_fixture_data:
        import discoship  # noqa # pragma: no cover
        discoship.testing.SAVE_FIXTURE_DATA = True  # pragma: no cover

    if args.action == 'config':
        if args.reset:
            print("For reference, this was your config before reset:", file=sys.stderr)
            pprint(dump_config(), stream=sys.stderr)
            reset_config()
            print("\nNew config:", file=sys.stderr)
            pprint(dump_config(), stream=sys.stderr)
        elif args.set:
            rowcount = set_config(args.set[0], args.set[1])
            print("\nNew config:", file=sys.stderr)
            pprint(dump_config(), stream=sys.stderr)
        elif args.dump:
            # always STDOUT when it is output asked for; STDERR when extra info
            pprint(dump_config(), stream=sys.stdout)

    elif args.action == 'init':
        if args.db:
            dbinit()
        elif args.all:
            dbinit()
            fetch_countries_data()
            fetch_discogs_data()
            fetch_usps_data(fetchall=True)
        elif args.reset_ingest_tables:
            recreate_ingest_tables()

    elif args.action == 'list':
        # primary purpose of list --countries & list --orphans is aid in
        # maintaining COUNTRY_ALIASES, but also useful as reminder for country code
        if args.countries:
            list_countries()
        elif args.orphans:
            list_orphans()

    elif args.action == 'policy':
        if args.country:
            policy = create_policy(service=args.service, country=args.country)
            pprint(policy)
        else:
            raise RuntimeError("Unclear intent.  See policy --help")

    elif args.action == 'ingest':
        if args.provider == 'countries':
            fetch_countries_data()
        elif args.provider == 'discogs':
            fetch_discogs_data()
        elif args.provider == 'usps':
            fetch_usps_data(fetchall=args.all, cpg=args.cpg, rates=args.rates,
                            service=args.service)

