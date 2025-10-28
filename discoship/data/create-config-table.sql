-- sqlite as kvs: https://sqlite.org/flextypegood.html
DROP TABLE IF EXISTS config;
CREATE TABLE config(name TEXT PRIMARY KEY, value) WITHOUT ROWID;

INSERT INTO config (name, value) VALUES
-- SELECT DATETIME('now') returns the current UTC datetime
("last_ingest_usps_cpg", NULL),
("last_ingest_usps_fcpis_rates", NULL),
("last_ingest_usps_pmi_rates", NULL),
("last_ingest_discogs_countries", NULL),
("last_ingest_iso3166_countries", NULL),
-- include packing supplies cost in base price
("packing_handling_fee", 1.50),
-- https://faq.usps.com/s/article/Certificate-of-Mailing-The-Basics
-- "Only available at a Post Office location"
-- https://www.usps.com/international/insurance-extra-services.htm
-- "A certificate of mailing cannot be obtained in combination with Registered
--  mail items, insured parcels, or items paid with a permit imprint."
("usps_fcpis_cert_mailing_fee", 2.50),
-- First-Class Package International Service $21.75 & up
("usps_fcpis_registered_fee", 24.00)
;

