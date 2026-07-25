from fastapi import FastAPI
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