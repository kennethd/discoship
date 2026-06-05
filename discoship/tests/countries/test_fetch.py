
import pytest

from discoship.countries import fetch
from discoship.testing import load_bs4_data_fixture, load_saved_output


def test_fetch_iso3166_countries(mocker):
    # fetch_url-fetch_iso3166_countries.htm created by @save_output_for_caller
    filename = 'fetch_url-fetch_iso3166_countries.htm'
    html = load_saved_output(filename)
    mock_fetch_url = mocker.patch('discoship.countries.fetch.fetch_url', return_value=html)
    # countries_data is list of tuples: (country_name, sovereignty, code2, code3)
    countries_data = fetch.fetch_iso3166_countries()
    mock_fetch_url.assert_called()
    expect_usa = ('United States', 'UN member', 'US', 'USA')
    assert expect_usa in countries_data

