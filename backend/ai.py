import json
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field, ValidationError

from backend.main_models import BoardData
from backend.openrouter import OpenRouterError, call_openrouter_messages


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class AiChatRequest(BaseModel):
    message: str
    board: BoardData
    history: list[ChatMessage] = Field(default_factory=list)


class AiChatResponse(BaseModel):
    message: str
    boardUpdate: Optional[BoardData] = None


AI_RESPONSE_SCHEMA = {
    "type": "json_schema",
    "json_schema": {
        "name": "kanban_ai_response",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "Brief response for the user.",
                },
                "boardUpdate": {
                    "anyOf": [
                        {
                            "type": "object",
                            "properties": {
                                "columns": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "id": {"type": "string"},
                                            "title": {"type": "string"},
                                            "cardIds": {
                                                "type": "array",
                                                "items": {"type": "string"},
                                            },
                                        },
                                        "required": ["id", "title", "cardIds"],
                                        "additionalProperties": False,
                                    },
                                },
                                "cards": {
                                    "type": "object",
                                    "additionalProperties": {
                                        "type": "object",
                                        "properties": {
                                            "id": {"type": "string"},
                                            "title": {"type": "string"},
                                            "details": {"type": "string"},
                                        },
                                        "required": ["id", "title", "details"],
                                        "additionalProperties": False,
                                    },
                                },
                            },
                            "required": ["columns", "cards"],
                            "additionalProperties": False,
                        },
                        {"type": "null"},
                    ],
                    "description": "Complete updated board JSON, or null when no board changes are needed.",
                },
            },
            "required": ["message", "boardUpdate"],
            "additionalProperties": False,
        },
    },
}


SYSTEM_PROMPT = (
    "You are the AI assistant for a local Kanban project management MVP. "
    "Return only JSON matching the provided schema. "
    "If the user asks to create, edit, rename, delete, or move cards or columns, "
    "return the complete updated board in boardUpdate. "
    "If no board change is needed, set boardUpdate to null."
)


def parse_ai_response(content: str) -> AiChatResponse:
    try:
        data = json.loads(content)
    except json.JSONDecodeError as exc:
        raise OpenRouterError("AI response was not valid JSON") from exc

    try:
        return AiChatResponse.model_validate(data)
    except ValidationError as exc:
        raise OpenRouterError(f"AI response did not match the expected schema: {exc}") from exc


def build_ai_messages(request: AiChatRequest) -> list[dict[str, str]]:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(message.model_dump() for message in request.history)
    messages.append(
        {
            "role": "user",
            "content": json.dumps(
                {
                    "prompt": request.message,
                    "board": request.board.model_dump(),
                }
            ),
        }
    )
    return messages


def request_structured_ai_response(request: AiChatRequest) -> AiChatResponse:
    content = call_openrouter_messages(build_ai_messages(request), AI_RESPONSE_SCHEMA)
    return parse_ai_response(content)
