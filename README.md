# Task CRUD API

A small FastAPI project for creating, reading, updating, and deleting tasks.
Tasks are stored in a SQLite database file called `tasks.db`, so they are still
there after the server restarts.

## Install and run

Requires Python 3.12 or newer.

Install FastAPI once:

```powershell
python -m pip install "fastapi[standard]"
```

Then start the API with this command:

```powershell
python -m fastapi dev main.py --app app
```

Nothing else to set up. SQLite ships with Python, and the first start creates
`tasks.db`, creates the `tasks` table, and seeds the three example tasks.

Open the API at <http://127.0.0.1:8000> or its interactive Swagger documentation
at <http://127.0.0.1:8000/docs>.

## Why SQLite

- **One file, zero setup.** The whole database is `tasks.db` next to the code.
  There is no server to install, start, or configure, and no credentials.
- **It ships with Python.** `sqlite3` is in the standard library, so a clone of
  this repo needs no extra database dependency.
- **The data survives restarts.** An in-memory list is gone the moment the
  process stops; rows written to `tasks.db` stay on disk.

## Where the database lives

`tasks.db` sits in the project root and is created automatically on the first
run. It is listed in `.gitignore`, so it is never committed and every clone
starts with a fresh database holding the same three example tasks. Delete the
file and restart the server to get back to that clean state.

The `tasks` table has three columns:

| Column | Type | Notes |
| --- | --- | --- |
| `id` | INTEGER | Primary key. SQLite assigns it. |
| `title` | TEXT | Required, never empty. |
| `done` | INTEGER | Stored as `0` or `1`, returned to clients as `false` or `true`. |

## How it is put together

- [`main.py`](main.py) holds the routes, the validation, and the status codes.
  The endpoints are exactly the ones from the in-memory version.
- [`db.py`](db.py) holds the storage layer: opening the database, creating the
  table, seeding it, and the SELECT, INSERT, UPDATE, and DELETE queries.
- Every query that takes user input uses `?` placeholders and passes the values
  separately, so nothing from a request is ever glued into an SQL string.

## Endpoints

| Method | Endpoint | Description | Success |
| --- | --- | --- | --- |
| GET | `/` | Show the API name, version, and task endpoint | `200` |
| GET | `/health` | Check whether the API is running | `200` |
| GET | `/tasks` | List all tasks | `200` |
| GET | `/tasks/{id}` | Get one task by ID | `200` |
| POST | `/tasks` | Create a task from a JSON `title` | `201` |
| PUT | `/tasks/{task_id}` | Update a task's `title` and/or `done` value | `200` |
| DELETE | `/tasks/{task_id}` | Delete a task by ID | `204` |

Missing tasks return `404`. Invalid POST or PUT bodies return `400`.

## Example

Request:

```powershell
curl.exe -i http://127.0.0.1:8000/tasks/1
```

Output:

```text
HTTP/1.1 200 OK
server: uvicorn
content-length: 38
content-type: application/json

{"id":1,"title":"Test 1","done":false}
```

## Persistence check

```powershell
curl.exe -i -X POST http://127.0.0.1:8000/tasks -H "Content-Type: application/json" -d "{\"title\":\"Buy milk\"}"
```

Stop the server, start it again with the same command as above, then run:

```powershell
curl.exe -i http://127.0.0.1:8000/tasks
```

`Buy milk` is still in the list, because it is a row in `tasks.db` and not an
entry in a Python list.

## SQL by hand

`tasks.db` opens directly in [DB Browser for SQLite](https://sqlitebrowser.org/).
Its rows are the same rows the API serves — there is one file and no syncing
step, so a change made in DB Browser shows up in `GET /tasks` immediately.

One query run in its "Execute SQL" tab:

```sql
SELECT * FROM tasks WHERE done = 1;
```

It returned one row, `3 | Test 3 | 1`, because `Test 3` is the only seeded task
whose `done` value is `1`.

More queries, and what each one returned, are in [docs/sql-notes.md](docs/sql-notes.md).

![The tasks table open in DB Browser for SQLite](docs/db-browser-tasks-table.png)

## Swagger UI

![Swagger UI showing all Task API endpoints](docs/swagger-ui-endpoints-overview.png)

## Postgres in Docker

The next version of this project stores its tasks in PostgreSQL instead of
SQLite. Postgres is not installed on the machine — it runs as a container, so
the same database version comes up on any computer with Docker.

Start it with:

```powershell
docker run --name taskdb -e POSTGRES_PASSWORD=dev -e POSTGRES_DB=tasks -p 5433:5432 -v taskdata:/var/lib/postgresql -d postgres:18
```

That command downloads the official `postgres:18` image, names the container
`taskdb`, creates a database called `tasks`, and publishes the container's port
5432 on the host as 5433, so the API can reach it at `localhost:5433`.

The host port is 5433 rather than 5432 because this machine already runs a
locally installed PostgreSQL 18 service on 5432. Windows lets Docker bind the
same port without complaining, but the installed service answers first, so
every connection failed with `password authentication failed for user
"postgres"` — the app was reaching the wrong database. Publishing on 5433
leaves the installed service alone and removes the ambiguity.

The `-v taskdata:/var/lib/postgresql` part is the important one. A container
loses everything it wrote the moment it is removed, so the rows are kept in a
named volume that lives outside the container instead. Postgres 18 expects that
mount at `/var/lib/postgresql`, not at `/var/lib/postgresql/data` as earlier
versions did.

Check that it is running and open a SQL prompt inside it:

```powershell
docker ps
docker exec -it taskdb psql -U postgres -d tasks
```

At the prompt, `\dt` lists the tables and `\q` exits. There are no tables yet —
the API creates the `tasks` table itself on its first start.

## Connecting the API to Postgres

The connection details are not in the code. They live in a `.env` file that Git
ignores, so the database password is never committed:

```
DATABASE_URL=postgresql://postgres:dev@localhost:5433/tasks
```

`.env.example` is committed in its place. It lists the same key with a
placeholder value, so anyone cloning this repository knows what to set without
ever seeing a real password. Copy it and fill it in:

```powershell
copy .env.example .env
```

Install the dependencies, including the `psycopg` driver that talks to Postgres:

```powershell
python -m pip install -r requirements.txt
```

On its first start the API creates the `tasks` table if it is missing and
inserts the three example tasks only when the table is empty. Starting the API
again finds three rows already there and inserts nothing, so restarts never
duplicate the examples.
