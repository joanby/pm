import json
import uuid
from datetime import UTC, datetime

from backend.db.connection import get_connection

EMPTY_BOARD = {
    "columns": [
        {"id": "col-backlog", "title": "Pendientes", "cardIds": []},
        {"id": "col-discovery", "title": "Descubrimiento", "cardIds": []},
        {"id": "col-progress", "title": "En Progreso", "cardIds": []},
        {"id": "col-review", "title": "Revisión", "cardIds": []},
        {"id": "col-done", "title": "Hecho", "cardIds": []},
    ],
    "cards": {},
}


def _row_to_summary(row) -> dict:
    return {"id": row["id"], "name": row["name"], "updated_at": row["updated_at"]}


def _row_to_board(row) -> dict:
    return {
        "id": row["id"],
        "name": row["name"],
        "updated_at": row["updated_at"],
        **json.loads(row["data"]),
    }


def list_boards_for_user(user_id, path=None) -> list[dict]:
    conn = get_connection(path)
    cursor = conn.cursor()
    rows = cursor.execute(
        "SELECT * FROM boards WHERE user_id = ? ORDER BY created_at", (user_id,)
    ).fetchall()
    conn.close()
    return [_row_to_summary(row) for row in rows]


def get_board(board_id, user_id, path=None) -> dict | None:
    conn = get_connection(path)
    cursor = conn.cursor()
    row = cursor.execute(
        "SELECT * FROM boards WHERE id = ? AND user_id = ?", (board_id, user_id)
    ).fetchone()
    conn.close()
    return _row_to_board(row) if row else None


def create_board(user_id, name, data=None, path=None) -> dict:
    conn = get_connection(path)
    cursor = conn.cursor()
    board_id = f"board-{uuid.uuid4().hex[:12]}"
    now = datetime.now(UTC).isoformat()
    cursor.execute(
        "INSERT INTO boards (id, user_id, name, data, created_at, updated_at) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (board_id, user_id, name, json.dumps(data if data is not None else EMPTY_BOARD), now, now),
    )
    conn.commit()
    conn.close()
    return get_board(board_id, user_id, path)


def update_board_data(board_id, user_id, data, path=None) -> bool:
    conn = get_connection(path)
    cursor = conn.cursor()
    updated_at = datetime.now(UTC).isoformat()
    cursor.execute(
        "UPDATE boards SET data = ?, updated_at = ? WHERE id = ? AND user_id = ?",
        (json.dumps(data), updated_at, board_id, user_id),
    )
    updated = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return updated


def rename_board(board_id, user_id, name, path=None) -> bool:
    conn = get_connection(path)
    cursor = conn.cursor()
    updated_at = datetime.now(UTC).isoformat()
    cursor.execute(
        "UPDATE boards SET name = ?, updated_at = ? WHERE id = ? AND user_id = ?",
        (name, updated_at, board_id, user_id),
    )
    updated = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return updated


def delete_board(board_id, user_id, path=None) -> bool:
    conn = get_connection(path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM boards WHERE id = ? AND user_id = ?", (board_id, user_id))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted
