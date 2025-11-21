import argparse
import pytest

from discoship import cli


def test_global_options():
    expect = argparse.Namespace(info=True, debug=False, action=None)
    for flag in ('-i', '--info'):
        args = cli.DiscoShipArgParser.parse_args([flag])
        assert args == expect

    expect = argparse.Namespace(info=False, debug=True, action=None)
    for flag in ('-d', '--debug'):
        args = cli.DiscoShipArgParser.parse_args([flag])
        assert args == expect

