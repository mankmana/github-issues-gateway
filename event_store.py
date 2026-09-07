import json
import sqlite3

DB_PATH = "events.db"


def init_db():
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS webhook_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_name TEXT NOT NULL,
                action TEXT,
                payload TEXT NOT NULL
            )
            """
        )


def save_event(event_name: str, action: str | None, payload: dict):
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute(
            """
            INSERT INTO webhook_events (event_name, action, payload)
            VALUES (?, ?, ?)
            """,
            (event_name, action, json.dumps(payload)),
        )


def get_events():
    with sqlite3.connect(DB_PATH) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute(
            "SELECT * FROM webhook_events ORDER BY id DESC"
        ).fetchall()

    return [dict(row) for row in rows]


init_db()
