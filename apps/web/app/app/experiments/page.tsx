import { AppShell } from "@/components/app-shell";
import { ExperimentsManager } from "@/components/experiments-manager";

export const metadata = { title: "Experiments" };

export default function ExperimentsPage() {
  return (
    <AppShell title="Experiments">
      <ExperimentsManager />
    </AppShell>
  );
}
