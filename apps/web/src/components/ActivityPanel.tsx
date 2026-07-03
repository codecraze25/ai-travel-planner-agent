"use client";

import { useCallback, useEffect, useState } from "react";
import { listActivity, type ActivityItem } from "@/lib/api";

export function ActivityPanel({ tripId }: { tripId: string }) {
  const [items, setItems] = useState<ActivityItem[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const data = await listActivity(tripId);
      setItems(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load activity");
    } finally {
      setLoading(false);
    }
  }, [tripId]);

  useEffect(() => {
    void load();
  }, [load]);

  if (loading) {
    return <p className="text-sm text-slate-500">Loading activity…</p>;
  }

  if (error) {
    return <p className="text-sm text-rose-600">{error}</p>;
  }

  if (items.length === 0) {
    return (
      <p className="text-sm text-slate-500">
        No activity yet. Search, chat, or draft an email to populate the audit feed.
      </p>
    );
  }

  return (
    <ul className="space-y-2">
      {items.map((item) => (
        <li
          key={`${item.kind}-${item.id}`}
          className="flex items-start justify-between gap-3 rounded-lg bg-slate-50 px-3 py-2 text-sm"
        >
          <div>
            <p className="font-medium text-slate-800">
              <span className="mr-2 rounded bg-white px-1.5 py-0.5 text-xs text-slate-500">
                {item.kind === "agent_action" ? "tool" : "audit"}
              </span>
              {item.action}
            </p>
            {item.error_message && (
              <p className="mt-0.5 text-xs text-rose-600">{item.error_message}</p>
            )}
          </div>
          <div className="shrink-0 text-right text-xs text-slate-400">
            {item.success === false ? (
              <span className="text-rose-500">failed</span>
            ) : (
              <span className="text-emerald-600">ok</span>
            )}
            <p>{new Date(item.created_at).toLocaleString()}</p>
          </div>
        </li>
      ))}
    </ul>
  );
}
