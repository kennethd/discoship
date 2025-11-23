import logging

from discoship.defs import USPS_SERVICES, USPS_SVC_FCPIS, USPS_SVC_PMEI, USPS_SVC_PMI
from discoship.usps.cpg import fetch_cpg_data, ingest_cpg_data
from discoship.usps.fcpis import fetch_fcpis_rates_data, ingest_fcpis_rates_data
from discoship.usps.pmi import fetch_pmi_rates_data, ingest_pmi_rates_data
#from discoship.usps.pmei import fetch_pmei_rates_data, ingest_pmei_rates_data


log = logging.getLogger(__name__)


def fetch(fetchall=False, cpg=False, rates=False, service=None):
    """entrypoint for ingesting data from usps

    * `fetchall` corresponds to `discoship ingest usps --all`: all cpg data &
      all rates for all supported services will be ingested from usps sources
    * `cpg` ingests Country Price Group data
    * `rates` ingests rate data
    * `service` is one of: FCPIS, PMI, possibly PMEI.  If `fetchall` is not
      `True`, and service is not provided, `cpg` &/or `rate` data will be
      ingested for all supported services.

    Expected usage for normal users is to run `discoship ingest usps --all`
    occasionally to be sure of up-to-date rate data; the other options are for
    convenience of devs.

    Raises `ValueError` if `service` is unrecognized.
    Raises `RuntimeError` if args do not specify something to do.
    Parsers may raise `AssertionError` if source HTML changes.
    """
    log.info(f"fetch(fetchall={fetchall}, cpg={cpg}, rates={rates}, service={service})")

    if service not in [None] + list(USPS_SERVICES):
        raise ValueError(f"Unrecognized service: {service}")
    # Q: what should happen: discoship ingest usps --service FCPIS
    if service and not fetchall and not cpg and not rates:
        # A: ingest both cpg & rate data for service
        cpg = True
        rates = True
    if not fetchall and not cpg and not rates:
        raise RuntimeError('Nothing to do')

    # Country Price Codes
    if fetchall or cpg:
        # First Class Package Int'l
        if fetchall or service == USPS_SVC_FCPIS:
            cpg_data = fetch_cpg_data(service=USPS_SVC_FCPIS)
            ingest_cpg_data(cpg_data, service=USPS_SVC_FCPIS)
        # Priority Mail Int'l
        if fetchall or service == USPS_SVC_PMI:
            cpg_data = fetch_cpg_data(service=USPS_SVC_PMI)
            ingest_cpg_data(cpg_data, service=USPS_SVC_PMI)
        # Priority Mail Express Int'l
        if fetchall or service == USPS_SVC_PMEI:
            #cpg_data = fetch_cpg_data(service=USPS_SVC_PMEI)
            #ingest_cpg_data(cpg_data, service=USPS_SVC_PMEI)
            pass

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

