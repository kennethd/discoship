import os
import sqlite3
from unittest.mock import call

import pytest

from discoship import db
from discoship.defs import DB_PATH, SQL_INGEST_PATH, SQL_CONFIG_PATH, USERDATA_PATH
from discoship.testing import tmpdir


@pytest.fixture
def tmp_db():
    with tmpdir() as tmp_path:
        db_path = os.path.sep.join([tmp_path, 'test.db'])
        with db.dbopen(db_path) as cur:
            # executefile() reads file & calls executescript()
            db.executefile(SQL_INGEST_PATH, db=db_path)
        # leave dbopen() context but not tmpdir()
        # caller will re-open test.db
        yield db_path


def test_dbopen_ro(tmp_db):

    # readonly parameter prevents writes
    with db.dbopen(tmp_db, readonly=True) as cur:
        query = ' '.join([
            'INSERT INTO usps_service',
            '("code", "name", "max_weight_oz", "max_value")',
            'VALUES (?, ?, ?, ?);'
        ])
        params = ("KLD", "Ken Test Svc", 64, 200)

        # sqlite3.OperationalError: attempt to write a readonly database
        with pytest.raises(sqlite3.OperationalError) as e:
            db.execute(query, params=params, db=tmp_db)
        assert e.match("attempt to write a readonly database")

        # reading is fine, without row_factory param default is tuples
        query = 'SELECT * FROM usps_service;'
        cur.execute(query)
        rows = cur.fetchall()
        assert len(rows) == 3
        for row in rows:
            assert isinstance(row, tuple)


def test_dbopen_rw(tmp_db):

    # opening w/out readonly allows writes
    with db.dbopen(tmp_db) as cur:
        query = ' '.join([
            'INSERT INTO usps_service',
            '("code", "name", "max_weight_oz", "max_value")',
            'VALUES (?, ?, ?, ?);'
        ])
        params = ("KLD", "Ken Test Svc", 64, 200)
        db.execute(query, params=params, db=tmp_db)

        # reading is still fine
        query = 'SELECT * FROM usps_service;'
        cur.execute(query)
        rows = cur.fetchall()
        assert len(rows) == 4


def test_selects(tmp_db):

    # for most SELECTs, db.select() is preferred to execute() + fetchall()
    # db.select() passes row_factory=sqlite3.Row to dbopen()
    query = 'SELECT * FROM usps_service;'
    rows = db.select(query, db=tmp_db)
    assert len(rows) == 3
    for row in rows:
        assert isinstance(row, sqlite3.Row)

    # or if after a single row, we can use selectone()
    query = 'SELECT * FROM usps_service WHERE code = ?;'
    params = ('FCPIS', )  # comma is subtle, or tuple(['FCPIS'])
    row = db.selectone(query, params=params, db=tmp_db)
    expect_keys = ['code', 'name', 'max_weight_oz', 'max_value']
    assert row.keys() == expect_keys


def test_executes(tmp_db):
    rows = db.select('SELECT * FROM usps_service;', db=tmp_db)
    assert len(rows) == 3  # freshly init'ed db

    # db.execute() is used for inserts:
    query = ' '.join([
        'INSERT INTO usps_service',
        '("code", "name", "max_weight_oz", "max_value")',
        'VALUES (?, ?, ?, ?);'
    ])

    params = ("KLD", "Ken Test Svc", 64, 300)
    rowcount = db.execute(query, params=params, db=tmp_db)
    assert rowcount == 1
    rows = db.select('SELECT * FROM usps_service;', db=tmp_db)
    assert len(rows) == 4  # successful insert

    # to insert multiple rows use executemany()
    data = [
        ("ABC", "Alpha-Beta Centauri", 42, 420),
        ("DEF", "Definitive Service", 56, 560),
    ]
    rowcount = db.executemany(query, data=data, db=tmp_db)
    assert rowcount == 2
    rows = db.select('SELECT * FROM usps_service;', db=tmp_db)
    assert len(rows) == 6  # successful insert

    # executemany() also supports dict-based keys:
    query = ' '.join([
        'INSERT INTO usps_service',
        '("code", "name", "max_weight_oz", "max_value")',
        'VALUES (:code, :name, :max_weight, :max_value);'
    ])
    data = [
        {"code":"GHI", "name": "Studio Ghibli", "max_weight": 62, "max_value": 620},
        {"code":"JKL", "name": "Joker Limited", "max_weight": 72, "max_value": 720},
    ]
    rowcount = db.executemany(query, data=data, db=tmp_db)
    assert rowcount == 2
    rows = db.select('SELECT * FROM usps_service;', db=tmp_db)
    assert len(rows) == 8  # successful insert


def test_dbinit(mocker):
    mock_execfile = mocker.patch('discoship.db.executefile')
    db.dbinit()
    expect_calls = [
        call(SQL_CONFIG_PATH, db=USERDATA_PATH),
        call(SQL_INGEST_PATH, db=DB_PATH),
    ]
    mock_execfile.assert_has_calls(expect_calls)

