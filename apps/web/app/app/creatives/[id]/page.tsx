import { AppShell } from "@/components/app-shell";
import { CreativeDetailPanel } from "@/components/creative-detail-panel";

export const metadata = { title: "Creative Lineage" };

export default async function CreativeDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return (
    <AppShell title="Creative Lineage">
      <CreativeDetailPanel creativeId={id} />
    </AppShell>
  );
}
