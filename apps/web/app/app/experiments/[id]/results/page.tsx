import { AppShell } from "@/components/app-shell";
import { ExperimentResultsPanel } from "@/components/experiment-results-panel";

export const metadata = { title: "Experiment Results" };

export default async function ExperimentResultsPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return (
    <AppShell title="Experiment Results">
      <ExperimentResultsPanel experimentId={id} />
    </AppShell>
  );
}
