"use client";

import { useCallback, useEffect, useState } from "react";
import {
  approveEmail,
  draftEmail,
  exportEmail,
  getLatestEmail,
  rejectEmail,
  updateEmail,
  type EmailDraft,
} from "@/lib/api";

export function EmailPanel({ tripId }: { tripId: string }) {
  const [email, setEmail] = useState<EmailDraft | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [confirmAction, setConfirmAction] = useState<"approve" | "reject" | null>(null);
  const [toast, setToast] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      const data = await getLatestEmail(tripId);
      setEmail(data);
    } catch {
      setEmail(null);
    }
  }, [tripId]);

  useEffect(() => {
    void load();
  }, [load]);

  function showToast(message: string) {
    setToast(message);
    window.setTimeout(() => setToast(null), 3000);
  }

  async function onDraft(template: "itinerary_summary" | "family_share") {
    setLoading(true);
    setError(null);
    try {
      const data = await draftEmail(tripId, template);
      setEmail(data);
      showToast("Draft created");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Draft failed");
    } finally {
      setLoading(false);
    }
  }

  async function onSave() {
    if (!email) return;
    setLoading(true);
    setError(null);
    try {
      const data = await updateEmail(tripId, email.id, {
        recipients: email.recipients,
        subject: email.subject,
        body_text: email.body_text,
        body_html: email.body_html,
      });
      setEmail(data);
      showToast("Draft saved");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Save failed");
    } finally {
      setLoading(false);
    }
  }

  async function onConfirm() {
    if (!email || !confirmAction) return;
    setLoading(true);
    setError(null);
    try {
      const data =
        confirmAction === "approve"
          ? await approveEmail(tripId, email.id)
          : await rejectEmail(tripId, email.id);
      setEmail(data);
      showToast(confirmAction === "approve" ? "Email approved" : "Email rejected");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Action failed");
    } finally {
      setLoading(false);
      setConfirmAction(null);
    }
  }

  async function onExport() {
    if (!email) return;
    setLoading(true);
    setError(null);
    try {
      const result = await exportEmail(tripId, email.id);
      setEmail(result.email);
      const blob = new Blob([result.eml], { type: "message/rfc822" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = result.filename;
      a.click();
      URL.revokeObjectURL(url);
      showToast("Downloaded .eml (not sent via SMTP)");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Export blocked — approve first");
    } finally {
      setLoading(false);
    }
  }

  const editable = email?.status === "draft" || email?.status === "rejected";

  return (
    <section className="space-y-4">
      {toast && (
        <p className="rounded-lg bg-emerald-50 px-3 py-2 text-sm text-emerald-800">{toast}</p>
      )}
      {error && <p className="rounded-lg bg-rose-50 px-3 py-2 text-sm text-rose-700">{error}</p>}

      <div className="flex flex-wrap gap-2">
        <button
          type="button"
          disabled={loading}
          onClick={() => void onDraft("itinerary_summary")}
          className="rounded-lg bg-brand-600 px-3 py-1.5 text-sm font-medium text-white disabled:opacity-50"
        >
          Draft itinerary email
        </button>
        <button
          type="button"
          disabled={loading}
          onClick={() => void onDraft("family_share")}
          className="rounded-lg border border-slate-300 px-3 py-1.5 text-sm text-slate-700 disabled:opacity-50"
        >
          Draft family share
        </button>
      </div>

      {!email ? (
        <div className="rounded-xl border border-dashed border-slate-300 bg-white p-8 text-center text-sm text-slate-500">
          No email draft yet. Generate an itinerary, then draft an email — or use Chat (“Plan my
          trip”).
        </div>
      ) : (
        <div className="space-y-3 rounded-xl border border-slate-200 bg-white p-4">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <span className="rounded-full bg-slate-100 px-2 py-0.5 text-xs font-medium capitalize text-slate-700">
              {email.status}
            </span>
            <p className="text-xs text-slate-400">Template: {email.template.replace("_", " ")}</p>
          </div>

          <label className="block text-sm">
            <span className="text-slate-600">To</span>
            <input
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2"
              value={email.recipients}
              disabled={!editable || loading}
              onChange={(e) => setEmail({ ...email, recipients: e.target.value })}
            />
          </label>

          <label className="block text-sm">
            <span className="text-slate-600">Subject</span>
            <input
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2"
              value={email.subject}
              disabled={!editable || loading}
              onChange={(e) => setEmail({ ...email, subject: e.target.value })}
            />
          </label>

          <label className="block text-sm">
            <span className="text-slate-600">Body</span>
            <textarea
              className="mt-1 min-h-[180px] w-full rounded-lg border border-slate-300 px-3 py-2 font-mono text-xs"
              value={email.body_text}
              disabled={!editable || loading}
              onChange={(e) =>
                setEmail({
                  ...email,
                  body_text: e.target.value,
                  body_html: `<pre>${e.target.value}</pre>`,
                })
              }
            />
          </label>

          <div className="flex flex-wrap gap-2 border-t border-slate-100 pt-3">
            {editable && (
              <button
                type="button"
                disabled={loading}
                onClick={() => void onSave()}
                className="rounded-lg border border-slate-300 px-3 py-1.5 text-sm disabled:opacity-50"
              >
                Save edits
              </button>
            )}
            {email.status === "draft" && (
              <>
                <button
                  type="button"
                  disabled={loading}
                  onClick={() => setConfirmAction("approve")}
                  className="rounded-lg bg-emerald-600 px-3 py-1.5 text-sm font-medium text-white disabled:opacity-50"
                >
                  Approve
                </button>
                <button
                  type="button"
                  disabled={loading}
                  onClick={() => setConfirmAction("reject")}
                  className="rounded-lg bg-rose-600 px-3 py-1.5 text-sm font-medium text-white disabled:opacity-50"
                >
                  Reject
                </button>
              </>
            )}
            {(email.status === "approved" || email.status === "exported") && (
              <button
                type="button"
                disabled={loading}
                onClick={() => void onExport()}
                className="rounded-lg bg-brand-600 px-3 py-1.5 text-sm font-medium text-white disabled:opacity-50"
              >
                Download .eml
              </button>
            )}
          </div>

          <p className="text-xs text-slate-500">
            Guardrail: nothing is sent over SMTP. Approve, then download a .eml file to send
            yourself.
          </p>
        </div>
      )}

      {confirmAction && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
          <div className="w-full max-w-sm rounded-xl bg-white p-5 shadow-lg">
            <h3 className="font-semibold text-slate-900">
              {confirmAction === "approve" ? "Approve this email?" : "Reject this email?"}
            </h3>
            <p className="mt-2 text-sm text-slate-600">
              {confirmAction === "approve"
                ? "Approval unlocks .eml export only. No message is sent automatically."
                : "You can edit and draft again after rejecting."}
            </p>
            <div className="mt-4 flex justify-end gap-2">
              <button
                type="button"
                className="rounded-lg border border-slate-300 px-3 py-1.5 text-sm"
                onClick={() => setConfirmAction(null)}
              >
                Cancel
              </button>
              <button
                type="button"
                className="rounded-lg bg-brand-600 px-3 py-1.5 text-sm font-medium text-white"
                onClick={() => void onConfirm()}
              >
                Confirm
              </button>
            </div>
          </div>
        </div>
      )}
    </section>
  );
}
