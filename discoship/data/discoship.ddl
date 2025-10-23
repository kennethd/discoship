-- vim: set filetype=sql :

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

-- sqlite as kvs: https://sqlite.org/flextypegood.html
DROP TABLE IF EXISTS prefs;
CREATE TABLE prefs(name TEXT PRIMARY KEY, value) WITHOUT ROWID;
