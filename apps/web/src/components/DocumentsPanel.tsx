"use client";

import { useEffect, useState } from "react";
import {
  deleteDocument,
  listDocuments,
  parseDocument,
  searchDocuments,
  uploadDocument,
  type DocumentCitation,
  type DocumentItem,
} from "@/lib/api";

export function DocumentsPanel({ tripId }: { tripId: string }) {
  const [docs, setDocs] = useState<DocumentItem[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [query, setQuery] = useState("check-in date");
  const [citations, setCitations] = useState<DocumentCitation[]>([]);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        const items = await listDocuments(tripId);
        if (!cancelled) setDocs(items);
      } catch {
        // empty until first upload
      }
    }
    void load();
    return () => {
      cancelled = true;
    };
  }, [tripId]);

  async function onUpload(fileList: FileList | null) {
    if (!fileList?.length) return;
    setBusy(true);
    setError(null);
    try {
      const file = fileList[0];
      const uploaded = await uploadDocument(tripId, file);
      const parsed = await parseDocument(tripId, uploaded.id);
      setDocs((prev) => [parsed, ...prev.filter((d) => d.id !== parsed.id)]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setBusy(false);
    }
  }

  async function onParse(documentId: string) {
    setBusy(true);
    setError(null);
    try {
      const parsed = await parseDocument(tripId, documentId);
      setDocs((prev) => prev.map((d) => (d.id === documentId ? parsed : d)));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Parse failed");
    } finally {
      setBusy(false);
    }
  }

  async function onDelete(documentId: string) {
    setBusy(true);
    setError(null);
    try {
      await deleteDocument(tripId, documentId);
      setDocs((prev) => prev.filter((d) => d.id !== documentId));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Delete failed");
    } finally {
      setBusy(false);
    }
  }

  async function onSearch() {
    setBusy(true);
    setError(null);
    try {
      const result = await searchDocuments(tripId, query);
      setCitations(result.citations);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Search failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="space-y-6">
      <div
        className="rounded-xl border-2 border-dashed border-slate-300 bg-white p-8 text-center"
        onDragOver={(e) => e.preventDefault()}
        onDrop={(e) => {
          e.preventDefault();
          void onUpload(e.dataTransfer.files);
        }}
      >
        <p className="text-sm font-medium text-slate-800">Upload a travel PDF</p>
        <p className="mt-1 text-xs text-slate-500">
          Confirmations, policies, agendas — max 20 MB. Parsed automatically.
        </p>
        <label className="mt-4 inline-block cursor-pointer rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700">
          {busy ? "Working…" : "Choose PDF"}
          <input
            type="file"
            accept="application/pdf,.pdf"
            className="hidden"
            disabled={busy}
            onChange={(e) => void onUpload(e.target.files)}
          />
        </label>
      </div>

      {error && <p className="rounded-lg bg-rose-50 px-4 py-3 text-sm text-rose-700">{error}</p>}

      {docs.length === 0 ? (
        <p className="text-sm text-slate-500">No documents yet.</p>
      ) : (
        <ul className="space-y-3">
          {docs.map((doc) => (
            <li key={doc.id} className="rounded-xl border border-slate-200 bg-white p-4">
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <p className="font-semibold text-slate-900">{doc.filename}</p>
                  <p className="text-xs capitalize text-slate-500">
                    status: {doc.status}
                    {doc.injection_flagged ? " · injection patterns redacted" : ""}
                  </p>
                  {doc.error_message && (
                    <p className="mt-1 text-xs text-rose-600">{doc.error_message}</p>
                  )}
                  {doc.extracted_fields && (
                    <div className="mt-2 space-y-1 text-sm text-slate-700">
                      {doc.extracted_fields.check_in && (
                        <p>
                          <span className="font-medium">Check-in:</span>{" "}
                          {doc.extracted_fields.check_in}
                          {doc.extracted_fields.times[0]
                            ? ` at ${doc.extracted_fields.times[0]}`
                            : ""}
                        </p>
                      )}
                      {doc.extracted_fields.check_out && (
                        <p>
                          <span className="font-medium">Check-out:</span>{" "}
                          {doc.extracted_fields.check_out}
                        </p>
                      )}
                      {doc.extracted_fields.confirmation_codes.length > 0 && (
                        <p>
                          <span className="font-medium">Confirmation:</span>{" "}
                          {doc.extracted_fields.confirmation_codes.join(", ")}
                        </p>
                      )}
                      <p className="text-xs text-slate-400">
                        Source: {doc.filename} (extracted facts)
                      </p>
                    </div>
                  )}
                </div>
                <div className="flex gap-2">
                  {doc.status !== "ready" && (
                    <button
                      type="button"
                      disabled={busy}
                      onClick={() => void onParse(doc.id)}
                      className="rounded-lg border border-slate-300 px-3 py-1.5 text-xs"
                    >
                      Parse
                    </button>
                  )}
                  <button
                    type="button"
                    disabled={busy}
                    onClick={() => void onDelete(doc.id)}
                    className="rounded-lg border border-rose-200 px-3 py-1.5 text-xs text-rose-700"
                  >
                    Delete
                  </button>
                </div>
              </div>
            </li>
          ))}
        </ul>
      )}

      <div className="rounded-xl border border-slate-200 bg-white p-4 space-y-3">
        <p className="text-sm font-semibold text-slate-900">Search documents (RAG)</p>
        <div className="flex flex-wrap gap-2">
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="min-w-[200px] flex-1 rounded-lg border border-slate-300 px-3 py-2 text-sm"
            placeholder="e.g. check-in date"
          />
          <button
            type="button"
            disabled={busy}
            onClick={() => void onSearch()}
            className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white"
          >
            Search
          </button>
        </div>
        {citations.length > 0 && (
          <ul className="space-y-2 text-sm">
            {citations.map((c) => (
              <li key={`${c.document_id}-${c.chunk_index}`} className="rounded-lg bg-slate-50 p-3">
                <p className="text-xs font-medium text-brand-700">
                  Source: {c.filename} (chunk {c.chunk_index}, score {c.score})
                </p>
                <p className="mt-1 text-slate-700 whitespace-pre-wrap">{c.content}</p>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
