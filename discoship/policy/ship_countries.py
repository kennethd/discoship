import logging
import sys

from discoship.db import select, selectone


log = logging.getLogger(__name__)


# discogs.name -- iso.name -- cpg.country_name
#                                .price_group       -- fcpis.price_group
#                                .usps_service_code -- "FCPIS"           -- svc.code
SQL_LIST_COUNTRIES = """
  SELECT country_name, cc2, cc3, usps_price_group, usps_svc_code
  FROM ship_countries
"""

# list countries present in iso3166_countries/usps_cpg & NOT present in discogs
SQL_LIST_ORPHANED_COUNTRIES = """
  SELECT iso.name AS country_name, 'ISO3166 (not in Discogs)' AS source
  FROM iso3166_countries AS iso
  LEFT JOIN discogs_destination_countries AS discogs
         ON iso.name = discogs.country_name
      WHERE discogs.country_name IS NULL
  UNION
  SELECT discogs.country_name, 'Discogs (not in ISO3166)' AS source
  FROM discogs_destination_countries AS discogs
  LEFT JOIN iso3166_countries AS iso
         ON discogs.country_name = iso.name
      WHERE iso.name IS NULL
  UNION
  SELECT cpg.country_name, 'USPS CPG (not in Discogs)' AS source
  FROM usps_cpg AS cpg
  LEFT JOIN discogs_destination_countries AS discogs
         ON cpg.country_name = discogs.country_name
      WHERE discogs.country_name IS NULL
  UNION
  SELECT discogs.country_name, 'Discogs (not in USPS CPG)' AS source
  FROM discogs_destination_countries AS discogs
  LEFT JOIN usps_cpg AS cpg
         ON discogs.country_name = cpg.country_name
      WHERE cpg.country_name IS NULL
  ORDER BY country_name ASC
"""


def select_countries(service=None):
    """select list of countries for which we have shipping prices

    if service is provided as usps service code ('FCPIS', 'PMI', 'PMEI'),
    list of countries will be restricted to those relevant to that policy

    return list of dicts"""
    log.info(f"select_countries: service={service}")
    if service:
        sql = f"{SQL_LIST_COUNTRIES}  WHERE usps_service_code = ?"
        params = (service,)
    else:
        sql = SQL_LIST_COUNTRIES
        params = ()
    rows = select(sql, params)
    countries = [ dict(row) for row in rows ]
    return countries


def list_countries(service=None, fh=sys.stdout):
    """prints list of countries for which shipping is supported

    if service is provided as usps service code ('FCPIS', 'PMI', 'PMEI'),
    list of countries will be restricted to those relevant to that policy

    optional `fh` is filehandle to write output to
    """
    countries = select_countries(service)
    log.info(f"list_countries: service={service} found {len(countries)} countries")
    max_name_len = max([ len(c['country_name']) for c in countries ])
    head = ('Country Name', '2-Code', '3-Code', 'Price Group', 'Service Code')
    tmpl = "{1:<{0}s}  {2:<6s}  {3:<6s}  {4:<11s}  {5:<12s}"
    if countries:
        print(tmpl.format(max_name_len, *head), file=fh)
        print('-' * max_name_len, '-' * 6, '-' * 6, '-' * 11, '-' * 12, sep='  ', file=fh)
        for country in countries:
            vals = [max_name_len] + [ str(v) for v in country.values() ]
            print(tmpl.format(*vals), file=fh)


def list_orphans(fh=sys.stdout):
    """prints list of countries that do not have matching names in iso & discogs tables

    for all shipping options, an inner join on iso3166_countries.name and
    discogs_destination_countries.name must be satisfied, additionally
    discogs_destination_countries.name value must appear in usps_cpg.country_name

    this function is intended to help populate COUNTRIES_ALIASES to reduce
    numbers of orphans:

    ```
    $ discoship  policy --list-orphans | head
    Total rows in iso3166_countries: 250
    Total rows in discogs_destination_countries: 243
    Total country names in usps_cpg: 218

    Country Name                                    Source
    ----------------------------------------------  -------------------------
    American Samoa                                  Discogs (not in USPS CPG)
    Antarctica                                      Discogs (not in USPS CPG)
    Ascension                                       USPS CPG (not in Discogs)
    Azerbaidjan                                     Discogs (not in ISO3166)
    Azerbaidjan                                     Discogs (not in USPS CPG)
    Azerbaijan                                      ISO3166 (not in Discogs)
    Azerbaijan                                      USPS CPG (not in Discogs)
    Bonaire                                         ISO3166 (not in Discogs)
    Bonaire, Sint Eustatius, and Saba               USPS CPG (not in Discogs)
    Bosnia and Herzegovina                          ISO3166 (not in Discogs)
    Bosnia-Herzegovina                              Discogs (not in ISO3166)
    Bouvet Island                                   ISO3166 (not in Discogs)
    British Indian Ocean Territory                  Discogs (not in USPS CPG)
    British Virgin Islands                          USPS CPG (not in Discogs)
    Cabo Verde                                      ISO3166 (not in Discogs)
    Cape Verde                                      Discogs (not in ISO3166)
    ```"""
    row = selectone("SELECT COUNT(*) AS c FROM iso3166_countries;")
    print(f"Total rows in iso3166_countries: {row['c']}", file=fh)
    row = selectone("SELECT COUNT(*) AS c FROM discogs_destination_countries;")
    print(f"Total rows in discogs_destination_countries: {row['c']}", file=fh)
    row = selectone("SELECT COUNT(DISTINCT(country_name)) AS c FROM usps_cpg;")
    print(f"Total country names in usps_cpg: {row['c']}", file=fh)
    print("", file=fh)

    rows = select(SQL_LIST_ORPHANED_COUNTRIES)
    log.info(f"list_orphan_countries: found {len(rows)} orphan countries")
    if not rows:
        return

    head = ('Country Name', 'Source')
    max_name_len = len(head[1])
    max_source_len = len(head[0])
    tmpl = "{2:<{0}s}  {3:<{1}s}"
    countries = []
    for row in rows:
        if len(row['country_name']) > max_name_len:
            max_name_len = len(row['country_name'])
        if len(row['source']) > max_source_len:
            max_source_len = len(row['source'])
        countries.append((row['country_name'], row['source']))
    print(tmpl.format(max_name_len, max_source_len, *head), file=fh)
    print('-' * max_name_len, '-' * max_source_len, sep='  ', file=fh)
    for country in countries:
        print(tmpl.format(max_name_len, max_source_len, *country), file=fh)

