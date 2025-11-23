import bs4
import logging
import os

from discoship.countries.aliases import COUNTRY_ALIASES
from discoship.db import USERDATA_PATH, execute, executemany, selectone
from discoship.io import fetch_url
from discoship.testing import save_bs4_data_fixture


log = logging.getLogger(__name__)


ISO3166_COUNTRIES_URL = "https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes"
ISO3166_H2_ID = "Current_ISO_3166_country_codes"

INSERT_ISO3166_COUNTRIES = """
  INSERT INTO iso3166_countries (name, official_name, code2, code3)
  VALUES (?, ?, ?, ?)
  ON CONFLICT DO NOTHING;
"""

UPDATE_LAST_INGEST_DATE = """
  UPDATE userdata SET value = DATETIME('now')
  WHERE name = 'last_ingest_iso3166_countries';
"""

SELECT_LAST_INGEST_DATE = """
  SELECT value FROM userdata WHERE name = 'last_ingest_iso3166_countries';
"""


@save_bs4_data_fixture
def _parse_iso3166_table_data(table_soup):
    """Parses BeautifulSoup table

    ISO3166 is maintained by the UN & currently defines codes for 249
    countries: https://en.wikipedia.org/wiki/ISO_3166-1

    The main purpose of this table is to allow specifying 2- or 3-letter country
    codes on the command line when generating policies for a specific country.

    returns dict {'country_name': ('Official Name', code2, code3), ...}
    """
    log.info('parsing iso3166 table data')
    assert isinstance(table_soup, bs4.element.Tag)
    assert table_soup.name == 'table'
    # remove all <sup> tags used for footnotes in source table
    for sup in table_soup.find_all('sup'):
        sup.decompose()
    tdata = table_soup.find('tbody')
    trs = tdata.find_all('tr')

    countries = {}
    # TODO: finish whatever I was doing with aliases...
    aliases = []
    for tr in trs:
        tds = tr.find_all('td')
        if not tds:
            continue
        if len(tds) == 1:
            assert tds[0].attrs['colspan'] == '8'
            aliases.append(tds[0].text.strip().strip('.').split(' – See '))
        else:
            assert len(tds) == 8
            names = [ li.text.strip() for li in tds[0].find_all('li') ]
            if not names:
                names = [ tds[0].text.replace(' (the)', '').strip() ]
            official_name = tds[1].text.replace('the ', '').strip()
            code2 = tds[3].text.strip()
            if code2 == 'GB':
                code2 = 'UK'
            code3 = tds[4].text.strip()
            for name in names:
                name = COUNTRY_ALIASES.get(name, name)
                countries[name] = (official_name, code2, code3)
    #print(aliases)
    #print(countries.keys())
    return countries


def fetch_iso3166_countries(url=ISO3166_COUNTRIES_URL):
    """Scrape ISO3166 Country data

    returns list of tuples: (country_name, official_name, code2, code3)"""
    log.info(f'fetching iso3166 country data from {url}')
    html = fetch_url(url)
    soup = bs4.BeautifulSoup(html, 'html.parser')
    h2 = soup.body.find('h2', id=ISO3166_H2_ID)

    # >>> h2.parent.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling
    #       .next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.name
    # 'table'
    safety = 0
    country_codes = []
    next_sib = h2.parent.next_sibling
    while True:
        if next_sib.name == 'table':
            table_data = _parse_iso3166_table_data(next_sib)
            break
        next_sib = next_sib.next_sibling
        safety += 1
        if safety >= 24:
            raise ValueError('Expected table not found. Has source HTML changed?')
    countries = [ (k, td[0], td[1], td[2]) for k, td in table_data.items() ]
    return countries


def ingest_iso3166_countries(countries):
    """insert fetched country data

    countries is list of tuples: (name, official_name, code2, code3)
    """
    #log.debug(f'ingest iso3166 countries: {countries}')
    rowcount = executemany(INSERT_ISO3166_COUNTRIES, countries)
    log.info(f'ingest_iso3166_countries: updated {rowcount} rows')
    rowcount = execute(UPDATE_LAST_INGEST_DATE, db=USERDATA_PATH)
    assert rowcount == 1
    row = selectone(SELECT_LAST_INGEST_DATE, db=USERDATA_PATH)
    log.info(f'updated last_ingest_iso3166_countries: {row[0]} (UTC)')


def fetch():
    countries = fetch_iso3166_countries()
    ingest_iso3166_countries(countries)

