const COLORS: Record<string, string> = {
  Idle: "bg-zinc-100 text-zinc-600 dark:bg-zinc-800 dark:text-zinc-300",
  Thinking: "bg-violet-100 text-violet-700 dark:bg-violet-950 dark:text-violet-300",
  Working: "bg-blue-100 text-blue-700 dark:bg-blue-950 dark:text-blue-300",
  Reviewing: "bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300",
  "Waiting Approval": "bg-orange-100 text-orange-800 dark:bg-orange-950 dark:text-orange-300",
  Pending: "bg-zinc-100 text-zinc-600 dark:bg-zinc-800 dark:text-zinc-300",
  Assigned: "bg-zinc-100 text-zinc-700 dark:bg-zinc-800 dark:text-zinc-300",
  "In Progress": "bg-blue-100 text-blue-700 dark:bg-blue-950 dark:text-blue-300",
  "Under Review": "bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300",
  Running: "bg-blue-100 text-blue-700 dark:bg-blue-950 dark:text-blue-300",
  Completed: "bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300",
  Failed: "bg-red-100 text-red-700 dark:bg-red-950 dark:text-red-300",
  Cancelled: "bg-zinc-200 text-zinc-600 dark:bg-zinc-800 dark:text-zinc-400",
  Offline: "bg-zinc-200 text-zinc-500 dark:bg-zinc-800 dark:text-zinc-500",
};

export default function StatusBadge({ status }: { status: string }) {
  return (
    <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${COLORS[status] ?? COLORS.Idle}`}>
      {status}
    </span>
  );
}
