import { AppShell } from "@/components/app-shell";
import { CreativesManager } from "@/components/creatives-manager";

export const metadata = { title: "Creatives" };

export default function CreativesPage() {
  return (
    <AppShell title="Creative Treatments">
      <CreativesManager />
    </AppShell>
  );
}
