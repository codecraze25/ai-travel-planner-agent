"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { listTrips, type Trip } from "@/lib/api";

const statusColors: Record<string, string> = {
  draft: "bg-slate-100 text-slate-700",
  planning: "bg-blue-100 text-blue-700",
  ready: "bg-emerald-100 text-emerald-700",
  archived: "bg-amber-100 text-amber-800",
};

export function TripDashboard() {
  const [trips, setTrips] = useState<Trip[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        const items = await listTrips();
        if (!cancelled) {
          setTrips(items);
          setError(null);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Failed to load trips");
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    void load();
    return () => {
      cancelled = true;
    };
  }, []);

  if (loading) {
    return <p className="text-sm text-slate-500">Loading trips…</p>;
  }

  if (error) {
    return (
      <div className="rounded-lg bg-rose-50 px-4 py-3 text-sm text-rose-700">
        {error}
        <p className="mt-2 text-xs text-rose-600">
          Ensure the API is running and migrations are applied (`alembic upgrade head`).
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold text-slate-900">Your trips</h2>
        <Link
          href="/trips/new"
          className="rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700"
        >
          New trip
        </Link>
      </div>

      {trips.length === 0 ? (
        <div className="rounded-xl border border-dashed border-slate-300 bg-white p-8 text-center">
          <p className="text-slate-600">No trips yet.</p>
          <Link href="/trips/new" className="mt-3 inline-block text-sm font-medium text-brand-600">
            Create your first trip
          </Link>
        </div>
      ) : (
        <ul className="divide-y divide-slate-200 rounded-xl border border-slate-200 bg-white">
          {trips.map((trip) => (
            <li key={trip.id}>
              <Link
                href={`/trips/${trip.id}`}
                className="flex items-center justify-between px-5 py-4 hover:bg-slate-50"
              >
                <div>
                  <p className="font-medium text-slate-900">
                    {trip.origin} → {trip.destination}
                  </p>
                  <p className="text-sm text-slate-500">
                    {trip.start_date} – {trip.end_date} · {trip.travelers} travelers · $
                    {trip.budget_usd.toLocaleString()}
                  </p>
                </div>
                <span
                  className={`rounded-full px-2.5 py-0.5 text-xs font-medium capitalize ${statusColors[trip.status] ?? statusColors.draft}`}
                >
                  {trip.status}
                </span>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
