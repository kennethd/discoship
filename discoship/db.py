from contextlib import contextmanager
import logging
import sqlite3

from discoship.defs import DB_PATH, SQL_INGEST_PATH, SQL_DISCOGS_PATH, SQL_CONFIG_PATH


log = logging.getLogger(__name__)


@contextmanager
def dbopen(readonly=False, row_factory=None, **connect_kwargs):
    """contextmanager to obtain sqlite3 cursor

    connection will close automatically when context goes out of scope.

    connect_kwargs are passed though to sqlite3.connect()
    https://docs.python.org/3/library/sqlite3.html#sqlite3.connect

    yields sqlite3 cursor"""
    log.info(f"dbopen: ro={readonly} row_factory={row_factory} connect_kwargs={connect_kwargs}")
    # https://www.sqlite.org/uri.html
    connect_kwargs["uri"] = True
    if readonly:
        db_path = f"file:{DB_PATH}?mode=ro&cache=shared"
    else:
        db_path = f"file:{DB_PATH}?mode=rwc&cache=shared"
    log.debug(f"dbopen: db_path={db_path}")
    conn = sqlite3.connect(db_path, **connect_kwargs)

    # for SELECT statements, allow setting row_factory to sqlite3.Row
    # "Row provides indexed and case-insensitive named access to columns, with
    #  minimal memory overhead and performance impact over a tuple.
    # https://docs.python.org/3/library/sqlite3.html#sqlite3-howto-row-factory
    if row_factory:
        conn.row_factory = row_factory

    try:
        cur = conn.cursor()
        yield cur
    except Exception as e:
        conn.rollback()
        raise e
    else:
        conn.commit()
    finally:
        conn.close()


def execute(sql, params=None):
    """execute parameterized SQL with values interpolated from params

    if params is tuple placeholders in sql use '?'

    if params is dict, use named placeholders style:
    ```
    data = (
        {"name": "C", "year": 1972},
        {"name": "Fortran", "year": 1957},
        {"name": "Python", "year": 1991},
        {"name": "Go", "year": 2009},
    )
    cur.executemany("INSERT INTO lang VALUES(:name, :year)", data)
    ```
    https://docs.python.org/3/library/sqlite3.html#how-to-use-placeholders-to-bind-values-in-sql-queries

    returns number of rows affected"""
    log.debug(f"execute: {sql} {params}")
    if not params:
        params = ()

    rowcount = 0
    with dbopen() as cur:
        cur.execute(sql, params)
        rowcount = cur.rowcount
    return rowcount


def executemany(sql, params=None):
    """execute parameterized SQL for each element of params

    params being a list of tuples or dicts, such as would be passed to
    execute() one-by-one

    returns number of rows affected"""
    log.debug(f"executemany: {sql} {params}")
    if not params:
        raise ValueError("executemany() without values makes no sense")

    rowcount = 0
    with dbopen() as cur:
        cur.executemany(sql, params)
        rowcount = cur.rowcount
    return rowcount


def executescript(sql_stmts):
    """execute all statements in string sql_stmts"""
    log.debug(f"executescript: {sql_stmts[:124]}...")
    with dbopen() as cur:
        cur.executescript(sql_stmts)


def executefile(sql_path):
    """execute all statements in file sql_path"""
    log.debug(f"executefile: {sql_path}")
    with open(sql_path) as fh:
        sql_stmts = fh.read()
        executescript(sql_stmts)


def select(sql, params=None):
    """execute sql statement & return list of row values as sqlite3.Rows

    returns list of sqlite3.Row objects"""
    log.debug(f"select: {sql} {params}")
    if not params:
        params = ()

    with dbopen(readonly=True, row_factory=sqlite3.Row) as cur:
        cur.execute(sql, params)
        return cur.fetchall()


def selectone(sql, params=None):
    """execute sql statement & return row values as sqlite3.Row object

    sqlite3.Row objects may be accessed by tuple index or case-insensitive
    dict key (from docs):
    ```
    > row.keys()
    ['name', 'radius']
    > row[0]         # Access by index.
    'Earth'
    > row["name"]    # Access by name.
    'Earth'
    > row["RADIUS"]  # Column names are case-insensitive.
    6378
    ```

    returns sqlite3.Row"""
    log.debug(f"selectone: {sql} {params}")
    if not params:
        params = ()

    with dbopen(readonly=True, row_factory=sqlite3.Row) as cur:
        cur.execute(sql, params)
        return cur.fetchone()


def dbinit():
    """initialize fresh db

    * * * WARNING: DESTROYS ALL DATA * * *
    drops all existing tables & recreates schema"""
    executefile(SQL_INGEST_PATH)
    executefile(SQL_DISCOGS_PATH)
    executefile(SQL_CONFIG_PATH)


def recreate_ingest_tables():
    """drops and recreates tables for data ingested from external sources

    ALL INGEST SCRIPTS WILL NEED TO BE RE-RUN

    Does not destroy user-modified data"""
    executefile(SQL_INGEST_PATH)
    executefile(SQL_DISCOGS_PATH)


def reset_config():
    """drops & recreates config table

    ALL USER DEFINED CONFIGS WILL BE LOST

    Consider backing up your config first"""
    executefile(SQL_CONFIG_PATH)


def dump_config():
    """selects everything from config table for backup/display"""
    rows = select("SELECT * FROM config")
    config = { row[0]: row[1] for row in rows }
    return config

