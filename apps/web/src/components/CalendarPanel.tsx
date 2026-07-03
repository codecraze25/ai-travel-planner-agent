"use client";

import { useCallback, useEffect, useState } from "react";
import { getCalendar, type CalendarEvent } from "@/lib/api";

export function CalendarPanel({ tripId }: { tripId: string }) {
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [source, setSource] = useState<string>("");
  const [note, setNote] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      const data = await getCalendar(tripId);
      setEvents(data.items);
      setSource(data.source);
      setNote(data.note ?? null);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load calendar");
    }
  }, [tripId]);

  useEffect(() => {
    void load();
  }, [load]);

  if (error) {
    return <p className="text-sm text-rose-600">{error}</p>;
  }

  return (
    <div className="space-y-2">
      <p className="text-xs text-slate-500">
        Source: {source || "…"}
        {note ? ` — ${note}` : ""}
      </p>
      {events.length === 0 ? (
        <p className="text-sm text-slate-500">No calendar events.</p>
      ) : (
        <ul className="space-y-2">
          {events.map((event) => (
            <li
              key={`${event.title}-${event.start}`}
              className="rounded-lg bg-slate-50 px-3 py-2 text-sm"
            >
              <p className="font-medium text-slate-800">{event.title}</p>
              <p className="text-xs text-slate-500">
                {event.start} → {event.end}
              </p>
              <p className="text-xs text-slate-500">{event.location}</p>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
