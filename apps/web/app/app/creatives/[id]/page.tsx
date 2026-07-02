import { AppShell } from "@/components/app-shell";
import { CreativeDetailPanel } from "@/components/creative-detail-panel";

export const metadata = { title: "Creative Lineage" };

export default function CreativeDetailPage({ params }: { params: { id: string } }) {
  return (
    <AppShell title="Creative Lineage">
      <CreativeDetailPanel creativeId={params.id} />
    </AppShell>
  );
}
