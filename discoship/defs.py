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
USPS_SVC_PMEI = "Priority Mail Express"
USPS_SVC_PMI = "Priority Mail"
USPS_SVC_FCMI = "First-Class"
USPS_SVC_FCPIS = "FCPIS"
USPS_SVC_AIR = "IPA"
USPS_SVC_AIRLIFT = "ISAL"

DEFAULT_PROVIDER = "USPS"
DEFAULT_SERVICE = USPS_SVC_FCPIS

PKG_PATH = os.path.dirname(__file__)
REPO_PATH = os.path.dirname(PKG_PATH)

with open(os.path.sep.join([PKG_PATH, 'VERSION']), 'r') as fh:
    VERSION = fh.read().strip()

# init'ed db is included with package repo
DB_PATH = os.path.sep.join([PKG_PATH, 'data', 'discoship.db'])
SQL_INGEST_PATH = os.path.sep.join([PKG_PATH, 'data', 'create-ingest-tables.sql'])
SQL_DISCOGS_PATH = os.path.sep.join([PKG_PATH, 'data', 'create-discogs-tables.sql'])
SQL_CONFIG_PATH = os.path.sep.join([PKG_PATH, 'data', 'create-config-table.sql'])
