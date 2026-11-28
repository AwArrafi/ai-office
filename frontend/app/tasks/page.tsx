"use client";

import { useEffect, useState } from "react";
import StatusBadge from "@/components/StatusBadge";
import { ACTIVE_TASK, Agent, Execution, Instruction, Task, api, fmtTime, usePoll } from "@/lib/api";

const card = "rounded-xl border border-zinc-200 bg-white p-4 dark:border-zinc-800 dark:bg-zinc-900";

export default function TasksPage() {
  const tasks = usePoll<Task[]>("/tasks");
  const agents = usePoll<Agent[]>("/agents", 10000);
  const [selected, setSelected] = useState<number | null>(null);

  // /tasks#12 opens task 12 (links from the Office page); hash avoids Suspense rules for search params.
  useEffect(() => {
    const fromHash = () => {
      const id = Number(window.location.hash.slice(1));
      if (id) setSelected(id);
    };
    fromHash();
    window.addEventListener("hashchange", fromHash);
    return () => window.removeEventListener("hashchange", fromHash);
  }, []);

  const top = tasks.data?.filter((t) => t.parent_task_id === null) ?? [];
  const agentName = (id: number | null) => agents.data?.find((a) => a.id === id)?.name ?? "-";

  return (
    <div className="grid gap-6 md:grid-cols-[18rem_1fr]">
      <aside>
        <h2 className="mb-3 text-lg font-semibold">Tasks</h2>
        {tasks.error && <p className="text-sm text-red-600">{tasks.error}</p>}
        <ul className="space-y-2">
          {top.map((t) => (
            <li key={t.id}>
              <a
                href={`#${t.id}`}
                className={`block rounded-lg border p-3 text-sm ${selected === t.id ? "border-zinc-500 bg-white dark:bg-zinc-900" : "border-zinc-200 dark:border-zinc-800"}`}
              >
                <div className="flex items-center justify-between gap-2">
                  <span className="text-xs text-zinc-500">#{t.id}</span>
                  <StatusBadge status={t.status} />
                </div>
                <div className="mt-1 line-clamp-2">{t.title}</div>
              </a>
            </li>
          ))}
          {tasks.data && top.length === 0 && <li className="text-sm text-zinc-500">Belum ada task. Kirim instruksi dari halaman Office.</li>}
        </ul>
      </aside>
      <section>{selected ? <TaskDetail id={selected} agentName={agentName} /> : <p className="text-sm text-zinc-500">Pilih task di kiri.</p>}</section>
    </div>
  );
}

function TaskDetail({ id, agentName }: { id: number; agentName: (id: number | null) => string }) {
  const { data, error, refresh } = usePoll<Instruction>(`/instructions/${id}`);
  const [stopError, setStopError] = useState<string | null>(null);

  if (error) return <p className="text-sm text-red-600">{error}</p>;
  if (!data) return <p className="text-sm text-zinc-500">Memuat...</p>;

  async function stop() {
    setStopError(null);
    try {
      await api(`/tasks/${id}/cancel`, { method: "POST" });
      refresh();
    } catch (e) {
      setStopError(e instanceof Error ? e.message : String(e));
    }
  }

  return (
    <div className="space-y-4">
      <div className={card}>
        <div className="flex flex-wrap items-center gap-3">
          <h2 className="text-lg font-semibold">#{data.id}</h2>
          <StatusBadge status={data.status} />
          {ACTIVE_TASK.includes(data.status) && (
            <button onClick={stop} className="ml-auto rounded-lg border border-red-300 px-3 py-1 text-sm text-red-700 hover:bg-red-50 dark:border-red-900 dark:text-red-400 dark:hover:bg-red-950">
              Stop
            </button>
          )}
        </div>
        <p className="mt-2 whitespace-pre-wrap text-sm">{data.description}</p>
        <p className="mt-2 text-xs text-zinc-500">
          Dibuat {fmtTime(data.created_at)} · Selesai {fmtTime(data.completed_at)}
        </p>
        {data.error && <p className="mt-2 text-sm text-red-600">Error: {data.error}</p>}
        {stopError && <p className="mt-2 text-sm text-red-600">Gagal menghentikan: {stopError}</p>}
      </div>

      {data.report && (
        <div className={card}>
          <h3 className="mb-2 font-semibold">Laporan akhir</h3>
          <div className="whitespace-pre-wrap text-sm">{data.report}</div>
        </div>
      )}

      <Steps title="Langkah Manager" executions={data.executions} agentName={agentName} />

      {data.subtasks.map((s, i) => (
        <div key={s.id} className={card}>
          <div className="flex flex-wrap items-center gap-2">
            <h3 className="font-semibold">
              Subtask {i + 1}: {s.title}
            </h3>
            <StatusBadge status={s.status} />
          </div>
          {s.description && <p className="mt-1 text-sm text-zinc-600 dark:text-zinc-400">{s.description}</p>}
          <Steps executions={s.executions} agentName={agentName} />
        </div>
      ))}
    </div>
  );
}

function Steps({ title, executions, agentName }: { title?: string; executions: Execution[]; agentName: (id: number | null) => string }) {
  if (executions.length === 0) return null;
  return (
    <div className={title ? card : "mt-3"}>
      {title && <h3 className="mb-2 font-semibold">{title}</h3>}
      <ol className="space-y-2">
        {executions.map((e) => {
          const secs = e.completed_at ? (new Date(e.completed_at).getTime() - new Date(e.started_at).getTime()) / 1000 : null;
          return (
            <li key={e.id} className="rounded-lg border border-zinc-200 dark:border-zinc-800">
              <details>
                <summary className="flex cursor-pointer flex-wrap items-center gap-2 px-3 py-2 text-sm">
                  <span className="font-medium">{e.step ?? "run"}</span>
                  <span className="text-zinc-500">{agentName(e.agent_id)}</span>
                  <StatusBadge status={e.status} />
                  <span className="ml-auto font-mono text-xs text-zinc-500">
                    {secs !== null && `${secs.toFixed(1)} dtk · `}
                    {e.output_tokens ?? "-"} token
                  </span>
                </summary>
                <div className="border-t border-zinc-200 px-3 py-2 dark:border-zinc-800">
                  {e.error_message && <p className="mb-2 text-sm text-red-600">{e.error_message}</p>}
                  <pre className="max-h-96 overflow-auto whitespace-pre-wrap font-mono text-xs">{e.output ?? "(belum ada output)"}</pre>
                </div>
              </details>
            </li>
          );
        })}
      </ol>
    </div>
  );
}
