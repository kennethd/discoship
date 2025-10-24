"""
unfortunately discogs API doesn't expose shipping policy editor stuff

in lieu of being able to ingest list of shipping destinations from API, I have
manually downloaded the source for that widget (24 Oct 2025) via chrome dev
tools, and will use that HTML fragment as source.
"""
import bs4
import logging
import os
import sqlite3

from discoship.db import execute, executemany, selectone
from discoship.defs import PKG_PATH


log = logging.getLogger(__name__)


SHIP_DESTS_PATH = os.path.sep.join([PKG_PATH, 'data', 'discogs-shipping-destinations.htm'])
# due to the organisation of data in the html, some unwanted subheaders will
# appear in results when selecting on css class 'region-name', though they are
# not shipping destinations themselves
IGNORE_REGION_NAMES = [
    'North America',
    'Central America',
    'South America',
    'Central Asia',
    'South-Eastern Asia',
    'Western Asia',
    'Eastern Asia',
    'Southern Asia',
]

INSERT_DISCOGS_COUNTRIES = """
  INSERT INTO discogs_destination_countries (country_name)
  VALUES (?)
  ON CONFLICT DO NOTHING;
"""

UPDATE_LAST_INGEST_DATE = """
  UPDATE config SET value = DATETIME('now')
  WHERE name = 'last_ingest_discogs_countries';
"""

SELECT_LAST_INGEST_DATE = """
  SELECT value FROM config WHERE name = 'last_ingest_discogs_countries';
"""


# the only thing to ingest from discogs is list of destination countries,
# and we are ingesting from local file so keeping it simple in one file..
def parse_destinations(source=SHIP_DESTS_PATH):
    """Parses Discogs' list of shipping destinations

    returns list of country names"""
    log.info(f'parsing {source} for Discogs shipping destinations')
    with open(source, 'r') as fh:
        html = fh.read()

    soup = bs4.BeautifulSoup(html, 'html.parser')
    labels = soup.find_all(class_='region-name')
    destinations = []
    for label in labels:
        country = label.text.replace('\n', ' ')
        if country not in IGNORE_REGION_NAMES:
            destinations.append(country)
    return sorted(destinations)


def ingest_destinations(destinations):
    """insert discogs destinations into discogs_destination_countries table

    exposed by cli via `ingest` subcommand:
    ```
    $ discoship ingest discogs --destinations
    ```
    """
    log.debug(f'ingest discogs destinations: {destinations}')
    vals = [ tuple([c]) for c in destinations ]
    rowcount = executemany(INSERT_DISCOGS_COUNTRIES, vals)
    log.info(f'ingest_destinations: updated {rowcount} rows')
    rowcount = execute(UPDATE_LAST_INGEST_DATE)
    assert rowcount == 1
    row = selectone(SELECT_LAST_INGEST_DATE)
    log.info(f'updated last_ingest_discogs_countries: {row[0]} (UTC)')


def fetch(source=SHIP_DESTS_PATH):
    destinations = parse_destinations()
    ingest_destinations(destinations)

