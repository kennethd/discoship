from argparse import Namespace
import sys

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


def test_init_all(mocker):
    mocker.patch('discoship.cli.dbinit')
    mocker.patch('discoship.cli.fetch_usps_data')
    mocker.patch('discoship.cli.fetch_discogs_data')
    mocker.patch('discoship.cli.fetch_countries_data')
    expect = Namespace(info=False, debug=False, action='init', all=True,
                       db=False, reset_ingest_tables=False)
    args = cli.DiscoShipArgParser.parse_args(['init', '--all'])
    assert args == expect
    cli.delegate_args(args)
    cli.dbinit.assert_called()
    cli.fetch_discogs_data.assert_called()
    cli.fetch_countries_data.assert_called()
    cli.fetch_usps_data.assert_called_with(fetchall=True)


def test_init_db(mocker):
    mocker.patch('discoship.cli.dbinit')
    expect = Namespace(info=False, debug=False, action='init', all=False,
                       db=True, reset_ingest_tables=False)
    args = cli.DiscoShipArgParser.parse_args(['init', '--db'])
    assert args == expect
    cli.delegate_args(args)
    cli.dbinit.assert_called()


def test_init_ingest_tables(mocker):
    mocker.patch('discoship.cli.recreate_ingest_tables')
    expect = Namespace(info=False, debug=False, action='init', all=False,
                       db=False, reset_ingest_tables=True)
    cmd = ['init', '--reset-ingest-tables']
    args = cli.DiscoShipArgParser.parse_args(cmd)
    assert args == expect
    cli.delegate_args(args)
    cli.recreate_ingest_tables.assert_called()


def test_ingest_usps_all(mocker):
    # --all with defaults
    mocker.patch('discoship.cli.fetch_usps_data')
    expect = Namespace(info=False, debug=False, action='ingest',
                       provider='usps', service=DEFAULT_SERVICE, all=True,
                       cpg=False, rates=False)
    cmd = ['ingest', 'usps', '--all']
    args = cli.DiscoShipArgParser.parse_args(cmd)
    assert args == expect
    cli.delegate_args(args)
    cli.fetch_usps_data.assert_called_with(fetchall=args.all,
                                           cpg=args.cpg,
                                           rates=args.rates,
                                           service=args.service)


def test_ingest_usps_other_options(mocker):
    # no --all ; no other defaults for UspsArgParser
    mocker.patch('discoship.cli.fetch_usps_data')
    expect = Namespace(info=False, debug=False, action='ingest',
                       provider='usps', service=USPS_SVC_PMI, all=False,
                       cpg=True, rates=True)
    cmd = ['ingest', 'usps', '--cpg', '--rates', '--service', USPS_SVC_PMI]
    args = cli.DiscoShipArgParser.parse_args(cmd)
    assert args == expect
    cli.delegate_args(args)
    cli.fetch_usps_data.assert_called_with(fetchall=args.all,
                                           cpg=args.cpg,
                                           rates=args.rates,
                                           service=args.service)


def test_ingest_discogs_options(mocker):
    mocker.patch('discoship.cli.fetch_discogs_data')
    expect = Namespace(info=False, debug=False, action='ingest',
                       provider='discogs', destinations=True)
    cmd = ['ingest', 'discogs', '--destinations']
    args = cli.DiscoShipArgParser.parse_args(cmd)
    assert args == expect
    cli.delegate_args(args)
    cli.fetch_discogs_data.assert_called()


def test_ingest_countries_options(mocker):
    mocker.patch('discoship.cli.fetch_countries_data')
    expect = Namespace(info=False, debug=False, action='ingest',
                       provider='countries', iso3166=True)
    cmd = ['ingest', 'countries', '--iso3166']
    args = cli.DiscoShipArgParser.parse_args(cmd)
    assert args == expect
    cli.delegate_args(args)
    cli.fetch_countries_data.assert_called()


def test_config_dump(mocker):
    mocker.patch('discoship.cli.dump_config')
    expect = Namespace(info=False, debug=False, action='config', dump=True,
                       reset=False, set=None)
    cmd = ['config', '--dump']
    args = cli.DiscoShipArgParser.parse_args(cmd)
    assert args == expect
    cli.delegate_args(args)
    cli.dump_config.assert_called()


def test_config_set(mocker):
    mocker.patch('discoship.cli.set_config')
    mocker.patch('discoship.cli.dump_config')
    expect = Namespace(info=False, debug=False, action='config', dump=False,
                       reset=False, set=['var-name', 'New Value'])
    cmd = ['config', '--set', 'var-name', 'New Value']
    args = cli.DiscoShipArgParser.parse_args(cmd)
    assert args == expect
    cli.delegate_args(args)
    cli.set_config.assert_called()
    cli.dump_config.assert_called()


def test_reset_config(mocker):
    mocker.patch('discoship.cli.reset_config')
    mocker.patch('discoship.cli.dump_config')
    expect = Namespace(info=False, debug=False, action='config', dump=False,
                       reset=True, set=None)
    cmd = ['config', '--reset']
    args = cli.DiscoShipArgParser.parse_args(cmd)
    assert args == expect
    cli.delegate_args(args)
    cli.reset_config.assert_called()
    cli.dump_config.assert_called()


def test_list_countries(mocker):
    mocker.patch('discoship.cli.list_countries')
    expect = Namespace(info=False, debug=False, action='list',
                       countries=True, orphans=False)
    cmd = ['list', '--countries']
    args = cli.DiscoShipArgParser.parse_args(cmd)
    assert args == expect
    cli.delegate_args(args)
    cli.list_countries.assert_called()


def test_list_orphans(mocker):
    mocker.patch('discoship.cli.list_orphans')
    expect = Namespace(info=False, debug=False, action='list',
                       countries=False, orphans=True)
    cmd = ['list', '--orphans']
    args = cli.DiscoShipArgParser.parse_args(cmd)
    assert args == expect
    cli.delegate_args(args)
    cli.list_orphans.assert_called()


def test_create_country_policy(mocker):
    mocker.patch('discoship.cli.create_policy')

    # test expected error without args
    with pytest.raises(RuntimeError) as exc:
        args = cli.DiscoShipArgParser.parse_args(['policy'])
        cli.delegate_args(args)
    assert "Unclear intent." in str(exc)

    expect = Namespace(info=False, debug=False, action='policy',
                       country='nz', service=USPS_SVC_PMI, all=False)
    cmd = ['policy', '--service', USPS_SVC_PMI, '--country', 'nz']
    args = cli.DiscoShipArgParser.parse_args(cmd)
    assert args == expect
    cli.delegate_args(args)
    cli.create_policy.assert_called_with(service=args.service, country=args.country)

