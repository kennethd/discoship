/*
This file drops & re-creates tables for data ingestion processes.  These
tables are not intended to be modified manually.  Do not add table definitions
to this file if dropping and recreating them will lose user-modified data.
*/

DROP VIEW IF EXISTS ship_countries;
DROP TABLE IF EXISTS usps_cpg;  -- FK refs usps_service; drop first
DROP TABLE IF EXISTS usps_service;
DROP TABLE IF EXISTS usps_fcpis_rates;
DROP TABLE IF EXISTS usps_pmi_rates;
DROP TABLE IF EXISTS usps_pmei_rates;
DROP TABLE IF EXISTS iso3166_countries;
DROP TABLE IF EXISTS discogs_destination_countries;


CREATE TABLE usps_service(
    code VARCHAR NOT NULL PRIMARY KEY,
    name VARCHAR,
    max_weight_oz INTEGER,
    max_value REAL
);

-- https://pe.usps.com/text/dmm300/Notice123.htm#_c419
CREATE TABLE usps_cpg(
    country_name VARCHAR NOT NULL,
    usps_service_code VARCHAR NOT NULL,
    price_group INTEGER NOT NULL,
    max_weight_lbs INTEGER NULL,  -- N/A for FCPIS
    flat_rate_price_group INTEGER NULL,  -- N/A for FCPIS
    FOREIGN KEY (usps_service_code) REFERENCES usps_service(code),
    PRIMARY KEY (country_name, usps_service_code)
);
CREATE INDEX idx_usps_cpg_price_group ON usps_cpg(price_group);

CREATE TABLE usps_fcpis_rates(
    price_group INTEGER NOT NULL PRIMARY KEY,
    -- packing material alone is ~6oz
    weight_to_8oz INTEGER NOT NULL,  -- ship cost up to 8oz
    -- one LP boxed up is ~18-20oz
    -- one 2xLP is ~22-24oz
    weight_to_32oz INTEGER NOT NULL,  -- 2 LPs ~28-32oz
    weight_to_48oz INTEGER NOT NULL,  -- 3 LPs ~36oz
    weight_to_64oz INTEGER NOT NULL   -- up to 64oz
);

CREATE TABLE usps_pmi_rates(
    price_group INTEGER NOT NULL PRIMARY KEY,
    -- packing material alone is ~6oz
    -- PMI & PMEI rates increase by the pound, to 66lbs total
    -- I think standard mailing boxes hold at most ~6lps
    weight_to_16oz INTEGER NOT NULL,
    weight_to_32oz INTEGER NOT NULL,
    weight_to_48oz INTEGER NOT NULL,
    weight_to_64oz INTEGER NOT NULL,
    weight_to_80oz INTEGER NOT NULL,
    weight_to_96oz INTEGER NOT NULL,
    weight_to_112oz INTEGER NOT NULL,
    weight_to_128oz INTEGER NOT NULL,
    weight_to_144oz INTEGER NOT NULL,
    weight_to_160oz INTEGER NOT NULL
);

CREATE TABLE usps_pmei_rates(
    price_group INTEGER NOT NULL PRIMARY KEY,
    -- packing material alone is ~6oz
    -- PMI & PMEI rates increase by the pound, to 66lbs total
    -- I think standard mailing boxes hold at most ~6lps
    weight_to_16oz INTEGER NOT NULL,
    weight_to_32oz INTEGER NOT NULL,
    weight_to_48oz INTEGER NOT NULL,
    weight_to_64oz INTEGER NOT NULL,
    weight_to_80oz INTEGER NOT NULL,
    weight_to_96oz INTEGER NOT NULL,
    weight_to_112oz INTEGER NOT NULL,
    weight_to_128oz INTEGER NOT NULL,
    weight_to_144oz INTEGER NOT NULL,
    weight_to_160oz INTEGER NOT NULL
);

-- https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes
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
CREATE TABLE discogs_destination_countries(
    country_name VARCHAR NOT NULL PRIMARY KEY
);


CREATE VIEW ship_countries AS
SELECT
    iso.name AS country_name,
    iso.code2 AS cc2,
    iso.code3 AS cc3,
    svc.code AS usps_svc_code,
    -- PMI price code is not nec == PMEI price code
    -- FCPIS price code is very often not == PMI/PMEI price code
    cpg.price_group AS usps_price_group,
    fcpis.weight_to_8oz AS fcpis_to_8oz,
    fcpis.weight_to_32oz AS fcpis_to_32oz,
    fcpis.weight_to_48oz AS fcpis_to_48oz,
    fcpis.weight_to_64oz AS fcpis_to_64oz,
    pmi.weight_to_16oz AS pmi_to_16oz,
    pmi.weight_to_32oz AS pmi_to_32oz,
    pmi.weight_to_48oz AS pmi_to_48oz,
    pmi.weight_to_64oz AS pmi_to_64oz,
    pmi.weight_to_80oz AS pmi_to_80oz,
    pmi.weight_to_96oz AS pmi_to_96oz,
    pmi.weight_to_112oz AS pmi_to_112oz,
    pmi.weight_to_128oz AS pmi_to_128oz,
    pmi.weight_to_144oz AS pmi_to_144oz,
    pmi.weight_to_160oz AS pmi_to_160oz,
    -- FCPIS has hard limits for weight & value
    -- PMI/PMEI values in svc table more arbitrarily set
    svc.max_weight_oz AS svc_max_weight_oz,
    svc.max_value AS svc_max_value,
    -- max_weight_lbs & flat rate prices only relevant to PMI/PMEI
    -- max_weight_lbs accepted for svc varies by destination (usually 22, 44, 66 LBS)
    -- svc_max_rate_oz intended to be more operationally relevant; max_weight_lbs strictly infomational
    cpg.max_weight_lbs,
    cpg.flat_rate_price_group,
    svc.name AS usps_svc_name
FROM iso3166_countries AS iso
-- ignore countries without matching row in discogs
INNER JOIN discogs_destination_countries AS discogs
        ON iso.name = discogs.country_name
 LEFT JOIN usps_cpg AS cpg
        ON iso.name = cpg.country_name
 LEFT JOIN usps_service AS svc
        ON cpg.usps_service_code = svc.code
 LEFT JOIN usps_fcpis_rates AS fcpis
        ON cpg.price_group = fcpis.price_group
       AND cpg.usps_service_code = 'FCPIS'
 LEFT JOIN usps_pmi_rates AS pmi
        ON cpg.price_group = pmi.price_group
       AND cpg.usps_service_code = 'PMI'
-- LEFT JOIN usps_pmei_rates AS pmei
--        ON cpg.price_group = pmei.price_group
--       AND cpg.usps_service_code = 'PMEI'
;

-- initial inserts

INSERT INTO usps_service
("code", "name", "max_weight_oz", "max_value")
VALUES
("FCPIS", "First-Class Package Int'l", 64, 400.00),
-- PMI comes in 2 flavors: flat-rate or by-weight
-- https://pe.usps.com/text/dmm300/Notice123.htm#_c334
-- flat-rate is for those special USPS boxes, none are correct dimensions for vinyl
-- by-weight allows up to 66lbs (1056oz) (70lbs for 2 price codes)
-- my postal scale only goes to 10lbs
("PMI", "Priority Mail Int'l", 160, 1025.00),  -- up tp 10lbs
("PMEI", "Priority Mail Express Int'l", 160, 5000.00)
;

