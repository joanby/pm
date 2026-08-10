from __future__ import annotations

import sqlite3
from datetime import UTC, datetime

from backend.app.kanban.models import BoardData, Card, Column


class KanbanRepositoryError(Exception):
    pass


class KanbanNotFoundError(KanbanRepositoryError):
    pass


def _now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


class KanbanRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def get_user_id(self, username: str) -> str | None:
        row = self.connection.execute(
            "SELECT id FROM users WHERE username = ?", (username,)
        ).fetchone()
        return None if row is None else row["id"]

    def get_board_id_for_user(self, user_id: str) -> str | None:
        row = self.connection.execute(
            "SELECT id FROM boards WHERE user_id = ? ORDER BY created_at LIMIT 1",
            (user_id,),
        ).fetchone()
        return None if row is None else row["id"]

    def get_board(self, board_id: str) -> BoardData:
        column_rows = self.connection.execute(
            """
            SELECT id, title
            FROM columns
            WHERE board_id = ?
            ORDER BY position
            """,
            (board_id,),
        ).fetchall()
        if not column_rows:
            raise KanbanNotFoundError(f"Board '{board_id}' not found")

        columns: list[Column] = []
        cards: dict[str, Card] = {}

        for column_row in column_rows:
            card_rows = self.connection.execute(
                """
                SELECT id, title, details
                FROM cards
                WHERE column_id = ?
                ORDER BY position
                """,
                (column_row["id"],),
            ).fetchall()
            card_ids = []
            for card_row in card_rows:
                card_ids.append(card_row["id"])
                cards[card_row["id"]] = Card(
                    id=card_row["id"],
                    title=card_row["title"],
                    details=card_row["details"],
                )
            columns.append(
                Column(id=column_row["id"], title=column_row["title"], card_ids=card_ids)
            )

        return BoardData(columns=columns, cards=cards)

    def replace_board(self, board_id: str, board: BoardData) -> BoardData:
        if not self.connection.execute(
            "SELECT 1 FROM boards WHERE id = ?", (board_id,)
        ).fetchone():
            raise KanbanNotFoundError(f"Board '{board_id}' not found")

        now = _now_iso()
        self.connection.execute(
            """
            DELETE FROM cards
            WHERE column_id IN (SELECT id FROM columns WHERE board_id = ?)
            """,
            (board_id,),
        )
        self.connection.execute("DELETE FROM columns WHERE board_id = ?", (board_id,))

        for position, column in enumerate(board.columns):
            self.connection.execute(
                """
                INSERT INTO columns (id, board_id, title, position, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (column.id, board_id, column.title, position, now, now),
            )
            for card_position, card_id in enumerate(column.card_ids):
                card = board.cards[card_id]
                self.connection.execute(
                    """
                    INSERT INTO cards (id, column_id, title, details, position, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        card.id,
                        column.id,
                        card.title,
                        card.details,
                        card_position,
                        now,
                        now,
                    ),
                )

        self.connection.execute(
            "UPDATE boards SET updated_at = ? WHERE id = ?",
            (now, board_id),
        )
        self.connection.commit()
        return self.get_board(board_id)

    def update_column_title(self, board_id: str, column_id: str, title: str) -> Column:
        row = self.connection.execute(
            """
            SELECT id FROM columns
            WHERE id = ? AND board_id = ?
            """,
            (column_id, board_id),
        ).fetchone()
        if row is None:
            raise KanbanNotFoundError(f"Column '{column_id}' not found")

        now = _now_iso()
        self.connection.execute(
            "UPDATE columns SET title = ?, updated_at = ? WHERE id = ?",
            (title, now, column_id),
        )
        self.connection.execute(
            "UPDATE boards SET updated_at = ? WHERE id = ?",
            (now, board_id),
        )
        self.connection.commit()
        board = self.get_board(board_id)
        return next(column for column in board.columns if column.id == column_id)

    def create_card(
        self,
        board_id: str,
        column_id: str,
        card_id: str,
        title: str,
        details: str,
    ) -> Card:
        column = self.connection.execute(
            "SELECT id FROM columns WHERE id = ? AND board_id = ?",
            (column_id, board_id),
        ).fetchone()
        if column is None:
            raise KanbanNotFoundError(f"Column '{column_id}' not found")

        existing = self.connection.execute(
            "SELECT id FROM cards WHERE id = ?", (card_id,)
        ).fetchone()
        if existing:
            raise KanbanRepositoryError(f"Card '{card_id}' already exists")

        position_row = self.connection.execute(
            "SELECT COALESCE(MAX(position), -1) + 1 AS next_position FROM cards WHERE column_id = ?",
            (column_id,),
        ).fetchone()
        position = int(position_row["next_position"])
        now = _now_iso()

        self.connection.execute(
            """
            INSERT INTO cards (id, column_id, title, details, position, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (card_id, column_id, title, details, position, now, now),
        )
        self.connection.execute(
            "UPDATE boards SET updated_at = ? WHERE id = ?",
            (now, board_id),
        )
        self.connection.commit()
        return Card(id=card_id, title=title, details=details)

    def update_card(
        self,
        board_id: str,
        card_id: str,
        title: str | None,
        details: str | None,
    ) -> Card:
        row = self.connection.execute(
            """
            SELECT cards.id, cards.title, cards.details
            FROM cards
            JOIN columns ON columns.id = cards.column_id
            WHERE cards.id = ? AND columns.board_id = ?
            """,
            (card_id, board_id),
        ).fetchone()
        if row is None:
            raise KanbanNotFoundError(f"Card '{card_id}' not found")

        next_title = title if title is not None else row["title"]
        next_details = details if details is not None else row["details"]
        now = _now_iso()
        self.connection.execute(
            """
            UPDATE cards SET title = ?, details = ?, updated_at = ?
            WHERE id = ?
            """,
            (next_title, next_details, now, card_id),
        )
        self.connection.execute(
            "UPDATE boards SET updated_at = ? WHERE id = ?",
            (now, board_id),
        )
        self.connection.commit()
        return Card(id=card_id, title=next_title, details=next_details)

    def delete_card(self, board_id: str, card_id: str) -> None:
        row = self.connection.execute(
            """
            SELECT cards.id, cards.column_id, cards.position
            FROM cards
            JOIN columns ON columns.id = cards.column_id
            WHERE cards.id = ? AND columns.board_id = ?
            """,
            (card_id, board_id),
        ).fetchone()
        if row is None:
            raise KanbanNotFoundError(f"Card '{card_id}' not found")

        column_id = row["column_id"]
        deleted_position = row["position"]
        now = _now_iso()
        self.connection.execute("DELETE FROM cards WHERE id = ?", (card_id,))
        self.connection.execute(
            """
            UPDATE cards SET position = position - 1, updated_at = ?
            WHERE column_id = ? AND position > ?
            """,
            (now, column_id, deleted_position),
        )
        self.connection.execute(
            "UPDATE boards SET updated_at = ? WHERE id = ?",
            (now, board_id),
        )
        self.connection.commit()

    def move_card(
        self,
        board_id: str,
        card_id: str,
        target_column_id: str,
        target_position: int,
    ) -> BoardData:
        source = self.connection.execute(
            """
            SELECT cards.id, cards.column_id, cards.position
            FROM cards
            JOIN columns ON columns.id = cards.column_id
            WHERE cards.id = ? AND columns.board_id = ?
            """,
            (card_id, board_id),
        ).fetchone()
        if source is None:
            raise KanbanNotFoundError(f"Card '{card_id}' not found")

        target_column = self.connection.execute(
            "SELECT id FROM columns WHERE id = ? AND board_id = ?",
            (target_column_id, board_id),
        ).fetchone()
        if target_column is None:
            raise KanbanNotFoundError(f"Column '{target_column_id}' not found")

        source_column_id = source["column_id"]
        source_position = source["position"]

        if source_column_id == target_column_id and target_position == source_position:
            return self.get_board(board_id)

        now = _now_iso()

        # Vacate the moving card's current slot first. Otherwise the sibling
        # shifts below can transiently collide with it under the
        # UNIQUE(column_id, position) index (see _shift_positions for why the
        # shifts themselves also need to avoid colliding with each other).
        self.connection.execute(
            "UPDATE cards SET position = -1, updated_at = ? WHERE id = ?",
            (now, card_id),
        )

        if source_column_id == target_column_id:
            if target_position > source_position:
                self._shift_positions(
                    source_column_id,
                    -1,
                    now,
                    "position > ? AND position <= ?",
                    (source_position, target_position),
                )
            else:
                self._shift_positions(
                    source_column_id,
                    1,
                    now,
                    "position >= ? AND position < ?",
                    (target_position, source_position),
                )
            self.connection.execute(
                "UPDATE cards SET position = ?, updated_at = ? WHERE id = ?",
                (target_position, now, card_id),
            )
        else:
            self._shift_positions(
                source_column_id, -1, now, "position > ?", (source_position,)
            )
            self._shift_positions(
                target_column_id, 1, now, "position >= ?", (target_position,)
            )
            self.connection.execute(
                """
                UPDATE cards
                SET column_id = ?, position = ?, updated_at = ?
                WHERE id = ?
                """,
                (target_column_id, target_position, now, card_id),
            )

        self.connection.execute(
            "UPDATE boards SET updated_at = ? WHERE id = ?",
            (now, board_id),
        )
        self.connection.commit()
        return self.get_board(board_id)

    # Positions are staged through this disjoint negative range before landing
    # on their final value. SQLite does not guarantee the row-processing order
    # within a single multi-row UPDATE, so shifting several sibling rows by
    # +-1 directly (their new values landing on each other's *current*
    # values) can trip the UNIQUE(column_id, position) index depending on
    # that order. Staging every matched row through a value derived only from
    # its own current position first (never colliding with an untouched
    # sibling or with another staged row) makes the shift order-independent.
    _POSITION_STAGING_OFFSET = 1_000_000

    def _shift_positions(
        self,
        column_id: str,
        delta: int,
        now: str,
        condition_sql: str,
        condition_params: tuple,
    ) -> None:
        offset = self._POSITION_STAGING_OFFSET
        self.connection.execute(
            f"""
            UPDATE cards
            SET position = -(position + {offset}), updated_at = ?
            WHERE column_id = ? AND {condition_sql}
            """,
            (now, column_id, *condition_params),
        )
        self.connection.execute(
            f"""
            UPDATE cards
            SET position = -position - {offset} + ({delta}), updated_at = ?
            WHERE column_id = ? AND position <= -{offset}
            """,
            (now, column_id),
        )
