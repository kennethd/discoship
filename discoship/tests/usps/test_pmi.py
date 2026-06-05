
import pytest

from discoship.testing import load_bs4_data_fixture, load_saved_output
from discoship.usps import pmi


PMI_RATES_PRICE_GROUP_1_10 = {
    1: ['43.55', '47.05', '50.45', '53.85', '59.05', '64.35', '69.70', '75.30', '80.60', '86.25'],
    2: ['61.45', '64.45', '68.40', '73.45', '78.55', '83.90', '89.40', '94.65', '100.05', '105.45'],
    3: ['69.40', '73.40', '79.10', '85.65', '92.30', '98.85', '105.45', '112.05', '118.65', '125.20'],
    4: ['70.40', '74.00', '77.85', '83.75', '89.70', '95.75', '101.80', '107.95', '113.95', '120.10'],
    5: ['71.70', '77.05', '83.15', '89.15', '95.05', '101.20', '107.35', '113.55', '119.55', '125.80'],
    6: ['66.25', '71.95', '77.55', '83.20', '89.45', '96.70', '104.10', '111.35', '118.70', '126.10'],
    7: ['67.05', '72.55', '78.60', '86.50', '94.15', '102.00', '109.85', '117.85', '125.80', '133.70'],
    8: ['65.75', '73.50', '81.30', '89.15', '96.95', '104.75', '112.60', '120.40', '128.20', '136.00'],
    9: ['68.35', '75.00', '83.00', '90.95', '98.85', '107.45', '116.45', '125.30', '134.15', '143.05'],
    10: ['63.05', '68.55', '74.20', '79.75', '85.65', '92.45', '99.05', '105.90', '112.65', '119.35'],
}

PMI_RATES_PRICE_GROUP_11_20 = {
    11: ['65.05', '69.50', '74.90', '81.80', '88.60', '100.60', '108.05', '115.50', '122.90', '130.40'],
    12: ['70.65', '77.95', '86.80', '96.80', '106.65', '130.85', '139.55', '148.50', '157.30', '166.15'],
    13: ['72.15', '76.25', '81.65', '87.95', '95.15', '103.00', '110.40', '118.00', '125.65', '133.00'],
    14: ['65.20', '70.30', '75.25', '80.25', '85.70', '92.00', '98.55', '105.05', '111.25', '117.90'],
    15: ['69.50', '73.65', '78.55', '83.60', '88.35', '93.35', '98.35', '103.40', '108.35', '113.50'],
    16: ['82.30', '85.50', '89.25', '94.65', '99.85', '105.30', '110.70', '116.20', '121.60', '127.15'],
    17: ['66.05', '69.45', '73.95', '78.50', '83.60', '89.20', '94.80', '100.35', '105.90', '111.55'],
    18: ['68.50', '71.90', '76.50', '82.25', '87.90', '93.75', '99.60', '105.45', '111.25', '117.15'],
    19: ['83.15', '91.65', '104.20', '116.60', '127.60', '138.55', '149.50', '160.45', '169.05', '176.90'],
    20: ['69.70', '76.90', '82.15', '88.45', '94.45', '97.45', '100.45', '106.45', '112.30', '118.40'],
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

