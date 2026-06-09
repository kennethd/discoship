from contextlib import contextmanager
import logging
import sqlite3

from discoship.defs import DB_PATH, SQL_INGEST_PATH, SQL_CONFIG_PATH, USERDATA_PATH


log = logging.getLogger(__name__)


@contextmanager
def dbopen(db=DB_PATH, readonly=False, row_factory=None, **connect_kwargs):
    """contextmanager to obtain sqlite3 cursor

    connection will close automatically when context goes out of scope.

    connect_kwargs are passed though to sqlite3.connect()
    https://docs.python.org/3/library/sqlite3.html#sqlite3.connect

    yields sqlite3 cursor"""
    log.debug(f"dbopen: {db} ro={readonly} row_factory={row_factory} connect_kwargs={connect_kwargs}")
    # https://www.sqlite.org/uri.html
    connect_kwargs["uri"] = True
    if readonly:
        mode = "ro"
    else:
        mode = "rwc"
    db_path = f"file:{db}?mode={mode}&cache=shared"
    log.info(f"dbopen: db_path={db_path}")
    conn = sqlite3.connect(db_path, **connect_kwargs)
    conn.execute("PRAGMA foreign_keys = ON;")

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
        log.error(f"db exception: {e}")
        conn.rollback()
        raise e
    else:
        conn.commit()
    finally:
        conn.close()


def execute(sql, params=None, db=DB_PATH):
    """execute parameterized SQL with values interpolated from params

    if params is tuple placeholders in sql use '?' (no quotes)
    ```
    cur.execute("INSERT INTO lang VALUES(?, ?)", params)
    ```
    if params is dict, use named placeholders style:
    ```
    cur.execute("INSERT INTO lang VALUES(:name, :year)", params)
    ```
    https://docs.python.org/3/library/sqlite3.html#how-to-use-placeholders-to-bind-values-in-sql-queries

    returns number of rows affected"""
    log.debug(f"execute: {sql} {params}")
    if not params:
        params = ()

    rowcount = 0
    with dbopen(db) as cur:
        cur.execute(sql, params)
        rowcount = cur.rowcount
    return rowcount


def executemany(sql, data=None, db=DB_PATH):
    """execute parameterized SQL for each element of seq data

    data being a list of tuples or dicts, such as would be passed to
    execute() one-by-one as `params`

    if data is seq of tuples placeholders in sql use '?' (no quotes)
    ```
    cur.executemany("INSERT INTO lang VALUES(?, ?)", data)
    ```
    if data is seq of dicts, use named placeholders style:
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
    log.debug(f"executemany: {sql} {data}")
    if not data:
        raise ValueError("executemany() without values makes no sense")

    rowcount = 0
    with dbopen(db) as cur:
        cur.executemany(sql, data)
        rowcount = cur.rowcount
    return rowcount


def executescript(sql_stmts, db=DB_PATH):
    """execute all statements in string sql_stmts"""
    log.debug(f"executescript: {sql_stmts[:256]}...")
    with dbopen(db) as cur:
        cur.executescript(sql_stmts)


def executefile(sql_path, db=DB_PATH):
    """execute all statements in file sql_path"""
    log.debug(f"executefile: {sql_path}")
    with open(sql_path) as fh:
        sql_stmts = fh.read()
        executescript(sql_stmts, db)


def select(sql, params=None, db=DB_PATH):
    """execute sql statement & return list of row values as sqlite3.Rows

    returns list of sqlite3.Row objects"""
    log.debug(f"select: {sql} {params}")
    if not params:
        params = ()

    with dbopen(db, readonly=True, row_factory=sqlite3.Row) as cur:
        cur.execute(sql, params)
        return cur.fetchall()


def selectone(sql, params=None, db=DB_PATH):
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

    with dbopen(db, readonly=True, row_factory=sqlite3.Row) as cur:
        cur.execute(sql, params)
        return cur.fetchone()


def dbinit():
    """initialize fresh db

    * * * WARNING: DESTROYS ALL DATA * * *
    drops all existing tables & recreates schema"""
    executefile(SQL_CONFIG_PATH, db=USERDATA_PATH)
    executefile(SQL_INGEST_PATH, db=DB_PATH)


def recreate_ingest_tables():
    """drops and recreates tables for data ingested from external sources

    ALL INGEST SCRIPTS WILL NEED TO BE RE-RUN

    Does not destroy user-modified data"""
    executefile(SQL_INGEST_PATH, db=DB_PATH)


def reset_config():
    """drops & recreates config table

    ALL USER DEFINED CONFIGS WILL BE LOST

    Consider backing up your config first"""
    executefile(SQL_CONFIG_PATH, db=USERDATA_PATH)


def select_config():
    """selects everything from config table for backup/display"""
    rows = select("SELECT * FROM userdata", db=USERDATA_PATH)
    config = { row[0]: row[1] for row in rows }
    return config


def set_config(key, value):
    """Update config value in `userdata` table"""
    params = (value.strip(), key.strip())
    rowcount = execute("UPDATE userdata SET value = ? WHERE name = ?", params,
                       db=USERDATA_PATH)
    log.info(f"set_config: updated {rowcount} rows")
    return rowcount

