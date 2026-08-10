from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator

from backend.app.kanban.models import BoardData


class AiPingResponse(BaseModel):
    model: str
    prompt: str
    response: str = Field(min_length=1)


class ChatMessage(BaseModel):
    id: str
    role: str
    content: str
    created_at: str


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)

    @field_validator("message")
    @classmethod
    def message_not_blank(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Message cannot be empty")
        return cleaned


class AiStructuredResponse(BaseModel):
    message: str = Field(min_length=1)
    board: BoardData | None = None


class ChatResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, ser_json_by_alias=True)

    message: str
    board: BoardData
    board_updated: bool = Field(alias="boardUpdated")


class ChatHistoryResponse(BaseModel):
    messages: list[ChatMessage]
