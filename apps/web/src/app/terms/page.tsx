import Link from "next/link";

export default function TermsPage() {
  return (
    <article className="prose prose-slate max-w-none space-y-4">
      <Link href="/" className="text-sm text-brand-600 hover:underline">
        ← Home
      </Link>
      <h1 className="text-2xl font-bold text-slate-900">Terms of Use</h1>
      <p className="text-slate-600">
        Placeholder for MVP. This assistant helps plan trips and does not book hotels or send email
        without explicit user approval. Flight and hotel results may use mock providers in local
        development.
      </p>
      <p className="text-slate-600">
        Booking links open third-party sites. You are responsible for purchases made outside this
        app.
      </p>
    </article>
  );
}
