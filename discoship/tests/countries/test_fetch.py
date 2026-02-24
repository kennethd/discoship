
import pytest

from discoship.countries import fetch
from discoship.testing import load_bs4_data_fixture, load_saved_output


def test_fetch_iso3166_countries():
    filename = 'fetch_url-fetch_iso3166_countries.htm'
    # html = load_saved_output(filename)
    # mocker.patch('discoship.countries.fetch_usps_rate_tables', return_value=html)
    countries_data = fetch.fetch_iso3166_countries()
    print(countries_data)
    fetch.fetch_iso3166_countries.assert_called()

