# this file should never import anything from discoship
import os

# USPS Int'l Services from https://pe.usps.com/text/dmm300/Notice123.htm#_c419
# service columns are labeled:
# Priority Mail Express<br>International  priority insanely $$$
# Priority Mail<br>International          priority insanely $$$
# First-Class<br>Mail Int'l               non-packages
# FCPIS                                   * * * our default * * *
# IPA                                     air mail
# ISAL                                    air lift
USPS_SVC_FCPIS = "FCPIS"
USPS_SVC_PMEI = "PMEI"
USPS_SVC_PMI = "PMI"
USPS_SVC_AIR = "IPA"
USPS_SVC_AIRLIFT = "ISAL"
USPS_SERVICES = (USPS_SVC_FCPIS, USPS_SVC_PMI)

USPS_RATE_TABLES_URL = "https://pe.usps.com/text/dmm300/Notice123.htm"

DEFAULT_PROVIDER = "USPS"
DEFAULT_SERVICE = USPS_SVC_FCPIS

PKG_PATH = os.path.dirname(__file__)
REPO_PATH = os.path.dirname(PKG_PATH)
TESTS_DATA_PATH = os.path.sep.join([PKG_PATH, 'tests', 'data'])

with open(os.path.sep.join([PKG_PATH, 'VERSION']), 'r') as fh:
    VERSION = fh.read().strip()

# init'ed db is included with package repo
DB_PATH = os.path.sep.join([PKG_PATH, 'data', 'discoship.db'])
USERDATA_PATH = os.path.sep.join([PKG_PATH, 'data', 'userdata.db'])
SQL_INGEST_PATH = os.path.sep.join([PKG_PATH, 'data', 'create-ingest-tables.sql'])
SQL_CONFIG_PATH = os.path.sep.join([PKG_PATH, 'data', 'create-userdata-table.sql'])

# html5lib & lxml insist on creating well-formed docs, adding <html>...</html>
# we want to write doc fragments, innerHTML style
SOUP_PARSER = 'html.parser'
