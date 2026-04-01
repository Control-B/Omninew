import type { ReactNode } from "react";

import { DashboardSidebar } from "@/components/layout/dashboard-sidebar";

export default function DashboardLayout({ children }: { children: ReactNode }) {
  return (
    <main className="mx-auto grid max-w-7xl gap-6 px-6 py-10 xl:grid-cols-[280px_1fr]">
      <DashboardSidebar />
      <section>{children}</section>
    </main>
  );
}
