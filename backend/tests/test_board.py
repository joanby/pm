def test_board_endpoints_initialize_and_read(client, auth_headers) -> None:
    response = client.get("/api/board", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert "columns" in body
    assert "cards" in body
    assert len(body["columns"]) == 5


def test_board_update_endpoint(client, auth_headers) -> None:
    board = client.get("/api/board", headers=auth_headers).json()
    board["columns"][0]["title"] = "Backlog Updated"
    update_response = client.post("/api/board", json=board, headers=auth_headers)
    assert update_response.status_code == 200
    assert update_response.json()["status"] == "ok"

    read_back = client.get("/api/board", headers=auth_headers).json()
    assert read_back["columns"][0]["title"] == "Backlog Updated"
