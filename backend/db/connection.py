import os
import sqlite3
from pathlib import Path

DB_FILENAME = "kanban.db"
DB_PATH_ENV = "KANBAN_DB_PATH"
DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / DB_FILENAME


def get_db_path() -> str | None:
    return os.environ.get(DB_PATH_ENV)


def _resolve_db_path(path=None) -> Path:
    if path is None:
        return DEFAULT_DB_PATH
    return Path(path)


def get_connection(path=None) -> sqlite3.Connection:
    db_path = _resolve_db_path(path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn
