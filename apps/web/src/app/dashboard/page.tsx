import Link from "next/link";
import { TripDashboard } from "@/components/TripDashboard";

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      <div>
        <Link href="/" className="text-sm text-brand-600 hover:underline">
          ← Home
        </Link>
        <div className="mt-2 flex flex-wrap items-end justify-between gap-3">
          <h1 className="text-2xl font-bold text-slate-900">Dashboard</h1>
          <Link
            href="/profile"
            className="text-sm font-medium text-brand-600 hover:underline"
          >
            Traveler profile
          </Link>
        </div>
      </div>
      <TripDashboard />
    </div>
  );
}
