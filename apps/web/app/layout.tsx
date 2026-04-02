import type { ReactNode } from "react";
import type { Metadata } from "next";
import Link from "next/link";

import "./globals.css";

export const metadata: Metadata = {
  title: "Omniweb",
  description: "Shopify AI sales and support assistant — by Omniweb.",
};

export default function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <div className="relative min-h-screen">
          <header className="sticky top-0 z-40 border-b border-white/8 bg-[#07111f]/90 backdrop-blur">
            <div className="mx-auto flex w-full max-w-[1600px] items-center justify-between px-6 py-3 xl:px-8">
              <Link href="/" className="flex items-center gap-3">
                <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-accent to-accent2 text-xs font-bold text-white shadow-glow">
                  OW
                </div>
                <span className="text-sm font-semibold text-white">Omniweb</span>
              </Link>
              <nav className="hidden items-center gap-1 md:flex">
                <Link href="/dashboard" className="rounded-lg px-3 py-1.5 text-sm text-slate-400 transition hover:bg-white/8 hover:text-white">Dashboard</Link>
                <Link href="/widget-demo" className="rounded-lg px-3 py-1.5 text-sm text-slate-400 transition hover:bg-white/8 hover:text-white">Widget Demo</Link>
              </nav>
            </div>
          </header>
          {children}
        </div>
      </body>
    </html>
  );
}
