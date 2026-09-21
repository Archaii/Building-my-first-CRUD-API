"""Storage layer for the Task API.

Every task lives in a SQLite database file called tasks.db instead of in a
Python list, so the data is still there after the server restarts.
"""

import sqlite3
from contextlib import closing, contextmanager
from pathlib import Path

DB_PATH = Path(__file__).parent / "tasks.db"

EXAMPLE_TASKS = [
    ("Test 1", 0),
    ("Test 2", 0),
    ("Test 3", 1),
]


@contextmanager
def get_connection():
    """Open the database file, creating it on the first run.

    Each request gets its own connection, which keeps SQLite happy when
    FastAPI runs endpoints on different threads. Leaving the block commits
    the transaction and closes the connection.
    """
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row

    with closing(connection), connection:
        yield connection


def init_db() -> None:
    """Create the tasks table if it is missing and seed it only when empty."""
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                done INTEGER NOT NULL DEFAULT 0
            )
            """
        )

        count = connection.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]

        if count == 0:
            # One transaction, so the three example tasks are all-or-nothing.
            connection.executemany(
                "INSERT INTO tasks (title, done) VALUES (?, ?)",
                EXAMPLE_TASKS,
            )
