import json
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = os.getenv("AI_OFFICE_DB", str(Path(__file__).resolve().parent.parent / "ai_office.db"))
DEFAULT_MODEL = os.getenv("AI_OFFICE_MODEL", "qwen2.5-coder:3b")

# Schema follows PRD §10, plus agents.status (real backend state for the dashboard)
# and executions.output (the agent's result). Approvals table arrives in Phase 4.
SCHEMA = """
CREATE TABLE IF NOT EXISTS agents (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    role TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    system_prompt TEXT NOT NULL,
    provider TEXT NOT NULL DEFAULT 'ollama',
    model TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'Idle',
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'Pending',
    priority INTEGER NOT NULL DEFAULT 0,
    assigned_agent_id INTEGER REFERENCES agents(id),
    parent_task_id INTEGER REFERENCES tasks(id),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    completed_at TEXT
);
CREATE TABLE IF NOT EXISTS executions (
    id INTEGER PRIMARY KEY,
    task_id INTEGER NOT NULL REFERENCES tasks(id),
    agent_id INTEGER NOT NULL REFERENCES agents(id),
    provider TEXT NOT NULL,
    model TEXT NOT NULL,
    status TEXT NOT NULL,
    output TEXT,
    input_tokens INTEGER,
    output_tokens INTEGER,
    estimated_cost REAL NOT NULL DEFAULT 0,
    started_at TEXT NOT NULL,
    completed_at TEXT,
    error_message TEXT
);
CREATE TABLE IF NOT EXISTS activity_logs (
    id INTEGER PRIMARY KEY,
    agent_id INTEGER REFERENCES agents(id),
    task_id INTEGER REFERENCES tasks(id),
    event_type TEXT NOT NULL,
    description TEXT NOT NULL,
    metadata TEXT,
    created_at TEXT NOT NULL
);
"""

SEED_AGENTS = [
    ("Manager", "AI Team Manager", "Menganalisis instruksi CEO, membuat task breakdown, dan menyusun laporan akhir.",
     "Kamu adalah Manager Agent di AI Office. Analisis instruksi CEO, pecah menjadi task yang jelas, "
     "dan susun laporan yang ringkas dan jujur. Jangan mengarang hasil yang belum dikerjakan."),
    ("Developer", "AI Software Engineer", "Menganalisis kebutuhan teknis, menulis kode, dan dokumentasi.",
     "Kamu adalah Developer Agent di AI Office. Kerjakan task teknis yang diberikan: analisis kebutuhan, "
     "tulis kode yang benar dan sederhana, lalu jelaskan hasilnya singkat."),
    ("QA", "AI Quality Assurance Engineer", "Mengevaluasi hasil Developer, menyusun test case, dan melaporkan bug.",
     "Kamu adalah QA Agent di AI Office. Evaluasi hasil kerja yang diberikan, susun test case, dan laporkan "
     "masalah. Jangan menyatakan lulus jika pengujian belum benar-benar dijalankan."),
]


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


@contextmanager
def conn():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA foreign_keys = ON")
    try:
        with c:  # commits on success, rolls back on error
            yield c
    finally:
        c.close()


def log(c, event_type: str, description: str, agent_id=None, task_id=None, metadata: dict | None = None):
    c.execute(
        "INSERT INTO activity_logs (agent_id, task_id, event_type, description, metadata, created_at) VALUES (?,?,?,?,?,?)",
        (agent_id, task_id, event_type, description, json.dumps(metadata) if metadata else None, now()),
    )


def set_task_status(c, task_id: int, status: str, agent_id=None):
    completed = now() if status in ("Completed", "Failed", "Cancelled") else None
    c.execute("UPDATE tasks SET status=?, updated_at=?, completed_at=? WHERE id=?", (status, now(), completed, task_id))
    log(c, "task_status", f"Task {task_id} -> {status}", agent_id=agent_id, task_id=task_id)


def set_agent_status(c, agent_id: int, status: str, task_id=None):
    c.execute("UPDATE agents SET status=?, updated_at=? WHERE id=?", (status, now(), agent_id))
    log(c, "agent_status", f"Agent {agent_id} -> {status}", agent_id=agent_id, task_id=task_id)


def init_db():
    with conn() as c:
        c.executescript(SCHEMA)
        ts = now()
        for name, role, desc, prompt in SEED_AGENTS:
            c.execute(
                "INSERT OR IGNORE INTO agents (name, role, description, system_prompt, model, created_at, updated_at) "
                "VALUES (?,?,?,?,?,?,?)",
                (name, role, desc, prompt, DEFAULT_MODEL, ts, ts),
            )
        # A restart kills in-flight work; record it honestly instead of leaving stale "In Progress" rows.
        for row in c.execute("SELECT id, assigned_agent_id FROM tasks WHERE status='In Progress'").fetchall():
            set_task_status(c, row["id"], "Failed", agent_id=row["assigned_agent_id"])
        c.execute(
            "UPDATE executions SET status='Failed', completed_at=?, error_message='Dihentikan karena backend restart' "
            "WHERE status='Running'",
            (ts,),
        )
        c.execute("UPDATE agents SET status='Idle', updated_at=? WHERE status != 'Idle'", (ts,))
