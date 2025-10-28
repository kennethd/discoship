/*
This file drops & re-creates tables for data ingestion processes.  These
tables are not intended to be modified manually.  Do not add table definitions
to this file if dropping and recreating them will lose user-modified data.
*/

DROP TABLE IF EXISTS usps_service;
CREATE TABLE usps_service(
    code VARCHAR PRIMARY KEY,
    name VARCHAR,
    max_weight_oz INTEGER,
    max_value REAL
);

DROP TABLE IF EXISTS usps_cpg;
CREATE TABLE usps_cpg(
    country_name VARCHAR NOT NULL,
    usps_service_code VARCHAR NOT NULL,
    price_group INTEGER NOT NULL,
    FOREIGN KEY (usps_service_code) REFERENCES usps_service(code),
    PRIMARY KEY (country_name, usps_service_code)
);
CREATE INDEX idx_usps_cpg_price_group ON usps_cpg(price_group);

DROP TABLE IF EXISTS usps_fcpis_rates;
CREATE TABLE usps_fcpis_rates(
    price_group INTEGER NOT NULL PRIMARY KEY,
    -- packing material alone is ~6oz
    weight_to_8oz INTEGER NOT NULL,  -- ship cost up to 8oz
    -- one LP boxed up is ~18-20oz
    -- one 2xLP is ~22-24oz
    -- 2 LPs ~28-32oz
    weight_to_32oz INTEGER NOT NULL,  -- up to 32oz
    -- 3 LPs ~36oz
    weight_to_48oz INTEGER NOT NULL,  -- up to 48oz
    weight_to_64oz INTEGER NOT NULL  -- up to 64oz
);

-- https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes
DROP TABLE IF EXISTS iso3166_countries;
CREATE TABLE iso3166_countries(
    name VARCHAR NOT NULL PRIMARY KEY,
    official_name VARCHAR NOT NULL,
    code2 VARCHAR NOT NULL,
    code3 VARCHAR NOT NULL
);
CREATE INDEX idx_iso3166_countries_official_name ON iso3166_countries(official_name);
CREATE INDEX idx_iso3166_countries_code2 ON iso3166_countries(code2);
CREATE INDEX idx_iso3166_countries_code3 ON iso3166_countries(code3);


-- the list of countries in the shipping policy editor
-- https://www.discogs.com/settings/shipping
DROP TABLE IF EXISTS discogs_destination_countries;
CREATE TABLE discogs_destination_countries(
    country_name VARCHAR NOT NULL PRIMARY KEY
);


DROP VIEW IF EXISTS ship_countries;
CREATE VIEW ship_countries AS
SELECT
    iso.name AS country_name,
    iso.code2 AS cc2,
    iso.code3 AS cc3,
    svc.code AS usps_svc_code,
    -- svc.name AS usps_svc_name,
    svc.max_weight_oz,
    svc.max_value,
    cpg.price_group AS usps_price_group,
    fcpis.weight_to_8oz AS fcpis_to_8oz,
    fcpis.weight_to_32oz AS fcpis_to_32oz,
    fcpis.weight_to_48oz AS fcpis_to_48oz,
    fcpis.weight_to_64oz AS fcpis_to_64oz
FROM iso3166_countries AS iso
LEFT JOIN usps_cpg AS cpg
       ON iso.name = cpg.country_name
LEFT JOIN usps_service AS svc
       ON cpg.usps_service_code = svc.code
LEFT JOIN usps_fcpis_rates AS fcpis
       ON cpg.price_group = fcpis.price_group
      AND cpg.usps_service_code = 'FCPIS'
;

-- initial inserts

INSERT INTO usps_service
("code", "name", "max_weight_oz", "max_value")
VALUES
("FCPIS", "First-Class Package Int'l", 64, 400.00),
-- PMI comes in 2 flavors: flat-rate or by-weight
("PMI", "Priority Mail Int'l", 1056, NULL),  -- up tp 66lbs
-- 2 price groups allow up to 70lbs but calling it at 66
-- https://pe.usps.com/text/dmm300/Notice123.htm#_c334
("PMEI", "Priority Mail Express Int'l", NULL, NULL)
;

