from typing import Literal

from pydantic import BaseModel, model_validator


class CardData(BaseModel):
    id: str
    title: str
    details: str


class ColumnData(BaseModel):
    id: str
    title: str
    cardIds: list[str]


class BoardData(BaseModel):
    columns: list[ColumnData]
    cards: dict[str, CardData]

    @model_validator(mode="after")
    def validate_card_references(self):
        seen_card_ids = set()
        for column in self.columns:
            for card_id in column.cardIds:
                if card_id not in self.cards:
                    raise ValueError(f"Column {column.id} references missing card {card_id}")
                if card_id in seen_card_ids:
                    raise ValueError(f"Card {card_id} is listed more than once")
                seen_card_ids.add(card_id)
        return self


class BoardSummary(BaseModel):
    id: str
    name: str
    updated_at: str


class BoardDetail(BoardData):
    id: str
    name: str
    updated_at: str


class BoardCreateRequest(BaseModel):
    name: str


class BoardRenameRequest(BaseModel):
    name: str


class UserPublic(BaseModel):
    id: str
    username: str
    display_name: str | None
    role: str
    created_at: str


class UserCreateRequest(BaseModel):
    username: str
    password: str
    display_name: str
    role: Literal["admin", "member"] = "member"


class UserUpdateRequest(BaseModel):
    display_name: str | None = None
    password: str | None = None
    role: Literal["admin", "member"] | None = None


class RegisterRequest(BaseModel):
    username: str
    password: str
    display_name: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str
