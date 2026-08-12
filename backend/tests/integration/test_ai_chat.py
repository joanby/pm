from backend.app.ai.config import get_openrouter_api_key
from backend.app.ai.exceptions import OpenRouterConfigError
from backend.tests.conftest import AUTH_HEADERS


def test_ai_chat_requires_auth_header(client) -> None:
    response = client.post("/api/ai/chat", json={"message": "Hello"})
    assert response.status_code == 401


def test_ai_chat_history_requires_auth_header(client) -> None:
    response = client.get("/api/ai/history")
    assert response.status_code == 401


def test_ai_chat_history_returns_persisted_messages(client) -> None:
    try:
        get_openrouter_api_key()
    except OpenRouterConfigError as error:
        raise AssertionError(str(error)) from error

    prompt = "Say hello in one short sentence."
    chat_response = client.post(
        "/api/ai/chat",
        headers=AUTH_HEADERS,
        json={"message": prompt},
    )
    assert chat_response.status_code == 200, chat_response.text

    history_response = client.get("/api/ai/history", headers=AUTH_HEADERS)
    assert history_response.status_code == 200
    messages = history_response.json()["messages"]
    assert any(message["role"] == "user" and prompt in message["content"] for message in messages)
    assert any(message["role"] == "assistant" for message in messages)


def test_ai_chat_text_only_response(client) -> None:
    try:
        get_openrouter_api_key()
    except OpenRouterConfigError as error:
        raise AssertionError(str(error)) from error

    response = client.post(
        "/api/ai/chat",
        headers=AUTH_HEADERS,
        json={"message": "How many columns are on my board? Reply briefly."},
    )
    assert response.status_code == 200, response.text

    payload = response.json()
    assert payload["boardUpdated"] is False
    assert isinstance(payload["message"], str)
    assert payload["message"].strip()
    assert len(payload["board"]["columns"]) == 5


def test_ai_chat_can_apply_board_update(client) -> None:
    try:
        get_openrouter_api_key()
    except OpenRouterConfigError as error:
        raise AssertionError(str(error)) from error

    card_title = "AI Integration Test Card"
    response = client.post(
        "/api/ai/chat",
        headers=AUTH_HEADERS,
        json={
            "message": (
                "Add a new card titled 'AI Integration Test Card' to the Backlog column "
                "with details 'Created by Part 9 integration test'. "
                "Return the full updated board in the board field."
            )
        },
    )
    assert response.status_code == 200, response.text

    payload = response.json()
    assert isinstance(payload["message"], str)
    board = payload["board"]
    backlog = next(column for column in board["columns"] if column["id"] == "col-backlog")
    created_ids = [
        card_id
        for card_id in backlog["cardIds"]
        if board["cards"][card_id]["title"] == card_title
    ]
    assert created_ids, payload

    if payload["boardUpdated"]:
        reload = client.get("/api/board", headers=AUTH_HEADERS).json()
        reloaded_ids = [
            card_id
            for card_id, card in reload["cards"].items()
            if card["title"] == card_title
        ]
        assert reloaded_ids
