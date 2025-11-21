from argparse import Namespace

import pytest

from discoship import cli
from discoship.defs import *


def test_global_options():
    expect = Namespace(info=True, debug=False, action=None)
    for flag in ('-i', '--info'):
        args = cli.DiscoShipArgParser.parse_args([flag])
        assert args == expect

    expect = Namespace(info=False, debug=True, action=None)
    for flag in ('-d', '--debug'):
        args = cli.DiscoShipArgParser.parse_args([flag])
        assert args == expect


def test_init_options():
    expect = Namespace(info=False, debug=False, action='init', db=True,
                       reset_ingest_tables=False)
    args = cli.DiscoShipArgParser.parse_args(['init', '--db'])
    assert args == expect

    expect = Namespace(info=False, debug=False, action='init', db=False,
                       reset_ingest_tables=True)
    cmd = ['init', '--reset-ingest-tables']
    args = cli.DiscoShipArgParser.parse_args(cmd)
    assert args == expect


def test_ingest_usps_options():
    # --all with defaults
    expect = Namespace(info=False, debug=False, action='ingest',
                       provider='usps', service=DEFAULT_SERVICE, all=True,
                       cpg=False, rates=False)
    cmd = ['ingest', 'usps', '--all']
    args = cli.DiscoShipArgParser.parse_args(cmd)
    assert args == expect

    # no --all ; no other defaults for UspsArgParser
    expect = Namespace(info=False, debug=False, action='ingest',
                       provider='usps', service=USPS_SVC_PMI, all=False,
                       cpg=True, rates=True)
    cmd = ['ingest', 'usps', '--cpg', '--rates', '--service', USPS_SVC_PMI]
    args = cli.DiscoShipArgParser.parse_args(cmd)
    assert args == expect


def test_ingest_discogs_options():
    expect = Namespace(info=False, debug=False, action='ingest',
                       provider='discogs', destinations=True)
    cmd = ['ingest', 'discogs', '--destinations']
    args = cli.DiscoShipArgParser.parse_args(cmd)
    assert args == expect


def test_ingest_countries_options():
    expect = Namespace(info=False, debug=False, action='ingest',
                       provider='countries', iso3166=True)
    cmd = ['ingest', 'countries', '--iso3166']
    args = cli.DiscoShipArgParser.parse_args(cmd)
    assert args == expect


