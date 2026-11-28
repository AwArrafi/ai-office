from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from . import agents, db, ollama, orchestrator


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init_db()
    yield


app = FastAPI(title="AI Office", lifespan=lifespan)


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=10_000)
    assigned_agent_id: int
    priority: int = Field(default=0, ge=0, le=10)


class InstructionCreate(BaseModel):
    instruction: str = Field(min_length=1, max_length=5_000)


def _get(c, table: str, id_: int):
    row = c.execute(f"SELECT * FROM {table} WHERE id=?", (id_,)).fetchone()
    if row is None:
        raise HTTPException(404, f"{table[:-1]} {id_} tidak ditemukan")
    return dict(row)


@app.get("/health")
async def health():
    return {"backend": "ok", "active_task_id": agents.active_task_id(), "ollama": await ollama.health()}


@app.get("/agents")
def list_agents():
    with db.conn() as c:
        return [dict(r) for r in c.execute("SELECT * FROM agents ORDER BY id")]


@app.get("/agents/{agent_id}")
def get_agent(agent_id: int):
    with db.conn() as c:
        return _get(c, "agents", agent_id)


@app.post("/tasks", status_code=201)
def create_task(body: TaskCreate):
    with db.conn() as c:
        agent = _get(c, "agents", body.assigned_agent_id)
        if not agent["is_active"]:
            raise HTTPException(400, f"Agent {agent['name']} nonaktif dan tidak menerima task baru")
        ts = db.now()
        task_id = c.execute(
            "INSERT INTO tasks (title, description, status, priority, assigned_agent_id, created_at, updated_at) "
            "VALUES (?,?,?,?,?,?,?)",
            (body.title, body.description, "Assigned", body.priority, agent["id"], ts, ts),
        ).lastrowid
        db.log(c, "task_created", f"Task {task_id} dibuat dan di-assign ke {agent['name']}",
               agent_id=agent["id"], task_id=task_id)
        return _get(c, "tasks", task_id)


@app.get("/tasks")
def list_tasks():
    with db.conn() as c:
        return [dict(r) for r in c.execute("SELECT * FROM tasks ORDER BY id DESC")]


@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    with db.conn() as c:
        task = _get(c, "tasks", task_id)
        task["executions"] = [dict(r) for r in c.execute("SELECT * FROM executions WHERE task_id=? ORDER BY id", (task_id,))]
        return task


# async (not threadpool) so asyncio.create_task has a loop and the check-then-start below is atomic.
@app.post("/tasks/{task_id}/run", status_code=202)
async def run_task(task_id: int):
    with db.conn() as c:
        task = _get(c, "tasks", task_id)
        if task["status"] not in ("Assigned", "Failed"):
            raise HTTPException(409, f"Task berstatus {task['status']}, tidak bisa dijalankan")
        agent = _get(c, "agents", task["assigned_agent_id"])
        if not agent["is_active"]:
            raise HTTPException(400, f"Agent {agent['name']} nonaktif")
    active = agents.active_task_id()
    if active is not None:
        raise HTTPException(409, f"Task {active} masih berjalan; hanya satu task aktif yang diizinkan")
    agents.start(task_id)
    return {"task_id": task_id, "status": "started"}


@app.post("/tasks/{task_id}/cancel")
async def cancel_task(task_id: int):
    if agents.cancel(task_id):
        return {"task_id": task_id, "status": "cancelling"}
    with db.conn() as c:
        task = _get(c, "tasks", task_id)
        if task["status"] in ("Completed", "Failed", "Cancelled"):
            raise HTTPException(409, f"Task sudah {task['status']}")
        db.set_task_status(c, task_id, "Cancelled", agent_id=task["assigned_agent_id"])
    return {"task_id": task_id, "status": "Cancelled"}


@app.post("/instructions", status_code=202)
async def create_instruction(body: InstructionCreate):
    active = agents.active_task_id()
    if active is not None:
        raise HTTPException(409, f"Task {active} masih berjalan; hanya satu task aktif yang diizinkan")
    with db.conn() as c:
        team = c.execute("SELECT name, is_active FROM agents WHERE name IN ('Manager','Developer','QA')").fetchall()
        inactive = [r["name"] for r in team if not r["is_active"]]
        if len(team) < 3 or inactive:
            raise HTTPException(400, f"Workflow butuh Manager, Developer, dan QA aktif (nonaktif: {inactive})")
        manager_id = c.execute("SELECT id FROM agents WHERE name='Manager'").fetchone()["id"]
        ts = db.now()
        text = body.instruction.strip()
        task_id = c.execute(
            "INSERT INTO tasks (title, description, status, assigned_agent_id, created_at, updated_at) VALUES (?,?,?,?,?,?)",
            (text[:80], text, "Assigned", manager_id, ts, ts),
        ).lastrowid
        db.log(c, "instruction_received", f"Instruksi CEO diterima sebagai task {task_id}", agent_id=manager_id, task_id=task_id)
    agents.start(task_id, orchestrator.run_instruction)
    return {"task_id": task_id, "status": "started"}


@app.get("/instructions/{task_id}")
def get_instruction(task_id: int):
    with db.conn() as c:
        task = _get(c, "tasks", task_id)
        execs = lambda tid: [dict(r) for r in c.execute("SELECT * FROM executions WHERE task_id=? ORDER BY id", (tid,))]
        task["executions"] = execs(task_id)
        task["subtasks"] = [dict(r, executions=execs(r["id"]))
                            for r in c.execute("SELECT * FROM tasks WHERE parent_task_id=? ORDER BY id", (task_id,))]
        report = next((e["output"] for e in reversed(task["executions"]) if e["step"] == "report" and e["output"]), None)
        # The note is added at read time so it can never be dropped by the model.
        task["report"] = f"{report}\n\n---\n{orchestrator.UNTESTED_NOTE}" if report else None
        task["tested"] = False
        err = c.execute("SELECT description FROM activity_logs WHERE task_id=? AND event_type='orchestration_error' "
                        "ORDER BY id DESC LIMIT 1", (task_id,)).fetchone()
        task["error"] = err["description"] if err else None
        return task


@app.get("/activity")
def activity(agent_id: int | None = None, task_id: int | None = None, limit: int = 100):
    sql, args = "SELECT * FROM activity_logs WHERE 1=1", []
    if agent_id is not None:
        sql += " AND agent_id=?"
        args.append(agent_id)
    if task_id is not None:
        sql += " AND task_id=?"
        args.append(task_id)
    sql += " ORDER BY id DESC LIMIT ?"
    args.append(max(1, min(limit, 1000)))
    with db.conn() as c:
        return [dict(r) for r in c.execute(sql, args)]
