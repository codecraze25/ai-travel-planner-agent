import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI Travel Planner",
  description: "Plan trips with flights, hotels, documents, and AI itineraries.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="min-h-screen">
          <header className="border-b border-slate-200 bg-white">
            <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-4">
              <div>
                <p className="text-xs font-semibold uppercase tracking-wider text-brand-600">
                  AI Travel Planner
                </p>
                <h1 className="text-xl font-bold text-slate-900">Assistant</h1>
              </div>
              <span className="rounded-full bg-brand-50 px-3 py-1 text-xs font-medium text-brand-700">
                Phase 1
              </span>
            </div>
          </header>
          <main className="mx-auto max-w-5xl px-6 py-10">{children}</main>
        </div>
      </body>
    </html>
  );
}
