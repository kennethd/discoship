import logging
import sys

from discoship.db import select, selectone, select_config
from discoship.defs import DEFAULT_SERVICE, USPS_SVC_FCPIS, USPS_SVC_PMI, USPS_SVC_PMEI


log = logging.getLogger(__name__)



SVC_SELECT_LIST = {
    USPS_SVC_FCPIS: [
        "country_name",
        "cc2",
        "cc3",
        "usps_svc_code",
        "usps_price_group",
        "usps_svc_name",
        "svc_max_weight_oz",
        "svc_max_value",
        "fcpis_to_32oz AS rate_1lp",  # 1LP boxed up =~ 20oz
        "fcpis_to_48oz AS rate_2lp",  # *it's often very close to 32oz border
        "fcpis_to_48oz AS rate_3lp",  # 3*1LP =~ 42oz
        "fcpis_to_64oz AS rate_4lp",  # 4*1LP =~ 52oz
        "fcpis_to_64oz AS rate_5lp",  # 5*1LP =~ 62oz
        "'N/A' AS max_weight_lbs",
        "'N/A' AS flat_rate_price_group",
    ],
    USPS_SVC_PMI: [
        "country_name",
        "cc2",
        "cc3",
        "usps_svc_code",
        "usps_price_group",
        "usps_svc_name",
        "svc_max_weight_oz",
        "svc_max_value",
        "pmi_to_32oz AS rate_1lp",  # 1LP boxed up =~ 20oz
        "pmi_to_48oz AS rate_2lp",  # *it's often very close to 32oz border
        "pmi_to_48oz AS rate_3lp",  # 3*1LP =~ 42oz
        "pmi_to_64oz AS rate_4lp",  # 4*1LP =~ 52oz
        "pmi_to_64oz AS rate_5lp",  # 5*1LP =~ 62oz
        "pmi_to_80oz AS rate_6lp",  # 6*1LP =~ 66~68oz
        "pmi_to_80oz AS rate_7lp",  # 7*1LP =~ 78oz * * CLOSE TO 80oz
        "pmi_to_96oz AS rate_8lp",  # 8*1LP =~ 88oz
        "pmi_to_112oz AS rate_9lp",  # 9*1LP =~ 96oz. exactly @ border++
        "pmi_to_112oz AS rate_10lp",  # 10*1LP =~ 106oz
        "pmi_to_128oz AS rate_11lp",  # 11*1LP =~ 118oz
        "pmi_to_144oz AS rate_12lp",  # 12*1LP =~ 128oz. exactly border++
        "pmi_to_144oz AS rate_13lp",  # 13*1LP =~ 138oz
        "pmi_to_160oz AS rate_14lp",  # 14*1LP =~ 144oz. exactly border++
        "pmi_to_160oz AS rate_15lp",  # 15*1LP =~ 154oz
        "pmi_to_160oz AS rate_16lp",  # 16*1LP =~ 160oz. exactly border++
        "max_weight_lbs",
        "flat_rate_price_group",
    ],
}


def countries_for_price_group(price_group, service=DEFAULT_SERVICE):
    """returns list of country names for (price_group, service)

    USPS price groups are not the same across services:

    India                             IN      IND     10           FCPIS
    India                             IN      IND     6            PMI
    Indonesia                         ID      IDN     4            FCPIS
    Indonesia                         ID      IDN     6            PMI
    """
    countries = []
    query = " ".join([
        "SELECT country_name FROM ship_countries",
        "WHERE usps_svc_code = ?",
        "AND usps_price_group = ?",
        "ORDER BY country_name",
    ])
    params = (service, price_group)
    rows = select(query, params)
    for row in rows:
        countries.append(row["country_name"])
    return countries


def country_name_from_code(country):
    """returns string

    performs case-insensitive look up of ISO3166 country name specified either
    as name, code2, or code3

    raises ValueError if country not found; some spellings can be tricky, try
    `discoship list --countries`

    >>> country_name_from_code('in')
    'India'
    >>> country_name_from_code('idn')
    'Indonesia'
    >>> country_name_from_code('australia')
    'Australia'
    """
    if not country:
        raise ValueError("country arg cannot be empty")
    query = "SELECT name FROM iso3166_countries WHERE name = ? OR code2 = ? OR code3 = ?"
    params = (country, country, country)
    row = selectone(query, params)
    if not row:
        raise ValueError(f"Country not found: {country}")
    return row['name']


def select_shipping_query(service=DEFAULT_SERVICE, country=None, price_group=None):
    """returns SQL statement for policy rate table, and tuple of params

    May raise `ValueError` if `service` is unrecognized

    returns (sql_stmt, params)"""
    # it's unlikely somebody would specify both country & price_group, but
    # just in case, make sure it makes sense
    if country and price_group:
        pg_countries = countries_for_price_group(price_group, service=service)
        country_name = country_name_from_code(country)
        if country_name not in pg_countries:
            msg = f"{country} ({country_name}) not in {service} price group {price_group}"
            raise ValueError(msg)

    params = []
    cols = SVC_SELECT_LIST.get(service.upper())
    if not cols:
        raise ValueError(f"Unrecognized service: {service}")

    col_list = ", ".join(cols)
    sql_parts = [f"SELECT {col_list} FROM ship_countries WHERE usps_svc_code = ?"]
    params.append(service.upper())

    if country:
        sql_parts.append("AND ( cc2 = ? OR country_name = ? OR cc3 = ? )")
        params.extend([country, country, country])

    if price_group:
        sql_parts.append("AND usps_price_group = ?")
        params.append(price_group)

    sql_stmt = " ".join(sql_parts)
    params = tuple(params)
    log.debug(f"select_shipping_query: {sql_stmt} {params}")
    return (sql_stmt, params)



# {'country_name': 'India', 'cc2': 'IN', 'cc3': 'IND',
#  'usps_svc_name': "First-Class Package Int'l", 'usps_svc_code': 'FCPIS',
#  'usps_price_group': 10,
#  'svc_max_weight_oz': 64, 'svc_max_value': 400.0,
#  'rate_1lp': 34.8, 'rate_2lp': 50.15, 'rate_3lp': 50.15, 'rate_4lp': 68.65, 'rate_5lp': 68.65,
#  'max_weight_lbs': 'N/A', 'flat_rate_price_group': 'N/A'}
POLICY_TMPL_FCPIS = """

    USPS First Class Package Int'l (FCPIS)
    FCPIS Price Group: {price_group}
    Rates last updated: {rates_last_updated} (UTC)
    Countries: {countries}

    There are two rates to choose from for FCPIS, registered or not:

    NOT Registered:

    Qty LPs:                       1 LP    2-3 LPs*    4-5 LPs
    -------------------------+----------+----------+----------+
    Base Shipping            | {rate_1:8.2f} | {rate_2_3:8.2f} | {rate_4_5:8.2f} |
    -------------------------+----------+----------+----------+
    Packaging/Materials Fee  | {mats:8.2f} | {mats:8.2f} | {mats:8.2f} |
    -------------------------+----------+----------+----------+
    Certificate of Mailing   | {cert:8.2f} | {cert:8.2f} | {cert:8.2f} |
    -------------------------+----------+----------+----------+
    TOTAL                    | {total_1:8.2f} | {total_2_3:8.2f} | {total_4_5:8.2f} |
    -------------------------+----------+----------+----------+

    REGISTERED

    Qty LPs:                       1 LP    2-3 LPs*    4-5 LPs
    -------------------------+----------+----------+----------+
    Base Shipping            | {rate_1:8.2f} | {rate_2_3:8.2f} | {rate_4_5:8.2f} |
    -------------------------+----------+----------+----------+
    Packaging/Materials Fee  | {mats:8.2f} | {mats:8.2f} | {mats:8.2f} |
    -------------------------+----------+----------+----------+
    Registered**             | {reg:8.2f} | {reg:8.2f} | {reg:8.2f} |
    -------------------------+----------+----------+----------+
    TOTAL                    | {regtotal_1:8.2f} | {regtotal_2_3:8.2f} | {regtotal_4_5:8.2f} |
    -------------------------+----------+----------+----------+

    *  Weights for 2 * 1LPs packed up vary, but are very close to
       price group boundary of 32oz (and double-LPs even more so),
       if you are ordering 2LPs it is probably worth it to reach out
       to me and ask me to pack up your order & edit real shipping
       cost before paying for your order, could save you ~$24

    ** International Registered Mail means different things for
       different countries, see
       https://www.usps.com/international/insurance-extra-services.htm

"""


def _format_fcpis_policy(policy_rates, config):
    """formats policy_rates into human-readable string something like:

    USPS First Class Package Int'l (FCPIS)
    FCPIS Price Group: 12
    Countries: Australia, New Zealand

    There are two rates to choose from for FCPIS, registered or not:

    NOT Registered:

    Qty LPs:                       1 LP    2-3 LPs*    4-5 LPs
    -------------------------+----------+----------+----------+
    Base Shipping            |    41.25 |    65.25 |    79.10 |
    -------------------------+----------+----------+----------+
    Packaging/Materials Fee  |     1.50 |     1.50 |     1.50 |
    -------------------------+----------+----------+----------+
    Certificate of Mailing   |     2.50 |     2.50 |     2.50 |
    -------------------------+----------+----------+----------+
    TOTAL                    |    44.25 |    68.25 |    82.10 |
    -------------------------+----------+----------+----------+

    REGISTERED

    Qty LPs:                       1 LP    2-3 LPs*    4-5 LPs
    -------------------------+----------+----------+----------+
    Base Shipping            |    41.25 |    65.25 |    79.10 |
    -------------------------+----------+----------+----------+
    Packaging/Materials Fee  |     1.50 |     1.50 |     1.50 |
    -------------------------+----------+----------+----------+
    Registered**             |    22.00 |    22.00 |    22.00 |
    -------------------------+----------+----------+----------+
    TOTAL                    |    64.75 |    89.75 |   102.60 |
    -------------------------+----------+----------+----------+

    *  Weights for 2 * 1LPs packed up vary, but are very close to
       price group boundary of 32oz (and double-LPs even more so),
       if you are ordering 2LPs it is probably worth it to reach out
       to me and ask me to pack up your order & edit real shipping
       cost before paying for your order, could save you ~$15-25
       depending on your country

    ** International Registered Mail means different things for
       different countries, see
       https://www.usps.com/international/insurance-extra-services.htm

    """
    # config vals:
    #  'packing_handling_fee': 1.5,
    #  'usps_fcpis_cert_mailing_fee': 2.5,  * not if registered
    #  'usps_fcpis_registered_fee': 22.0,
    #  'last_ingest_usps_fcpis_rates': '2026-06-09 08:10:35',
    #  'weight_1_lp_oz': 20, 'weight_2_lp_oz': 34, 'weight_3_lp_oz': 42, 'weight_4_lp_oz': 52, 'weight_5_lp_oz': 60

    # policy_rates looks something like:
    # {'country_name': 'Australia', 'cc2': 'AU', 'cc3': 'AUS',
    #  'usps_svc_code': 'FCPIS', 'usps_price_group': 12, 'usps_svc_name': "First-Class Package Int'l",
    #  'svc_max_weight_oz': 64, 'svc_max_value': 400.0,
    #  'rate_1lp': 41.25, 'rate_2lp': 65.25, 'rate_3lp': 65.25, 'rate_4lp': 79.1, 'rate_5lp': 79.1,
    # 'max_weight_lbs': 'N/A', 'flat_rate_price_group': 'N/A'}

    tmpl_vars = {
        'rates_last_updated': config['last_ingest_usps_fcpis_rates'],
        'price_group': policy_rates['usps_price_group'],
        'countries': policy_rates['country_name'],
        'rate_1': policy_rates['rate_1lp'],
        'rate_2_3': policy_rates['rate_2lp'],
        'rate_4_5': policy_rates['rate_4lp'],
        'mats': config['packing_handling_fee'],
        'cert': config['usps_fcpis_cert_mailing_fee'],
        'total_1': policy_rates['rate_1lp'] + config['packing_handling_fee'] + config['usps_fcpis_cert_mailing_fee'],
        'total_2_3': policy_rates['rate_2lp'] + config['packing_handling_fee'] + config['usps_fcpis_cert_mailing_fee'],
        'total_4_5': policy_rates['rate_4lp'] + config['packing_handling_fee'] + config['usps_fcpis_cert_mailing_fee'],
        'reg': config['usps_fcpis_registered_fee'],
        'regtotal_1': policy_rates['rate_1lp'] + config['packing_handling_fee'] + config['usps_fcpis_registered_fee'],
        'regtotal_2_3': policy_rates['rate_2lp'] + config['packing_handling_fee'] + config['usps_fcpis_registered_fee'],
        'regtotal_4_5': policy_rates['rate_4lp'] + config['packing_handling_fee'] + config['usps_fcpis_registered_fee'],
    }

    return POLICY_TMPL_FCPIS.format(**tmpl_vars)



def _format_pmi_policy(policy_rates):
    """
    Beyond 4LBs USPS only ships International via PMI service:

    USPS Priority Mail Int'l (PMI)
    PMI Price Group: 12
    PMI Max Weight for Price Group: 66lbs
    Countries: Australia, New Zealand

    PRIORITY MAIL INTERNATIONAL

    Qty LPs:                       1 LP    2-3 LPs*    4-5 LPs
    -------------------------+----------+----------+----------+
    Base Shipping            |    73.70 |    82.65 |    91.45 |
    -------------------------+----------+----------+----------+
    Packaging/Materials Fee  |     1.50 |     1.50 |     1.50 |
    -------------------------+----------+----------+----------+
    TOTAL                    |    75.20 |    84.15 |    92.95 |
    -------------------------+----------+----------+----------+

    Beyond that price increments at 1 lb intervals:

    Qty LPs   Est Weight             Base Shipping + Fee = Total
    --------+----------------------+----------------------------
    6 LPs  =~ 68-70oz (< 5lb/80oz)   100.10      + 1.50 = 101.60
    7 LPs  =~ 78oz    (< 5lb/80oz)   110.10      + 1.50 = 101.60
    8 LPs  =~ 88oz    (< 6lb/96oz)   125.15      + 1.50 = 126.65
    9 LPs  =~ 96oz    (< 7lb/112oz)  133.50      + 1.50 = 135.00
    10 LPs =~ 106oz   (< 7lb/112oz)  133.50      + 1.50 = 135.00
    11 LPs =~ 118oz   (< 8lb/128oz)  142.50      + 1.50 = 144.00
    12 LPs =~ 128oz   (< 9lb/144oz)  150.45      + 1.50 = 151.95
    13 LPs =~ 136oz   (< 9lb/144oz)  150.45      + 1.50 = 151.95
    14 LPs =~ 144oz   (< 10lb/160oz) 158.90      + 1.50 = 160.40
    15 LPs =~ 152oz   (< 10lb/160oz) 158.90      + 1.50 = 160.40


{'country_name': 'Australia', 'cc2': 'AU', 'cc3': 'AUS', 'usps_svc_code':
'PMI', 'usps_price_group': 12, 'usps_svc_name': "Priority Mail Int'l",
'svc_max_weight_oz': 160, 'svc_max_value': 1025.0, 'rate_1lp': 73.7,
'rate_2lp': 82.65, 'rate_3lp': 82.65, 'rate_4lp': 91.45, 'rate_5lp': 91.45,
'rate_6lp': 100.1, 'rate_7lp': 100.1, 'rate_8lp': 125.15, 'rate_9lp': 133.5,
'rate_10lp': 133.5, 'rate_11lp': 142, 'rate_12lp': 150.45, 'rate_13lp':
150.45, 'rate_14lp': 158.9, 'rate_15lp': 158.9, 'rate_16lp': 158.9,
'max_weight_lbs': 66, 'flat_rate_price_group': 6}
    """
    pass


def print_policy(policy, service=DEFAULT_SERVICE, file=sys.stdout):
    pass


def create_policy(service=DEFAULT_SERVICE, country=None, price_code=None):
    sql_stmt, params = select_shipping_query(service, country, price_code)
    service_rates = selectone(sql_stmt, params)
    print(dict(service_rates))
    log.debug(f"create_policy({service}, {country}, {price_code}): found {len(service_rates)} rows")
    config = select_config()
    print(config)
    fcpis_policy = _format_fcpis_policy(service_rates, config)
    print(fcpis_policy)


def create_all_policies():
    pass

