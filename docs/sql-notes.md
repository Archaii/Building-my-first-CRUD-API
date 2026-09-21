# SQL notes (Stage 4)

Queries run by hand against `tasks.db`, either in the "Execute SQL" tab of
DB Browser for SQLite or with `sqlite3 tasks.db`. The API and DB Browser read
the same file, so a change made here shows up in `GET /tasks` right away, with
no server restart and no syncing step.

| Query | What it returns |
| --- | --- |
| `SELECT * FROM tasks;` | Every row in the table: id, title, and done as 0 or 1. |
| `SELECT * FROM tasks WHERE done = 1;` | Only the completed tasks — on a freshly seeded database that is the single row `Test 3`. |
| `SELECT COUNT(*) FROM tasks;` | One number: how many tasks exist, for example `3`. |
| `UPDATE tasks SET done = 1;` | Marks every task completed. There is no `WHERE`, so it touches all rows. |
| `DELETE FROM tasks WHERE done = 1;` | Removes every completed task and reports how many rows it deleted. |

Careful with the last two: a missing `WHERE` clause applies the change to the
whole table. Run the destructive ones on a copy of `tasks.db` first if you want
to keep your data.

## What I saw

`SELECT * FROM tasks WHERE done = 1;` returned one row, `(3, 'Test 3', 1)`,
because `Test 3` is the only seeded task with `done` set to 1.
