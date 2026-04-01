import type { ReactNode } from "react";
import type { Metadata } from "next";
import Link from "next/link";

import "./globals.css";

export const metadata: Metadata = {
  title: "OmniNew | Shopify AI Assistant",
  description: "Shopify-focused AI sales and support assistant dashboard and widget.",
};

export default function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <div className="relative min-h-screen">
          <header className="sticky top-0 z-40 border-b border-white/10 bg-[#07111f]/85 backdrop-blur">
            <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
              <Link href="/" className="flex items-center gap-3 font-semibold tracking-tight">
                <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-gradient-to-br from-accent to-accent2 text-sm text-white shadow-glow">
                  ON
                </div>
                <div>
                  <div className="text-base text-white">OmniNew</div>
                  <div className="text-xs text-slate-400">Shopify AI conversions + support</div>
                </div>
              </Link>
              <nav className="hidden items-center gap-6 text-sm text-slate-300 md:flex">
                <Link href="/dashboard">Dashboard</Link>
                <Link href="/widget-demo">Widget Demo</Link>
              </nav>
            </div>
          </header>
          {children}
        </div>
      </body>
    </html>
  );
}
