import json
from datetime import datetime

from backend.db.connection import get_connection
from backend.db.seed import DEFAULT_USER


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
