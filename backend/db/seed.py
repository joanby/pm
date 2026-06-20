import json
from datetime import datetime

from backend.db.connection import get_connection

DEFAULT_BOARD = {
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
    "password_hash": "contraseña",
    "display_name": "Usuario MVP",
    "created_at": datetime.utcnow().isoformat() + "Z",
}

DEFAULT_CONVERSATIONS = []  # type: list[dict]


def init_db(path=None):
    conn = get_connection(path)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS boards (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            data TEXT NOT NULL,
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

    if cursor.execute("SELECT 1 FROM boards WHERE id = ?", ("board-1",)).fetchone() is None:
        cursor.execute(
            "INSERT INTO boards (id, user_id, data, updated_at) VALUES (?, ?, ?, ?)",
            ("board-1", DEFAULT_USER["id"], json.dumps(DEFAULT_BOARD), datetime.utcnow().isoformat() + "Z"),
        )

    if cursor.execute("SELECT 1 FROM users WHERE id = ?", (DEFAULT_USER["id"],)).fetchone() is None:
        cursor.execute(
            "INSERT INTO users (id, username, password_hash, display_name, created_at) VALUES (?, ?, ?, ?, ?)",
            (
                DEFAULT_USER["id"],
                DEFAULT_USER["username"],
                DEFAULT_USER["password_hash"],
                DEFAULT_USER["display_name"],
                DEFAULT_USER["created_at"],
            ),
        )

    if cursor.execute("SELECT 1 FROM conversations LIMIT 1").fetchone() is None:
        for conversation in DEFAULT_CONVERSATIONS:
            cursor.execute(
                "INSERT INTO conversations (id, user_id, board_id, messages, last_updated_at) VALUES (?, ?, ?, ?, ?)",
                (
                    conversation["id"],
                    conversation["user_id"],
                    conversation["board_id"],
                    json.dumps(conversation["messages"]),
                    conversation["last_updated_at"],
                ),
            )

    conn.commit()
    conn.close()
