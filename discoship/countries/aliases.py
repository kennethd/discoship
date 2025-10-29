"""
The trouble with country data: After ingestion from the various sources,
inconsistencies in spelling result in a large number of mis-matches

$ sqlite3 discoship/data/discoship.db "select COUNT(*) from discogs_destination_countries;"
243

$ sqlite3 discoship/data/discoship.db "select COUNT(*) from usps_cpg;"
219

$ sqlite3 discoship/data/discoship.db "select COUNT(*) from discogs_destination_countries
    AS discogs INNER JOIN usps_cpg ON discogs.country_name = usps_cpg.country_name;"
180
"""

# countries that exist in discogs_destination_countries but not usps_cpg:
#
# SELECT d.country_name FROM discogs_destination_countries AS d
# LEFT JOIN usps_cpg AS u
#        ON d.country_name = u.country_name
# WHERE u.country_name IS NULL;
#
# Countries that exist in usps_cpg but not discogs_destination_countries:
#
# sqlite3 discoship/data/discoship.db ".headers on" ".mode column" "
# SELECT u.country_name FROM discogs_destination_countries AS d
# RIGHT JOIN usps_cpg AS u
#         ON d.country_name = u.country_name
# WHERE d.country_name IS NULL;
"""
DROP TABLE IF EXISTS country_aliases;
CREATE TABLE country_aliases (
    iso3166_name VARCHAR,
    usps_cpg_name VARCHAR,
    discogs_name VARCHAR
);
CREATE INDEX idx_country_aliases_iso3166_name ON country_aliases(iso3166_name);
CREATE INDEX idx_country_aliases_usps_cpg_name ON country_aliases(usps_cpg_name);
CREATE INDEX idx_country_aliases_discogs_name ON country_aliases(discogs_name);
*/
"""

# simplest option: map aliases to cononical spellings at insert time:
COUNTRY_ALIASES = {
    "Bolivia (Plurinational State of)": "Bolivia",
    "Cote d'Ivoire": "Côte d'Ivoire",
    "Ivory Coast": "Côte d'Ivoire",
    "Ivory Coast (Cote D'Ivoire)": "Côte d'Ivoire",
    "Georgia, Republic of": "Georgia",
    "Guinea Bissau": "Guinea-Bissau",
    "French Guiana": "Guyana",
    "Iran (Islamic Republic of)": "Iran",
    "Kosovo, Republic of": "Kosovo",
    "Lao People's Democratic Republic": "Laos",
    "Macao": "Macau",
    "North Macedonia, Republic of": "Macedonia",
    "Micronesia (Federated States of)": "Micronesia",
    "Moldova (the Republic of)": "Moldova",
    "Burma": "Myanmar",
    "Netherlands (Kingdom of the)": "Netherlands",
    "Korea, Democratic Peoples Republic of (North Korea)": "North Korea",
    "Korea (the Democratic People's Republic of)": "North Korea",
    "Reunion": "Réunion",
    "Russian Federation": "Russia",
    "Saint (St.) Kitts and Nevis": "Saint Kitts and Nevis",
    "Saint Kitts & Nevis Anguilla": "Saint Kitts and Nevis",
    "Saint Tome (Sao Tome) and Princi": "São Tomé and Príncipe",
    "Sao Tome and Principe": "São Tomé and Príncipe",
    "Serbia, Republic of": "Serbia",
    "Sint Maarten (Dutch)": "Sint Maarten",
    "Slovak Republic (Slovakia)": "Slovak Republic",
    "Slovakia": "Slovak Republic",
    "South Sudan, Republic of": "South Sudan",
    "Korea, Republic of (South Korea)": "South Korea",
    "Korea (the Republic of)": "South Korea",
    "Syrian Arab Republic (Syria)": "Syria",
    "Taiwan (Province of China)": "Taiwan",
    "Tadjikistan": "Tajikistan",
    "Tanzania, the United Republic of": "Tanzania",
    "East Timor": "Timor-Leste",
    "Timor-Leste, Democratic Republic of": "Timor-Leste",
    "Turkiye, Republic of": "Turkey",
    "Türkiye": "Turkey",
    "United Kingdom of Great Britain and Northern Ireland": "United Kingdom",
    "Holy See": "Vatican City",
    "Vatican City State": "Vatican City",
    "Venezuela (Bolivarian Republic of)": "Venezuela",
    "Viet Nam": "Vietnam",
}

