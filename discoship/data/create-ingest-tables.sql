/*
This file drops & re-creates tables for data ingestion processes.  These
tables are not intended to be modified manually.  Do not add table definitions
to this file if dropping and recreating them will lose user-modified data.
*/

DROP TABLE IF EXISTS usps_service;
CREATE TABLE usps_service(
    id INTEGER PRIMARY KEY,
    code VARCHAR,
    name VARCHAR,
    max_weight_oz REAL,
    max_value REAL,
    max_dim VARCHAR
);
CREATE UNIQUE INDEX idx_usps_service_code ON usps_service(code);

DROP TABLE IF EXISTS usps_cpg;
CREATE TABLE usps_cpg(
    country_name VARCHAR NOT NULL,
    usps_service_code VARCHAR NOT NULL,
    price_group INTEGER NOT NULL,
    PRIMARY KEY (country_name, usps_service_code)
);
CREATE INDEX idx_usps_cpg_price_group ON usps_cpg(price_group);

DROP TABLE IF EXISTS usps_fcpis_rates;
CREATE TABLE usps_fcpis_rates(
    price_group INTEGER NOT NULL,
    -- packing material alone is ~6oz
    weight_to_8oz INTEGER NOT NULL,  -- ship cost up to 8oz
    -- one LP boxed up is ~18-20oz
    -- one 2xLP is ~22-24oz
    -- 2 LPs ~28-32oz
    weight_to_32oz INTEGER NOT NULL,  -- up to 32oz
    -- 3 LPs ~36oz
    weight_to_48oz INTEGER NOT NULL,  -- up to 48oz
    weight_to_64oz INTEGER NOT NULL,  -- up to 64oz
    PRIMARY KEY (price_group)
);


-- initial inserts

INSERT INTO usps_service
("code", "name", "max_weight_oz", "max_value", "max_dim")
VALUES
("FCPIS", "First-Class Package Int'l", 64, 400.00, ""),
("PMEI", "Priority Mail Express Int'l", NULL, NULL, ""),
("PMI", "Priority Mail Int'l", NULL, NULL, ""),
("FCMI", "First-Class Mail Int'l", NULL, NULL, ""),
("AIR", "Int'l Package Airmail", NULL, NULL, "");

