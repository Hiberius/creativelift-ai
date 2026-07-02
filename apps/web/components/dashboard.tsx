import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { experiments, metrics, treatments } from "@/lib/site-data";
import { DashboardApprovalRisk } from "./dashboard-approval-risk";
import { DashboardIngestionHealth } from "./dashboard-ingestion-health";
import { DashboardLineagePanel } from "./dashboard-lineage-panel";
import { DashboardSummary } from "./dashboard-summary";
import { DemoScenarioLauncher } from "./demo-scenario-launcher";
import { LiftChart, MiniChart } from "./mini-chart";
import { StatusPill } from "./status-pill";

export function MetricGrid() {
  return (
    <section className="grid gap-3 md:grid-cols-2 xl:grid-cols-6">
      {metrics.map((metric) => (
        <article key={metric.label} className="panel rounded-lg p-4">
          <p className="text-sm text-slate-400">{metric.label}</p>
          <p className={`mt-2 text-3xl font-semibold ${metric.tone === "mint" ? "text-mint" : "text-white"}`}>
            {metric.value}
          </p>
          <p className={`mt-1 text-sm ${metric.tone === "warning" ? "text-yellow-300" : "text-slate-400"}`}>
            {metric.hint}
          </p>
          <MiniChart tone={metric.tone === "mint" ? "mint" : metric.tone === "warning" ? "lime" : "cyan"} />
        </article>
      ))}
    </section>
  );
}

export function DashboardOverview() {
  return (
    <div className="grid gap-4">
      <DemoScenarioLauncher />
      <DashboardSummary />
      <div className="grid gap-4 2xl:grid-cols-[1fr_0.78fr]">
        <section className="panel rounded-lg p-5">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold">Creative Lift Over Time</h2>
            <div className="flex gap-2 text-xs text-slate-300">
              {["7D", "30D", "90D"].map((range) => (
                <button key={range} className="rounded border border-white/10 px-3 py-2 hover:bg-white/10">
                  {range}
                </button>
              ))}
            </div>
          </div>
          <LiftChart />
        </section>
        <ExperimentConfidence />
      </div>
      <div className="grid gap-4 2xl:grid-cols-[1fr_0.78fr]">
        <CreativeTreatmentsTable />
        <div className="grid gap-4">
          <DashboardApprovalRisk />
          <DashboardIngestionHealth />
          <DashboardLineagePanel />
        </div>
      </div>
    </div>
  );
}

export function ExperimentConfidence() {
  return (
    <section className="panel rounded-lg p-5">
      <div className="mb-3 flex items-center justify-between">
        <h2 className="text-lg font-semibold">Experiment Confidence</h2>
        <Link className="text-sm text-cyan" href="/app/experiments">
          View all
        </Link>
      </div>
      <div className="divide-y divide-white/10">
        {experiments.map((experiment) => (
          <Link key={experiment.id} href={`/app/experiments/${experiment.id}/results`} className="grid gap-3 py-4 md:grid-cols-[1fr_90px_1fr_120px_20px] md:items-center">
            <div>
              <p className="text-sm font-semibold text-cyan">{experiment.name}</p>
              <p className="mt-1 text-xs text-slate-400">{experiment.channel}</p>
            </div>
            <p className={experiment.lift.startsWith("-") ? "text-red-300" : "text-mint"}>{experiment.lift}</p>
            <div>
              <p className="text-2xl font-semibold">{experiment.confidence}%</p>
              <div className="mt-2 h-2 rounded-full bg-white/8">
                <div className="h-2 rounded-full bg-mint" style={{ width: `${experiment.confidence}%` }} />
              </div>
            </div>
            <StatusPill label={experiment.status} />
            <ArrowRight className="h-4 w-4 text-slate-500" />
          </Link>
        ))}
      </div>
    </section>
  );
}

export function CreativeTreatmentsTable() {
  return (
    <section className="panel overflow-hidden rounded-lg">
      <div className="flex items-center justify-between border-b border-white/10 p-5">
        <h2 className="text-lg font-semibold">Creative Treatments</h2>
        <Link className="text-sm text-cyan" href="/app/creatives">
          View all
        </Link>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full min-w-[820px] text-left text-sm">
          <thead className="text-xs uppercase text-slate-500">
            <tr>
              {["Treatment", "Type", "Experiment", "Channel", "Spend", "Lift", "Incremental Revenue", "Status"].map((heading) => (
                <th key={heading} className="border-b border-white/10 px-4 py-3 font-medium">
                  {heading}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-white/10">
            {treatments.map((treatment) => (
              <tr key={treatment.id} className="hover:bg-white/[0.03]">
                <td className="px-4 py-4">
                  <Link className="font-medium text-white hover:text-cyan" href={`/app/creatives/${treatment.id}`}>
                    {treatment.name}
                  </Link>
                </td>
                <td className="px-4 py-4 text-slate-300">{treatment.type}</td>
                <td className="px-4 py-4 text-slate-300">{treatment.experiment}</td>
                <td className="px-4 py-4 text-slate-300">{treatment.channel}</td>
                <td className="px-4 py-4 text-slate-300">{treatment.spend}</td>
                <td className={`px-4 py-4 ${treatment.lift.startsWith("-") ? "text-red-300" : "text-mint"}`}>{treatment.lift}</td>
                <td className="px-4 py-4 text-slate-300">{treatment.revenue}</td>
                <td className="px-4 py-4"><StatusPill label={treatment.status} /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="border-t border-white/10 p-4 text-xs text-slate-500">Showing 1-5 of 24 treatments</div>
    </section>
  );
}
