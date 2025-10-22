from bs4 import BeautifulSoup
import logging

from discoship.io import fetch_url


log = logging.getLogger(__name__)


CPG_DATA_URL = "https://pe.usps.com/text/dmm300/Notice123.htm"
CPG_DATA_DIVID = "_c419"
# data service columns are labeled:
# Priority Mail Express International  priority insanely $$$
# Priority Mail International          priority insanely $$$
# First-Class Mail Int'l               non-packages
# FCPIS                                * * * our default * * *
# IPA                                  airmail
# ISAL                                 air lift
CPG_DATA_SERVICE = "FCPIS"


def fetch_cpg_data(url=CPG_DATA_URL, divid=CPG_DATA_DIVID,
                   service=CPG_DATA_SERVICE, verbose=False):
    """parses Country Price Group data from pe.usps.com

    returns dict {country: price_group}"""
    log.info(f"fetching CPG data from {url}")
    body = fetch_url(url, verbose=verbose)
    print(body)
    soup = BeautifulSoup(body, 'html.parser')


