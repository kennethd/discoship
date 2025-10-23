import bs4
import logging
import re

from discoship.db import execute, executemany, selectone
from discoship.defs import DEFAULT_SERVICE
from discoship.io import fetch_url


log = logging.getLogger(__name__)


CPG_DATA_URL = "https://pe.usps.com/text/dmm300/Notice123.htm"
CPG_HEADER_TEXT = "Country Price Groups"

# usps_cpg primary key is (country_name, usps_service_code); to allow
# updates without rebuilding db from scratch, do UPSERT on conflict
INSERT_USPS_CPG = """
  INSERT INTO usps_cpg (country_name, usps_service_code, price_group)
  VALUES (?, ?, ?)
  ON CONFLICT (country_name, usps_service_code)
  DO UPDATE SET price_group = excluded.price_group;
"""

UPDATE_LAST_INGEST_DATE = """
  UPDATE prefs SET value = DATETIME('now')
  WHERE name = 'last_ingest_usps_cpg';
"""

SELECT_LAST_INGEST_DATE = """
  SELECT value FROM prefs WHERE name = 'last_ingest_usps_cpg';
"""


# there is not a single <div> enclosing only the Country Price Groups
# so must find_all CPG_HEADER_TEXT & navigate the soup to each table:
# <div id="_c419">
#   <div class="h2-container row">
#     <div class="col-md-11">
#       <h2>Country Price Groups</h2>            <-- selector ***
#   <table>
#     <thead>
#       <tr>
#         <th>Country</th>
#         <th colspan=3>Priority Mail Express Int'l</th>
#         <th colspan=3>Priority Mail Int'l</th>
#         <th>First Class Mail Int'l</th>
#         <th>FCPIS</th>                         <-- target col (8)
#         <th>IPA</th>
#         <th>ISAL</th>
#     <tbody>
#       <tr>
#         <td>Cayman Islands</td>                <-- target col (0)
#         ...7 more <td> elements
#         <td>6</td>                             <-- target col (8)
#         ...2 more <td> elements
def _parse_cpg_data_table(table_soup, service=DEFAULT_SERVICE):
    """parse bs4 table Tag object for {Country:Price Group} data for service

    There are several such tables on pe.usps.com page being scraped

    May raise AssertionError if source HTML changes

    returns dict {country: price_group}"""
    assert isinstance(table_soup, bs4.element.Tag)
    assert table_soup.name == 'table'
    #print(table_soup.contents)
    # [' ', <thead> <tr><th rowspan="2">Country</th>...</thead>, ' ', <tbody> ...]
    thead = table_soup.contents[1]
    assert thead.name == 'thead'
    tbody = table_soup.contents[3]
    assert tbody.name == 'tbody'

    parsed_cpg_data = {}
    service_index = 0
    log.debug(f'looking for service_index for {service}')
    trs = thead.find_all('tr')
    for th in trs[0].find_all('th'):
        # <th rowspan="2">Country</th>
        # <th colspan="3">Priority Mail Express<br/>International</th>
        # <th colspan="3">Priority Mail<br/>International</th>
        # <th>First-Class<br/>Mail Int'l<sup>3</sup></th>
        # <th>FCPIS<sup>3</sup></th>             *note th.text == FCPIS3
        # <th>IPA<sup>4</sup></th>
        # <th>ISAL<sup>4</sup></th>
        if service.lower() in th.text.lower():
            # TODO: if enabling PMEI/PMI prev line needs change to re.match() with \b
            log.debug(f'{service} found in {th.text}')
            break
        colspan = th.attrs.get('colspan', 1)
        service_index += int(colspan)
    log.debug(f'{service} service_index is {service_index}')

    for tr in tbody.find_all('tr'):
        #print(tr.contents)
        # [<td>Afghanistan</td>, <td>n/a</td>, <td>n/a</td>, <td>n/a</td>, <td>7</td>,
        #  <td>66</td>, <td>8</td>, <td>6</td>, <td>4</td>, <td>4</td>, <td>n/a</td>]
        country = tr.contents[0].text.strip()
        cpg = tr.contents[service_index].text.strip()
        parsed_cpg_data[country] = cpg

    log.debug(f'Parsed {len(parsed_cpg_data)} Country Rate Groups')
    return parsed_cpg_data


def fetch_cpg_data(url=CPG_DATA_URL, service=DEFAULT_SERVICE):
    """parses Country Price Group data from pe.usps.com

    returns dict {country: price_group}"""
    log.info(f"fetching CPG data from {url}")
    cpg_data = {}
    html = fetch_url(url)
    soup = bs4.BeautifulSoup(html, 'html.parser')
    h2s = soup.body.find_all('h2', string=re.compile(CPG_HEADER_TEXT))
    log.debug(f'Found {len(h2s)} <h2> elements w/text {CPG_HEADER_TEXT}')
    for h2 in h2s:
        #print(h2.parent.parent.contents)
        # [' ', <div class="col-md-11"><h2>Country Price Groups</h2></div>, ' ',
        #  <div class="col-md-1 text-right"><a class="small hidden-print" href="#top">^ Top</a></div>, ' ']
        table_soup = h2.parent.parent.next_sibling.next_sibling
        parsed_cpg_data = _parse_cpg_data_table(table_soup, service=service)
        #print(parsed_cpg_data)
        cpg_data.update(parsed_cpg_data)
    log.info(f'Fetched {len(cpg_data)} Country Price Groups')
    #print(cpg_data)
    return cpg_data


def ingest_cpg_data(cpg_data, service=DEFAULT_SERVICE):
    """insert fetched cpg_data into usps_cpg table

    exposed by cli via `fetch` subcommand:
    ```
    $ discoship fetch --cpg
    ```
    to verify success (reqs installed sqlite3 package for client):
    ```
    $ sqlite3 discoship/data/discoship.db "SELECT COUNT(*) FROM usps_cpg;"
    219
    $ sqlite3 discoship/data/discoship.db ".headers on" ".mode column" "select * from usps_cpg limit 3;"
    country_name         usps_service_code  price_group
    -------------------  -----------------  -----------
    Afghanistan          FCPIS              4
    Albania              FCPIS              3
    Algeria              FCPIS              5
    ```"""
    log.debug(f'ingest_cpg_data: service={service} {cpg_data}')
    # incoming cpg_data is formatted as:
    # {'Afghanistan': '4', 'Albania': '3', 'Algeria': '5', ...}
    vals = [ (k, service, v) for k, v in cpg_data.items() ]
    #print(vals)
    rowcount = executemany(INSERT_USPS_CPG, vals)
    log.info(f'ingest_cpg_data: updated {rowcount} rows')
    rowcount = execute(UPDATE_LAST_INGEST_DATE)
    assert rowcount == 1
    row = selectone(SELECT_LAST_INGEST_DATE)
    log.info(f'updated last_ingest_usps_cpg: {row[0]} (UTC)')

