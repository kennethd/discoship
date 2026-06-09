
import pytest

from discoship.testing import load_bs4_data_fixture, load_saved_output
from discoship.usps import fcpis


FCPIS_RATES_PRICE_GROUP_1_10 = {
  '1': ['19.40', '26.00', '29.05', '38.50', '47.60'],
  '2': ['20.15', '26.60', '29.70', '39.00', '51.05'],
  '3': ['22.65', '37.35', '41.70', '61.70', '74.35'],
  '4': ['22.05', '38.35', '42.80', '59.75', '78.30'],
  '5': ['21.95', '38.30', '42.75', '57.30', '72.60'],
  '6': ['21.40', '34.25', '38.30', '56.95', '69.85'],
  '7': ['21.85', '29.95', '33.45', '48.90', '66.25'],
  '8': ['23.50', '31.15', '34.80', '50.10', '67.50'],
  '9': ['25.70', '35.90', '40.20', '58.30', '75.55'],
  '10': ['22.25', '31.15', '34.80', '50.15', '68.65'],
}

FCPIS_RATES_PRICE_GROUP_11_20 = {
  '11': ['26.60', '40.45', '45.15', '63.15', '80.85'],
  '12': ['24.80', '41.25', '46.05', '65.25', '79.10'],
  '13': ['27.75', '37.40', '41.75', '56.40', '75.70'],
  '14': ['22.40', '32.05', '35.15', '48.80', '66.70'],
  '15': ['24.60', '29.40', '32.85', '47.75', '65.05'],
  '16': ['21.80', '29.95', '32.85', '48.60', '66.25'],
  '17': ['24.15', '33.95', '37.90', '56.45', '71.90'],
  '18': ['23.05', '32.05', '35.15', '51.65', '67.30'],
  '19': ['23.20', '31.80', '35.50', '50.70', '70.00'],
  '20': ['23.05', '31.95', '35.70', '49.25', '64.25'],
}

FCPIS_RATE_TABLE_DATA = FCPIS_RATES_PRICE_GROUP_1_10.copy()
FCPIS_RATE_TABLE_DATA.update(FCPIS_RATES_PRICE_GROUP_11_20)


def test_parse_fcpis_rate_table():
    filename = 'usps.fcpis._parse_fcpis_rate_table.htm'
    table_soup = load_bs4_data_fixture(filename, expect_to_find='table')
    result = fcpis._parse_fcpis_rate_table(table_soup)
    assert result == FCPIS_RATES_PRICE_GROUP_11_20


def test_fetch_fcpis_rates_data(mocker):
    filename = 'fetch_url-fetch_usps_rate_tables.htm'
    html = load_saved_output(filename)
    mocker.patch('discoship.usps.fcpis.fetch_usps_rate_tables', return_value=html)
    rates_data = fcpis.fetch_fcpis_rates_data()
    assert rates_data == FCPIS_RATE_TABLE_DATA
    fcpis.fetch_usps_rate_tables.assert_called()


def test_fetch_fcpis_rates_data_raises_error(mocker):
    # return html not containing table we're looking for
    filename = 'fetch_url-fetch_iso3166_countries.htm'
    html = load_saved_output(filename)
    mocker.patch('discoship.usps.fcpis.fetch_usps_rate_tables', return_value=html)
    with pytest.raises(AssertionError) as exc:
        _ = fcpis.fetch_fcpis_rates_data()
    assert 'Could not locate pe-content-document' in str(exc)
    fcpis.fetch_usps_rate_tables.assert_called()


def test_insert_fcpis_rates_data(mocker):
    mocker.patch('discoship.usps.fcpis.executemany', return_value=1)
    mocker.patch('discoship.usps.fcpis.execute', return_value=1)
    mocker.patch('discoship.usps.fcpis.selectone')
    fcpis.insert_fcpis_rates_data(FCPIS_RATE_TABLE_DATA)
    insert_vals = [ (k, v[0], v[1], v[2], v[3], v[4]) for k, v in FCPIS_RATE_TABLE_DATA.items() ]
    fcpis.executemany.assert_called_with(fcpis.INSERT_USPS_FCPIS_RATES, insert_vals)
    fcpis.execute.assert_called_with(fcpis.UPDATE_LAST_INGEST_DATE, db=fcpis.USERDATA_PATH)
    fcpis.selectone.assert_called_with(fcpis.SELECT_LAST_INGEST_DATE, db=fcpis.USERDATA_PATH)

