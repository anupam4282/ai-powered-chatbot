import os
import sqlite3
from datetime import datetime, timezone

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "chatbot.db")

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection

def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender TEXT NOT NULL CHECK(sender IN ('user', 'bot')),
                message TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        conn.commit()

def save_message(sender, message):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO messages (sender, message, created_at) VALUES (?, ?, ?)",
            (sender, message, datetime.now(timezone.utc).isoformat())
        )
        conn.commit()

def get_recent_messages(limit=50):
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT sender, message, created_at FROM messages "
            "ORDER BY id DESC LIMIT ?",
            (limit,)
        ).fetchall()
    return [dict(row) for row in reversed(rows)]

def clear_messages():
    with get_connection() as conn:
        conn.execute("DELETE FROM messages")
        conn.commit()
