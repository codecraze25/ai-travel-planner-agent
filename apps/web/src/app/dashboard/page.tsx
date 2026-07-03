import Link from "next/link";
import { TripDashboard } from "@/components/TripDashboard";

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      <div>
        <Link href="/" className="text-sm text-brand-600 hover:underline">
          ← Home
        </Link>
        <h1 className="mt-2 text-2xl font-bold text-slate-900">Dashboard</h1>
      </div>
      <TripDashboard />
    </div>
  );
}
