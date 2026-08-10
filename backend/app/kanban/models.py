from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class Card(BaseModel):
    model_config = ConfigDict(populate_by_name=True, ser_json_by_alias=True)

    id: str
    title: str
    details: str


class Column(BaseModel):
    model_config = ConfigDict(populate_by_name=True, ser_json_by_alias=True)

    id: str
    title: str
    card_ids: list[str] = Field(alias="cardIds")

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Column title cannot be empty")
        return cleaned


class BoardData(BaseModel):
    model_config = ConfigDict(populate_by_name=True, ser_json_by_alias=True)

    columns: list[Column]
    cards: dict[str, Card]

    @field_validator("columns")
    @classmethod
    def require_columns(cls, value: list[Column]) -> list[Column]:
        if not value:
            raise ValueError("Board must include at least one column")
        return value

    @model_validator(mode="after")
    def validate_card_references(self) -> "BoardData":
        referenced_ids: list[str] = []
        for column in self.columns:
            referenced_ids.extend(column.card_ids)

        missing = [card_id for card_id in referenced_ids if card_id not in self.cards]
        if missing:
            raise ValueError(f"Missing card definitions for: {', '.join(missing)}")

        seen: set[str] = set()
        duplicated: list[str] = []
        for card_id in referenced_ids:
            if card_id in seen and card_id not in duplicated:
                duplicated.append(card_id)
            seen.add(card_id)
        if duplicated:
            raise ValueError(
                f"Cards referenced by more than one column: {', '.join(duplicated)}"
            )

        for card_id, card in self.cards.items():
            if card.id != card_id:
                raise ValueError(f"Card key '{card_id}' does not match card id '{card.id}'")

        unused = [card_id for card_id in self.cards if card_id not in referenced_ids]
        if unused:
            raise ValueError(f"Cards not referenced by any column: {', '.join(unused)}")

        return self


class ColumnUpdate(BaseModel):
    title: str

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Column title cannot be empty")
        return cleaned


class CardCreate(BaseModel):
    title: str
    details: str = "No details yet."
    id: str | None = None

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Card title cannot be empty")
        return cleaned


class CardUpdate(BaseModel):
    title: str | None = None
    details: str | None = None

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, value: str | None) -> str | None:
        if value is None:
            return value
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Card title cannot be empty")
        return cleaned


class CardMove(BaseModel):
    column_id: str
    position: int = Field(ge=0)
