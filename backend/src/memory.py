import sqlite3
import json
from datetime import datetime, timezone
from pathlib import Path


DB_PATH = Path(__file__).parent / "memory.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_database():
    conn = get_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            language_preference TEXT,
            facts TEXT,
            last_interaction TEXT
        )
    """)

    conn.commit()
    conn.close()


def get_user(user_id: str):
    conn = get_connection()

    cursor = conn.execute(
        """
        SELECT user_id, name, language_preference, facts, last_interaction
        FROM users
        WHERE user_id = ?
        """,
        (user_id,),
    )

    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "user_id": row[0],
        "name": row[1],
        "language_preference": row[2],
        "facts": json.loads(row[3] or "{}"),
        "last_interaction": row[4],
    }


def save_user(
    user_id: str,
    name: str,
    language_preference: str,
    facts: dict,
):
    conn = get_connection()

    now = datetime.now(timezone.utc).isoformat()

    conn.execute(
        """
        INSERT INTO users (
            user_id,
            name,
            language_preference,
            facts,
            last_interaction
        )
        VALUES (?, ?, ?, ?, ?)

        ON CONFLICT(user_id)
        DO UPDATE SET
            name = excluded.name,
            language_preference = excluded.language_preference,
            facts = excluded.facts,
            last_interaction = excluded.last_interaction
        """,
        (
            user_id,
            name,
            language_preference,
            json.dumps(facts),
            now,
        ),
    )

    conn.commit()
    conn.close()