import os

import pytest

from discoship import db
from discoship.defs import SQL_CONFIG_PATH
from discoship.testing import tmpdir


def test_config():

    with tmpdir() as tmp_path:

        db_path = os.path.sep.join([tmp_path, 'config.db'])

        # SQL_CONFIG_PATH creates userdata table that functions as key-value store
        with db.dbopen(db_path) as cur:
            db.executefile(SQL_CONFIG_PATH, db=db_path)

        config = db.select_config(db=db_path)
        expect_cols = [
            "last_ingest_usps_cpg",
            "last_ingest_usps_fcpis_rates",
            "last_ingest_usps_pmi_rates",
            "last_ingest_usps_pmei_rates",
            "last_ingest_discogs_countries",
            "last_ingest_iso3166_countries",
            "packing_handling_fee",
            "usps_fcpis_cert_mailing_fee",
            "usps_fcpis_registered_fee",
            "usps_pmi_insurance_included",
            "usps_pmei_insurance_included",
            "weight_1_lp_oz",
            "weight_2_lp_oz",
            "weight_3_lp_oz",
            "weight_4_lp_oz",
            "weight_5_lp_oz",
            "weight_6_lp_oz",
        ]
        for col in expect_cols:
            assert col in dict(config)

        # values hardcoded in SQL_CONFIG_PATH
        assert config["packing_handling_fee"] == 1.5
        assert config["usps_fcpis_cert_mailing_fee"] == 2.5
        assert config["usps_fcpis_registered_fee"] == 22
        assert config["weight_1_lp_oz"] == 20
        assert config["weight_2_lp_oz"] == 34
        assert config["weight_3_lp_oz"] == 42
        assert config["weight_4_lp_oz"] == 52
        assert config["weight_5_lp_oz"] == 60
        assert config["weight_6_lp_oz"] == 70

        rowcount = db.set_config("packing_handling_fee", 2.5, db=db_path)
        assert rowcount == 1
        config = db.select_config(db=db_path)
        assert config["packing_handling_fee"] == 2.5
        # reset back to defaults
        db.reset_config(db=db_path)
        config = db.select_config(db=db_path)
        assert config["packing_handling_fee"] == 1.5

