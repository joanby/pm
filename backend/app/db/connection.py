from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from collections.abc import Iterator

from backend.app.db.init_db import get_database_path, init_database


def get_connection() -> sqlite3.Connection:
    db_path = get_database_path()
    if not db_path.exists():
        init_database(db_path)
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


@contextmanager
def db_connection() -> Iterator[sqlite3.Connection]:
    connection = get_connection()
    try:
        yield connection
    finally:
        connection.close()
