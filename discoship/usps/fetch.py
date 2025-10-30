import logging

from discoship.defs import DEFAULT_SERVICE, USPS_SVC_FCPIS, USPS_SVC_PMEI, USPS_SVC_PMI
from discoship.usps.cpg import fetch_cpg_data, ingest_cpg_data
from discoship.usps.fcpis import fetch_fcpis_rates_data, ingest_fcpis_rates_data
from discoship.usps.pmi import fetch_pmi_rates_data, ingest_pmi_rates_data
#from discoship.usps.pmei import fetch_pmei_rates_data, ingest_pmei_rates_data


def fetch(fetchall=False, cpg=False, rates=False, service=DEFAULT_SERVICE):
    """entrypoint for ingesting data from usps"""
    # Country Price Codes
    if fetchall or cpg:
        cpg_data = fetch_cpg_data(service=service)
        ingest_cpg_data(cpg_data, service=service)
    if fetchall or rates:
        # First Class Package Int'l
        if fetchall or service == USPS_SVC_FCPIS:
            fcpis_rates_data = fetch_fcpis_rates_data()
            ingest_fcpis_rates_data(fcpis_rates_data)
        # Priority Mail Int'l
        if fetchall or service == USPS_SVC_PMI:
            pmi_rates_data = fetch_pmi_rates_data()
            ingest_pmi_rates_data(pmi_rates_data)
        # Priority Mail Express Int'l
        if fetchall or service == USPS_SVC_PMEI:
            #pmei_rates_data = fetch_pmei_rates_data()
            #ingest_pmei_rates_data(pmei_rates_data)
            pass

