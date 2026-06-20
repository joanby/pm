import json
from datetime import UTC, datetime

from backend.db.connection import get_connection
from backend.db.users import hash_password

DEFAULT_BOARD_DATA = {
    "columns": [
        {"id": "col-backlog", "title": "Pendientes", "cardIds": ["card-1", "card-2"]},
        {"id": "col-discovery", "title": "Descubrimiento", "cardIds": ["card-3"]},
        {"id": "col-progress", "title": "En Progreso", "cardIds": ["card-4", "card-5"]},
        {"id": "col-review", "title": "Revisión", "cardIds": ["card-6"]},
        {"id": "col-done", "title": "Hecho", "cardIds": ["card-7", "card-8"]},
    ],
    "cards": {
        "card-1": {
            "id": "card-1",
            "title": "Alinear temas del roadmap",
            "details": "Redactar temas trimestrales con metas de impacto y métricas.",
        },
        "card-2": {
            "id": "card-2",
            "title": "Recopilar señales de clientes",
            "details": "Revisar etiquetas de soporte, notas de ventas y bajas.",
        },
        "card-3": {
            "id": "card-3",
            "title": "Prototipar vista de analítica",
            "details": "Bocetar el diseño inicial del panel y sus desgloses clave.",
        },
        "card-4": {
            "id": "card-4",
            "title": "Refinar el lenguaje de los estados",
            "details": "Estandarizar las etiquetas de columna y el tono del tablero.",
        },
        "card-5": {
            "id": "card-5",
            "title": "Diseñar el formato de tarjeta",
            "details": "Añadir jerarquía y espaciado para listas densas.",
        },
        "card-6": {
            "id": "card-6",
            "title": "Revisar microinteracciones",
            "details": "Verificar estados de hover, foco y carga.",
        },
        "card-7": {
            "id": "card-7",
            "title": "Publicar página de marketing",
            "details": "Copy final aprobado y paquete de recursos entregado.",
        },
        "card-8": {
            "id": "card-8",
            "title": "Cerrar sprint de onboarding",
            "details": "Documentar notas de versión y compartir internamente.",
        },
    },
}

DEFAULT_USER = {
    "id": "user-1",
    "username": "usuario",
    "password": "contraseña",
    "display_name": "Usuario MVP",
    "role": "admin",
    "created_at": datetime.now(UTC).isoformat(),
}

DEFAULT_BOARD_ID = "board-1"
DEFAULT_BOARD_NAME = "Tablero principal"


def _column_names(cursor, table: str) -> set[str]:
    return {row[1] for row in cursor.execute(f"PRAGMA table_info({table})").fetchall()}


def _migrate_schema(cursor) -> None:
    user_columns = _column_names(cursor, "users")
    if "role" not in user_columns:
        cursor.execute("ALTER TABLE users ADD COLUMN role TEXT NOT NULL DEFAULT 'member'")

    board_columns = _column_names(cursor, "boards")
    if "name" not in board_columns:
        cursor.execute("ALTER TABLE boards ADD COLUMN name TEXT NOT NULL DEFAULT 'Tablero'")
    if "created_at" not in board_columns:
        cursor.execute("ALTER TABLE boards ADD COLUMN created_at TEXT NOT NULL DEFAULT ''")
        cursor.execute("UPDATE boards SET created_at = updated_at WHERE created_at = ''")

    # One-time migration: legacy MVP stored the password in plain text.
    legacy_user = cursor.execute(
        "SELECT id, password_hash FROM users WHERE id = ?", (DEFAULT_USER["id"],)
    ).fetchone()
    if legacy_user and legacy_user["password_hash"] == DEFAULT_USER["password"]:
        cursor.execute(
            "UPDATE users SET password_hash = ?, role = 'admin' WHERE id = ?",
            (hash_password(DEFAULT_USER["password"]), DEFAULT_USER["id"]),
        )


def init_db(path=None):
    conn = get_connection(path)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS boards (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            name TEXT NOT NULL DEFAULT 'Tablero',
            data TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT '',
            updated_at TEXT NOT NULL
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            display_name TEXT,
            role TEXT NOT NULL DEFAULT 'member',
            created_at TEXT NOT NULL
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            board_id TEXT NOT NULL,
            messages TEXT NOT NULL,
            last_updated_at TEXT NOT NULL
        )
        """
    )

    _migrate_schema(cursor)

    if cursor.execute("SELECT 1 FROM users WHERE id = ?", (DEFAULT_USER["id"],)).fetchone() is None:
        cursor.execute(
            "INSERT INTO users (id, username, password_hash, display_name, role, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (
                DEFAULT_USER["id"],
                DEFAULT_USER["username"],
                hash_password(DEFAULT_USER["password"]),
                DEFAULT_USER["display_name"],
                DEFAULT_USER["role"],
                DEFAULT_USER["created_at"],
            ),
        )

    if cursor.execute("SELECT 1 FROM boards WHERE id = ?", (DEFAULT_BOARD_ID,)).fetchone() is None:
        now = datetime.now(UTC).isoformat()
        cursor.execute(
            "INSERT INTO boards (id, user_id, name, data, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (
                DEFAULT_BOARD_ID,
                DEFAULT_USER["id"],
                DEFAULT_BOARD_NAME,
                json.dumps(DEFAULT_BOARD_DATA),
                now,
                now,
            ),
        )

    conn.commit()
    conn.close()
