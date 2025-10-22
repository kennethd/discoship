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

with open(os.path.sep.join([os.path.dirname(__file__), 'VERSION']), 'r') as fh:
    VERSION = fh.read().strip()

