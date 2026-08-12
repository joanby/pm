from backend.tests.conftest import AUTH_HEADERS


def test_get_board_requires_auth_header(client) -> None:
    response = client.get("/api/board")
    assert response.status_code == 401


def test_get_board_returns_seeded_demo(client) -> None:
    response = client.get("/api/board", headers=AUTH_HEADERS)
    assert response.status_code == 200
    payload = response.json()
    assert len(payload["columns"]) == 5
    assert "card-1" in payload["cards"]


def test_rename_column_persists(client) -> None:
    response = client.patch(
        "/api/columns/col-backlog",
        headers=AUTH_HEADERS,
        json={"title": "Ideas"},
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Ideas"

    board = client.get("/api/board", headers=AUTH_HEADERS).json()
    assert board["columns"][0]["title"] == "Ideas"


def test_create_update_delete_card_flow(client) -> None:
    create_response = client.post(
        "/api/columns/col-backlog/cards",
        headers=AUTH_HEADERS,
        json={"id": "card-test", "title": "API card", "details": "Created in test"},
    )
    assert create_response.status_code == 201
    assert create_response.json()["title"] == "API card"

    update_response = client.patch(
        "/api/cards/card-test",
        headers=AUTH_HEADERS,
        json={"title": "Updated card"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Updated card"

    delete_response = client.delete("/api/cards/card-test", headers=AUTH_HEADERS)
    assert delete_response.status_code == 204

    board = client.get("/api/board", headers=AUTH_HEADERS).json()
    assert "card-test" not in board["cards"]


def test_move_card_updates_board(client) -> None:
    response = client.put(
        "/api/cards/card-1/move",
        headers=AUTH_HEADERS,
        json={"column_id": "col-review", "position": 0},
    )
    assert response.status_code == 200
    payload = response.json()
    review_column = next(column for column in payload["columns"] if column["id"] == "col-review")
    assert review_column["cardIds"][0] == "card-1"


def test_replace_board_syncs_full_state(client) -> None:
    board = client.get("/api/board", headers=AUTH_HEADERS).json()
    board["columns"][0]["title"] = "Synced"
    board["cards"]["card-1"]["title"] = "Synced card"

    response = client.put("/api/board", headers=AUTH_HEADERS, json=board)
    assert response.status_code == 200
    assert response.json()["columns"][0]["title"] == "Synced"
    assert response.json()["cards"]["card-1"]["title"] == "Synced card"

    reloaded = client.get("/api/board", headers=AUTH_HEADERS).json()
    assert reloaded["columns"][0]["title"] == "Synced"
