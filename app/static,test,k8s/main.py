import importlib.util
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session


if __package__:
    from .database import Base, engine, get_db
    from .models import Task
    from .schema import TaskCreate, TaskResponse, TaskUpdate
else:
    MODULE_DIR = Path(__file__).resolve().parent
    if str(MODULE_DIR) not in sys.path:
        sys.path.insert(0, str(MODULE_DIR))

    database_spec = importlib.util.spec_from_file_location("database", MODULE_DIR / "database.py")
    database_module = importlib.util.module_from_spec(database_spec)
    sys.modules["database"] = database_module
    database_spec.loader.exec_module(database_module)

    models_spec = importlib.util.spec_from_file_location("models", MODULE_DIR / "models.py")
    models_module = importlib.util.module_from_spec(models_spec)
    sys.modules["models"] = models_module
    models_spec.loader.exec_module(models_module)

    schema_spec = importlib.util.spec_from_file_location("schema", MODULE_DIR / "schema.py")
    schema_module = importlib.util.module_from_spec(schema_spec)
    schema_spec.loader.exec_module(schema_module)

    Base = database_module.Base
    engine = database_module.engine
    get_db = database_module.get_db
    Task = models_module.Task
    TaskCreate = schema_module.TaskCreate
    TaskResponse = schema_module.TaskResponse
    TaskUpdate = schema_module.TaskUpdate


BASE_DIR = Path(__file__).resolve().parent


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


Base.metadata.create_all(bind=engine)
app = FastAPI(title="Task Manager", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=str(BASE_DIR)), name="static")


@app.get("/")
def serve_index() -> FileResponse:
    return FileResponse(BASE_DIR / "index.html")


@app.get("/tasks", response_model=list[TaskResponse])
def list_tasks(db: Session = Depends(get_db)):
    return db.query(Task).order_by(Task.id.desc()).all()


@app.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    db_task = Task(title=task.task, completed=False)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


@app.patch("/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task: TaskUpdate, db: Session = Depends(get_db)):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if db_task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    db_task.completed = task.completed
    db.commit()
    db.refresh(db_task)
    return db_task


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if db_task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    db.delete(db_task)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)