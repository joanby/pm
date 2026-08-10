from __future__ import annotations

import sqlite3
from datetime import UTC, datetime

from backend.app.ai.models import ChatMessage


class ChatRepositoryError(Exception):
    pass


def _now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


class ChatRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def list_messages(self, board_id: str, *, limit: int = 20) -> list[ChatMessage]:
        rows = self.connection.execute(
            """
            SELECT id, role, content, created_at
            FROM chat_messages
            WHERE board_id = ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (board_id, limit),
        ).fetchall()
        messages = [
            ChatMessage(
                id=row["id"],
                role=row["role"],
                content=row["content"],
                created_at=row["created_at"],
            )
            for row in reversed(rows)
        ]
        return messages

    def add_message(self, board_id: str, message_id: str, role: str, content: str) -> ChatMessage:
        if role not in {"user", "assistant"}:
            raise ChatRepositoryError(f"Invalid chat role: {role}")

        created_at = _now_iso()
        self.connection.execute(
            """
            INSERT INTO chat_messages (id, board_id, role, content, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (message_id, board_id, role, content, created_at),
        )
        self.connection.commit()
        return ChatMessage(id=message_id, role=role, content=content, created_at=created_at)
