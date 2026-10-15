import importlib.util
import os
import tempfile
from pathlib import Path

from fastapi.testclient import TestClient


def load_main_module():
    db_path = Path(tempfile.gettempdir()) / f"task_app_test_{os.getpid()}.db"
    if db_path.exists():
        db_path.unlink()

    os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"

    module_path = Path(__file__).resolve().parents[1] / "static,test,k8s" / "main.py"
    spec = importlib.util.spec_from_file_location("task_app_main", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module, db_path


def test_list_tasks_returns_empty_list():
    module, _ = load_main_module()
    client = TestClient(module.app)

    response = client.get("/tasks")

    assert response.status_code == 200
    assert response.json() == []


def test_create_and_update_and_delete_task():
    module, _ = load_main_module()
    client = TestClient(module.app)

    create_response = client.post("/tasks", json={"task": "Write tests"})
    assert create_response.status_code == 201
    created = create_response.json()
    assert created["title"] == "Write tests"
    assert created["completed"] is False

    task_id = created["id"]

    patch_response = client.patch(f"/tasks/{task_id}", json={"completed": True})
    assert patch_response.status_code == 200
    assert patch_response.json()["completed"] is True

    delete_response = client.delete(f"/tasks/{task_id}")
    assert delete_response.status_code == 204

    list_response = client.get("/tasks")
    assert list_response.status_code == 200
    assert list_response.json() == []
