import pytest
from pydantic import ValidationError

from backend.app.kanban.models import BoardData, Card, Column


def test_board_data_rejects_missing_card_reference() -> None:
    with pytest.raises(ValidationError):
        BoardData(
            columns=[Column(id="col-1", title="Backlog", cardIds=["card-1"])],
            cards={},
        )


def test_board_data_rejects_unused_cards() -> None:
    with pytest.raises(ValidationError):
        BoardData(
            columns=[Column(id="col-1", title="Backlog", cardIds=["card-1"])],
            cards={
                "card-1": Card(id="card-1", title="One", details=""),
                "card-2": Card(id="card-2", title="Two", details=""),
            },
        )


def test_board_data_accepts_valid_structure() -> None:
    board = BoardData(
        columns=[Column(id="col-1", title="Backlog", cardIds=["card-1"])],
        cards={"card-1": Card(id="card-1", title="One", details="Details")},
    )
    assert board.cards["card-1"].title == "One"
