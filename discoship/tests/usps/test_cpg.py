
import pytest

from discoship.defs import USPS_SVC_PMI
from discoship.testing import load_bs4_data_fixture, load_saved_output
from discoship.usps import cpg


COUNTRY_PRICE_GROUPS = {
    'Syria': ('4', None, None),
    'Taiwan': ('10', None, None),
    'Tajikistan': ('4', None, None),
    'Tanzania': ('5', None, None),
    'Thailand': ('10', None, None),
    'Timor-Leste': ('4', None, None),
    'Togo': ('5', None, None),
    'Tonga': ('4', None, None),
    'Trinidad and Tobago': ('6', None, None),
    'Tristan da Cunha': ('5', None, None),
    'Tunisia': ('5', None, None),
    'Turkey': ('3', None, None),
    'Turkmenistan': ('4', None, None),
    'Turks and Caicos Islands': ('6', None, None),
    'Tuvalu': ('4', None, None),
    'Uganda': ('5', None, None),
    'Ukraine': ('3', None, None),
    'United Arab Emirates': ('10', None, None),
    'United Kingdom': ('20', None, None),
    'Uruguay': ('6', None, None),
    'Uzbekistan': ('4', None, None),
    'Vanuatu': ('4', None, None),
    'Vatican City': ('9', None, None),
    'Venezuela': ('11', None, None),
    'Vietnam': ('4', None, None),
    'Wallis and Futuna': ('4', None, None),
    'Yemen': ('4', None, None),
    'Zambia': ('5', None, None),
    'Zimbabwe': ('5', None, None)
}


def test_parse_cpg_rate_table():
    filename = 'usps.cpg._parse_cpg_data_table.htm'
    table_soup = load_bs4_data_fixture(filename, expect_to_find='table')
    result = cpg._parse_cpg_data_table(table_soup)
    assert result == COUNTRY_PRICE_GROUPS


def test_fetch_cpg_data(mocker):
    filename = 'fetch_url-fetch_usps_rate_tables.htm'
    html = load_saved_output(filename)
    mocker.patch('discoship.usps.cpg.fetch_usps_rate_tables', return_value=html)
    cpg_data = cpg.fetch_cpg_data()
    # use dict union operator to verify COUNTRY_PRICE_GROUPS is "subset" of cpg_data
    # https://peps.python.org/pep-0584/
    assert cpg_data | COUNTRY_PRICE_GROUPS == cpg_data
    cpg.fetch_usps_rate_tables.assert_called()


def test_insert_cpg_data(mocker):
    mocker.patch('discoship.usps.cpg.executemany', return_value=1)
    mocker.patch('discoship.usps.cpg.execute', return_value=1)
    mocker.patch('discoship.usps.cpg.selectone')
    cpg.insert_cpg_data(COUNTRY_PRICE_GROUPS, service=USPS_SVC_PMI)
    insert_vals = [ tuple([ctry, USPS_SVC_PMI] + list(v)) for ctry, v in COUNTRY_PRICE_GROUPS.items() ]
    cpg.executemany.assert_called_with(cpg.INSERT_USPS_CPG, insert_vals)
    cpg.execute.assert_called_with(cpg.UPDATE_LAST_INGEST_DATE, db=cpg.USERDATA_PATH)
    cpg.selectone.assert_called_with(cpg.SELECT_LAST_INGEST_DATE, db=cpg.USERDATA_PATH)

