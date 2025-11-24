
import pytest

from discoship.testing import load_bs4_data_fixture, load_saved_output
from discoship.usps import fcpis


FCPIS_RATES_PRICE_GROUP_1_10 = {
   '1': ['17.85', '26.00', '38.50', '47.60'],
   '2': ['18.05', '26.60', '39.00', '51.05'],
   '3': ['20.00', '37.35', '56.25', '74.35'],
   '4': ['19.05', '38.35', '54.45', '78.30'],
   '5': ['19.05', '38.30', '52.20', '72.60'],
   '6': ['19.05', '34.25', '51.95', '69.85'],
   '7': ['19.30', '29.95', '48.90', '66.25'],
   '8': ['21.35', '31.15', '50.10', '67.50'],
   '9': ['22.50', '34.65', '54.40', '75.55'],
   '10': ['19.35', '31.15', '50.15', '68.65'],
}

FCPIS_RATES_PRICE_GROUP_11_20 = {
  '11': ['23.80', '40.45', '55.95', '72.00'],
  '12': ['22.60', '41.25', '65.25', '79.10'],
  '13': ['24.35', '37.40', '56.40', '75.70'],
  '14': ['19.90', '32.05', '48.80', '66.70'],
  '15': ['22.05', '29.40', '47.75', '65.05'],
  '16': ['20.60', '29.95', '48.60', '66.25'],
  '17': ['21.05', '33.95', '52.65', '71.90'],
  '18': ['21.85', '32.05', '51.65', '67.30'],
  '19': ['20.55', '31.80', '50.70', '70.00'],
  '20': ['21.00', '31.95', '49.25', '64.25'],
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


def test_ingest_fcpis_rates_data(mocker):
    mocker.patch('discoship.usps.fcpis.executemany', return_value=1)
    mocker.patch('discoship.usps.fcpis.execute', return_value=1)
    mocker.patch('discoship.usps.fcpis.selectone')
    fcpis.ingest_fcpis_rates_data(FCPIS_RATE_TABLE_DATA)
    insert_vals = [ (k, v[0], v[1], v[2], v[3]) for k, v in FCPIS_RATE_TABLE_DATA.items() ]
    fcpis.executemany.assert_called_with(fcpis.INSERT_USPS_FCPIS_RATES, insert_vals)
    fcpis.execute.assert_called_with(fcpis.UPDATE_LAST_INGEST_DATE, db=fcpis.USERDATA_PATH)
    fcpis.selectone.assert_called_with(fcpis.SELECT_LAST_INGEST_DATE, db=fcpis.USERDATA_PATH)

