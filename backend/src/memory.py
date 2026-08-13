import sqlite3
import json
from datetime import datetime, timezone
from pathlib import Path


DB_PATH = Path(__file__).parent / "memory.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_database():
    conn = get_connection()

    # Existing user memory table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            language_preference TEXT,
            facts TEXT,
            last_interaction TEXT
        )
    """)

    # Day 8: Call tracking table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS calls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            started_at TEXT NOT NULL,
            ended_at TEXT,
            channel TEXT DEFAULT 'browser',
            outcome TEXT DEFAULT 'failed'
        )
    """)

    conn.commit()
    conn.close()


# =========================
# USER MEMORY FUNCTIONS
# =========================

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


# =========================
# DAY 8 CALL TRACKING
# =========================

def start_call(channel: str = "browser"):
    """
    Creates a new call record and returns its ID.
    """
    conn = get_connection()

    started_at = datetime.now(timezone.utc).isoformat()

    cursor = conn.execute(
        """
        INSERT INTO calls (
            started_at,
            channel,
            outcome
        )
        VALUES (?, ?, ?)
        """,
        (
            started_at,
            channel,
            "failed",
        ),
    )

    call_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return call_id


def end_call(call_id: int, outcome: str):
    """
    Updates a call when the conversation ends.

    outcome must be:
    - success
    - failed
    """

    if outcome not in ("success", "failed"):
        outcome = "failed"

    conn = get_connection()

    ended_at = datetime.now(timezone.utc).isoformat()

    conn.execute(
        """
        UPDATE calls
        SET ended_at = ?,
            outcome = ?
        WHERE id = ?
        """,
        (
            ended_at,
            outcome,
            call_id,
        ),
    )

    conn.commit()
    conn.close()


def get_call_stats():
    """
    Returns dashboard statistics.
    """

    conn = get_connection()

    total = conn.execute(
        "SELECT COUNT(*) FROM calls"
    ).fetchone()[0]

    successful = conn.execute(
        "SELECT COUNT(*) FROM calls WHERE outcome = 'success'"
    ).fetchone()[0]

    failed = conn.execute(
        "SELECT COUNT(*) FROM calls WHERE outcome = 'failed'"
    ).fetchone()[0]

    conn.close()

    return {
        "total": total,
        "successful": successful,
        "failed": failed,
    }


def get_call_history():
    """
    Returns basic call history without sensitive information.
    """

    conn = get_connection()

    cursor = conn.execute(
        """
        SELECT id, started_at, ended_at, channel, outcome
        FROM calls
        ORDER BY id DESC
        """
    )

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "id": row[0],
            "started_at": row[1],
            "ended_at": row[2],
            "channel": row[3],
            "outcome": row[4],
        }
        for row in rows
    ]