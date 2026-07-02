import { AppShell } from "@/components/app-shell";
import { ConnectorsManager } from "@/components/connectors-manager";

export const metadata = { title: "Connectors" };

export default function ConnectorsPage() {
  return (
    <AppShell title="Connectors">
      <ConnectorsManager />
    </AppShell>
  );
}
