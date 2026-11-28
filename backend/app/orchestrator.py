"""Phase 2: sequential Manager -> Developer -> QA -> Manager workflow (PRD FR-04)."""
import asyncio
import collections
import json

from . import db, ollama
from .agents import call_model

MAX_SUBTASKS = 3
MAX_JSON_ATTEMPTS = 3  # first try + 2 retries
MAX_REVISIONS = 1
CLIP_CHARS = 6000  # ~1.7k tokens; keeps each prompt inside num_ctx 4096

UNTESTED_NOTE = ("Catatan sistem: review QA bersifat statis. Kode belum dijalankan atau diuji, "
                 "jadi hasil ini belum terverifikasi.")


class OutputError(Exception):
    pass


def _clip(text: str, n: int) -> str:
    return text if len(text) <= n else text[:n] + "\n...[dipotong]"


def _no_dupes(pairs):
    keys = [k for k, _ in pairs]
    dupes = {k for k in keys if keys.count(k) > 1}
    if dupes:
        raise ValueError(f"key duplikat: {sorted(dupes)}")
    return dict(pairs)


def _load(text: str) -> dict:
    data = json.loads(text, object_pairs_hook=_no_dupes)  # stdlib silently drops duplicate keys otherwise
    if not isinstance(data, dict):
        raise ValueError("JSON harus berupa object")
    return data


def parse_plan(text: str) -> list[dict]:
    tasks = _load(text).get("tasks")
    if not isinstance(tasks, list) or not 1 <= len(tasks) <= MAX_SUBTASKS:
        raise ValueError(f"'tasks' harus list berisi 1 sampai {MAX_SUBTASKS} item")
    out = []
    for t in tasks:
        title = t.get("title") if isinstance(t, dict) else None
        if not isinstance(title, str) or not title.strip():
            raise ValueError("setiap task wajib punya 'title' berupa teks")
        desc = t.get("description")
        out.append({"title": title.strip()[:200], "description": desc.strip()[:10_000] if isinstance(desc, str) else ""})
    return out


def parse_review(text: str) -> dict:
    data = _load(text)
    summary, issues = data.get("summary"), data.get("issues")
    if not isinstance(summary, str) or not isinstance(issues, list) or not all(isinstance(i, str) for i in issues):
        raise ValueError("format wajib: {\"summary\": string, \"issues\": [string]}")
    return {"summary": summary.strip(), "issues": [i.strip() for i in issues if i.strip()]}


DEV_RULES = ("Aturan:\n- Kerjakan HANYA subtask ini; bagian lain dikerjakan di subtask terpisah.\n"
             "- Jawab ringkas: satu blok kode lalu penjelasan singkat (maksimal 5 kalimat).\n"
             "- Jika menulis test, maksimal 8 test case dan jangan mengulang kasus yang sama.\n"
             "- Jangan mengklaim kode sudah dijalankan atau diuji.")
REPEAT_LINE_LIMIT = 3  # clean outputs had 0-1 repeated lines; a live run slipped through with 3 at limit 5


def output_problems(text: str) -> list[str]:
    """Deterministic checks the 3B QA model missed in live tests."""
    problems = []
    if ollama.TRUNCATED_NOTE.strip() in text:
        problems.append("Output terpotong karena terlalu panjang; tulis ulang lebih ringkas.")
    counts = collections.Counter(line.strip() for line in text.splitlines() if len(line.strip()) > 20)
    if sum(n - 1 for n in counts.values() if n > 1) >= REPEAT_LINE_LIMIT:
        problems.append("Output berisi banyak baris yang diulang; hapus pengulangan.")
    return problems


def plan_prompt(instruction: str, error: str | None) -> str:
    p = (f"Instruksi CEO:\n{instruction}\n\n"
         f"Pecah instruksi ini menjadi 1 sampai {MAX_SUBTASKS} subtask untuk Developer Agent.\n"
         "Aturan:\n- Setiap subtask menghasilkan satu hasil tertulis yang jelas (kode atau dokumen).\n"
         "- Jangan membuat subtask untuk menjalankan, menguji, memverifikasi, atau me-review kode; "
         "agent tidak bisa menjalankan kode dan QA dijadwalkan otomatis oleh sistem.\n"
         "- Jangan membuat subtask yang tumpang tindih.\n"
         'Balas HANYA JSON: {"tasks":[{"title":string,"description":string}]}')
    return p + (f"\n\nJawaban sebelumnya tidak valid ({error}). Perbaiki." if error else "")


def work_prompt(instruction: str, sub: dict) -> str:
    return (f"Konteks instruksi CEO (hanya latar belakang):\n{instruction}\n\n"
            f"Subtask yang harus kamu kerjakan: {sub['title']}\n{sub['description']}\n\n{DEV_RULES}")


def review_prompt(sub: dict, output: str, error: str | None) -> str:
    p = (f"Subtask: {sub['title']}\n{sub['description']}\n\nHasil Developer:\n{_clip(output, CLIP_CHARS)}\n\n"
         "Review hasil ini secara statis (kode TIDAK dijalankan). Periksa:\n"
         "- bug dan logika yang salah,\n- contoh atau klaim output yang tidak sesuai kode,\n"
         "- bagian yang tidak sesuai subtask atau mengerjakan subtask lain,\n- pengulangan yang tidak perlu.\n"
         "Tulis issue yang spesifik dan bisa diperbaiki. Jangan menulis saran umum.\n"
         'Balas HANYA JSON: {"summary":string,"issues":[string]}. Kosongkan "issues" jika tidak ada masalah.')
    return p + (f"\n\nJawaban sebelumnya tidak valid ({error}). Perbaiki." if error else "")


def revise_prompt(sub: dict, output: str, issues: list[str]) -> str:
    found = "\n".join(f"- {i}" for i in issues)
    return (f"Subtask: {sub['title']}\n{sub['description']}\n\nHasil sebelumnya:\n{_clip(output, CLIP_CHARS)}\n\n"
            f"Temuan QA:\n{found}\n\nPerbaiki hasil sesuai temuan QA dan tulis ulang hasil lengkapnya.\n{DEV_RULES}")


def report_prompt(instruction: str, results: list[dict]) -> str:
    parts = []
    for i, r in enumerate(results, 1):
        issues = "\n".join(f"  - {x}" for x in r["review"]["issues"]) or "  (tidak ada)"
        # Code is left out on purpose: given full outputs, the model copied and looped them until truncated.
        parts.append(f"## Subtask {i}: {r['title']}\nRingkasan QA: {r['review']['summary']}\n"
                     f"Masalah yang masih ada:\n{issues}")
    return (f"Instruksi CEO:\n{instruction}\n\n" + "\n\n".join(parts) +
            "\n\nSusun laporan akhir untuk CEO: ringkasan, status per subtask, dan masalah yang masih ada.\n"
            "Aturan:\n- Maksimal 200 kata. Jangan menyalin kode; hasil lengkap ada di detail subtask.\n"
            "- Hanya laporkan apa yang tertulis di atas; jangan menambah klaim baru.\n"
            "- Kode BELUM dijalankan atau diuji. Jangan pernah menulis bahwa kode sudah diuji, berhasil diuji, "
            "atau terbukti benar.")


async def _json_call(task_id, agent, step, build_prompt, parse):
    error = None
    for _ in range(MAX_JSON_ATTEMPTS):
        result = await call_model(task_id, agent, step, build_prompt(error), fmt="json")
        try:
            return parse(result["text"])
        except ValueError as e:  # includes json.JSONDecodeError
            error = str(e)
            with db.conn() as c:
                db.log(c, "invalid_output", f"{agent['name']} ({step}): {error}", agent_id=agent["id"], task_id=task_id)
    raise OutputError(f"{agent['name']} gagal menghasilkan JSON valid setelah {MAX_JSON_ATTEMPTS} percobaan: {error}")


def _status(task_id: int | None, task_status: str | None, agent, agent_status: str):
    with db.conn() as c:
        if task_id is not None and task_status:
            db.set_task_status(c, task_id, task_status, agent_id=agent["id"])
        db.set_agent_status(c, agent["id"], agent_status, task_id=task_id)


async def run_instruction(parent_id: int) -> None:
    with db.conn() as c:
        parent = dict(c.execute("SELECT * FROM tasks WHERE id=?", (parent_id,)).fetchone())
        team = {r["name"]: dict(r) for r in c.execute("SELECT * FROM agents WHERE name IN ('Manager','Developer','QA')")}
    manager, dev, qa = team["Manager"], team["Developer"], team["QA"]
    instruction = parent["description"]
    child_id = None
    final = "Failed"
    try:
        _status(parent_id, "In Progress", manager, "Thinking")
        plan = await _json_call(parent_id, manager, "plan", lambda e: plan_prompt(instruction, e), parse_plan)
        _status(None, None, manager, "Idle")

        results = []
        for sub in plan:
            with db.conn() as c:
                ts = db.now()
                child_id = c.execute(
                    "INSERT INTO tasks (title, description, status, assigned_agent_id, parent_task_id, created_at, updated_at) "
                    "VALUES (?,?,?,?,?,?,?)",
                    (sub["title"], sub["description"], "Assigned", dev["id"], parent_id, ts, ts),
                ).lastrowid
                db.log(c, "task_created", f"Subtask {child_id} dibuat oleh Manager untuk Developer",
                       agent_id=manager["id"], task_id=child_id)

            _status(child_id, "In Progress", dev, "Working")
            output = (await call_model(child_id, dev, "work", work_prompt(instruction, sub)))["text"]
            _status(None, None, dev, "Idle")

            for revision in range(MAX_REVISIONS + 1):
                _status(child_id, "Under Review", qa, "Reviewing")
                review = await _json_call(child_id, qa, "review", lambda e: review_prompt(sub, output, e), parse_review)
                _status(None, None, qa, "Idle")
                if problems := output_problems(output):
                    review["issues"] = problems + review["issues"]
                    with db.conn() as c:
                        db.log(c, "system_check", "; ".join(problems), agent_id=qa["id"], task_id=child_id)
                if not review["issues"] or revision == MAX_REVISIONS:
                    break
                _status(child_id, "In Progress", dev, "Working")
                output = (await call_model(child_id, dev, "revise", revise_prompt(sub, output, review["issues"])))["text"]
                _status(None, None, dev, "Idle")

            _status(child_id, "Completed", dev, "Idle")
            child_id = None
            results.append({"title": sub["title"], "output": output, "review": review})

        _status(None, None, manager, "Thinking")
        await call_model(parent_id, manager, "report", report_prompt(instruction, results))
        final = "Completed"
    except asyncio.CancelledError:
        final = "Cancelled"
    except Exception as e:
        with db.conn() as c:
            db.log(c, "orchestration_error", str(e), task_id=parent_id)
    finally:
        with db.conn() as c:
            if child_id is not None:
                db.set_task_status(c, child_id, final, agent_id=dev["id"])
            db.set_task_status(c, parent_id, final, agent_id=manager["id"])
            for a in (manager, dev, qa):
                if c.execute("SELECT status FROM agents WHERE id=?", (a["id"],)).fetchone()["status"] != "Idle":
                    db.set_agent_status(c, a["id"], "Idle", task_id=parent_id)
