import logging

from discoship.defs import DEFAULT_SERVICE
from discoship.usps.cpg import fetch_cpg_data


# (venv3.11) kenneth@fado ~/git/discoship $ discoship fetch --cpg
# Namespace(verbose=False, provider='usps', action='fetch', all=False,
#           cpg=True, rates=False, service='fcpis')
def fetch(fetchall=False, cpg=False, rates=False, service=DEFAULT_SERVICE,
          verbose=False):
    if fetchall or cpg:
        fetch_cpg_data(service=service, verbose=verbose)


