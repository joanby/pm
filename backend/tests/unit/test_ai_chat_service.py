from backend.app.ai.chat_service import ChatService
from backend.app.ai.client import OpenRouterClient


class FakeOpenRouterClient(OpenRouterClient):
    def __init__(self, response: str) -> None:
        self.response = response
        self.model = "test-model"

    def complete_messages(self, messages, *, json_mode: bool = False) -> str:
        del messages, json_mode
        return self.response


def test_chat_applies_valid_board_update(client) -> None:
    updated_board = {
        "columns": [
            {"id": "col-backlog", "title": "Backlog", "cardIds": ["card-1", "card-2"]},
            {"id": "col-discovery", "title": "Discovery", "cardIds": ["card-3"]},
            {"id": "col-progress", "title": "In Progress", "cardIds": ["card-4", "card-5"]},
            {"id": "col-review", "title": "Review", "cardIds": ["card-6"]},
            {"id": "col-done", "title": "Done", "cardIds": ["card-7", "card-8"]},
        ],
        "cards": {
            "card-1": {"id": "card-1", "title": "Align roadmap themes", "details": "Draft quarterly themes with impact statements and metrics."},
            "card-2": {"id": "card-2", "title": "Gather customer signals", "details": "Review support tags, sales notes, and churn feedback."},
            "card-3": {"id": "card-3", "title": "Prototype analytics view", "details": "Sketch initial dashboard layout and key drill-downs."},
            "card-4": {"id": "card-4", "title": "Refine status language", "details": "Standardize column labels and tone across the board."},
            "card-5": {"id": "card-5", "title": "Design card layout", "details": "Add hierarchy and spacing for scanning dense lists."},
            "card-6": {"id": "card-6", "title": "QA drag and drop", "details": "Verify keyboard and pointer interactions across breakpoints."},
            "card-7": {"id": "card-7", "title": "Ship login guard", "details": "Require authentication before rendering the board."},
            "card-8": {"id": "card-8", "title": "Release notes draft", "details": "Summarize MVP scope and known limitations."},
            "card-ai-test": {"id": "card-ai-test", "title": "AI unit test card", "details": "Created in unit test"},
        },
    }
    for column in updated_board["columns"]:
        if column["id"] == "col-backlog":
            column["cardIds"].append("card-ai-test")

    fake_response = (
        '{"message":"Added AI unit test card.","board":'
        + __import__("json").dumps(updated_board)
        + "}"
    )
    service = ChatService(client=FakeOpenRouterClient(fake_response))
    result = service.chat("user", "Add AI unit test card to Backlog")

    assert result.board_updated is True
    assert "card-ai-test" in result.board.cards
    assert result.board.cards["card-ai-test"].title == "AI unit test card"


def test_chat_keeps_board_when_update_changes_column_ids(client) -> None:
    fake_response = (
        '{"message":"I tried to change columns.","board":{"columns":[{"id":"col-new","title":"New","cardIds":[]}],"cards":{}}}'
    )
    service = ChatService(client=FakeOpenRouterClient(fake_response))
    before = service.kanban_service.get_board("user")
    result = service.chat("user", "Replace all columns")

    assert result.board_updated is False
    assert [column.id for column in result.board.columns] == [column.id for column in before.columns]
