from pathlib import Path

from backend.app.db.init_db import init_database, list_tables
from backend.app.db.schema import REQUIRED_TABLE_NAMES


def test_init_database_creates_sqlite_file_and_tables(tmp_path: Path) -> None:
    db_path = tmp_path / "test.db"
    created_path = init_database(db_path)

    assert created_path == db_path
    assert db_path.is_file()

    tables = list_tables(db_path)
    assert REQUIRED_TABLE_NAMES.issubset(tables)


def test_init_database_is_idempotent(tmp_path: Path) -> None:
    db_path = tmp_path / "test.db"
    init_database(db_path)
    first_tables = list_tables(db_path)
    init_database(db_path)
    second_tables = list_tables(db_path)
    assert first_tables == second_tables
