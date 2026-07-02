import { AppShell } from "@/components/app-shell";
import { EventsManager } from "@/components/events-manager";

export const metadata = { title: "Events" };

export default function EventsPage() {
  return (
    <AppShell title="Event Ingestion">
      <EventsManager />
    </AppShell>
  );
}
