import { AppShell } from "@/components/app-shell";
import { ExperimentDetailPanel } from "@/components/experiment-detail-panel";

export const metadata = { title: "Experiment" };

export default function ExperimentPage({ params }: { params: { id: string } }) {
  return (
    <AppShell title="Experiment">
      <ExperimentDetailPanel experimentId={params.id} />
    </AppShell>
  );
}
