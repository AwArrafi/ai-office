import asyncio

from . import db, ollama

# shortcut: in-memory registry assumes a single uvicorn worker; move to a DB/queue lock if workers > 1.
_running: dict[int, asyncio.Task] = {}


def active_task_id() -> int | None:
    return next(iter(_running), None)


def start(task_id: int, runner=None) -> None:
    """Schedule a run. Caller must check active_task_id() first (one active task, NFR-01)."""
    t = asyncio.create_task((runner or run_task)(task_id))
    _running[task_id] = t
    t.add_done_callback(lambda _: _running.pop(task_id, None))


def cancel(task_id: int) -> bool:
    t = _running.get(task_id)
    if t is None:
        return False
    t.cancel()  # closes the HTTP request; Ollama stops generating when the client disconnects
    return True


async def call_model(task_id: int, agent, step: str, prompt: str, fmt: str | None = None) -> dict:
    """One model call recorded as an execution row. Re-raises failures after recording them."""
    with db.conn() as c:
        exec_id = c.execute(
            "INSERT INTO executions (task_id, agent_id, provider, model, status, step, started_at) VALUES (?,?,?,?,?,?,?)",
            (task_id, agent["id"], agent["provider"], agent["model"], "Running", step, db.now()),
        ).lastrowid
    status, result, error = "Failed", None, None
    try:
        result = await ollama.generate(agent["model"], agent["system_prompt"], prompt, fmt=fmt)
        status = "Completed"
        return result
    except asyncio.CancelledError:
        status, error = "Cancelled", "Dihentikan oleh user"
        raise
    except ollama.OllamaError as e:
        error = str(e)
        raise
    except Exception as e:
        error = f"Error tidak terduga: {e!r}"
        raise
    finally:
        with db.conn() as c:
            c.execute(
                "UPDATE executions SET status=?, output=?, input_tokens=?, output_tokens=?, completed_at=?, error_message=? "
                "WHERE id=?",
                (status, result and result["text"], result and result["input_tokens"],
                 result and result["output_tokens"], db.now(), error, exec_id),
            )
            db.log(c, "execution", f"Execution {exec_id} ({step}) {status}", agent_id=agent["id"], task_id=task_id,
                   metadata={"provider": agent["provider"], "model": agent["model"], "step": step, "error": error})


async def run_task(task_id: int) -> None:
    """Phase 1 path: one task, one agent."""
    with db.conn() as c:
        task = c.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
        agent = c.execute("SELECT * FROM agents WHERE id=?", (task["assigned_agent_id"],)).fetchone()
        db.set_task_status(c, task_id, "In Progress", agent_id=agent["id"])
        db.set_agent_status(c, agent["id"], "Working", task_id=task_id)
    status = "Failed"
    try:
        await call_model(task_id, agent, "work", f"Task: {task['title']}\n\n{task['description']}".strip())
        status = "Completed"
    except asyncio.CancelledError:
        status = "Cancelled"
    except Exception:
        pass  # already recorded on the execution row; never leave the task stuck "In Progress"
    finally:
        with db.conn() as c:
            db.set_task_status(c, task_id, status, agent_id=agent["id"])
            db.set_agent_status(c, agent["id"], "Idle", task_id=task_id)
