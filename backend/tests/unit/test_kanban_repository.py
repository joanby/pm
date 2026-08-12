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


def test_repository_reorders_cards_within_a_three_card_column(seeded_db) -> None:
    # col-progress starts with card-4, card-5; add a third card so a reorder
    # forces a sibling to shift into a position still held by the card being
    # moved — this is what trips UNIQUE(column_id, position) if the move
    # isn't staged correctly (regression for that bug).
    with db_connection() as connection:
        repository = KanbanRepository(connection)
        repository.create_card(MVP_BOARD_ID, "col-progress", "card-extra", "Extra", "")

    with db_connection() as connection:
        repository = KanbanRepository(connection)
        board = repository.move_card(MVP_BOARD_ID, "card-4", "col-progress", 1)

    progress = next(column for column in board.columns if column.id == "col-progress")
    assert progress.card_ids == ["card-5", "card-4", "card-extra"]


def test_repository_moves_card_into_a_column_with_two_existing_cards(seeded_db) -> None:
    # col-done already has two cards; inserting at position 0 shifts both of
    # them, which previously collided under UNIQUE(column_id, position)
    # depending on row-processing order (regression for that bug).
    with db_connection() as connection:
        repository = KanbanRepository(connection)
        board = repository.move_card(MVP_BOARD_ID, "card-6", "col-done", 0)

    done = next(column for column in board.columns if column.id == "col-done")
    review = next(column for column in board.columns if column.id == "col-review")
    assert done.card_ids == ["card-6", "card-7", "card-8"]
    assert review.card_ids == []
