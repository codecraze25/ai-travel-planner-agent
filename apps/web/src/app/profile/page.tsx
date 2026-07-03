"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { getProfile, upsertProfile, type TravelerProfile } from "@/lib/api";

export default function ProfilePage() {
  const [profile, setProfile] = useState<TravelerProfile | null>(null);
  const [fullName, setFullName] = useState("");
  const [nationality, setNationality] = useState("");
  const [dateOfBirth, setDateOfBirth] = useState("");
  const [passportNumber, setPassportNumber] = useState("");
  const [passportExpiry, setPassportExpiry] = useState("");
  const [hotelPrefs, setHotelPrefs] = useState("");
  const [flightPrefs, setFlightPrefs] = useState("");
  const [clearPassport, setClearPassport] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [toast, setToast] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        const data = await getProfile();
        if (cancelled) return;
        setProfile(data);
        setFullName(data.full_name);
        setNationality(data.nationality ?? "");
        setDateOfBirth(data.date_of_birth ?? "");
        setPassportExpiry(data.passport_expiry ?? "");
        setHotelPrefs(data.preferences?.hotel_prefs ?? "");
        setFlightPrefs(data.preferences?.flight_prefs ?? "");
      } catch {
        // no profile yet
      }
    }
    void load();
    return () => {
      cancelled = true;
    };
  }, []);

  async function onSave(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const data = await upsertProfile({
        full_name: fullName,
        nationality: nationality || null,
        date_of_birth: dateOfBirth || null,
        passport_number: clearPassport ? null : passportNumber || null,
        clear_passport: clearPassport,
        passport_expiry: passportExpiry || null,
        preferences: {
          hotel_prefs: hotelPrefs || undefined,
          flight_prefs: flightPrefs || undefined,
        },
      });
      setProfile(data);
      setPassportNumber("");
      setClearPassport(false);
      setToast("Profile saved. Passport is encrypted at rest.");
      window.setTimeout(() => setToast(null), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Save failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-xl space-y-6">
      <div>
        <Link href="/dashboard" className="text-sm text-brand-600 hover:underline">
          ← Dashboard
        </Link>
        <h1 className="mt-2 text-2xl font-bold text-slate-900">Traveler profile</h1>
        <p className="text-sm text-slate-500">
          Passport numbers are encrypted at rest and only shown masked (last 4 characters).
        </p>
      </div>

      {toast && (
        <p className="rounded-lg bg-emerald-50 px-3 py-2 text-sm text-emerald-800">{toast}</p>
      )}
      {error && <p className="rounded-lg bg-rose-50 px-3 py-2 text-sm text-rose-700">{error}</p>}

      <form onSubmit={onSave} className="space-y-4 rounded-xl border border-slate-200 bg-white p-6">
        <label className="block text-sm">
          <span className="font-medium text-slate-700">Full name</span>
          <input
            required
            className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
          />
        </label>

        <label className="block text-sm">
          <span className="font-medium text-slate-700">Nationality</span>
          <input
            className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2"
            value={nationality}
            onChange={(e) => setNationality(e.target.value)}
          />
        </label>

        <div className="grid gap-4 sm:grid-cols-2">
          <label className="block text-sm">
            <span className="font-medium text-slate-700">Date of birth</span>
            <input
              type="date"
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2"
              value={dateOfBirth}
              onChange={(e) => setDateOfBirth(e.target.value)}
            />
          </label>
          <label className="block text-sm">
            <span className="font-medium text-slate-700">Passport expiry</span>
            <input
              type="date"
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2"
              value={passportExpiry}
              onChange={(e) => setPassportExpiry(e.target.value)}
            />
          </label>
        </div>

        <div className="rounded-lg bg-slate-50 p-3 text-sm">
          <p className="font-medium text-slate-700">Passport number</p>
          {profile?.has_passport ? (
            <p className="mt-1 text-slate-600">
              On file: <span className="font-mono">{profile.passport_masked}</span>
            </p>
          ) : (
            <p className="mt-1 text-slate-500">No passport stored yet.</p>
          )}
          <input
            className="mt-2 w-full rounded-lg border border-slate-300 px-3 py-2 font-mono"
            placeholder="Enter to update (never shown in full after save)"
            value={passportNumber}
            onChange={(e) => setPassportNumber(e.target.value)}
            autoComplete="off"
          />
          {profile?.has_passport && (
            <label className="mt-2 flex items-center gap-2 text-xs text-slate-600">
              <input
                type="checkbox"
                checked={clearPassport}
                onChange={(e) => setClearPassport(e.target.checked)}
              />
              Remove stored passport
            </label>
          )}
        </div>

        <label className="block text-sm">
          <span className="font-medium text-slate-700">Default hotel preferences</span>
          <input
            className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2"
            value={hotelPrefs}
            onChange={(e) => setHotelPrefs(e.target.value)}
            placeholder="e.g. near transit, quiet"
          />
        </label>

        <label className="block text-sm">
          <span className="font-medium text-slate-700">Default flight preferences</span>
          <input
            className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2"
            value={flightPrefs}
            onChange={(e) => setFlightPrefs(e.target.value)}
            placeholder="e.g. nonstop, aisle"
          />
        </label>

        <button
          type="submit"
          disabled={loading || !fullName.trim()}
          className="rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
        >
          {loading ? "Saving…" : "Save profile"}
        </button>
      </form>
    </div>
  );
}
