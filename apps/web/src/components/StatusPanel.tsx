"use client";

import { useEffect, useState } from "react";
import { fetchHealth, fetchReady, type ReadyResponse } from "@/lib/api";

function StatusBadge({ ok, label }: { ok: boolean; label: string }) {
  return (
    <span
      className={`inline-flex items-center gap-2 rounded-full px-3 py-1 text-sm font-medium ${
        ok ? "bg-emerald-100 text-emerald-800" : "bg-amber-100 text-amber-800"
      }`}
    >
      <span className={`h-2 w-2 rounded-full ${ok ? "bg-emerald-500" : "bg-amber-500"}`} />
      {label}
    </span>
  );
}

export function StatusPanel() {
  const [healthStatus, setHealthStatus] = useState("checking…");
  const [readyStatus, setReadyStatus] = useState("checking…");
  const [checks, setChecks] = useState<ReadyResponse["checks"]>({});
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        const [health, ready] = await Promise.all([fetchHealth(), fetchReady()]);
        if (cancelled) return;
        setHealthStatus(health.status);
        setReadyStatus(ready.status);
        setChecks(ready.checks);
        setError(null);
      } catch (err) {
        if (cancelled) return;
        setError(err instanceof Error ? err.message : "Unknown error");
        setHealthStatus("unreachable");
        setReadyStatus("unreachable");
      }
    }

    void load();
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <h2 className="text-lg font-semibold text-slate-900">System status</h2>
      <p className="mt-1 text-sm text-slate-500">
        Live checks against the FastAPI backend (`/health` and `/ready`).
      </p>

      {error ? (
        <p className="mt-4 rounded-lg bg-rose-50 px-4 py-3 text-sm text-rose-700">{error}</p>
      ) : (
        <div className="mt-4 flex flex-wrap gap-3">
          <StatusBadge ok={healthStatus === "ok"} label={`API health: ${healthStatus}`} />
          <StatusBadge ok={readyStatus === "ok"} label={`Readiness: ${readyStatus}`} />
        </div>
      )}

      {Object.keys(checks).length > 0 && (
        <ul className="mt-4 space-y-2 text-sm text-slate-700">
          {Object.entries(checks).map(([name, ok]) => (
            <li key={name} className="flex items-center justify-between rounded-lg bg-slate-50 px-3 py-2">
              <span className="capitalize">{name}</span>
              <span className={ok ? "text-emerald-600" : "text-amber-600"}>
                {ok ? "healthy" : "down"}
              </span>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
