import { AppShell } from "@/components/app-shell";
import { BriefComposer } from "@/components/brief-composer";

export const metadata = { title: "New Brief" };

export default function NewBriefPage() {
  return (
    <AppShell title="New Brief">
      <BriefComposer />
    </AppShell>
  );
}
