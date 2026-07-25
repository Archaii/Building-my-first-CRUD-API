# Task CRUD API

A small FastAPI project for creating, reading, updating, and deleting tasks. Tasks are stored in memory, so they reset to the three example tasks whenever the server restarts.

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

Open the API at <http://127.0.0.1:8000> or its interactive Swagger documentation at <http://127.0.0.1:8000/docs>.

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

## Swagger UI

![Swagger UI showing all Task API endpoints](docs/swagger-ui-endpoints-overview.png)
