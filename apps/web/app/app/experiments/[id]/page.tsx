import { AppShell } from "@/components/app-shell";
import { ExperimentDetailPanel } from "@/components/experiment-detail-panel";

export const metadata = { title: "Experiment" };

export default async function ExperimentPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return (
    <AppShell title="Experiment">
      <ExperimentDetailPanel experimentId={id} />
    </AppShell>
  );
}
