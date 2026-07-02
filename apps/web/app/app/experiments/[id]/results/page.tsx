import { AppShell } from "@/components/app-shell";
import { ExperimentResultsPanel } from "@/components/experiment-results-panel";

export const metadata = { title: "Experiment Results" };

export default function ExperimentResultsPage({ params }: { params: { id: string } }) {
  return (
    <AppShell title="Experiment Results">
      <ExperimentResultsPanel experimentId={params.id} />
    </AppShell>
  );
}
