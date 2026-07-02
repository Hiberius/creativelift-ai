import { AppShell } from "@/components/app-shell";
import { SettingsManager } from "@/components/settings-manager";

export const metadata = { title: "Settings" };

export default function SettingsPage() {
  return (
    <AppShell title="Settings">
      <SettingsManager />
    </AppShell>
  );
}
