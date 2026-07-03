"use client";

import { useEffect, useState } from "react";
import { listHotels, searchHotels, selectHotel, type Budget, type Hotel } from "@/lib/api";

export function HotelsPanel({
  tripId,
  onBudgetChange,
}: {
  tripId: string;
  onBudgetChange: (budget: Budget) => void;
}) {
  const [hotels, setHotels] = useState<Hotel[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        const items = await listHotels(tripId);
        if (!cancelled) setHotels(items);
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
      const result = await searchHotels(tripId, { rooms: 1 });
      setHotels(result.items);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Search failed");
    } finally {
      setLoading(false);
    }
  }

  async function onSelect(hotelId: string) {
    setError(null);
    try {
      const result = await selectHotel(tripId, hotelId);
      setHotels((prev) => prev.map((h) => ({ ...h, selected: h.id === hotelId })));
      onBudgetChange(result.budget);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Select failed");
    }
  }

  return (
    <div className="space-y-4">
      <button
        type="button"
        onClick={() => void onSearch()}
        disabled={loading}
        className="rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-60"
      >
        {loading ? "Searching…" : "Search hotels"}
      </button>

      {error && <p className="rounded-lg bg-rose-50 px-4 py-3 text-sm text-rose-700">{error}</p>}

      {hotels.length === 0 ? (
        <p className="text-sm text-slate-500">No hotels yet. Run a search to see options.</p>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2">
          {hotels.map((hotel) => (
            <article
              key={hotel.id}
              className={`rounded-xl border bg-white p-4 ${
                hotel.selected ? "border-brand-500 ring-1 ring-brand-200" : "border-slate-200"
              }`}
            >
              <h3 className="font-semibold text-slate-900">{hotel.name}</h3>
              <p className="text-sm text-slate-500">{hotel.location}</p>
              <p className="mt-1 text-sm text-slate-600">
                ★ {hotel.rating ?? "—"} · ${hotel.price_per_night_usd}/night
              </p>
              <p className="text-lg font-bold text-slate-900">
                ${hotel.total_price_usd.toLocaleString()} total
              </p>
              {hotel.amenities && hotel.amenities.length > 0 && (
                <p className="mt-1 text-xs text-slate-500">{hotel.amenities.join(" · ")}</p>
              )}
              {hotel.cancellation_policy && (
                <p className="mt-1 text-xs text-slate-500">{hotel.cancellation_policy}</p>
              )}
              <div className="mt-3 flex items-center gap-3">
                <button
                  type="button"
                  onClick={() => void onSelect(hotel.id)}
                  className="rounded-lg bg-slate-900 px-3 py-1.5 text-xs font-medium text-white"
                >
                  {hotel.selected ? "Selected" : "Select"}
                </button>
                {hotel.booking_link && (
                  <a
                    href={hotel.booking_link}
                    target="_blank"
                    rel="noreferrer"
                    className="text-xs text-brand-600 hover:underline"
                  >
                    Booking link
                  </a>
                )}
              </div>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}
