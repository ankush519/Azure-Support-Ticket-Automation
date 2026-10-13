import sqlite3
from pathlib import Path
import os

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "tickets.db"

DB_PATH = Path(
    os.getenv("DATABASE_PATH", str(DEFAULT_DB_PATH))
)

DB_PATH.parent.mkdir(parents=True, exist_ok=True)

def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                ticket_id INTEGER PRIMARY KEY,
                message TEXT NOT NULL,
                category TEXT NOT NULL,
                priority TEXT NOT NULL,
                assigned_team TEXT NOT NULL,
                summary TEXT NOT NULL,
                draft_response TEXT NOT NULL,
                status TEXT NOT NULL
            )
        """)
        columns = {
            row[1]
            for row in connection.execute(
                "PRAGMA table_info(tickets)"
            ).fetchall()
        }

        if "confidence" not in columns:
            connection.execute(
                "ALTER TABLE tickets ADD COLUMN confidence REAL"
            )

        if "review_required" not in columns:
            connection.execute(
                "ALTER TABLE tickets ADD COLUMN review_required INTEGER NOT NULL DEFAULT 0"
            )


def save_ticket(ticket, result):
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO tickets (
                ticket_id, message, category, priority,
                assigned_team, summary, draft_response, status, confidence, review_required
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                ticket.ticket_id,
                ticket.message,
                result["category"],
                result["priority"],
                result["assigned_team"],
                result["summary"],
                result["draft_response"],
                result["status"],
                result["confidence"],
                int(result["review_required"])
            ),
        )


def get_ticket(ticket_id):
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM tickets WHERE ticket_id = ?",
            (ticket_id,),
        ).fetchone()

    return dict(row) if row else None


def update_ticket_status(ticket_id: int, status: str) -> bool:
    with get_connection() as connection:
        cursor = connection.execute(
            """
            UPDATE tickets
            SET status = ?
            WHERE ticket_id = ?
              AND status = 'Pending Approval'
            """,
            (status, ticket_id),
        )

        return cursor.rowcount == 1