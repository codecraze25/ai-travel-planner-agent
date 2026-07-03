import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Travel Agent",
  description: "Plan a trip in one sentence.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-slate-50 text-slate-900 antialiased">
        <header className="flex h-14 items-center border-b border-slate-200 bg-white px-4">
          <a href="/" className="text-sm font-semibold tracking-tight text-slate-900">
            Travel Agent
          </a>
        </header>
        <main>{children}</main>
      </body>
    </html>
  );
}
