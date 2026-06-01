"""PostgreSQL connection and schema initialization for Lab 1.

The first laboratory work requires low-level SQL access without ORM.
This module uses psycopg directly and executes hand-written SQL DDL/DML.
"""

from __future__ import annotations

import os
from pathlib import Path

import psycopg
from psycopg.rows import dict_row

DEFAULT_DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/phone_station_lab1"
DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)
SCHEMA_PATH = Path(__file__).with_name("schema.sql")


def get_connection():
    """Return a PostgreSQL connection with rows available as dictionaries."""
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)


def init_db() -> None:
    """Create tables and seed base data using explicit SQL statements."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(SCHEMA_PATH.read_text(encoding="utf-8"))
