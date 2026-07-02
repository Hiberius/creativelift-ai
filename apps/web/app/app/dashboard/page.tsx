import { AppShell } from "@/components/app-shell";
import { DashboardOverview } from "@/components/dashboard";

export const metadata = { title: "Dashboard" };

export default function DashboardPage() {
  return (
    <AppShell title="Dashboard">
      <DashboardOverview />
    </AppShell>
  );
}
