"use client";

import { useEffect, useState } from "react";
import {
  listFlights,
  searchFlights,
  selectFlight,
  type Budget,
  type Flight,
  type FlightSearchResult,
} from "@/lib/api";

function formatDuration(minutes: number): string {
  const h = Math.floor(minutes / 60);
  const m = minutes % 60;
  return `${h}h ${m}m`;
}

export function FlightsPanel({
  tripId,
  onBudgetChange,
}: {
  tripId: string;
  onBudgetChange: (budget: Budget) => void;
}) {
  const [flights, setFlights] = useState<Flight[]>([]);
  const [tradeoffs, setTradeoffs] = useState<FlightSearchResult["tradeoffs"] | null>(null);
  const [nonstopOnly, setNonstopOnly] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        const items = await listFlights(tripId);
        if (!cancelled) setFlights(items);
      } catch {
        // empty until first search
      }
    }
    void load();
    return () => {
      cancelled = true;
    };
  }, [tripId]);

  async function onSearch() {
    setLoading(true);
    setError(null);
    try {
      const result = await searchFlights(tripId, { nonstop_only: nonstopOnly });
      setFlights(result.items);
      setTradeoffs(result.tradeoffs);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Search failed");
    } finally {
      setLoading(false);
    }
  }

  async function onSelect(flightId: string) {
    setError(null);
    try {
      const result = await selectFlight(tripId, flightId);
      setFlights((prev) =>
        prev.map((f) => ({ ...f, selected: f.id === flightId })),
      );
      onBudgetChange(result.budget);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Select failed");
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-3">
        <label className="flex items-center gap-2 text-sm text-slate-700">
          <input
            type="checkbox"
            checked={nonstopOnly}
            onChange={(e) => setNonstopOnly(e.target.checked)}
          />
          Nonstop only
        </label>
        <button
          type="button"
          onClick={() => void onSearch()}
          disabled={loading}
          className="rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-60"
        >
          {loading ? "Searching…" : "Search flights"}
        </button>
      </div>

      {error && <p className="rounded-lg bg-rose-50 px-4 py-3 text-sm text-rose-700">{error}</p>}

      {tradeoffs && (
        <div className="rounded-xl border border-brand-100 bg-brand-50 p-4 text-sm text-brand-900 space-y-1">
          <p className="font-semibold">Tradeoffs</p>
          {tradeoffs.explanations.map((line) => (
            <p key={line}>{line}</p>
          ))}
        </div>
      )}

      {flights.length === 0 ? (
        <p className="text-sm text-slate-500">No flights yet. Run a search to see options.</p>
      ) : (
        <ul className="space-y-3">
          {flights.map((flight) => (
            <li
              key={flight.id}
              className={`rounded-xl border bg-white p-4 ${
                flight.selected ? "border-brand-500 ring-1 ring-brand-200" : "border-slate-200"
              }`}
            >
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <p className="font-semibold text-slate-900">
                    {flight.airline} {flight.flight_number}
                  </p>
                  <p className="text-sm text-slate-600">
                    {flight.departure_time.replace("T", " ")} → {flight.arrival_time.replace("T", " ")}
                  </p>
                  <p className="text-sm text-slate-500">
                    {formatDuration(flight.duration_minutes)} · {flight.stops} stop(s)
                  </p>
                  {flight.cancellation_policy && (
                    <p className="mt-1 text-xs text-slate-500">{flight.cancellation_policy}</p>
                  )}
                </div>
                <div className="text-right">
                  <p className="text-lg font-bold text-slate-900">
                    ${flight.price_usd.toLocaleString()}
                  </p>
                  <div className="mt-2 flex flex-col gap-2">
                    <button
                      type="button"
                      onClick={() => void onSelect(flight.id)}
                      className="rounded-lg bg-slate-900 px-3 py-1.5 text-xs font-medium text-white"
                    >
                      {flight.selected ? "Selected" : "Select"}
                    </button>
                    {flight.booking_link && (
                      <a
                        href={flight.booking_link}
                        target="_blank"
                        rel="noreferrer"
                        className="text-xs text-brand-600 hover:underline"
                      >
                        Booking link
                      </a>
                    )}
                  </div>
                </div>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
