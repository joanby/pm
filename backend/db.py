import json
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

DB_FILENAME = "kanban.db"
DB_PATH_ENV = "KANBAN_DB_PATH"
DEFAULT_DB_PATH = Path(__file__).resolve().parent / DB_FILENAME

DEFAULT_BOARD = {
    "columns": [
        {"id": "col-backlog", "title": "Backlog", "cardIds": ["card-1", "card-2"]},
        {"id": "col-discovery", "title": "Discovery", "cardIds": ["card-3"]},
        {"id": "col-progress", "title": "In Progress", "cardIds": ["card-4", "card-5"]},
        {"id": "col-review", "title": "Review", "cardIds": ["card-6"]},
        {"id": "col-done", "title": "Done", "cardIds": ["card-7", "card-8"]},
    ],
    "cards": {
        "card-1": {
            "id": "card-1",
            "title": "Align roadmap themes",
            "details": "Draft quarterly themes with impact statements and metrics.",
        },
        "card-2": {
            "id": "card-2",
            "title": "Gather customer signals",
            "details": "Review support tags, sales notes, and churn feedback.",
        },
        "card-3": {
            "id": "card-3",
            "title": "Prototype analytics view",
            "details": "Sketch initial dashboard layout and key drill-downs.",
        },
        "card-4": {
            "id": "card-4",
            "title": "Refine status language",
            "details": "Standardize column labels and tone across the board.",
        },
        "card-5": {
            "id": "card-5",
            "title": "Design card layout",
            "details": "Add hierarchy and spacing for scanning dense lists.",
        },
        "card-6": {
            "id": "card-6",
            "title": "QA micro-interactions",
            "details": "Verify hover, focus, and loading states.",
        },
        "card-7": {
            "id": "card-7",
            "title": "Ship marketing page",
            "details": "Final copy approved and asset pack delivered.",
        },
        "card-8": {
            "id": "card-8",
            "title": "Close onboarding sprint",
            "details": "Document release notes and share internally.",
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


def get_db_path(path=None):
    if path is None:
        return DEFAULT_DB_PATH
    return Path(path)


def get_connection(path=None):
    db_path = get_db_path(path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


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


def load_board(path=None):
    conn = get_connection(path)
    cursor = conn.cursor()
    row = cursor.execute("SELECT data FROM boards WHERE id = ?", ("board-1",)).fetchone()
    conn.close()
    if row is None:
        raise RuntimeError("Board data not found")
    return json.loads(row["data"])


def save_board(board, path=None):
    conn = get_connection(path)
    cursor = conn.cursor()
    updated_at = datetime.utcnow().isoformat() + "Z"
    cursor.execute(
        "UPDATE boards SET data = ?, updated_at = ? WHERE id = ?",
        (json.dumps(board), updated_at, "board-1"),
    )
    if cursor.rowcount == 0:
        cursor.execute(
            "INSERT INTO boards (id, user_id, data, updated_at) VALUES (?, ?, ?, ?)",
            ("board-1", DEFAULT_USER["id"], json.dumps(board), updated_at),
        )
    conn.commit()
    conn.close()
