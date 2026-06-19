from backend import ai as ai_module
from backend.ai import AiChatRequest, parse_ai_response
from backend.main_models import BoardData
from backend.openrouter import OpenRouterError


def test_ai_validation_reaches_openrouter(client, auth_headers) -> None:
    response = client.get("/api/ai/validate", headers=auth_headers)
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["model"] == "openai/gpt-oss-120b:free"
    assert "4" in body["answer"]


def test_ai_chat_requires_auth(client) -> None:
    response = client.post(
        "/api/ai/chat",
        json={"message": "hi", "board": {"columns": [], "cards": {}}, "history": []},
    )
    assert response.status_code == 401


def test_ai_chat_returns_structured_response_from_openrouter(client, auth_headers) -> None:
    board = client.get("/api/board", headers=auth_headers).json()
    response = client.post(
        "/api/ai/chat",
        json={
            "message": "Reply with message exactly 'ok'. Do not change the board.",
            "board": board,
            "history": [],
        },
        headers=auth_headers,
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["message"].lower() == "ok"
    assert body["boardUpdate"] is None


def test_parse_ai_response_rejects_invalid_json() -> None:
    try:
        parse_ai_response("not json")
    except OpenRouterError as exc:
        assert "valid JSON" in str(exc)
    else:
        raise AssertionError("Expected invalid JSON to be rejected")


def test_parse_ai_response_rejects_missing_message() -> None:
    try:
        parse_ai_response('{"boardUpdate": null}')
    except OpenRouterError as exc:
        assert "expected schema" in str(exc)
    else:
        raise AssertionError("Expected invalid schema to be rejected")


def test_parse_ai_response_rejects_invalid_board_update() -> None:
    try:
        parse_ai_response(
            """
            {
              "message": "updated",
              "boardUpdate": {
                "columns": [
                  {"id": "col-1", "title": "Todo", "cardIds": ["missing-card"]}
                ],
                "cards": {}
              }
            }
            """
        )
    except OpenRouterError as exc:
        assert "expected schema" in str(exc)
    else:
        raise AssertionError("Expected invalid boardUpdate to be rejected")


def test_request_structured_ai_response_retries_until_valid_json(monkeypatch) -> None:
    call_count = {"value": 0}

    def fake_call(messages, schema):
        call_count["value"] += 1
        if call_count["value"] < 3:
            return "not json"
        return '{"message": "ok", "boardUpdate": null}'

    monkeypatch.setattr(ai_module, "call_openrouter_messages", fake_call)

    request = AiChatRequest(message="hi", board=BoardData(columns=[], cards={}), history=[])
    response = ai_module.request_structured_ai_response(request)

    assert response.message == "ok"
    assert call_count["value"] == 3


def test_request_structured_ai_response_raises_after_max_attempts(monkeypatch) -> None:
    monkeypatch.setattr(ai_module, "call_openrouter_messages", lambda messages, schema: "not json")

    request = AiChatRequest(message="hi", board=BoardData(columns=[], cards={}), history=[])

    try:
        ai_module.request_structured_ai_response(request)
    except OpenRouterError:
        pass
    else:
        raise AssertionError("Expected OpenRouterError after exhausting retries")
