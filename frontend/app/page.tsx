"use client";

import Link from "next/link";
import { useState } from "react";
import StatusBadge from "@/components/StatusBadge";
import { Activity, Agent, Health, Task, api, fmtTime, usePoll } from "@/lib/api";

const card = "rounded-xl border border-zinc-200 bg-white p-4 dark:border-zinc-800 dark:bg-zinc-900";

export default function OfficePage() {
  const health = usePoll<Health>("/health");
  const agents = usePoll<Agent[]>("/agents");
  const tasks = usePoll<Task[]>("/tasks");
  const [selected, setSelected] = useState<number | null>(null);

  const activeId = health.data?.active_task_id ?? null;
  const active = tasks.data?.find((t) => t.id === activeId);
  const backendDown = health.error !== null;

  return (
    <div className="space-y-6">
      <section className="flex flex-wrap items-center gap-3 text-sm">
        <span>Backend: {backendDown ? <b className="text-red-600">tidak terhubung ({health.error})</b> : <b className="text-emerald-600">ok</b>}</span>
        {health.data && (
          <span>
            Ollama:{" "}
            {health.data.ollama.ok ? (
              <b className="text-emerald-600">v{health.data.ollama.version}</b>
            ) : (
              <b className="text-red-600">tidak terhubung</b>
            )}
          </span>
        )}
      </section>

      <section>
        <h2 className="mb-3 text-lg font-semibold">Kantor</h2>
        <div className="grid gap-4 sm:grid-cols-3">
          {agents.data?.map((a) => (
            <button
              key={a.id}
              onClick={() => setSelected(selected === a.id ? null : a.id)}
              className={`${card} text-left transition hover:border-zinc-400 ${selected === a.id ? "ring-2 ring-zinc-400" : ""}`}
            >
              <div className="flex items-center gap-3">
                <div className="relative flex h-12 w-12 items-center justify-center rounded-full bg-zinc-100 text-lg font-semibold dark:bg-zinc-800">
                  {a.name[0]}
                  {a.status !== "Idle" && (
                    <span className="absolute -right-0.5 -top-0.5 h-3 w-3 animate-pulse rounded-full bg-blue-500" aria-hidden />
                  )}
                </div>
                <div className="min-w-0">
                  <div className="font-medium">{a.name}</div>
                  <div className="truncate text-xs text-zinc-500">{a.role}</div>
                </div>
              </div>
              <div className="mt-3 flex items-center justify-between">
                <StatusBadge status={a.is_active ? a.status : "Offline"} />
                <span className="font-mono text-xs text-zinc-500">{a.model}</span>
              </div>
            </button>
          ))}
          {!agents.data && !agents.error && <p className="text-sm text-zinc-500">Memuat agent...</p>}
        </div>
      </section>

      {selected !== null && agents.data && <AgentDetail agent={agents.data.find((a) => a.id === selected)!} />}

      <section className={card}>
        <h2 className="mb-2 font-semibold">Task aktif</h2>
        {active ? (
          <div className="flex flex-wrap items-center gap-3 text-sm">
            <StatusBadge status={active.status} />
            <Link href={`/tasks#${active.id}`} className="underline">
              #{active.id} {active.title}
            </Link>
          </div>
        ) : (
          <p className="text-sm text-zinc-500">Tidak ada task yang berjalan.</p>
        )}
      </section>

      <InstructionForm busy={activeId !== null} disabled={backendDown} />
    </div>
  );
}

function AgentDetail({ agent }: { agent: Agent }) {
  const activity = usePoll<Activity[]>(`/activity?agent_id=${agent.id}&limit=15`);
  return (
    <section className={card}>
      <h2 className="font-semibold">
        {agent.name} <span className="font-normal text-zinc-500">· {agent.role}</span>
      </h2>
      <p className="mt-1 text-sm text-zinc-600 dark:text-zinc-400">{agent.description}</p>
      <dl className="mt-3 grid grid-cols-[auto_1fr] gap-x-4 gap-y-1 text-sm">
        <dt className="text-zinc-500">Provider / model</dt>
        <dd className="font-mono">{agent.provider} / {agent.model}</dd>
        <dt className="text-zinc-500">Aktif</dt>
        <dd>{agent.is_active ? "Ya" : "Tidak"}</dd>
        <dt className="text-zinc-500">System prompt</dt>
        <dd className="whitespace-pre-wrap">{agent.system_prompt}</dd>
      </dl>
      <h3 className="mt-4 mb-1 text-sm font-medium">Aktivitas terbaru</h3>
      <ul className="space-y-0.5 text-xs">
        {activity.data?.map((e) => (
          <li key={e.id} className="flex gap-2">
            <span className="shrink-0 text-zinc-500">{fmtTime(e.created_at)}</span>
            <span>{e.description}</span>
          </li>
        ))}
        {activity.data?.length === 0 && <li className="text-zinc-500">Belum ada aktivitas.</li>}
      </ul>
    </section>
  );
}

function InstructionForm({ busy, disabled }: { busy: boolean; disabled: boolean }) {
  const [text, setText] = useState("");
  const [sending, setSending] = useState(false);
  const [msg, setMsg] = useState<{ ok: boolean; text: string; id?: number } | null>(null);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setSending(true);
    setMsg(null);
    try {
      const r = await api<{ task_id: number }>("/instructions", { method: "POST", body: JSON.stringify({ instruction: text }) });
      setMsg({ ok: true, text: `Instruksi dikirim sebagai task #${r.task_id}.`, id: r.task_id });
      setText("");
    } catch (err) {
      setMsg({ ok: false, text: err instanceof Error ? err.message : String(err) });
    } finally {
      setSending(false);
    }
  }

  return (
    <form onSubmit={submit} className={card}>
      <label htmlFor="instruction" className="mb-2 block font-semibold">
        Instruksi untuk Manager
      </label>
      <textarea
        id="instruction"
        value={text}
        onChange={(e) => setText(e.target.value)}
        rows={3}
        maxLength={5000}
        placeholder="Contoh: Buat fungsi Python untuk menghitung faktorial beserta unit test-nya."
        className="w-full rounded-lg border border-zinc-300 bg-transparent p-2 text-sm dark:border-zinc-700"
      />
      <div className="mt-2 flex flex-wrap items-center gap-3">
        <button
          type="submit"
          disabled={sending || busy || disabled || !text.trim()}
          className="rounded-lg bg-zinc-900 px-4 py-2 text-sm font-medium text-white disabled:opacity-40 dark:bg-zinc-100 dark:text-zinc-900"
        >
          {sending ? "Mengirim..." : "Kirim"}
        </button>
        {busy && <span className="text-xs text-zinc-500">Tunggu task aktif selesai (hanya satu task dalam satu waktu).</span>}
        {msg && (
          <span className={`text-sm ${msg.ok ? "text-emerald-600" : "text-red-600"}`}>
            {msg.text}{" "}
            {msg.id && (
              <Link href={`/tasks#${msg.id}`} className="underline">
                Lihat progres
              </Link>
            )}
          </span>
        )}
      </div>
    </form>
  );
}
