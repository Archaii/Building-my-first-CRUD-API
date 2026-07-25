from fastapi import FastAPI, Body, Response
from fastapi.responses import JSONResponse

app = FastAPI()

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

@app.get("/")
async def root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/tasks")
def get_tasks():
    return tasks

@app.get("/tasks/{id}")
def get_task(id: int):
    for task in tasks:
        if task["id"] == id:
            return task

    return JSONResponse(
        status_code=404,
        content={"error": f"Task {id} not found"},
    )

@app.post("/tasks", status_code=201)
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

    next_id = max(
        (task["id"] for task in tasks),
        default=0,
    ) + 1

    new_task = {
        "id": next_id,
        "title": payload["title"].strip(),
        "done": False,
    }

    tasks.append(new_task)
    return new_task