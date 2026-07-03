"use client";

import type { Budget } from "@/lib/api";

export function BudgetBar({ budget }: { budget: Budget | null }) {
  if (!budget) {
    return (
      <div className="rounded-xl border border-slate-200 bg-white p-4 text-sm text-slate-500">
        Select a flight or hotel to track budget.
      </div>
    );
  }

  const pct = Math.min(budget.utilization_pct, 100);
  const over = budget.remaining_usd < 0;
  const barColor = over ? "bg-rose-500" : budget.warning ? "bg-amber-500" : "bg-emerald-500";

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4 space-y-3">
      <div className="flex items-center justify-between text-sm">
        <span className="font-semibold text-slate-900">Budget</span>
        <span className="text-slate-600">
          ${budget.committed_usd.toLocaleString()} / ${budget.trip_budget_usd.toLocaleString()}
        </span>
      </div>
      <div className="h-2.5 overflow-hidden rounded-full bg-slate-100">
        <div className={`h-full ${barColor} transition-all`} style={{ width: `${pct}%` }} />
      </div>
      <div className="grid grid-cols-3 gap-2 text-xs text-slate-600">
        <div>
          <p className="text-slate-400">Flights</p>
          <p className="font-medium">${budget.flight_cost_usd.toLocaleString()}</p>
        </div>
        <div>
          <p className="text-slate-400">Hotels</p>
          <p className="font-medium">${budget.hotel_cost_usd.toLocaleString()}</p>
        </div>
        <div>
          <p className="text-slate-400">Remaining</p>
          <p className={`font-medium ${over ? "text-rose-600" : ""}`}>
            ${budget.remaining_usd.toLocaleString()}
          </p>
        </div>
      </div>
      {budget.warning && (
        <p className="rounded-lg bg-amber-50 px-3 py-2 text-xs text-amber-800">{budget.warning}</p>
      )}
    </div>
  );
}
