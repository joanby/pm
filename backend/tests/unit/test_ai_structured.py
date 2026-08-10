import json

import pytest

from backend.app.ai.exceptions import OpenRouterResponseError
from backend.app.ai.structured import extract_json_text, parse_structured_response, validate_board_column_ids
from backend.app.kanban.models import BoardData, Card, Column


def _sample_board() -> BoardData:
    return BoardData(
        columns=[
            Column(id="col-backlog", title="Backlog", card_ids=["card-1"]),
            Column(id="col-done", title="Done", card_ids=[]),
        ],
        cards={
            "card-1": Card(id="card-1", title="Existing", details="Details"),
        },
    )


def test_extract_json_text_from_code_fence() -> None:
    raw = 'Here you go:\n```json\n{"message":"Hi","board":null}\n```'
    assert extract_json_text(raw) == '{"message":"Hi","board":null}'


def test_parse_structured_response_text_only() -> None:
    payload = parse_structured_response('{"message":"You have two columns.","board":null}')
    assert payload.message == "You have two columns."
    assert payload.board is None


def test_parse_structured_response_with_board_update() -> None:
    board_json = {
        "columns": [
            {"id": "col-backlog", "title": "Backlog", "cardIds": ["card-1", "card-2"]},
            {"id": "col-done", "title": "Done", "cardIds": []},
        ],
        "cards": {
            "card-1": {"id": "card-1", "title": "Existing", "details": "Details"},
            "card-2": {"id": "card-2", "title": "New card", "details": "Added"},
        },
    }
    payload = parse_structured_response(
        json.dumps({"message": "Added a card.", "board": board_json})
    )
    assert payload.message == "Added a card."
    assert payload.board is not None
    assert "card-2" in payload.board.cards


def test_parse_structured_response_rejects_invalid_board() -> None:
    with pytest.raises(OpenRouterResponseError, match="invalid"):
        parse_structured_response(
            json.dumps(
                {
                    "message": "Broken",
                    "board": {
                        "columns": [{"id": "col-backlog", "title": "Backlog", "cardIds": ["missing"]}],
                        "cards": {},
                    },
                }
            )
        )


def test_validate_board_column_ids_rejects_changed_columns() -> None:
    current = _sample_board()
    updated = BoardData(
        columns=[Column(id="col-new", title="New", card_ids=[])],
        cards={},
    )
    with pytest.raises(OpenRouterResponseError, match="fixed column IDs"):
        validate_board_column_ids(current, updated)
