import os
from contextlib import contextmanager

import psycopg
from dotenv import load_dotenv
from psycopg.rows import dict_row

# Read .env into the environment once, when this module is first imported.
load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]

EXAMPLE_TASKS = [
    ("Test 1", False),
    ("Test 2", False),
    ("Test 3", True),
]


@contextmanager
def get_connection():
    """Open a connection to Postgres using the URL from .env.

    Each request gets its own connection. Leaving the block commits the
    transaction and closes the connection; an exception rolls it back instead.
    """
    with psycopg.connect(DATABASE_URL, row_factory=dict_row) as connection:
        yield connection


def init_db() -> None:
    """Create the tasks table if it is missing and seed it only when empty."""
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                done BOOLEAN NOT NULL DEFAULT FALSE
            )
            """
        )

        count = connection.execute("SELECT COUNT(*) AS total FROM tasks").fetchone()["total"]

        if count == 0:
            # One transaction, so the three example tasks are all-or-nothing.
            connection.cursor().executemany(
                "INSERT INTO tasks (title, done) VALUES (%s, %s)",
                EXAMPLE_TASKS,
            )


def row_to_task(row: dict) -> dict:
    """Turn one database row into the JSON shape the API has always returned."""
    return {
        "id": row["id"],
        "title": row["title"],
        "done": row["done"],
    }


def list_tasks() -> list[dict]:
    """Return every task, oldest first.

    Postgres has no natural row order. An UPDATE writes a new copy of the row,
    so without ORDER BY an edited task would jump to the end of the list.
    """
    with get_connection() as connection:
        rows = connection.execute("SELECT * FROM tasks ORDER BY id").fetchall()

    return [row_to_task(row) for row in rows]


def get_task(task_id: int) -> dict | None:
    """Return one task by id, or None when no row matches."""
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM tasks WHERE id = %s",
            (task_id,),
        ).fetchone()

    return row_to_task(row) if row else None


def create_task(title: str) -> dict:
    """Insert one task and return the row exactly as Postgres stored it."""
    with get_connection() as connection:
        row = connection.execute(
            "INSERT INTO tasks (title, done) VALUES (%s, %s) RETURNING *",
            (title, False),
        ).fetchone()

    return row_to_task(row)


def update_task(task_id: int, title: str, done: bool) -> dict | None:
    """Overwrite one task's title and done value, or return None if it is gone."""
    with get_connection() as connection:
        row = connection.execute(
            "UPDATE tasks SET title = %s, done = %s WHERE id = %s RETURNING *",
            (title, done, task_id),
        ).fetchone()

    return row_to_task(row) if row else None


def delete_task(task_id: int) -> bool:
    """Delete one task and report whether a row was actually removed."""
    with get_connection() as connection:
        cursor = connection.execute(
            "DELETE FROM tasks WHERE id = %s",
            (task_id,),
        )

        return cursor.rowcount > 0
