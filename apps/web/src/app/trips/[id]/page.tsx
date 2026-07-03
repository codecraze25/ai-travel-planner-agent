"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { ActivityPanel } from "@/components/ActivityPanel";
import { BudgetBar } from "@/components/BudgetBar";
import { CalendarPanel } from "@/components/CalendarPanel";
import { ChatPanel } from "@/components/ChatPanel";
import { DocumentsPanel } from "@/components/DocumentsPanel";
import { EmailPanel } from "@/components/EmailPanel";
import { FlightsPanel } from "@/components/FlightsPanel";
import { HotelsPanel } from "@/components/HotelsPanel";
import { ItineraryPanel } from "@/components/ItineraryPanel";
import { getBudget, getTrip, type Budget, type Trip } from "@/lib/api";

const tabs = [
  "Overview",
  "Chat",
  "Flights",
  "Hotels",
  "Documents",
  "Itinerary",
  "Email",
  "Activity",
] as const;

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
          <p className="pt-2 text-slate-500">
            Tip: use Chat → “Plan my trip”, then review Itinerary and Email tabs.
          </p>
          <div className="border-t border-slate-100 pt-4">
            <h3 className="mb-2 text-sm font-semibold text-slate-900">Calendar (stub)</h3>
            <CalendarPanel tripId={trip.id} />
          </div>
        </section>
      )}

      {activeTab === "Flights" && (
        <FlightsPanel tripId={trip.id} onBudgetChange={setBudget} />
      )}

      {activeTab === "Hotels" && (
        <HotelsPanel tripId={trip.id} onBudgetChange={setBudget} />
      )}

      {activeTab === "Documents" && <DocumentsPanel tripId={trip.id} />}

      {activeTab === "Chat" && <ChatPanel tripId={trip.id} />}

      {activeTab === "Itinerary" && <ItineraryPanel tripId={trip.id} />}

      {activeTab === "Email" && <EmailPanel tripId={trip.id} />}

      {activeTab === "Activity" && (
        <section className="rounded-xl border border-slate-200 bg-white p-6">
          <h2 className="mb-3 text-sm font-semibold text-slate-900">Trip activity</h2>
          <ActivityPanel tripId={trip.id} />
        </section>
      )}
    </div>
  );
}
