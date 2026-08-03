from __future__ import annotations

from datetime import UTC, datetime

from backend.app.db.connection import db_connection

MVP_USER_ID = "user-demo"
MVP_USERNAME = "user"
MVP_PASSWORD = "password"
MVP_BOARD_ID = "board-demo"

DEMO_COLUMNS = [
    {"id": "col-backlog", "title": "Backlog", "position": 0, "card_ids": ["card-1", "card-2"]},
    {"id": "col-discovery", "title": "Discovery", "position": 1, "card_ids": ["card-3"]},
    {"id": "col-progress", "title": "In Progress", "position": 2, "card_ids": ["card-4", "card-5"]},
    {"id": "col-review", "title": "Review", "position": 3, "card_ids": ["card-6"]},
    {"id": "col-done", "title": "Done", "position": 4, "card_ids": ["card-7", "card-8"]},
]

DEMO_CARDS = {
    "card-1": {
        "title": "Align roadmap themes",
        "details": "Draft quarterly themes with impact statements and metrics.",
    },
    "card-2": {
        "title": "Gather customer signals",
        "details": "Review support tags, sales notes, and churn feedback.",
    },
    "card-3": {
        "title": "Prototype analytics view",
        "details": "Sketch initial dashboard layout and key drill-downs.",
    },
    "card-4": {
        "title": "Refine status language",
        "details": "Standardize column labels and tone across the board.",
    },
    "card-5": {
        "title": "Design card layout",
        "details": "Add hierarchy and spacing for scanning dense lists.",
    },
    "card-6": {
        "title": "QA micro-interactions",
        "details": "Verify hover, focus, and loading states.",
    },
    "card-7": {
        "title": "Ship marketing page",
        "details": "Final copy approved and asset pack delivered.",
    },
    "card-8": {
        "title": "Close onboarding sprint",
        "details": "Document release notes and share internally.",
    },
}


def _now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def seed_demo_data() -> None:
    with db_connection() as connection:
        existing = connection.execute(
            "SELECT id FROM users WHERE username = ?", (MVP_USERNAME,)
        ).fetchone()
        if existing:
            return

        now = _now_iso()
        connection.execute(
            "INSERT INTO users (id, username, password, created_at) VALUES (?, ?, ?, ?)",
            (MVP_USER_ID, MVP_USERNAME, MVP_PASSWORD, now),
        )
        connection.execute(
            "INSERT INTO boards (id, user_id, title, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            (MVP_BOARD_ID, MVP_USER_ID, "Kanban Studio", now, now),
        )

        for column in DEMO_COLUMNS:
            connection.execute(
                """
                INSERT INTO columns (id, board_id, title, position, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (column["id"], MVP_BOARD_ID, column["title"], column["position"], now, now),
            )
            for position, card_id in enumerate(column["card_ids"]):
                card = DEMO_CARDS[card_id]
                connection.execute(
                    """
                    INSERT INTO cards (id, column_id, title, details, position, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        card_id,
                        column["id"],
                        card["title"],
                        card["details"],
                        position,
                        now,
                        now,
                    ),
                )
        connection.commit()
