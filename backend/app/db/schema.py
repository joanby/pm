from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REQUIRED_ROOT_KEYS = {"version", "engine", "tables"}
REQUIRED_TABLE_NAMES = {"users", "boards", "columns", "cards", "chat_messages"}
ALLOWED_SQL_TYPES = {"TEXT", "INTEGER"}
SCHEMA_PATH = Path(__file__).resolve().parents[3] / "docs" / "db-schema.json"


def load_schema(path: Path | None = None) -> dict[str, Any]:
    schema_file = path or SCHEMA_PATH
    with schema_file.open(encoding="utf-8") as handle:
        return json.load(handle)


def validate_schema(schema: dict[str, Any]) -> None:
    missing_root = REQUIRED_ROOT_KEYS - schema.keys()
    if missing_root:
        raise ValueError(f"Schema missing root keys: {sorted(missing_root)}")

    if schema["engine"] != "sqlite":
        raise ValueError("Only sqlite engine is supported in MVP")

    tables = schema["tables"]
    missing_tables = REQUIRED_TABLE_NAMES - set(tables)
    if missing_tables:
        raise ValueError(f"Schema missing tables: {sorted(missing_tables)}")

    for table_name, table_def in tables.items():
        _validate_table(table_name, table_def)


def _validate_table(table_name: str, table_def: dict[str, Any]) -> None:
    columns = table_def.get("columns")
    if not columns:
        raise ValueError(f"Table '{table_name}' must define columns")

    primary_keys = [
        name for name, column in columns.items() if column.get("primaryKey")
    ]
    if len(primary_keys) != 1:
        raise ValueError(f"Table '{table_name}' must have exactly one primary key")

    for column_name, column_def in columns.items():
        column_type = column_def.get("type")
        if column_type not in ALLOWED_SQL_TYPES:
            raise ValueError(
                f"Table '{table_name}'.'{column_name}' has unsupported type '{column_type}'"
            )
        if column_def.get("required") and "default" not in column_def and not column_def.get("primaryKey"):
            pass  # required columns are valid without default

    for foreign_key in table_def.get("foreignKeys", []):
        if "column" not in foreign_key or "references" not in foreign_key:
            raise ValueError(f"Invalid foreign key in table '{table_name}'")


def build_create_table_sql(table_name: str, table_def: dict[str, Any]) -> str:
    columns = table_def["columns"]
    parts: list[str] = []

    for column_name, column_def in columns.items():
        sql_type = column_def["type"]
        definition = f"{column_name} {sql_type}"
        if column_def.get("primaryKey"):
            definition += " PRIMARY KEY"
        if column_def.get("required") and not column_def.get("primaryKey"):
            definition += " NOT NULL"
        if "default" in column_def:
            default = column_def["default"]
            if isinstance(default, str):
                definition += f" DEFAULT '{default}'"
            else:
                definition += f" DEFAULT {default}"
        parts.append(definition)

    for foreign_key in table_def.get("foreignKeys", []):
        ref = foreign_key["references"]
        on_delete = foreign_key.get("onDelete", "NO ACTION")
        parts.append(
            "FOREIGN KEY ({column}) REFERENCES {table}({ref_column}) ON DELETE {on_delete}".format(
                column=foreign_key["column"],
                table=ref["table"],
                ref_column=ref["column"],
                on_delete=on_delete,
            )
        )

    for index in table_def.get("indexes", []):
        if index.get("unique"):
            index_columns = ", ".join(index["columns"])
            parts.append(f"UNIQUE ({index_columns})")

    body = ",\n  ".join(parts)
    return f"CREATE TABLE IF NOT EXISTS {table_name} (\n  {body}\n);"


def build_schema_sql(schema: dict[str, Any]) -> list[str]:
    validate_schema(schema)
    table_order = ["users", "boards", "columns", "cards", "chat_messages"]
    statements = [
        build_create_table_sql(name, schema["tables"][name]) for name in table_order
    ]
    return statements
