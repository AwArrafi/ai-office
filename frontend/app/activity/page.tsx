"use client";

import { useState } from "react";
import { Activity, Agent, fmtTime, usePoll } from "@/lib/api";

export default function ActivityPage() {
  const agents = usePoll<Agent[]>("/agents", 10000);
  const [agentId, setAgentId] = useState("");
  const feed = usePoll<Activity[]>(`/activity?limit=200${agentId ? `&agent_id=${agentId}` : ""}`);
  const name = (id: number | null) => agents.data?.find((a) => a.id === id)?.name ?? "Sistem";

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-3">
        <h2 className="text-lg font-semibold">Activity</h2>
        <label className="ml-auto flex items-center gap-2 text-sm">
          Agent
          <select
            value={agentId}
            onChange={(e) => setAgentId(e.target.value)}
            className="rounded-lg border border-zinc-300 bg-transparent px-2 py-1 dark:border-zinc-700"
          >
            <option value="">Semua</option>
            {agents.data?.map((a) => (
              <option key={a.id} value={a.id}>
                {a.name}
              </option>
            ))}
          </select>
        </label>
      </div>
      {feed.error && <p className="text-sm text-red-600">{feed.error}</p>}
      <div className="overflow-x-auto rounded-xl border border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-900">
        <table className="w-full text-left text-sm">
          <thead className="border-b border-zinc-200 text-xs text-zinc-500 dark:border-zinc-800">
            <tr>
              <th className="px-3 py-2 font-medium">Waktu</th>
              <th className="px-3 py-2 font-medium">Agent</th>
              <th className="px-3 py-2 font-medium">Task</th>
              <th className="px-3 py-2 font-medium">Event</th>
              <th className="px-3 py-2 font-medium">Keterangan</th>
            </tr>
          </thead>
          <tbody>
            {feed.data?.map((e) => (
              <tr key={e.id} className={`border-b border-zinc-100 last:border-0 dark:border-zinc-800 ${e.event_type.includes("error") || e.event_type === "invalid_output" ? "text-red-600" : ""}`}>
                <td className="whitespace-nowrap px-3 py-1.5 text-zinc-500">{fmtTime(e.created_at)}</td>
                <td className="px-3 py-1.5">{name(e.agent_id)}</td>
                <td className="px-3 py-1.5">{e.task_id ? <a href={`/tasks#${e.task_id}`} className="underline">#{e.task_id}</a> : "-"}</td>
                <td className="px-3 py-1.5 font-mono text-xs">{e.event_type}</td>
                <td className="px-3 py-1.5">{e.description}</td>
              </tr>
            ))}
            {feed.data?.length === 0 && (
              <tr>
                <td colSpan={5} className="px-3 py-4 text-center text-zinc-500">
                  Belum ada aktivitas.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
