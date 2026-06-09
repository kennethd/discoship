import bs4
from collections import defaultdict
import logging
import re

from discoship.db import USERDATA_PATH, execute, executemany, selectone
from discoship.defs import SOUP_PARSER
from discoship.io import fetch_usps_rate_tables


log = logging.getLogger(__name__)


PMEI_RATE_TABLE_HEADER_TEXT = "Priority Mail Express International"

INSERT_USPS_PMEI_RATES = """
  INSERT INTO usps_pmei_rates (
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
  WHERE name = 'last_ingest_usps_pmei_rates';
"""

SELECT_LAST_INGEST_DATE = """
  SELECT value FROM userdata WHERE name = 'last_ingest_usps_pmei_rates';
"""


def fetch_pmei_rates_data():
    pass


def insert_pmei_rates_data(pmei_rates_data):
    pass


