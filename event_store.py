import json
import sqlite3

DB_PATH = "events.db"


def init_db():
    connection = sqlite3.connect(DB_PATH)

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS webhook_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            delivery_id TEXT,
            event_name TEXT NOT NULL,
            action TEXT,
            payload TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    columns = {
        row[1]
        for row in connection.execute(
            "PRAGMA table_info(webhook_events)"
        ).fetchall()
    }

    if "delivery_id" not in columns:
        connection.execute(
            "ALTER TABLE webhook_events ADD COLUMN delivery_id TEXT"
        )

    if "created_at" not in columns:
        connection.execute(
            "ALTER TABLE webhook_events ADD COLUMN created_at TEXT"
        )

    connection.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS
        idx_webhook_events_delivery_id
        ON webhook_events(delivery_id)
        WHERE delivery_id IS NOT NULL
        """
    )

    connection.commit()
    connection.close()


def save_event(delivery_id, event_name, action, payload):
    connection = sqlite3.connect(DB_PATH)

    cursor = connection.execute(
        """
        INSERT OR IGNORE INTO webhook_events
        (delivery_id, event_name, action, payload, created_at)
        VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        """,
        (
            delivery_id,
            event_name,
            action,
            json.dumps(payload),
        ),
    )

    connection.commit()
    inserted = cursor.rowcount == 1
    connection.close()

    return inserted


def get_events():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row

    rows = connection.execute(
        """
        SELECT id, delivery_id, event_name, action, payload, created_at
        FROM webhook_events
        ORDER BY id DESC
        """
    ).fetchall()

    connection.close()

    return [dict(row) for row in rows]


init_db()
