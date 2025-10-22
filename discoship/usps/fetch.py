import logging

from discoship.defs import DEFAULT_SERVICE
from discoship.usps.cpg import fetch_cpg_data, ingest_cpg_data


# (venv3.11) kenneth@fado ~/git/discoship $ discoship fetch --cpg
# Namespace(provider='usps', action='fetch', all=False, cpg=True, rates=False, service='fcpis')
def fetch(fetchall=False, cpg=False, rates=False, service=DEFAULT_SERVICE):
    if fetchall or cpg:
        cpg_data = fetch_cpg_data(service=service)
        ingest_cpg_data(cpg_data, service=service)

