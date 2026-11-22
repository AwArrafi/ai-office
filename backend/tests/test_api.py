import asyncio
import time

import pytest
from fastapi.testclient import TestClient

from app import db, main, ollama


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "test.db"))
    with TestClient(main.app) as c:
        yield c


def fake_generate(text="hasil", delay=0.0, error=None):
    async def gen(model, system, prompt):
        await asyncio.sleep(delay)
        if error:
            raise ollama.OllamaError(error)
        return {"text": ollama.strip_think(text), "input_tokens": 10, "output_tokens": 5}
    return gen


def wait_status(client, task_id, done=("Completed", "Failed", "Cancelled"), timeout=5):
    end = time.time() + timeout
    while time.time() < end:
        task = client.get(f"/tasks/{task_id}").json()
        if task["status"] in done:
            return task
        time.sleep(0.05)
    raise AssertionError(f"task {task_id} stuck at {task['status']}")


def new_task(client, agent_id=2):
    r = client.post("/tasks", json={"title": "Tulis fungsi", "description": "validasi email", "assigned_agent_id": agent_id})
    assert r.status_code == 201, r.text
    return r.json()["id"]


def test_strip_think():
    assert ollama.strip_think("<think>hmm</think>\n jawaban ") == "jawaban"
    assert ollama.strip_think("bocor tanpa tag pembuka</think>jawaban") == "jawaban"
    assert ollama.strip_think("biasa") == "biasa"


def test_seeded_agents(client):
    names = [a["name"] for a in client.get("/agents").json()]
    assert names == ["Manager", "Developer", "QA"]


def test_run_task_success(client, monkeypatch):
    monkeypatch.setattr(ollama, "generate", fake_generate("<think>x</think>kode selesai"))
    tid = new_task(client)
    assert client.post(f"/tasks/{tid}/run").status_code == 202
    task = wait_status(client, tid)
    assert task["status"] == "Completed" and task["completed_at"]
    ex = task["executions"][0]
    assert (ex["status"], ex["output"], ex["input_tokens"], ex["output_tokens"]) == ("Completed", "kode selesai", 10, 5)
    assert ex["model"] == db.DEFAULT_MODEL and ex["estimated_cost"] == 0
    assert client.get("/agents/2").json()["status"] == "Idle"
    events = [a["description"] for a in client.get(f"/activity?task_id={tid}").json()]
    assert "Task 1 -> In Progress" in events and "Task 1 -> Completed" in events


def test_ollama_error_marks_failed(client, monkeypatch):
    monkeypatch.setattr(ollama, "generate", fake_generate(error="Ollama tidak dapat dihubungi"))
    tid = new_task(client)
    client.post(f"/tasks/{tid}/run")
    task = wait_status(client, tid)
    assert task["status"] == "Failed"
    assert task["executions"][0]["error_message"] == "Ollama tidak dapat dihubungi"
    assert client.get("/agents/2").json()["status"] == "Idle"


def test_one_active_task_and_cancel(client, monkeypatch):
    monkeypatch.setattr(ollama, "generate", fake_generate(delay=10))
    t1, t2 = new_task(client), new_task(client, agent_id=3)
    assert client.post(f"/tasks/{t1}/run").status_code == 202
    wait_status(client, t1, done=("In Progress",))
    assert client.get("/agents/2").json()["status"] == "Working"
    assert client.post(f"/tasks/{t2}/run").status_code == 409
    assert client.post(f"/tasks/{t1}/cancel").status_code == 200
    task = wait_status(client, t1)
    assert task["status"] == "Cancelled"
    assert task["executions"][0]["status"] == "Cancelled"
    assert client.post(f"/tasks/{t1}/run").status_code == 409  # cancelled tasks stay cancelled


def test_cancel_pending_task(client):
    tid = new_task(client)
    assert client.post(f"/tasks/{tid}/cancel").json()["status"] == "Cancelled"
    assert client.post(f"/tasks/{tid}/cancel").status_code == 409


def test_inactive_agent_rejected(client):
    with db.conn() as c:
        c.execute("UPDATE agents SET is_active=0 WHERE id=2")
    r = client.post("/tasks", json={"title": "x", "assigned_agent_id": 2})
    assert r.status_code == 400


def test_validation(client):
    assert client.post("/tasks", json={"title": "", "assigned_agent_id": 2}).status_code == 422
    assert client.post("/tasks", json={"title": "x", "assigned_agent_id": 99}).status_code == 404
    assert client.get("/tasks/99").status_code == 404


def test_restart_marks_interrupted_task_failed(client, tmp_path):
    tid = new_task(client)
    with db.conn() as c:
        db.set_task_status(c, tid, "In Progress", agent_id=2)
        db.set_agent_status(c, 2, "Working")
    db.init_db()
    assert client.get(f"/tasks/{tid}").json()["status"] == "Failed"
    assert client.get("/agents/2").json()["status"] == "Idle"
