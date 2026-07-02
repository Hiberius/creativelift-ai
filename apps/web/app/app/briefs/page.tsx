import { AppShell } from "@/components/app-shell";
import { BriefsManager } from "@/components/briefs-manager";

export const metadata = { title: "Briefs" };

export default function BriefsPage() {
  return (
    <AppShell title="Briefs">
      <BriefsManager />
    </AppShell>
  );
}
