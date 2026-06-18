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
