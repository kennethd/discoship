import bs4
from collections import defaultdict
import logging
import re

from discoship.db import execute, executemany, selectone
from discoship.defs import USPS_SVC_FCPIS
from discoship.io import fetch_url


log = logging.getLogger(__name__)


RATE_TABLE_URL = "https://pe.usps.com/text/dmm300/Notice123.htm"
FCPIS_RATE_TABLE_HEADER_TEXT = "First-Class Package International Service Price Groups"

# usps_fcpis_rates has UNIQUE const on (price_group); to allow
# updates without rebuilding db from scratch, do UPSERT on conflict
INSERT_USPS_FCPIS_RATES = """
  INSERT INTO usps_fcpis_rates (
    price_group,
    weight_group_1,
    weight_group_2,
    weight_group_3,
    weight_group_4
  )
  VALUES (?, ?, ?, ?, ?)
  ON CONFLICT (price_group)
  DO UPDATE SET
    weight_group_1 = excluded.weight_group_1,
    weight_group_2 = excluded.weight_group_2,
    weight_group_3 = excluded.weight_group_3,
    weight_group_4 = excluded.weight_group_4
;
"""

UPDATE_LAST_INGEST_DATE = """
  UPDATE prefs SET value = DATETIME('now')
  WHERE name = 'last_ingest_usps_fcpis_rates';
"""

SELECT_LAST_INGEST_DATE = """
  SELECT value FROM prefs WHERE name = 'last_ingest_usps_fcpis_rates';
"""


def _parse_fcpis_rate_table(table_soup):
    """parse bs4 table Tag object for {Price Group: [rates]} data for FCPIS

    Data is presented in 2 tables on pe.usps.com page being scraped

    May raise AssertionError if source HTML changes

    returns dict {price_group: [rate, rate, rate, rate]}"""
    assert isinstance(table_soup, bs4.element.Tag)
    assert table_soup.name == 'table'
    #print(table_soup.contents)
    # [' ', <thead><tr><th>Weight Not Over (oz.)</th>...</th></tr></thead>,
    #  ' ', <tbody> <tr><td>1–8</td><td>...
    thead = table_soup.contents[1]
    assert thead.name == 'thead'
    tbody = table_soup.contents[3]
    assert tbody.name == 'tbody'

    pgindex = {}
    for i, th in enumerate(thead.find_all('th')):
        # skip col 0 == weight class description
        if i > 0:
            pgindex[i] = th.text
    #print(pgindex)
    # {1: '1', 2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7', 8: '8', 9: '9', 10: '10'}
    # {1: '11', 2: '12', 3: '13', 4: '14', 5: '15', 6: '16', 7: '17', 8: '18', 9: '19', 10: '20'}

    table_data = defaultdict(list)
    for tr in tbody.find_all('tr'):
        for i, td in enumerate(tr.find_all('td')):
            # skip col 0 == weight class description
            if i > 0:
                table_data[pgindex[i]].append(td.text.replace('$', ''))
    #print(table_data)
    return dict(table_data)


# <h4>First-Class Package International Service Price Groups
#   <a id="a_First-Class Package International Service Price Groups"
#      name="First-Class Package International Service Price Groups"></a>
# </h4>
# <a id="a_" name=""></a>
# <table class="table table-hover table-condensed table-pricing">
#   <thead>
#     <tr>
#       <th>Weight Not Over (oz.)</th>
#       ...10 <th>s containing price code 1-10 (11-20 in next table):
#       <th>1</th><th>2</th><th>3</th><th>4</th><th>5</th>
#       <th>6</th><th>7</th><th>8</th><th>9</th><th>10</th>
#     </tr>
#   </thead>
#   <tbody>
#     <tr>
#       <td>1–8</td>
#       ...10 <td>s w/price including "$"sign (following rows have no "$")
def fetch_fcpis_rates_data(url=RATE_TABLE_URL):
    """parses price by weight per price_group table

    USPS maintains 20 Price Groups for international shipping, each country
    is a member of 1 group (see cpg.py & usps_cpg table in db)

    Rates are determined by Price Group and Weight.  There are 4 weight
    classes: up to 8oz, 32oz, 48oz, and 64oz.  FCPIS packages cannot weigh
    more than 64oz (4lbs).

    returns dict {price_group: [rate, rate, rate, rate]} where for each price_group
    rates are returned for 4 increasing weight classes (8oz, 32oz, 48oz, 64oz)
    """
    log.info(f'fetching rates data from {url}')
    html = fetch_url(url)
    soup = bs4.BeautifulSoup(html, 'html.parser')
    soup = soup.body.find(id='pe-content-document')
    atag = soup.find(id=f'a_{FCPIS_RATE_TABLE_HEADER_TEXT}')
    h4tag = atag.parent
    assert h4tag.name == 'h4'
    next_sib = h4tag.next_sibling
    safety = 0
    tables_parsed = 0
    rates_data = {}
    while tables_parsed < 2:
        if next_sib.name == 'table':
            table_data = _parse_fcpis_rate_table(next_sib)
            rates_data.update(table_data)
            tables_parsed += 1
        next_sib = next_sib.next_sibling
        safety += 1
        if safety >= 24:
            raise ValueError('Expected tables not found. Has source HTML changed?')
    log.info(f'Fetched rate data for price groups: {rates_data}')
    #print(rates_data)
    return rates_data


def ingest_fcpis_rates_data(rates_data):
    """insert fetched rates_data into usps_fcpis_rates table

    exposed by cli via `fetch` subcommand:
    ```
    $ discoship fetch --rates
    ```
    to verify success (reqs installed sqlite3 package for client):
    ```
    $ sqlite3 discoship/data/discoship.db "SELECT COUNT(*) FROM usps_fcpis_rates;"
    20
    $ sqlite3 discoship/data/discoship.db ".headers on" ".mode column" "select * from usps_fcpis_rates limit 3;"
    price_group  weight_group_1  weight_group_2  weight_group_3  weight_group_4
    -----------  --------------  --------------  --------------  --------------
    1            17.85           26              38.5            47.6
    2            18.05           26.6            39              51.05
    3            20              37.35           56.25           74.35
    """
    log.debug(f'ingest_fcpis_rates_data: {rates_data}')
    # incoming rates_data is formatted as dict {price_group: [rates]}:
    # {'1': ['17.85', '26.00', '38.50', '47.60'], ...}
    vals = [ (k, v[0], v[1], v[2], v[3]) for k, v in rates_data.items() ]
    #print(vals)
    rowcount = executemany(INSERT_USPS_FCPIS_RATES, vals)
    log.info(f'ingest_fcpis_rates_data: updated {rowcount} rows')
    rowcount = execute(UPDATE_LAST_INGEST_DATE)
    assert rowcount == 1
    row = selectone(SELECT_LAST_INGEST_DATE)
    log.info(f'updated last_ingest_usps_fcpis_rates: {row[0]} (UTC)')

