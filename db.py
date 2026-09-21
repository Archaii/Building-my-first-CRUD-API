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


def row_to_task(row: sqlite3.Row) -> dict:
    """Turn one database row into the JSON shape the API has always returned."""
    return {
        "id": row["id"],
        "title": row["title"],
        "done": bool(row["done"]),
    }


def list_tasks() -> list[dict]:
    """Return every task, oldest first."""
    with get_connection() as connection:
        rows = connection.execute("SELECT * FROM tasks").fetchall()

    return [row_to_task(row) for row in rows]


def get_task(task_id: int) -> dict | None:
    """Return one task by id, or None when no row matches."""
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()

    return row_to_task(row) if row else None


def create_task(title: str) -> dict:
    """Insert one task and return it with the id the database handed out."""
    with get_connection() as connection:
        cursor = connection.execute(
            "INSERT INTO tasks (title, done) VALUES (?, ?)",
            (title, 0),
        )
        new_id = cursor.lastrowid

    return {"id": new_id, "title": title, "done": False}


def update_task(task_id: int, title: str, done: bool) -> dict | None:
    """Overwrite one task's title and done value, or return None if it is gone."""
    with get_connection() as connection:
        cursor = connection.execute(
            "UPDATE tasks SET title = ?, done = ? WHERE id = ?",
            (title, int(done), task_id),
        )

        if cursor.rowcount == 0:
            return None

    return {"id": task_id, "title": title, "done": done}


def delete_task(task_id: int) -> bool:
    """Delete one task and report whether a row was actually removed."""
    with get_connection() as connection:
        cursor = connection.execute(
            "DELETE FROM tasks WHERE id = ?",
            (task_id,),
        )

        return cursor.rowcount > 0
