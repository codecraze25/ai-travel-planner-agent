"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { BudgetBar } from "@/components/BudgetBar";
import { FlightsPanel } from "@/components/FlightsPanel";
import { HotelsPanel } from "@/components/HotelsPanel";
import { getBudget, getTrip, type Budget, type Trip } from "@/lib/api";

const tabs = ["Overview", "Flights", "Hotels", "Documents", "Itinerary", "Email"] as const;

export default function TripDetailPage() {
  const params = useParams<{ id: string }>();
  const [trip, setTrip] = useState<Trip | null>(null);
  const [budget, setBudget] = useState<Budget | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<(typeof tabs)[number]>("Overview");

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        const [data, budgetData] = await Promise.all([
          getTrip(params.id),
          getBudget(params.id).catch(() => null),
        ]);
        if (!cancelled) {
          setTrip(data);
          setBudget(budgetData);
        }
      } catch (err) {
        if (!cancelled) setError(err instanceof Error ? err.message : "Failed to load trip");
      }
    }
    void load();
    return () => {
      cancelled = true;
    };
  }, [params.id]);

  if (error) {
    return <p className="text-sm text-rose-600">{error}</p>;
  }

  if (!trip) {
    return <p className="text-sm text-slate-500">Loading trip…</p>;
  }

  return (
    <div className="space-y-6">
      <div>
        <Link href="/dashboard" className="text-sm text-brand-600 hover:underline">
          ← Dashboard
        </Link>
        <h1 className="mt-2 text-2xl font-bold text-slate-900">
          {trip.origin} → {trip.destination}
        </h1>
        <p className="text-sm text-slate-500 capitalize">
          {trip.start_date} – {trip.end_date} · {trip.status}
        </p>
      </div>

      <BudgetBar budget={budget} />

      <nav className="flex flex-wrap gap-2 border-b border-slate-200 pb-2">
        {tabs.map((tab) => (
          <button
            key={tab}
            type="button"
            onClick={() => setActiveTab(tab)}
            className={`rounded-lg px-3 py-1.5 text-sm font-medium ${
              activeTab === tab
                ? "bg-brand-100 text-brand-700"
                : "text-slate-600 hover:bg-slate-100"
            }`}
          >
            {tab}
          </button>
        ))}
      </nav>

      {activeTab === "Overview" && (
        <section className="rounded-xl border border-slate-200 bg-white p-6 space-y-3 text-sm">
          <p>
            <span className="font-medium">Travelers:</span> {trip.travelers}
          </p>
          <p>
            <span className="font-medium">Budget:</span> ${trip.budget_usd.toLocaleString()}
          </p>
          {trip.preferences?.style && (
            <p>
              <span className="font-medium">Style:</span> {trip.preferences.style.join(", ")}
            </p>
          )}
          {trip.preferences?.hotel_prefs && (
            <p>
              <span className="font-medium">Hotel:</span> {trip.preferences.hotel_prefs}
            </p>
          )}
          {trip.preferences?.flight_prefs && (
            <p>
              <span className="font-medium">Flight:</span> {trip.preferences.flight_prefs}
            </p>
          )}
        </section>
      )}

      {activeTab === "Flights" && (
        <FlightsPanel tripId={trip.id} onBudgetChange={setBudget} />
      )}

      {activeTab === "Hotels" && (
        <HotelsPanel tripId={trip.id} onBudgetChange={setBudget} />
      )}

      {(activeTab === "Documents" || activeTab === "Itinerary" || activeTab === "Email") && (
        <section className="rounded-xl border border-dashed border-slate-300 bg-white p-8 text-center text-sm text-slate-500">
          {activeTab} — coming in a later phase.
        </section>
      )}
    </div>
  );
}
