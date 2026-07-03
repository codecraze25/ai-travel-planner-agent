"use client";

import { useCallback, useRef, useState } from "react";
import { streamAgentChat, type AgentStreamEvent } from "@/lib/api";

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export function ChatPanel({ tripId }: { tripId: string }) {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: "assistant",
      content: "Hi! Ask me to plan your trip, or ask about uploaded PDF confirmations.",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [toolActivity, setToolActivity] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  const handleEvent = useCallback((event: AgentStreamEvent) => {
    if (event.type === "message" && event.content) {
      setMessages((prev) => [...prev, { role: "assistant", content: event.content! }]);
      setToolActivity(null);
    }
    if (event.type === "tool_call" && event.tool) {
      setToolActivity(`Running ${event.tool}…`);
    }
    if (event.type === "itinerary") {
      setToolActivity("Itinerary generated — see Itinerary tab.");
    }
  }, []);

  async function onSend(e: React.FormEvent) {
    e.preventDefault();
    const text = input.trim();
    if (!text || loading) return;

    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setInput("");
    setLoading(true);
    setToolActivity(null);

    abortRef.current?.abort();
    abortRef.current = new AbortController();

    try {
      await streamAgentChat(tripId, text, handleEvent, abortRef.current.signal);
    } catch (err) {
      if (err instanceof Error && err.name !== "AbortError") {
        setMessages((prev) => [
          ...prev,
          { role: "assistant", content: `Error: ${err.message}` },
        ]);
      }
    } finally {
      setLoading(false);
      setToolActivity(null);
    }
  }

  return (
    <section className="flex flex-col rounded-xl border border-slate-200 bg-white">
      <div className="flex-1 space-y-3 overflow-y-auto p-4 min-h-[280px] max-h-[420px]">
        {messages.map((msg, i) => (
          <div
            key={`${msg.role}-${i}`}
            className={`rounded-lg px-3 py-2 text-sm max-w-[85%] ${
              msg.role === "user"
                ? "ml-auto bg-brand-600 text-white"
                : "bg-slate-100 text-slate-800"
            }`}
          >
            {msg.content}
          </div>
        ))}
        {toolActivity && (
          <p className="text-xs text-slate-500 italic">{toolActivity}</p>
        )}
      </div>
      <form onSubmit={onSend} className="flex gap-2 border-t border-slate-200 p-3">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder='Try "Plan my trip"'
          className="flex-1 rounded-lg border border-slate-300 px-3 py-2 text-sm"
          disabled={loading}
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          className="rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
        >
          {loading ? "…" : "Send"}
        </button>
      </form>
    </section>
  );
}
