from __future__ import annotations

import json
import re
from typing import Any

from pydantic import ValidationError

from backend.app.ai.exceptions import OpenRouterResponseError
from backend.app.ai.models import AiStructuredResponse
from backend.app.kanban.models import BoardData


_JSON_FENCE_PATTERN = re.compile(r"```(?:json)?\s*(.*?)\s*```", re.DOTALL | re.IGNORECASE)


def extract_json_text(raw_content: str) -> str:
    cleaned = raw_content.strip()
    if not cleaned:
        raise OpenRouterResponseError("OpenRouter response missing assistant content")

    fence_match = _JSON_FENCE_PATTERN.search(cleaned)
    if fence_match:
        return fence_match.group(1).strip()

    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start != -1 and end != -1 and end > start:
        return cleaned[start : end + 1]

    return cleaned


def parse_structured_response(raw_content: str) -> AiStructuredResponse:
    json_text = extract_json_text(raw_content)
    try:
        payload = json.loads(json_text)
    except json.JSONDecodeError as error:
        raise OpenRouterResponseError("Assistant response is not valid JSON") from error

    if not isinstance(payload, dict):
        raise OpenRouterResponseError("Assistant response must be a JSON object")

    message = payload.get("message")
    if not isinstance(message, str) or not message.strip():
        raise OpenRouterResponseError("Assistant response missing message")

    board_payload = payload.get("board")
    board: BoardData | None = None
    if board_payload is not None:
        if not isinstance(board_payload, dict):
            raise OpenRouterResponseError("Assistant board update must be an object")
        try:
            board = BoardData.model_validate(board_payload)
        except ValidationError as error:
            raise OpenRouterResponseError("Assistant board update is invalid") from error

    return AiStructuredResponse(message=message.strip(), board=board)


def validate_board_column_ids(current_board: BoardData, updated_board: BoardData) -> None:
    current_ids = [column.id for column in current_board.columns]
    updated_ids = [column.id for column in updated_board.columns]
    if current_ids != updated_ids:
        raise OpenRouterResponseError("Assistant board update changed fixed column IDs")
