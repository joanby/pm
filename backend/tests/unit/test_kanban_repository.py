from backend.app.db.connection import db_connection
from backend.app.kanban.repository import KanbanRepository
from backend.app.kanban.seed import MVP_BOARD_ID


def test_repository_loads_seeded_board(seeded_db) -> None:
    with db_connection() as connection:
        repository = KanbanRepository(connection)
        board = repository.get_board(MVP_BOARD_ID)

    assert len(board.columns) == 5
    assert len(board.cards) == 8
    assert board.columns[0].id == "col-backlog"


def test_repository_persists_column_rename(seeded_db) -> None:
    with db_connection() as connection:
        repository = KanbanRepository(connection)
        repository.update_column_title(MVP_BOARD_ID, "col-backlog", "Ideas")

    with db_connection() as connection:
        repository = KanbanRepository(connection)
        board = repository.get_board(MVP_BOARD_ID)

    assert board.columns[0].title == "Ideas"
