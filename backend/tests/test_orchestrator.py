import asyncio
import json
import time

import pytest

from app import ollama, orchestrator

PLAN = json.dumps({"tasks": [{"title": "Fungsi email", "description": "regex"}, {"title": "Dokumentasi", "description": "README"}]})
CLEAN = json.dumps({"summary": "oke", "issues": []})
ISSUE = json.dumps({"summary": "ada bug", "issues": ["contoh output salah"]})


def scripted(manager=(), developer=(), qa=(), delay=0.0):
    """Fake Ollama: each agent (told apart by its system prompt) pops its next scripted reply."""
    queues = {"Manager": list(manager), "Developer": list(developer), "QA": list(qa)}
    calls = []

    async def gen(model, system, prompt, fmt=None):
        role = next(r for r in queues if f"{r} Agent" in system)
        calls.append((role, fmt))
        await asyncio.sleep(delay)
        reply = queues[role].pop(0)
        if isinstance(reply, Exception):
            raise reply
        return {"text": reply, "input_tokens": 1, "output_tokens": 1}

    gen.calls = calls
    return gen


def wait_done(client, tid, done=("Completed", "Failed", "Cancelled"), timeout=5):
    end = time.time() + timeout
    while time.time() < end:
        data = client.get(f"/instructions/{tid}").json()
        if data["status"] in done:
            return data
        time.sleep(0.05)
    raise AssertionError(f"stuck at {data['status']}")


def start(client, text="Buat fungsi validasi email dan dokumentasinya"):
    r = client.post("/instructions", json={"instruction": text})
    assert r.status_code == 202, r.text
    return r.json()["task_id"]


def test_full_workflow(client, monkeypatch):
    gen = scripted(manager=[PLAN, "Laporan akhir"], developer=["kode", "docs"], qa=[CLEAN, CLEAN])
    monkeypatch.setattr(ollama, "generate", gen)
    data = wait_done(client, start(client))
    assert data["status"] == "Completed", data["error"]
    assert [s["status"] for s in data["subtasks"]] == ["Completed", "Completed"]
    assert [e["step"] for e in data["executions"]] == ["plan", "report"]
    assert [e["step"] for e in data["subtasks"][0]["executions"]] == ["work", "review"]
    assert data["report"].startswith("Laporan akhir") and orchestrator.UNTESTED_NOTE in data["report"]
    assert data["tested"] is False
    assert all(a["status"] == "Idle" for a in client.get("/agents").json())
    # JSON mode only for plan + review, free text for work + report
    assert ("Manager", "json") in gen.calls and ("Developer", None) in gen.calls and ("QA", "json") in gen.calls


def test_revision_is_bounded(client, monkeypatch):
    one_task = json.dumps({"tasks": [{"title": "Fungsi email", "description": ""}]})
    # QA keeps finding issues; Developer must revise exactly once, then the workflow moves on.
    monkeypatch.setattr(ollama, "generate", scripted(manager=[one_task, "Laporan"], developer=["v1", "v2"], qa=[ISSUE, ISSUE]))
    data = wait_done(client, start(client))
    assert data["status"] == "Completed"
    assert [e["step"] for e in data["subtasks"][0]["executions"]] == ["work", "review", "revise", "review"]
    assert data["subtasks"][0]["executions"][2]["output"] == "v2"


def test_invalid_plan_retries_then_fails(client, monkeypatch):
    dup = '{"tasks": [{"title": "a"}], "tasks": [{"title": "b"}]}'
    monkeypatch.setattr(ollama, "generate", scripted(manager=["bukan json", dup, json.dumps({"tasks": []})]))
    data = wait_done(client, start(client))
    assert data["status"] == "Failed"
    assert len(data["executions"]) == orchestrator.MAX_JSON_ATTEMPTS
    assert "JSON valid" in data["error"] and data["subtasks"] == []
    events = [a["description"] for a in client.get(f"/activity?task_id={data['id']}").json()]
    assert any("key duplikat" in e for e in events)


def test_invalid_review_recovers_on_retry(client, monkeypatch):
    one_task = json.dumps({"tasks": [{"title": "x", "description": ""}]})
    monkeypatch.setattr(ollama, "generate", scripted(manager=[one_task, "Laporan"], developer=["kode"], qa=["{}", CLEAN]))
    assert wait_done(client, start(client))["status"] == "Completed"


def test_ollama_error_fails_open_subtask(client, monkeypatch):
    monkeypatch.setattr(ollama, "generate", scripted(manager=[PLAN], developer=[ollama.OllamaError("Ollama mati")]))
    data = wait_done(client, start(client))
    assert data["status"] == "Failed" and data["error"] == "Ollama mati"
    assert [s["status"] for s in data["subtasks"]] == ["Failed"]
    assert data["report"] is None


def test_cancel_mid_workflow(client, monkeypatch):
    monkeypatch.setattr(ollama, "generate", scripted(manager=[PLAN], developer=["kode"], delay=0.3))
    tid = start(client)
    end = time.time() + 5
    while not client.get(f"/instructions/{tid}").json()["subtasks"]:
        assert time.time() < end
        time.sleep(0.05)
    assert client.post("/instructions", json={"instruction": "lain"}).status_code == 409  # one active task
    assert client.post(f"/tasks/{tid}/cancel").status_code == 200
    data = wait_done(client, tid)
    assert data["status"] == "Cancelled"
    assert data["subtasks"][0]["status"] == "Cancelled"
    assert all(a["status"] == "Idle" for a in client.get("/agents").json())


def test_inactive_agent_blocks_workflow(client):
    from app import db
    with db.conn() as c:
        c.execute("UPDATE agents SET is_active=0 WHERE name='QA'")
    assert client.post("/instructions", json={"instruction": "x"}).status_code == 400


@pytest.mark.parametrize("bad", ['[]', '{"tasks": [1]}', '{"tasks": [{"title": ""}]}',
                                 json.dumps({"tasks": [{"title": "t"}] * 4})])
def test_parse_plan_rejects(bad):
    with pytest.raises(ValueError):
        orchestrator.parse_plan(bad)


def test_parse_review_rejects_non_string_issues():
    with pytest.raises(ValueError):
        orchestrator.parse_review('{"summary": "x", "issues": [1]}')


def test_system_check_forces_revision_when_qa_misses_repetition(client, monkeypatch):
    one_task = json.dumps({"tasks": [{"title": "Unit test", "description": ""}]})
    looping = "\n".join(['    assert is_valid_email("user@domain.com") == True'] * 10)
    # QA approves the looping output; the backend check must still send it back to Developer.
    monkeypatch.setattr(ollama, "generate", scripted(manager=[one_task, "Laporan"], developer=[looping, "kode bersih"],
                                                     qa=[CLEAN, CLEAN]))
    data = wait_done(client, start(client))
    assert data["status"] == "Completed"
    assert [e["step"] for e in data["subtasks"][0]["executions"]] == ["work", "review", "revise", "review"]
    events = [a["event_type"] for a in client.get(f"/activity?task_id={data['subtasks'][0]['id']}").json()]
    assert "system_check" in events


def test_output_problems():
    assert orchestrator.output_problems("kode biasa\nreturn True") == []
    assert len(orchestrator.output_problems("x" + ollama.TRUNCATED_NOTE)) == 1
    assert len(orchestrator.output_problems("\n".join(["a_long_repeated_line_of_code()"] * 6))) == 1
