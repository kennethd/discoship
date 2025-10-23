-- initial inserts

INSERT INTO usps_service
("code", "name", "max_weight_oz", "max_value", "max_dim")
VALUES
("FCPIS", "First-Class Package Int'l", 64, 400.00, ""),
("PMEI", "Priority Mail Express Int'l", NULL, NULL, ""),
("PMI", "Priority Mail Int'l", NULL, NULL, ""),
("FCMI", "First-Class Mail Int'l", NULL, NULL, ""),
("AIR", "Int'l Package Airmail", NULL, NULL, "");


INSERT INTO prefs VALUES
-- SELECT DATETIME('now') returns the current UTC datetime
("last_ingest_usps_cpg", NULL),
("last_ingest_usps_fcpis_rates", NULL),
-- https://faq.usps.com/s/article/Certificate-of-Mailing-The-Basics
-- "Only available at a Post Office location"
-- https://www.usps.com/international/insurance-extra-services.htm
-- "A certificate of mailing cannot be obtained in combination with Registered
--  mail items, insured parcels, or items paid with a permit imprint."
("usps_fcpis_cert_mailing_req", 1),
("usps_fcpis_cert_mailing_fee", 2.50),
-- https://www.usps.com/international/insurance-extra-services.htm
-- "Only available at a Post Office location."
-- First-Class Package International Service $21.75
("usps_fcpis_registered_offer", 0),
("usps_fcpis_registered_req", 0),
("usps_fcpis_registered_fee", 24.00);


