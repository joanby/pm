def test_list_boards_returns_seeded_board(client, auth_headers) -> None:
    response = client.get("/api/boards", headers=auth_headers)
    assert response.status_code == 200
    boards = response.json()
    assert len(boards) == 1
    assert boards[0]["name"] == "Tablero principal"


def test_get_board_returns_full_content(client, auth_headers, default_board_id) -> None:
    response = client.get(f"/api/boards/{default_board_id}", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert len(body["columns"]) == 5
    assert "cards" in body


def test_create_board_adds_to_list(client, auth_headers) -> None:
    create_response = client.post(
        "/api/boards", json={"name": "Tablero de marketing"}, headers=auth_headers
    )
    assert create_response.status_code == 201
    created = create_response.json()
    assert created["name"] == "Tablero de marketing"
    assert created["cards"] == {}

    boards = client.get("/api/boards", headers=auth_headers).json()
    assert len(boards) == 2


def test_update_board_data_persists(client, auth_headers, default_board_id) -> None:
    board = client.get(f"/api/boards/{default_board_id}", headers=auth_headers).json()
    board["columns"][0]["title"] = "Backlog Updated"
    update_response = client.put(
        f"/api/boards/{default_board_id}",
        json={"columns": board["columns"], "cards": board["cards"]},
        headers=auth_headers,
    )
    assert update_response.status_code == 200

    read_back = client.get(f"/api/boards/{default_board_id}", headers=auth_headers).json()
    assert read_back["columns"][0]["title"] == "Backlog Updated"


def test_rename_board(client, auth_headers, default_board_id) -> None:
    response = client.patch(
        f"/api/boards/{default_board_id}", json={"name": "Renombrado"}, headers=auth_headers
    )
    assert response.status_code == 200

    boards = client.get("/api/boards", headers=auth_headers).json()
    assert boards[0]["name"] == "Renombrado"


def test_delete_board_removes_it(client, auth_headers) -> None:
    created = client.post(
        "/api/boards", json={"name": "Tablero temporal"}, headers=auth_headers
    ).json()
    delete_response = client.delete(f"/api/boards/{created['id']}", headers=auth_headers)
    assert delete_response.status_code == 200

    boards = client.get("/api/boards", headers=auth_headers).json()
    assert all(board["id"] != created["id"] for board in boards)


def test_board_endpoints_require_auth(client, default_board_id) -> None:
    assert client.get("/api/boards").status_code == 401
    assert client.get(f"/api/boards/{default_board_id}").status_code == 401


def test_user_cannot_access_another_users_board(client, auth_headers, member_headers, default_board_id) -> None:
    response = client.get(f"/api/boards/{default_board_id}", headers=member_headers)
    assert response.status_code == 404


def test_get_missing_board_returns_404(client, auth_headers) -> None:
    response = client.get("/api/boards/does-not-exist", headers=auth_headers)
    assert response.status_code == 404
