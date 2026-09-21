from contextlib import asynccontextmanager

from fastapi import FastAPI, Body, Response
from fastapi.responses import JSONResponse

from db import create_task as insert_task, get_task, init_db, list_tasks


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create tasks.db, its table, and the example tasks before serving."""
    init_db()
    yield


app = FastAPI(lifespan=lifespan)

tasks = [
        {
        "id": 1,
        "title": "Test 1",
        "done": False,
    },
    {
        "id": 2,
        "title": "Test 2",
        "done": False,
    },
    {
        "id": 3,
        "title": "Test 3",
        "done": True,
    },
]

@app.get("/", description="Returns the API name, version, and available endpoints")
async def root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}

@app.get("/health", description="Returns the health status of the API")
def health():
    return {"status": "ok"}

@app.get("/tasks", description="Returns the list of tasks")
def get_tasks():
    return list_tasks()

@app.get("/tasks/{id}", description="Returns a specific task by ID")
def read_task(id: int):
    task = get_task(id)

    if task is None:
        return JSONResponse(
            status_code=404,
            content={"error": f"Task {id} not found"},
        )

    return task

@app.post("/tasks", status_code=201, description="Creates a new task")
def create_task(payload: dict | None = Body(default=None)):
    if (
        not payload
        or not isinstance(payload.get("title"), str)
        or not payload["title"].strip()
    ):
        return JSONResponse(
            status_code=400,
            content={"error": "Title is required"},
        )

    return insert_task(payload["title"].strip())

@app.put("/tasks/{task_id}", description="Updates an existing task")
def update_task(
    task_id: int,
    payload: dict | None = Body(default=None),
):
    selected_task = None

    for task in tasks:
        if task["id"] == task_id:
            selected_task = task
            break

    if selected_task is None:
        return JSONResponse(
            status_code=404,
            content={"error": f"Task {task_id} not found"},
        )

    if not payload or not any(
        field in payload for field in ("title", "done")
    ):
        return JSONResponse(
            status_code=400,
            content={"error": "Provide title or done"},
        )

    if "title" in payload:
        if (
            not isinstance(payload["title"], str)
            or not payload["title"].strip()
        ):
            return JSONResponse(
                status_code=400,
                content={"error": "Title cannot be empty"},
            )

        selected_task["title"] = payload["title"].strip()

    if "done" in payload:
        if not isinstance(payload["done"], bool):
            return JSONResponse(
                status_code=400,
                content={"error": "Done must be true or false"},
            )

        selected_task["done"] = payload["done"]

    return selected_task

@app.delete("/tasks/{task_id}", status_code=204, description="Deletes a task")
def delete_task(task_id: int):
    for index, task in enumerate(tasks):
        if task["id"] == task_id:
            tasks.pop(index)
            return Response(status_code=204)

    return JSONResponse(
        status_code=404,
        content={"error": f"Task {task_id} not found"},
    )