from __future__ import annotations

import secrets
from collections.abc import Callable
from typing import TypeVar

from backend.app.ai.chat_repository import ChatRepository
from backend.app.ai.client import OpenRouterClient
from backend.app.ai.exceptions import OpenRouterResponseError
from backend.app.ai.models import ChatResponse, ChatHistoryResponse, ChatMessage as ChatMessageModel
from backend.app.ai.prompts import build_chat_messages
from backend.app.ai.structured import parse_structured_response, validate_board_column_ids
from backend.app.db.connection import db_connection
from backend.app.kanban.models import BoardData
from backend.app.kanban.repository import KanbanNotFoundError, KanbanRepository
from backend.app.kanban.service import KanbanService

T = TypeVar("T")
HISTORY_LIMIT = 20


class ChatService:
    def __init__(
        self,
        *,
        kanban_service: KanbanService | None = None,
        client: OpenRouterClient | None = None,
    ) -> None:
        self.kanban_service = kanban_service or KanbanService()
        self.client = client or OpenRouterClient()

    def chat(self, username: str, message: str) -> ChatResponse:
        current_board = self.kanban_service.get_board(username)
        history, board_id = self._load_history(username)

        ai_messages = build_chat_messages(current_board, history, message)
        raw_response = self.client.complete_messages(ai_messages, json_mode=True)
        structured = self._parse_or_fallback(raw_response)

        board = current_board
        board_updated = False
        if structured.board is not None:
            try:
                validate_board_column_ids(current_board, structured.board)
                board = self.kanban_service.replace_board(username, structured.board)
                board_updated = True
            except OpenRouterResponseError:
                pass

        self._persist_exchange(board_id, message, structured.message)
        return ChatResponse(
            message=structured.message,
            board=board,
            board_updated=board_updated,
        )

    def get_history(self, username: str) -> ChatHistoryResponse:
        history, _ = self._load_history(username)
        return ChatHistoryResponse(messages=history)

    def _parse_or_fallback(self, raw_response: str):
        try:
            return parse_structured_response(raw_response)
        except OpenRouterResponseError:
            cleaned = raw_response.strip()
            if not cleaned:
                raise
            from backend.app.ai.models import AiStructuredResponse

            return AiStructuredResponse(message=cleaned, board=None)

    def _load_history(self, username: str) -> tuple[list[ChatMessageModel], str]:
        def operation(repository: KanbanRepository) -> tuple[list[ChatMessageModel], str]:
            user_id = repository.get_user_id(username)
            if user_id is None:
                raise KanbanNotFoundError(f"User '{username}' not found")
            board_id = repository.get_board_id_for_user(user_id)
            if board_id is None:
                raise KanbanNotFoundError(f"Board for user '{username}' not found")

            chat_repository = ChatRepository(repository.connection)
            history = chat_repository.list_messages(board_id, limit=HISTORY_LIMIT)
            return history, board_id

        return self._run(operation)

    def _persist_exchange(self, board_id: str, user_message: str, assistant_message: str) -> None:
        def operation(repository: KanbanRepository) -> None:
            chat_repository = ChatRepository(repository.connection)
            chat_repository.add_message(board_id, _generate_message_id(), "user", user_message)
            chat_repository.add_message(board_id, _generate_message_id(), "assistant", assistant_message)

        self._run(operation)

    def _run(self, operation: Callable[[KanbanRepository], T]) -> T:
        with db_connection() as connection:
            return operation(KanbanRepository(connection))


def _generate_message_id() -> str:
    return f"msg-{secrets.token_hex(6)}"
