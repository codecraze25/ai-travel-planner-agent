import Link from "next/link";
import { NewTripForm } from "@/components/NewTripForm";

export default function NewTripPage() {
  return (
    <div className="space-y-6">
      <div>
        <Link href="/dashboard" className="text-sm text-brand-600 hover:underline">
          ← Dashboard
        </Link>
        <h1 className="mt-2 text-2xl font-bold text-slate-900">New trip</h1>
        <p className="text-sm text-slate-500">Plan a trip with origin, dates, budget, and preferences.</p>
      </div>
      <NewTripForm />
    </div>
  );
}
