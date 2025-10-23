import logging

from discoship.defs import DEFAULT_SERVICE
from discoship.usps.cpg import fetch_cpg_data, ingest_cpg_data
from discoship.usps.rates import fetch_fcpis_rates_data, ingest_fcpis_rates_data


def fetch(fetchall=False, cpg=False, rates=False, service=DEFAULT_SERVICE):
    """entrypoint for ingesting data from usps"""
    if fetchall or cpg:
        cpg_data = fetch_cpg_data(service=service)
        ingest_cpg_data(cpg_data, service=service)
    if fetchall or rates:
        rates_data = fetch_fcpis_rates_data()
        ingest_fcpis_rates_data(rates_data)

