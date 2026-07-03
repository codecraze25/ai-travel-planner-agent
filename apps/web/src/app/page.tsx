import Link from "next/link";

import { StatusPanel } from "@/components/StatusPanel";

export default function HomePage() {
  return (
    <div className="space-y-8">
      <section className="space-y-3">
        <h2 className="text-3xl font-bold tracking-tight text-slate-900">
          Plan trips end-to-end with AI
        </h2>
        <p className="max-w-2xl text-lg text-slate-600">
          Search flights and hotels, read travel PDFs, generate day-by-day itineraries, and draft
          emails — with explicit approval before anything is sent or booked.
        </p>
      </section>

      <StatusPanel />

      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 className="text-lg font-semibold text-slate-900">Get started</h2>
        <p className="mt-1 text-sm text-slate-500">Phase 1 — create and manage trips.</p>
        <div className="mt-4 flex flex-wrap gap-3">
          <Link
            href="/dashboard"
            className="rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700"
          >
            Open dashboard
          </Link>
          <Link
            href="/trips/new"
            className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
          >
            New trip
          </Link>
        </div>
      </section>
    </div>
  );
}
