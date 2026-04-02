import type { ReactNode } from "react";

import { DashboardSidebar } from "@/components/layout/dashboard-sidebar";

export default function DashboardLayout({ children }: { children: ReactNode }) {
  return (
    <main className="mx-auto grid w-full max-w-[1600px] gap-6 px-6 py-10 xl:grid-cols-[320px_minmax(0,1fr)] xl:px-8">
      <DashboardSidebar />
      <section className="min-w-0">{children}</section>
    </main>
  );
}
