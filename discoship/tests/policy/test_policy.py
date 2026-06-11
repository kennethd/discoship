
import pytest

from discoship.policy import policy
from discoship.defs import USPS_SVC_FCPIS, USPS_SVC_PMI

PG_FCPIS_INDIA = 10
PG_FCPIS_INDONESIA = 4
PG_PMI_INDIA = 6
PG_PMI_INDONESIA = 6


def test_countries_for_price_group():
    # India & Indonesia are in different FCPIS price codes
    fcpis_countries = policy.countries_for_price_group(PG_FCPIS_INDIA)
    assert 'India' in fcpis_countries
    assert 'Indonesia' not in fcpis_countries
    # India & Indonesia are in the same PMI price code
    pmi_countries = policy.countries_for_price_group(PG_PMI_INDIA, USPS_SVC_PMI)
    assert 'India' in pmi_countries
    assert 'Indonesia' in pmi_countries


def test_select_shipping_query():
    # select_shipping_query(service=DEFAULT_SERVICE,
    #                       country=None,
    #                       price_group=None)

    # non-existent service raises ValueError
    with pytest.raises(ValueError) as e:
        query = policy.select_shipping_query(service="KLD")
    assert e.match("Unrecognized service: KLD")

    # valid service, no country, price_group
    for svc in (USPS_SVC_FCPIS, USPS_SVC_PMI):
        cols = ", ".join(policy.SVC_SELECT_LIST[svc])
        expect = f"SELECT {cols} FROM ship_countries WHERE usps_svc_code = ?"
        query, params = policy.select_shipping_query(service=svc)
        assert query == expect
        assert params == (svc, )

    # valid service & country
    for country in ("in", "india", "ind"):
        cols = ", ".join(policy.SVC_SELECT_LIST[USPS_SVC_FCPIS])
        expect = " ".join([
            f"SELECT {cols} FROM ship_countries WHERE usps_svc_code = ?",
            f"AND ( cc2 = ? OR country_name = ? OR cc3 = ? )",
        ])
        query, params = policy.select_shipping_query(country=country)
        assert query == expect
        assert params == (USPS_SVC_FCPIS, country.upper(), country.capitalize(), country.upper())

    # valid service & price_group
    svc_pgs = [(USPS_SVC_FCPIS, PG_FCPIS_INDIA), (USPS_SVC_PMI, PG_PMI_INDIA)]
    for svc, pg in svc_pgs:
        cols = ", ".join(policy.SVC_SELECT_LIST[svc])
        expect = " ".join([
            f"SELECT {cols} FROM ship_countries WHERE usps_svc_code = ?",
            f"AND usps_price_group = ?",
        ])
        query, params = policy.select_shipping_query(service=svc, price_group=pg)
        assert query == expect
        assert params == (svc, pg)


