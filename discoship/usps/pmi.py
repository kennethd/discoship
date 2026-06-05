from collections import defaultdict
import logging
import re

import bs4

from discoship.db import USERDATA_PATH, execute, executemany, selectone
from discoship.defs import SOUP_PARSER
from discoship.io import fetch_usps_rate_tables
from discoship.testing import save_bs4_data_fixture


log = logging.getLogger(__name__)


PMI_RATE_TABLE_HEADER_TEXT = "Priority Mail International"

INSERT_USPS_PMI_RATES = """
  INSERT INTO usps_pmi_rates (
    price_group,
    weight_to_16oz,   -- 1LB (not useful for LPs, 1xLP boxed up =~ 20+oz)
    weight_to_32oz,   -- 2LB (1xLP) ...single 2xLP often =~ 30oz
    weight_to_48oz,   -- 3LB (2-3 1xLPs) 2x1LPs =~ 36oz; 3x1LPs =~ 44oz
    weight_to_64oz,   -- 4LB (4-5 1xLPs) 4x1LPs =~ 52oz; 5x1LPs =~ 60oz
    weight_to_80oz,   -- 5LB (6 1xLPs) 6x1LPs =~ 70oz
    weight_to_96oz,   -- 6LB
    weight_to_112oz,  -- 7LB
    weight_to_128oz,  -- 8LB
    weight_to_144oz,  -- 9LB
    weight_to_160oz   -- 10LB
  )
  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
  ON CONFLICT (price_group)
  DO UPDATE SET
    weight_to_16oz = excluded.weight_to_16oz,
    weight_to_32oz = excluded.weight_to_32oz,
    weight_to_48oz = excluded.weight_to_48oz,
    weight_to_64oz = excluded.weight_to_64oz,
    weight_to_80oz = excluded.weight_to_80oz,
    weight_to_96oz = excluded.weight_to_96oz,
    weight_to_112oz = excluded.weight_to_112oz,
    weight_to_128oz = excluded.weight_to_128oz,
    weight_to_144oz = excluded.weight_to_144oz,
    weight_to_160oz = excluded.weight_to_160oz
;
"""

UPDATE_LAST_INGEST_DATE = """
  UPDATE userdata SET value = DATETIME('now')
  WHERE name = 'last_ingest_usps_pmi_rates';
"""

SELECT_LAST_INGEST_DATE = """
  SELECT value FROM userdata WHERE name = 'last_ingest_usps_pmi_rates';
"""


@save_bs4_data_fixture
def _parse_pmi_rate_table(table_soup):
    """parse bs4 table Tag object for PMI price data

    Source HTML splits rates across 2 tables, one for price groups 1-10 & a
    second for price groups 11-20.

    May raise AssertionError if source HTML changes

    returns dict {price_group: [list of rates]}"""
    log.info('parsing pmi rate table')
    assert isinstance(table_soup, bs4.element.Tag)
    assert table_soup.name == 'table'
    #print(table_soup.contents)
    # [' ', <thead> <tr><th rowspan="2">Weight Not Over<br/>(lbs.)</th>
    #       <th colspan="10">Price Group</th></tr> <tr><th>Canada 1</th>...</tr></thead>,
    #  ' ', <tbody>...</tbody>, ' ']
    _, thead, _, tbody, _ = table_soup.contents

    assert thead.name == 'thead'
    trs = thead.find_all('tr')
    ths = trs[1].find_all('th')
    # Price Group 1 is labelled "Canada 1", rest are just number
    pgs = [ int(th.text.replace('Canada', '').strip()) for th in ths ]
    table_data = { pg:[] for pg in pgs }

    assert tbody.name == 'tbody'
    trs = tbody.find_all('tr')
    # 70 rows of 11 cells: [up_to_weight, pg_1_price, ..., pg_10_price]
    i = 0
    for tr in trs:
        tds = tr.find_all('td')

        i += 1
        up_to_lbs = int(tds[0].text)
        assert i == up_to_lbs
        for j, pg in enumerate(pgs, start=1):
            rate = tds[j].text.replace('$', '').strip()
            table_data[pg].append(rate)
        # only collect data up to 10lbs
        if i == 10:
            break

    return table_data


# >>> h2.parent.next_sibling.next_sibling.parent.parent
# <div id="_c334" style="page-break-before: always">
#   <div class="h2-container row">
#     <div class="col-md-11">
#       <h2>Priority Mail International</h2>
#     </div>
#     <div class="col-md-1 text-right">
#       <a class="small hidden-print" href="#top">^ Top</a>
#     </div>
#   </div>
#   <h3>Retail—Large Envelopes &amp; Parcels</h3>
#   <div class="row">
#     <div class="col-md-10">
#       <table class="table table-hover table-condensed table-pricing-condensed">
#         <!--   ...SKIP FLAT RATES TABLE...   -->
#       </table>
#     </div>
#   </div>
#   <table class="table table-hover table-condensed table-pricing-condensed row-5-border">
#     <thead>
#       <tr>
#         <th rowspan="2">Weight Not Over<br/>(lbs.)</th>
#         <th colspan="10">Price Group</th>
#       </tr>
#       <tr>
#         <th>Canada 1</th><th>2</th><th>3</th><th>4</th><th>5</th><th>6</th><th>7</th><th>8</th><th>9</th><th>10</th>
#       </tr>
#     </thead>
#     <tbody>
#       <tr>
#         <td>1</td>         <!-- UP TO ONE POUND -->
#         <td>$42.95</td>    <!-- PRICE CODE 1 -->
#         <td>$56.70</td>    <!-- ETC... -->

def fetch_pmi_rates_data():
    """parses price by weight per price_group table

    USPS maintains 20 Price Groups for international shipping, each country
    is a member of 1 group (see cpg.py & usps_cpg table in db)

    Rates are determined by Price Group and Weight.  PMI & PMEI service rates
    increate per pound.

    May raise AssertionError if source HTML changes

    returns dict {price_group: [rates]} where for each price_group rates are
    returned for 10 weight classes (up to 1lb, ..., up to 10lbs)
    """
    log.info('fetching PMI rates data')
    pmi_rates = { i:[] for i in range(1, 21) }

    html = fetch_usps_rate_tables()
    soup = bs4.BeautifulSoup(html, SOUP_PARSER)
    h2 = soup.body.find('h2', string=re.compile(PMI_RATE_TABLE_HEADER_TEXT))
    assert h2.name == 'h2'
    div_c334 = h2.parent.next_sibling.next_sibling.parent.parent
    assert div_c334.attrs.get('id') == '_c334'
    thead = div_c334.find(string=re.compile("Weight Not Over")).parent.parent.parent
    assert thead.name == 'thead'
    table_soup = thead.parent
    table_data = _parse_pmi_rate_table(table_soup)
    pmi_rates.update(table_data)

    # Next table: Price Group—Continued
    div_c339 = div_c334.next_sibling.next_sibling.next_sibling.next_sibling
    assert div_c339.attrs.get('id') == '_c339'
    table_soup = div_c339.find('table')
    table_data = _parse_pmi_rate_table(table_soup)
    pmi_rates.update(table_data)

    log.debug(f'collected data for {len(table_data.keys())} price groups')
    assert len(pmi_rates.keys()) == 20
    return pmi_rates


def ingest_pmi_rates_data(pmi_rates_data):
    """insert fetched `pmi_rates_data` into `usps_pmi_rates` table

    exposed by cli via `ingest` subcommand:
    ```
    $ discoship ingest usps --rates --pmi
    ```
    """
    log.info('ingesting pmi rates data')
    log.debug(pmi_rates_data)
    # incoming rates_data is formatted as dict {price_group: [rates]}:
    # {'1': ['17.85', '26.00', '38.50', '47.60'], ...}
    vals = [ tuple([k] + v) for k, v in pmi_rates_data.items() ]
    rowcount = executemany(INSERT_USPS_PMI_RATES, vals)
    log.info(f'ingest_pmi_rates_data: updated {rowcount} rows')
    rowcount = execute(UPDATE_LAST_INGEST_DATE, db=USERDATA_PATH)
    assert rowcount == 1
    row = selectone(SELECT_LAST_INGEST_DATE, db=USERDATA_PATH)
    log.info(f'updated last_ingest_usps_pmi_rates: {row[0]} (UTC)')

