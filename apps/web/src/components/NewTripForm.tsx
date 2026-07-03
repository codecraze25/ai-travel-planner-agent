"use client";

import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";
import { createTrip } from "@/lib/api";

export function NewTripForm() {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    setError(null);

    const form = new FormData(event.currentTarget);
    const styleRaw = String(form.get("style") ?? "");
    const style = styleRaw
      .split(",")
      .map((s) => s.trim())
      .filter(Boolean);

    try {
      const trip = await createTrip({
        origin: String(form.get("origin") ?? ""),
        destination: String(form.get("destination") ?? ""),
        start_date: String(form.get("start_date") ?? ""),
        end_date: String(form.get("end_date") ?? ""),
        travelers: Number(form.get("travelers") ?? 1),
        budget_usd: Number(form.get("budget_usd") ?? 0),
        preferences: {
          style: style.length ? style : undefined,
          hotel_prefs: String(form.get("hotel_prefs") ?? "") || undefined,
          flight_prefs: String(form.get("flight_prefs") ?? "") || undefined,
          food_prefs: String(form.get("food_prefs") ?? "") || undefined,
          activity_prefs: String(form.get("activity_prefs") ?? "") || undefined,
        },
      });
      router.push(`/trips/${trip.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create trip");
      setSubmitting(false);
    }
  }

  return (
    <form onSubmit={onSubmit} className="space-y-6 rounded-xl border border-slate-200 bg-white p-6">
      <div className="grid gap-4 sm:grid-cols-2">
        <label className="block text-sm">
          <span className="font-medium text-slate-700">Origin</span>
          <input
            name="origin"
            required
            defaultValue="San Francisco"
            className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2"
          />
        </label>
        <label className="block text-sm">
          <span className="font-medium text-slate-700">Destination</span>
          <input
            name="destination"
            required
            defaultValue="Tokyo"
            className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2"
          />
        </label>
        <label className="block text-sm">
          <span className="font-medium text-slate-700">Start date</span>
          <input
            name="start_date"
            type="date"
            required
            defaultValue="2026-10-10"
            className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2"
          />
        </label>
        <label className="block text-sm">
          <span className="font-medium text-slate-700">End date</span>
          <input
            name="end_date"
            type="date"
            required
            defaultValue="2026-10-15"
            className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2"
          />
        </label>
        <label className="block text-sm">
          <span className="font-medium text-slate-700">Travelers</span>
          <input
            name="travelers"
            type="number"
            min={1}
            required
            defaultValue={2}
            className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2"
          />
        </label>
        <label className="block text-sm">
          <span className="font-medium text-slate-700">Budget (USD)</span>
          <input
            name="budget_usd"
            type="number"
            min={1}
            required
            defaultValue={4000}
            className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2"
          />
        </label>
      </div>

      <label className="block text-sm">
        <span className="font-medium text-slate-700">Travel style (comma-separated)</span>
        <input
          name="style"
          defaultValue="food, culture, museums"
          className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2"
        />
      </label>

      <div className="grid gap-4 sm:grid-cols-2">
        <label className="block text-sm">
          <span className="font-medium text-slate-700">Hotel preference</span>
          <input
            name="hotel_prefs"
            defaultValue="4-star, near train station"
            className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2"
          />
        </label>
        <label className="block text-sm">
          <span className="font-medium text-slate-700">Flight preference</span>
          <input
            name="flight_prefs"
            defaultValue="Nonstop preferred"
            className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2"
          />
        </label>
        <label className="block text-sm sm:col-span-2">
          <span className="font-medium text-slate-700">Food preference</span>
          <input
            name="food_prefs"
            defaultValue="Good local food, easy transportation"
            className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2"
          />
        </label>
        <label className="block text-sm sm:col-span-2">
          <span className="font-medium text-slate-700">Activities</span>
          <input
            name="activity_prefs"
            defaultValue="Museums, neighborhoods"
            className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2"
          />
        </label>
      </div>

      {error && <p className="rounded-lg bg-rose-50 px-4 py-3 text-sm text-rose-700">{error}</p>}

      <button
        type="submit"
        disabled={submitting}
        className="rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-60"
      >
        {submitting ? "Creating…" : "Create trip"}
      </button>
    </form>
  );
}
