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

simplest option: map aliases to canonical spellings at insert time:
"""

COUNTRY_ALIASES = {
    "Azerbaidjan": "Azerbaijan",
    "Bolivia (Plurinational State of)": "Bolivia",
    "Bosnia-Herzegovina": "Bosnia and Herzegovina",
    "Cabo Verde": "Cape Verde",
    "Cote d'Ivoire": "Côte d'Ivoire",
    "Ivory Coast": "Côte d'Ivoire",
    "Ivory Coast (Cote D'Ivoire)": "Côte d'Ivoire",
    "Curacao": "Curaçao",
    "Czechia": "Czech Republic",
    "Congo (the Democratic Republic of the)": "Democratic Republic of the Congo",
    "Congo, Democratic Republic of the": "Democratic Republic of the Congo",
    "Zaire": "Democratic Republic of the Congo",
    "Georgia, Republic of": "Georgia",
    "Guadeloupe (French)": "Guadeloupe",
    "Guinea Bissau": "Guinea-Bissau",
    "Falkland Islands [Malvinas]": "Falkland Islands",
    "French Guiana": "Guyana",
    "Iran (Islamic Republic of)": "Iran",
    "Kosovo, Republic of": "Kosovo",
    "Lao People's Democratic Republic": "Laos",
    "Martinique (French)": "Martinique",
    "Macao": "Macau",
    "Moldavia": "Moldova",
    "New Caledonia (French)": "New Caledonia",
    "North Macedonia, Republic of": "Macedonia",
    "Micronesia (Federated States of)": "Micronesia",
    "Moldova (the Republic of)": "Moldova",
    "Burma": "Myanmar",
    "Netherlands (Kingdom of the)": "Netherlands",
    "Korea, Democratic Peoples Republic of (North Korea)": "North Korea",
    "Korea (the Democratic People's Republic of)": "North Korea",
    "Pitcairn": "Pitcairn Island",
    "Congo, Republic of the": "Republic of the Congo",
    "Congo": "Republic of the Congo",
    "Reunion": "Réunion",
    "Reunion (French)": "Réunion",
    "Russian Federation": "Russia",
    "Saint (St.) Kitts and Nevis": "Saint Kitts and Nevis",
    "Saint Kitts & Nevis Anguilla": "Saint Kitts and Nevis",
    "Saint Tome (Sao Tome) and Princi": "São Tomé and Príncipe",
    "Saint Vincent and the Grenadines": "Saint Vincent & Grenadines",
    "Sao Tome and Principe": "São Tomé and Príncipe",
    "Serbia, Republic of": "Serbia",
    "Sint Maarten (Dutch)": "Sint Maarten",
    "Slovak Republic (Slovakia)": "Slovak Republic",
    "Slovakia": "Slovak Republic",
    "South Sudan, Republic of": "South Sudan",
    "Korea, Republic of (South Korea)": "South Korea",
    "Korea (the Republic of)": "South Korea",
    "Svalbard Jan Mayen": "Svalbard and Jan Mayen Islands",
    "Syrian Arab Republic": "Syria",
    "Syrian Arab Republic (Syria)": "Syria",
    "Taiwan (Province of China)": "Taiwan",
    "Tadjikistan": "Tajikistan",
    "Tanzania, the United Republic of": "Tanzania",
    "East Timor": "Timor-Leste",
    "Timor-Leste, Democratic Republic of": "Timor-Leste",
    "Turkiye, Republic of": "Turkey",
    "Türkiye": "Turkey",
    "United Kingdom of Great Britain and Northern Ireland": "United Kingdom",
    "United States of America": "United States",
    "Holy See": "Vatican City",
    "Vatican City State": "Vatican City",
    "Venezuela (Bolivarian Republic of)": "Venezuela",
    "Viet Nam": "Vietnam",
    "Virgin Islands (USA)": "Virgin Islands (U.S.)",
    "Wallis and Futuna Islands": "Wallis and Futuna",
}

