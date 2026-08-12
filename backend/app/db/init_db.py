from __future__ import annotations

import os
import sqlite3
from pathlib import Path

from backend.app.db.schema import build_schema_sql, load_schema, validate_schema

DEFAULT_DB_PATH = Path(__file__).resolve().parents[2] / "data" / "pm.db"


def get_database_path() -> Path:
    configured = os.environ.get("PM_DATABASE_PATH")
    if configured:
        return Path(configured)
    return DEFAULT_DB_PATH


def init_database(db_path: Path | None = None) -> Path:
    target = db_path or get_database_path()
    target.parent.mkdir(parents=True, exist_ok=True)

    schema = load_schema()
    validate_schema(schema)
    statements = build_schema_sql(schema)

    with sqlite3.connect(target) as connection:
        for statement in statements:
            connection.execute(statement)
        connection.commit()

    return target


def list_tables(db_path: Path) -> set[str]:
    with sqlite3.connect(db_path) as connection:
        rows = connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    return {row[0] for row in rows}
