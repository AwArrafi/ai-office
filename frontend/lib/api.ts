"use client";

import { useCallback, useEffect, useState } from "react";

export type Agent = {
  id: number;
  name: string;
  role: string;
  description: string;
  system_prompt: string;
  provider: string;
  model: string;
  status: string;
  is_active: number;
};

export type Task = {
  id: number;
  title: string;
  description: string;
  status: string;
  assigned_agent_id: number | null;
  parent_task_id: number | null;
  created_at: string;
  completed_at: string | null;
};

export type Execution = {
  id: number;
  agent_id: number;
  provider: string;
  model: string;
  status: string;
  step: string | null;
  output: string | null;
  input_tokens: number | null;
  output_tokens: number | null;
  started_at: string;
  completed_at: string | null;
  error_message: string | null;
};

export type Instruction = Task & {
  executions: Execution[];
  subtasks: (Task & { executions: Execution[] })[];
  report: string | null;
  tested: boolean;
  error: string | null;
};

export type Activity = {
  id: number;
  agent_id: number | null;
  task_id: number | null;
  event_type: string;
  description: string;
  created_at: string;
};

export type Health = {
  backend: string;
  active_task_id: number | null;
  ollama: { ok: boolean; version?: string; models?: string[]; error?: string };
};

export async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const r = await fetch(`/api${path}`, {
    cache: "no-store",
    ...init,
    headers: { "Content-Type": "application/json" },
  });
  if (!r.ok) {
    let msg = `${r.status} ${r.statusText}`;
    try {
      const body = await r.json();
      msg = typeof body.detail === "string" ? body.detail : JSON.stringify(body.detail);
    } catch {}
    throw new Error(msg);
  }
  return r.json();
}

// shortcut: polling every 2s is enough for one local user; switch to SSE if updates feel laggy.
export function usePoll<T>(path: string | null, ms = 2000) {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    if (!path) return;
    try {
      setData(await api<T>(path));
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    }
  }, [path]);

  useEffect(() => {
    setData(null);
    if (!path) return;
    refresh();
    const id = setInterval(refresh, ms);
    return () => clearInterval(id);
  }, [path, ms, refresh]);

  return { data, error, refresh };
}

export function fmtTime(iso: string | null) {
  return iso ? new Date(iso).toLocaleString("id-ID", { dateStyle: "short", timeStyle: "medium" }) : "-";
}

export const ACTIVE_TASK = ["Assigned", "In Progress", "Under Review", "Waiting Approval"];
