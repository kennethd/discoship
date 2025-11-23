-- sqlite as kvs: https://sqlite.org/flextypegood.html
DROP TABLE IF EXISTS userdata;
CREATE TABLE userdata(name TEXT PRIMARY KEY, value) WITHOUT ROWID;

INSERT INTO userdata (name, value) VALUES
-- SELECT DATETIME('now') returns the current UTC datetime
("last_ingest_usps_cpg", NULL),
("last_ingest_usps_fcpis_rates", NULL),
("last_ingest_usps_pmi_rates", NULL),
("last_ingest_usps_pmei_rates", NULL),
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
("usps_fcpis_registered_fee", 22.00),
-- https://www.usps.com/international/insurance-extra-services.htm
("usps_pmi_insurance_included", 200.00),
("usps_pmei_insurance_included", 200.00),
("weight_1_lp_oz", 20),  -- single LP =~ 1lb + 4oz; <16oz might work for 1xCD
("weight_2_lp_oz", 34),  -- 2LPs =~ 34-36oz (single 2xLP often ~30oz < 32oz boundary)
("weight_3_lp_oz", 42),  -- 3LPs =~ 42-44oz (next boundary 48oz)
("weight_4_lp_oz", 52),  -- 4LPs =~ 52oz (well between 48-64 boundaries)
("weight_5_lp_oz", 60),  -- 5LPs =~ 60oz (next boundary 64oz)
("weight_6_lp_oz", 70)  -- 6LPs =~ 70oz (4lbs + 4oz)
;

