import os

from backend.db import DB_PATH_ENV
from backend.db.connection import get_connection
from backend.db.seed import init_db
from backend.db.users import find_user, update_user, verify_password


def test_verify_password_rejects_malformed_hash() -> None:
    assert verify_password("anything", "not-a-real-bcrypt-hash") is False


def test_update_user_with_no_fields_returns_existing_user() -> None:
    path = os.environ[DB_PATH_ENV]
    init_db(path)
    before = find_user("usuario", path)
    after = update_user(before["id"], path=path)
    assert after == before


def test_init_db_migrates_legacy_plaintext_password() -> None:
    path = os.environ[DB_PATH_ENV]

    conn = get_connection(path)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE boards (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            data TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE users (
            id TEXT PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            display_name TEXT,
            created_at TEXT NOT NULL
        )
        """
    )
    cursor.execute(
        "INSERT INTO users (id, username, password_hash, display_name, created_at) "
        "VALUES ('user-1', 'usuario', 'contraseña', 'Usuario MVP', '2024-01-01T00:00:00Z')"
    )
    conn.commit()
    conn.close()

    init_db(path)

    user = find_user("usuario", path)
    assert user["role"] == "admin"
    assert user["password_hash"] != "contraseña"
    assert verify_password("contraseña", user["password_hash"])
