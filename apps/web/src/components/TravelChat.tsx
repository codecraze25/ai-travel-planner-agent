"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import {
  approveEmail,
  selectFlight,
  selectHotel,
  sendEmail,
  streamSessionChat,
  type AgentStreamEvent,
  type EmailDraft,
} from "@/lib/api";

interface TripSummary {
  id: string;
  origin: string;
  destination: string;
  start_date: string;
  end_date: string;
  travelers: number;
  budget_usd: number;
}

interface FlightItem {
  id: string;
  airline: string;
  flight_number: string;
  departure_time: string;
  arrival_time: string;
  duration_minutes: number;
  stops: number;
  price_usd: number;
}

interface HotelItem {
  id: string;
  name: string;
  location?: string | null;
  total_price_usd: number;
  rating?: number | null;
}

type ChatBlock =
  | { kind: "text"; role: "user" | "assistant"; content: string }
  | { kind: "flights"; items: FlightItem[] }
  | { kind: "hotels"; items: HotelItem[] }
  | { kind: "itinerary"; days: number; total: number }
  | { kind: "email"; email: EmailDraft };

const SUGGESTIONS = [
  "Plan San Francisco to Tokyo 2026-10-10 to 2026-10-15 for 2 travelers $4000",
  "Plan New York to Paris 2026-11-01 to 2026-11-05 for 1 traveler $2500",
];

export function TravelChat() {
  const [blocks, setBlocks] = useState<ChatBlock[]>([
    {
      kind: "text",
      role: "assistant",
      content:
        "Book a trip in one sentence. Tell me where, when, and your budget — I'll handle flights, hotels, and the itinerary here.",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [trip, setTrip] = useState<TripSummary | null>(null);
  const [status, setStatus] = useState<string | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);
  const abortRef = useRef<AbortController | null>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [blocks, status]);

  const handleEvent = useCallback((event: AgentStreamEvent) => {
    if (event.type === "trip" && event.data) {
      setTrip(event.data as TripSummary);
      return;
    }
    if (event.type === "message" && event.content) {
      setBlocks((prev) => [
        ...prev,
        { kind: "text", role: "assistant", content: event.content! },
      ]);
      setStatus(null);
      return;
    }
    if (event.type === "tool_call" && event.tool) {
      const labels: Record<string, string> = {
        search_flights: "Searching flights…",
        search_hotels: "Searching hotels…",
        calculate_budget: "Checking budget…",
        generate_itinerary: "Building itinerary…",
        draft_email: "Drafting email…",
      };
      setStatus(labels[event.tool] ?? `Running ${event.tool}…`);
      return;
    }
    if (event.type === "tool_result" && event.tool === "search_flights") {
      const output = event.output as { items?: FlightItem[] };
      if (output?.items?.length) {
        setBlocks((prev) => [...prev, { kind: "flights", items: output.items! }]);
      }
      return;
    }
    if (event.type === "tool_result" && event.tool === "search_hotels") {
      const output = event.output as { items?: HotelItem[] };
      if (output?.items?.length) {
        setBlocks((prev) => [...prev, { kind: "hotels", items: output.items! }]);
      }
      return;
    }
    if (event.type === "itinerary" && event.data) {
      const data = event.data as {
        items?: { day_number: number }[];
        total_est_cost_usd?: number;
      };
      const days = new Set((data.items ?? []).map((i) => i.day_number)).size;
      setBlocks((prev) => [
        ...prev,
        { kind: "itinerary", days, total: data.total_est_cost_usd ?? 0 },
      ]);
      return;
    }
    if (event.type === "email_draft" && event.data) {
      setBlocks((prev) => [...prev, { kind: "email", email: event.data as EmailDraft }]);
    }
  }, []);

  async function onSend(text: string) {
    const message = text.trim();
    if (!message || loading) return;

    setBlocks((prev) => [...prev, { kind: "text", role: "user", content: message }]);
    setInput("");
    setLoading(true);
    setStatus(null);
    abortRef.current?.abort();
    abortRef.current = new AbortController();

    try {
      await streamSessionChat(message, handleEvent, abortRef.current.signal, trip?.id);
    } catch (err) {
      if (err instanceof Error && err.name !== "AbortError") {
        setBlocks((prev) => [
          ...prev,
          { kind: "text", role: "assistant", content: `Something went wrong: ${err.message}` },
        ]);
      }
    } finally {
      setLoading(false);
      setStatus(null);
    }
  }

  async function onSelectFlight(flightId: string) {
    if (!trip) return;
    try {
      await selectFlight(trip.id, flightId);
      setBlocks((prev) => [
        ...prev,
        { kind: "text", role: "assistant", content: "Flight selected." },
      ]);
    } catch (err) {
      setBlocks((prev) => [
        ...prev,
        {
          kind: "text",
          role: "assistant",
          content: err instanceof Error ? err.message : "Could not select flight",
        },
      ]);
    }
  }

  async function onSelectHotel(hotelId: string) {
    if (!trip) return;
    try {
      await selectHotel(trip.id, hotelId);
      setBlocks((prev) => [
        ...prev,
        { kind: "text", role: "assistant", content: "Hotel selected." },
      ]);
    } catch (err) {
      setBlocks((prev) => [
        ...prev,
        {
          kind: "text",
          role: "assistant",
          content: err instanceof Error ? err.message : "Could not select hotel",
        },
      ]);
    }
  }

  async function onApproveEmail(emailId: string) {
    if (!trip) return;
    try {
      const email = await approveEmail(trip.id, emailId);
      setBlocks((prev) =>
        prev.map((b) => (b.kind === "email" && b.email.id === emailId ? { ...b, email } : b)),
      );
      setBlocks((prev) => [
        ...prev,
        {
          kind: "text",
          role: "assistant",
          content: "Email approved. Tap Send when you are ready.",
        },
      ]);
    } catch (err) {
      setBlocks((prev) => [
        ...prev,
        {
          kind: "text",
          role: "assistant",
          content: err instanceof Error ? err.message : "Approve failed",
        },
      ]);
    }
  }

  async function onSendEmail(emailId: string) {
    if (!trip) return;
    try {
      const result = await sendEmail(trip.id, emailId);
      setBlocks((prev) =>
        prev.map((b) =>
          b.kind === "email" && b.email.id === emailId ? { ...b, email: result.email } : b,
        ),
      );
      setBlocks((prev) => [
        ...prev,
        {
          kind: "text",
          role: "assistant",
          content: result.mock
            ? `Mock send recorded (${result.message_id}).`
            : `Sent via ${result.provider}.`,
        },
      ]);
    } catch (err) {
      setBlocks((prev) => [
        ...prev,
        {
          kind: "text",
          role: "assistant",
          content: err instanceof Error ? err.message : "Send failed",
        },
      ]);
    }
  }

  return (
    <div className="flex h-[calc(100vh-3.5rem)] flex-col">
      {trip && (
        <div className="border-b border-slate-200 bg-white px-4 py-2 text-center text-xs text-slate-500">
          {trip.origin} → {trip.destination} · {trip.start_date} – {trip.end_date} ·{" "}
          {trip.travelers} traveler(s) · ${trip.budget_usd.toLocaleString()}
        </div>
      )}

      <div className="mx-auto flex w-full max-w-2xl flex-1 flex-col overflow-hidden">
        <div className="flex-1 space-y-4 overflow-y-auto px-4 py-6">
          {blocks.map((block, i) => (
            <div key={i}>
              {block.kind === "text" && (
                <div
                  className={`max-w-[90%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                    block.role === "user"
                      ? "ml-auto bg-brand-600 text-white"
                      : "bg-white text-slate-800 shadow-sm ring-1 ring-slate-200"
                  }`}
                >
                  {block.content}
                </div>
              )}

              {block.kind === "flights" && (
                <div className="space-y-2">
                  <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                    Flights
                  </p>
                  {block.items.map((f) => (
                    <div
                      key={f.id}
                      className="flex items-center justify-between gap-3 rounded-xl bg-white p-3 text-sm shadow-sm ring-1 ring-slate-200"
                    >
                      <div>
                        <p className="font-medium text-slate-900">
                          {f.airline} {f.flight_number}
                        </p>
                        <p className="text-xs text-slate-500">
                          {f.stops === 0 ? "Nonstop" : `${f.stops} stop(s)`} · $
                          {f.price_usd.toLocaleString()}
                        </p>
                      </div>
                      <button
                        type="button"
                        onClick={() => void onSelectFlight(f.id)}
                        className="shrink-0 rounded-lg bg-slate-900 px-3 py-1.5 text-xs font-medium text-white"
                      >
                        Select
                      </button>
                    </div>
                  ))}
                </div>
              )}

              {block.kind === "hotels" && (
                <div className="space-y-2">
                  <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                    Hotels
                  </p>
                  {block.items.map((h) => (
                    <div
                      key={h.id}
                      className="flex items-center justify-between gap-3 rounded-xl bg-white p-3 text-sm shadow-sm ring-1 ring-slate-200"
                    >
                      <div>
                        <p className="font-medium text-slate-900">{h.name}</p>
                        <p className="text-xs text-slate-500">
                          {h.location ?? "City center"} · ${h.total_price_usd.toLocaleString()}
                        </p>
                      </div>
                      <button
                        type="button"
                        onClick={() => void onSelectHotel(h.id)}
                        className="shrink-0 rounded-lg bg-slate-900 px-3 py-1.5 text-xs font-medium text-white"
                      >
                        Select
                      </button>
                    </div>
                  ))}
                </div>
              )}

              {block.kind === "itinerary" && (
                <div className="rounded-xl bg-emerald-50 px-4 py-3 text-sm text-emerald-900 ring-1 ring-emerald-100">
                  {block.days}-day itinerary ready · est. activities $
                  {block.total.toLocaleString()}
                </div>
              )}

              {block.kind === "email" && (
                <div className="space-y-2 rounded-xl bg-white p-4 text-sm shadow-sm ring-1 ring-slate-200">
                  <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                    Email · {block.email.status}
                  </p>
                  <p className="font-medium text-slate-900">{block.email.subject}</p>
                  <p className="text-xs text-slate-500">To: {block.email.recipients}</p>
                  <pre className="max-h-32 overflow-y-auto whitespace-pre-wrap rounded-lg bg-slate-50 p-2 text-xs text-slate-600">
                    {block.email.body_text}
                  </pre>
                  <div className="flex flex-wrap gap-2">
                    {block.email.status === "draft" && (
                      <button
                        type="button"
                        onClick={() => void onApproveEmail(block.email.id)}
                        className="rounded-lg bg-emerald-600 px-3 py-1.5 text-xs font-medium text-white"
                      >
                        Approve
                      </button>
                    )}
                    {(block.email.status === "approved" ||
                      block.email.status === "exported") && (
                      <button
                        type="button"
                        onClick={() => void onSendEmail(block.email.id)}
                        className="rounded-lg bg-brand-600 px-3 py-1.5 text-xs font-medium text-white"
                      >
                        Send (mock)
                      </button>
                    )}
                  </div>
                </div>
              )}
            </div>
          ))}

          {status && <p className="text-xs italic text-slate-400">{status}</p>}
          <div ref={bottomRef} />
        </div>

        {!loading && blocks.length <= 1 && (
          <div className="flex flex-wrap gap-2 px-4 pb-2">
            {SUGGESTIONS.map((s) => (
              <button
                key={s}
                type="button"
                onClick={() => void onSend(s)}
                className="rounded-full border border-slate-200 bg-white px-3 py-1.5 text-left text-xs text-slate-600 hover:border-brand-300 hover:text-brand-700"
              >
                {s}
              </button>
            ))}
          </div>
        )}

        <form
          onSubmit={(e) => {
            e.preventDefault();
            void onSend(input);
          }}
          className="border-t border-slate-200 bg-white p-4"
        >
          <div className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Describe your trip in one sentence…"
              className="flex-1 rounded-xl border border-slate-300 px-4 py-3 text-sm outline-none focus:border-brand-500 focus:ring-2 focus:ring-brand-100"
              disabled={loading}
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="rounded-xl bg-brand-600 px-5 py-3 text-sm font-medium text-white disabled:opacity-50"
            >
              {loading ? "…" : "Send"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
