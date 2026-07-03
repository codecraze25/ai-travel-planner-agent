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
              <nav className="flex items-center gap-3 text-sm">
                <a href="/dashboard" className="text-slate-600 hover:text-brand-700">
                  Dashboard
                </a>
                <a href="/privacy" className="text-slate-500 hover:text-brand-700">
                  Privacy
                </a>
                <a href="/terms" className="text-slate-500 hover:text-brand-700">
                  Terms
                </a>
                <span className="rounded-full bg-brand-50 px-3 py-1 text-xs font-medium text-brand-700">
                  MVP
                </span>
              </nav>
            </div>
          </header>
          <main className="mx-auto max-w-5xl px-6 py-10">{children}</main>
          <footer className="border-t border-slate-200 py-6 text-center text-xs text-slate-400">
            AI Travel Planner — no auto-booking, no auto-send.
          </footer>
        </div>
      </body>
    </html>
  );
}
