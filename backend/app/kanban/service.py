from __future__ import annotations

import secrets
from collections.abc import Callable
from typing import TypeVar

from backend.app.db.connection import db_connection
from backend.app.kanban.models import BoardData, Card, CardCreate, CardMove, CardUpdate, Column, ColumnUpdate
from backend.app.kanban.repository import KanbanNotFoundError, KanbanRepository, KanbanRepositoryError

T = TypeVar("T")


class KanbanService:
    def _run(self, operation: Callable[[KanbanRepository], T]) -> T:
        with db_connection() as connection:
            return operation(KanbanRepository(connection))

    def _board_id_for_username(self, repository: KanbanRepository, username: str) -> str:
        user_id = repository.get_user_id(username)
        if user_id is None:
            raise KanbanNotFoundError(f"User '{username}' not found")
        board_id = repository.get_board_id_for_user(user_id)
        if board_id is None:
            raise KanbanNotFoundError(f"Board for user '{username}' not found")
        return board_id

    def get_board(self, username: str) -> BoardData:
        def operation(repository: KanbanRepository) -> BoardData:
            board_id = self._board_id_for_username(repository, username)
            return repository.get_board(board_id)

        return self._run(operation)

    def replace_board(self, username: str, board: BoardData) -> BoardData:
        def operation(repository: KanbanRepository) -> BoardData:
            board_id = self._board_id_for_username(repository, username)
            return repository.replace_board(board_id, board)

        return self._run(operation)

    def rename_column(self, username: str, column_id: str, payload: ColumnUpdate) -> Column:
        def operation(repository: KanbanRepository) -> Column:
            board_id = self._board_id_for_username(repository, username)
            return repository.update_column_title(board_id, column_id, payload.title)

        return self._run(operation)

    def create_card(self, username: str, column_id: str, payload: CardCreate) -> Card:
        def operation(repository: KanbanRepository) -> Card:
            board_id = self._board_id_for_username(repository, username)
            card_id = payload.id or _generate_card_id()
            return repository.create_card(
                board_id,
                column_id,
                card_id,
                payload.title,
                payload.details,
            )

        return self._run(operation)

    def update_card(self, username: str, card_id: str, payload: CardUpdate) -> Card:
        if payload.title is None and payload.details is None:
            raise KanbanRepositoryError("At least one field must be provided")

        def operation(repository: KanbanRepository) -> Card:
            board_id = self._board_id_for_username(repository, username)
            return repository.update_card(
                board_id,
                card_id,
                payload.title,
                payload.details,
            )

        return self._run(operation)

    def delete_card(self, username: str, card_id: str) -> None:
        def operation(repository: KanbanRepository) -> None:
            board_id = self._board_id_for_username(repository, username)
            repository.delete_card(board_id, card_id)

        self._run(operation)

    def move_card(self, username: str, card_id: str, payload: CardMove) -> BoardData:
        def operation(repository: KanbanRepository) -> BoardData:
            board_id = self._board_id_for_username(repository, username)
            return repository.move_card(
                board_id,
                card_id,
                payload.column_id,
                payload.position,
            )

        return self._run(operation)


def _generate_card_id() -> str:
    return f"card-{secrets.token_hex(4)}"
