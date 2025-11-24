
import pytest

from discoship.testing import load_bs4_data_fixture, load_saved_output
from discoship.usps import pmi


PMI_RATES_PRICE_GROUP_1_10 = {
    1: ['42.95', '46.40', '49.80', '53.25', '57.90', '62.70', '67.65', '72.70', '77.55', '82.70'],
    2: ['56.70', '61.20', '66.45', '70.90', '75.40', '80.10', '84.90', '89.55', '94.30', '99.05'],
    3: ['64.20', '69.60', '75.30', '81.20', '87.10', '93.25', '99.50', '105.70', '111.95', '118.15'],
    4: ['64.25', '69.45', '74.75', '80.00', '85.20', '90.55', '95.90', '101.25', '106.60', '112.00'],
    5: ['68.75', '74.05', '79.40', '84.75', '89.95', '95.35', '100.75', '106.25', '111.50', '117.00'],
    6: ['62.55', '67.90', '73.20', '78.75', '85.00', '91.40', '97.90', '104.30', '110.75', '117.25'],
    7: ['63.70', '69.10', '75.45', '82.35', '89.15', '96.05', '103.00', '110.00', '117.00', '123.95'],
    8: ['62.05', '69.40', '76.70', '84.10', '91.50', '98.85', '106.25', '113.65', '120.95', '128.35'],
    9: ['62.60', '69.75', '77.70', '85.55', '93.10', '100.85', '108.80', '116.55', '124.35', '132.20'],
    10: ['59.50', '64.70', '70.15', '75.75', '81.60', '87.65', '93.45', '99.45', '105.45', '111.35']
}

PMI_RATES_PRICE_GROUP_11_20 = {
    11: ['59.85', '65.65', '72.15', '78.25', '84.25', '90.45', '96.70', '102.95', '109.15', '115.45'],
    12: ['66.20', '73.70', '82.65', '91.45', '100.10', '125.15', '133.50', '142.00', '150.45', '158.90'],
    13: ['64.85', '70.60', '76.85', '83.65', '90.00', '96.95', '103.45', '110.15', '116.85', '123.35'],
    14: ['61.50', '66.30', '71.00', '76.10', '81.70', '87.20', '93.00', '98.75', '104.20', '110.05'],
    15: ['66.75', '71.05', '75.40', '79.80', '84.00', '88.40', '92.80', '97.30', '101.65', '106.15'],
    16: ['75.30', '80.05', '84.80', '89.55', '94.15', '98.95', '103.70', '108.55', '113.30', '118.20'],
    17: ['61.25', '65.55', '70.25', '75.20', '79.85', '84.80', '89.70', '94.60', '99.45', '104.50'],
    18: ['63.75', '68.55', '73.55', '78.65', '83.65', '88.75', '93.90', '99.10', '104.20', '109.40'],
    19: ['79.45', '85.00', '98.00', '108.95', '118.60', '128.25', '137.90', '147.55', '155.15', '162.00'],
    20: ['67.60', '73.00', '78.60', '84.10', '89.35', '94.90', '100.45', '106.05', '111.55', '117.25']
}

PMI_RATE_TABLE_DATA = PMI_RATES_PRICE_GROUP_1_10.copy()
PMI_RATE_TABLE_DATA.update(PMI_RATES_PRICE_GROUP_11_20)


def test_parse_pmi_rate_table():
    filename = 'usps.pmi._parse_pmi_rate_table.htm'
    table_soup = load_bs4_data_fixture(filename, expect_to_find='table')
    result = pmi._parse_pmi_rate_table(table_soup)
    assert result == PMI_RATES_PRICE_GROUP_11_20


def test_fetch_pmi_rates_data(mocker):
    filename = 'fetch_url-fetch_usps_rate_tables.htm'
    html = load_saved_output(filename)
    mocker.patch('discoship.usps.pmi.fetch_usps_rate_tables', return_value=html)
    rates_data = pmi.fetch_pmi_rates_data()
    assert rates_data == PMI_RATE_TABLE_DATA
    pmi.fetch_usps_rate_tables.assert_called()


def test_ingest_pmi_rates_data(mocker):
    mocker.patch('discoship.usps.pmi.executemany', return_value=1)
    mocker.patch('discoship.usps.pmi.execute', return_value=1)
    mocker.patch('discoship.usps.pmi.selectone')
    pmi.ingest_pmi_rates_data(PMI_RATE_TABLE_DATA)
    insert_vals = [ tuple([k] + v) for k, v in PMI_RATE_TABLE_DATA.items() ]
    pmi.executemany.assert_called_with(pmi.INSERT_USPS_PMI_RATES, insert_vals)
    pmi.execute.assert_called_with(pmi.UPDATE_LAST_INGEST_DATE, db=pmi.USERDATA_PATH)
    pmi.selectone.assert_called_with(pmi.SELECT_LAST_INGEST_DATE, db=pmi.USERDATA_PATH)

