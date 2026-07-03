"use client";

import { useCallback, useEffect, useState } from "react";
import {
  generateItinerary,
  getItinerary,
  type Itinerary,
  type ItineraryItem,
} from "@/lib/api";

function groupByDay(items: ItineraryItem[]): Map<number, ItineraryItem[]> {
  const map = new Map<number, ItineraryItem[]>();
  for (const item of items) {
    const list = map.get(item.day_number) ?? [];
    list.push(item);
    map.set(item.day_number, list);
  }
  return map;
}

export function ItineraryPanel({ tripId }: { tripId: string }) {
  const [itinerary, setItinerary] = useState<Itinerary | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      const data = await getItinerary(tripId);
      setItinerary(data);
    } catch {
      setItinerary(null);
    }
  }, [tripId]);

  useEffect(() => {
    void load();
  }, [load]);

  async function onGenerate(regenerateDay?: number) {
    setLoading(true);
    setError(null);
    try {
      const data = await generateItinerary(tripId, regenerateDay);
      setItinerary(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Generation failed");
    } finally {
      setLoading(false);
    }
  }

  if (!itinerary) {
    return (
      <section className="rounded-xl border border-slate-200 bg-white p-6 text-center space-y-4">
        <p className="text-sm text-slate-500">
          No itinerary yet. Generate one from chat (“Plan my trip”) or click below.
        </p>
        {error && <p className="text-sm text-rose-600">{error}</p>}
        <button
          type="button"
          onClick={() => void onGenerate()}
          disabled={loading}
          className="rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
        >
          {loading ? "Generating…" : "Generate itinerary"}
        </button>
      </section>
    );
  }

  const byDay = groupByDay(itinerary.items);

  return (
    <section className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div>
          <p className="text-sm text-slate-500">
            Version {itinerary.version} · Est. activities cost $
            {itinerary.total_est_cost_usd.toLocaleString()}
          </p>
        </div>
        <button
          type="button"
          onClick={() => void onGenerate()}
          disabled={loading}
          className="rounded-lg border border-brand-600 px-3 py-1.5 text-sm text-brand-700 hover:bg-brand-50 disabled:opacity-50"
        >
          {loading ? "Regenerating…" : "Regenerate all"}
        </button>
      </div>

      {error && <p className="text-sm text-rose-600">{error}</p>}

      {[...byDay.entries()].map(([dayNum, blocks]) => (
        <article
          key={dayNum}
          className="rounded-xl border border-slate-200 bg-white p-4 space-y-3"
        >
          <div className="flex items-center justify-between">
            <h3 className="font-semibold text-slate-900">Day {dayNum}</h3>
            <button
              type="button"
              onClick={() => void onGenerate(dayNum)}
              disabled={loading}
              className="text-xs text-brand-600 hover:underline disabled:opacity-50"
            >
              Regenerate day
            </button>
          </div>
          {blocks.map((block) => (
            <div key={block.id} className="border-l-2 border-brand-200 pl-3 text-sm">
              <p className="text-xs uppercase tracking-wide text-slate-400">
                {block.time_block}
              </p>
              <p className="font-medium text-slate-800">{block.title}</p>
              <p className="text-slate-600">{block.description}</p>
              {block.location && (
                <p className="text-slate-500 mt-1">📍 {block.location}</p>
              )}
              <p className="text-slate-500 mt-1">
                Est. ${block.est_cost_usd.toLocaleString()}
                {block.map_url && (
                  <>
                    {" · "}
                    <a
                      href={block.map_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-brand-600 hover:underline"
                    >
                      Map
                    </a>
                  </>
                )}
              </p>
              {block.backup_option && (
                <p className="text-xs text-slate-400 mt-1">Backup: {block.backup_option}</p>
              )}
            </div>
          ))}
        </article>
      ))}
    </section>
  );
}
