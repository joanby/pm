import json
from pathlib import Path

import pytest

from backend.app.db.schema import (
    REQUIRED_TABLE_NAMES,
    build_schema_sql,
    load_schema,
    validate_schema,
)

SCHEMA_PATH = Path(__file__).resolve().parents[3] / "docs" / "db-schema.json"


def test_db_schema_json_is_valid_json() -> None:
    payload = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    assert payload["engine"] == "sqlite"


def test_validate_schema_accepts_official_schema() -> None:
    schema = load_schema()
    validate_schema(schema)


def test_validate_schema_rejects_missing_tables() -> None:
    schema = load_schema()
    schema["tables"] = {
        name: table for name, table in schema["tables"].items() if name != "users"
    }
    with pytest.raises(ValueError, match="missing tables"):
        validate_schema(schema)


def test_build_schema_sql_creates_all_tables() -> None:
    schema = load_schema()
    statements = build_schema_sql(schema)
    joined = "\n".join(statements)
    for table_name in REQUIRED_TABLE_NAMES:
        assert f"CREATE TABLE IF NOT EXISTS {table_name}" in joined
