
-- the list of countries in the shipping policy editor
-- https://www.discogs.com/settings/shipping
DROP TABLE IF EXISTS discogs_destination_countries;
CREATE TABLE discogs_destination_countries(
    country_name VARCHAR NOT NULL,
    PRIMARY KEY (country_name)
);

