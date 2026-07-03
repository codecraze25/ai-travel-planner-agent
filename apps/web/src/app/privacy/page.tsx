import Link from "next/link";

export default function PrivacyPage() {
  return (
    <article className="prose prose-slate max-w-none space-y-4">
      <Link href="/" className="text-sm text-brand-600 hover:underline">
        ← Home
      </Link>
      <h1 className="text-2xl font-bold text-slate-900">Privacy Policy</h1>
      <p className="text-slate-600">
        Placeholder for MVP. Trip data is stored in your local or configured database. Uploaded
        PDFs are treated as untrusted input and are not used to authorize actions without your
        approval.
      </p>
      <p className="text-slate-600">
        No emails are sent automatically. Approved drafts can only be exported as <code>.eml</code>{" "}
        files in this MVP.
      </p>
    </article>
  );
}
