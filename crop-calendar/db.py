"""
PostgreSQL Connection Helper
==============================
Replaces the original sqlite3 backend. Reads connection settings from
environment variables (loaded from .env via python-dotenv in app.py) so
the real database password is never hardcoded or committed.

See PGADMIN_SETUP.md for how to create the database in pgAdmin and fill
in .env - that file walks through the exact clicks.

`Connection.execute(sql, params)` mirrors sqlite3's connection.execute()
convenience method (psycopg2 connections don't have one - normally you'd
need conn.cursor() then cur.execute()), so the rest of the app's query
code in app.py didn't need to be rewritten for the migration - only this
module, the CREATE TABLE schema, and the two spots that used SQLite's
lastrowid/last_insert_rowid() needed real changes.
"""

import os

import psycopg2
from psycopg2.extras import RealDictCursor

DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_NAME = os.environ.get("DB_NAME", "crop_calendar")
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "")


class Connection:
    """Thin wrapper so call sites can keep using
    conn.execute(sql, params) -> cursor, the same shape sqlite3 offered."""

    def __init__(self, raw):
        self._raw = raw

    def execute(self, sql, params=()):
        cur = self._raw.cursor(cursor_factory=RealDictCursor)
        # SQLite placeholders are "?"; psycopg2 uses "%s". Every SQL string
        # in this app only ever uses "?" as a placeholder (never as literal
        # data), so a plain replace is safe here. Note for future queries:
        # psycopg2 also treats a literal "%" in the query text as the start
        # of a %s-style placeholder once params are passed - a raw "%" in
        # new SQL (e.g. inside a LIKE pattern) would need to be written as
        # "%%" to survive this path. None of the current queries use one.
        cur.execute(sql.replace("?", "%s"), params)
        return cur

    def executescript(self, sql):
        # psycopg2's execute() handles a semicolon-separated multi-statement
        # string fine as long as no params are bound, so the CREATE TABLE
        # block in init_db() doesn't need per-statement splitting.
        cur = self._raw.cursor()
        cur.execute(sql)
        return cur

    def cursor(self):
        return self._raw.cursor(cursor_factory=RealDictCursor)

    def commit(self):
        self._raw.commit()

    def close(self):
        self._raw.close()


def get_db():
    raw = psycopg2.connect(
        host=DB_HOST, port=DB_PORT, dbname=DB_NAME,
        user=DB_USER, password=DB_PASSWORD,
    )
    return Connection(raw)
