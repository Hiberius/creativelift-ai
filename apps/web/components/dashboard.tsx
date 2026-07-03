"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { ArrowRight } from "lucide-react";
import { CreativeTreatment, creativeLiftApi } from "@/lib/api-client";
import { experiments as fallbackExperiments, treatments as fallbackTreatments } from "@/lib/site-data";
import { DashboardApprovalRisk } from "./dashboard-approval-risk";
import { DashboardIngestionHealth } from "./dashboard-ingestion-health";
import { DashboardLineagePanel } from "./dashboard-lineage-panel";
import { DashboardSummary } from "./dashboard-summary";
import { DemoScenarioLauncher } from "./demo-scenario-launcher";
import { LiftChart } from "./mini-chart";
import { StatusPill } from "./status-pill";
import { ApiErrorBanner, DemoDataBadge, toApiErrorMessage } from "./ui/data-source-notice";

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

interface ExperimentConfidenceRow {
  id: string;
  name: string;
  channel: string;
  status: string;
  lift: string | null;
  confidence: number | null;
  resultsHref: string;
}

function demoExperimentRows(): ExperimentConfidenceRow[] {
  return fallbackExperiments.map((item) => ({
    id: item.id,
    name: item.name,
    channel: item.channel,
    status: item.status,
    lift: item.lift,
    confidence: item.confidence,
    resultsHref: `/app/experiments/${item.id}/results`
  }));
}

export function ExperimentConfidence() {
  const [rows, setRows] = useState<ExperimentConfidenceRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadExperiments = useCallback(async () => {
    setLoading(true);
    try {
      const experiments = await creativeLiftApi.listExperiments();
      setRows(
        experiments.map((experiment) => ({
          id: experiment.id,
          name: experiment.name,
          channel: experiment.channel || "-",
          status: experiment.status,
          // Lift and confidence require a per-experiment results call; open
          // the results page for the real numbers instead of guessing here.
          lift: null,
          confidence: null,
          resultsHref: `/app/experiments/${experiment.id}/results`
        }))
      );
      setError(null);
    } catch (err) {
      setRows([]);
      setError(toApiErrorMessage(err, "Could not reach the API. Showing demo experiments."));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadExperiments();
  }, [loadExperiments]);

  const isDemo = !loading && error !== null;
  const displayRows = isDemo ? demoExperimentRows() : rows;

  return (
    <section className="panel rounded-lg p-5">
      <div className="mb-3 flex items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <h2 className="text-lg font-semibold">Experiment Confidence</h2>
          {isDemo ? <DemoDataBadge /> : null}
        </div>
        <Link className="text-sm text-cyan" href="/app/experiments">
          View all
        </Link>
      </div>
      {error ? <ApiErrorBanner message={error} onRetry={loadExperiments} retrying={loading} /> : null}
      <div className="divide-y divide-white/10">
        {loading ? <p className="py-4 text-sm text-slate-400">Loading experiments...</p> : null}
        {!loading && displayRows.length === 0 ? (
          <p className="py-4 text-sm text-slate-500">No experiments yet. Create one to see confidence here.</p>
        ) : null}
        {!loading &&
          displayRows.map((row) => (
            <Link key={row.id} href={row.resultsHref} className="grid gap-3 py-4 md:grid-cols-[1fr_90px_1fr_120px_20px] md:items-center">
              <div>
                <p className="text-sm font-semibold text-cyan">{row.name}</p>
                <p className="mt-1 text-xs text-slate-400">{row.channel}</p>
              </div>
              <p className={row.lift && row.lift.startsWith("-") ? "text-red-300" : "text-mint"}>{row.lift ?? "View"}</p>
              <div>
                {row.confidence == null ? (
                  <p className="text-sm text-slate-500">See results for lift &amp; confidence</p>
                ) : (
                  <>
                    <p className="text-2xl font-semibold">{row.confidence}%</p>
                    <div className="mt-2 h-2 rounded-full bg-white/8">
                      <div className="h-2 rounded-full bg-mint" style={{ width: `${row.confidence}%` }} />
                    </div>
                  </>
                )}
              </div>
              <StatusPill label={row.status} />
              <ArrowRight className="h-4 w-4 text-slate-500" />
            </Link>
          ))}
      </div>
    </section>
  );
}

function demoTreatments(): CreativeTreatment[] {
  return fallbackTreatments.map((item) => ({
    id: item.id,
    organization_id: "demo",
    name: item.name,
    objective: "Demo fallback until the API is reachable.",
    target_audience: "US growth teams",
    channel: item.channel,
    placement: item.experiment,
    angle: item.type,
    hook: item.name,
    cta: "Run a lift test",
    offer: "Open-source local demo",
    body_copy: "Track the chain from generated prompt to incremental revenue.",
    media_metadata: {},
    ai_generated: true,
    human_edited: item.status === "Control",
    compliance_status: item.status,
    approval_status: item.status === "Winning" ? "approved" : "draft",
    metrics_snapshot: { spend: item.spend, lift: item.lift, revenue: item.revenue, type: item.type, experiment: item.experiment }
  }));
}

export function CreativeTreatmentsTable() {
  const [treatments, setTreatments] = useState<CreativeTreatment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadTreatments = useCallback(async () => {
    setLoading(true);
    try {
      const next = await creativeLiftApi.listCreativeTreatments();
      setTreatments(next);
      setError(null);
    } catch (err) {
      setTreatments([]);
      setError(toApiErrorMessage(err, "Could not reach the API. Showing demo treatments."));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadTreatments();
  }, [loadTreatments]);

  const isDemo = !loading && error !== null;
  const rows = isDemo ? demoTreatments() : treatments;

  return (
    <section className="panel overflow-hidden rounded-lg">
      <div className="flex items-center justify-between gap-3 border-b border-white/10 p-5">
        <div className="flex items-center gap-2">
          <h2 className="text-lg font-semibold">Creative Treatments</h2>
          {isDemo ? <DemoDataBadge /> : null}
        </div>
        <Link className="text-sm text-cyan" href="/app/creatives">
          View all
        </Link>
      </div>
      {error ? (
        <div className="p-5 pb-0">
          <ApiErrorBanner message={error} onRetry={loadTreatments} retrying={loading} />
        </div>
      ) : null}
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
            {loading ? (
              <tr>
                <td className="px-4 py-5 text-slate-500" colSpan={8}>
                  Loading treatments...
                </td>
              </tr>
            ) : null}
            {!loading && rows.length === 0 ? (
              <tr>
                <td className="px-4 py-5 text-slate-500" colSpan={8}>
                  No creative treatments yet.
                </td>
              </tr>
            ) : null}
            {!loading &&
              rows.map((treatment) => {
                const snapshot = treatment.metrics_snapshot ?? {};
                const type = String(snapshot.type ?? treatment.angle ?? "-");
                const experimentLabel = String(snapshot.experiment ?? treatment.placement ?? "-");
                const spend = String(snapshot.spend ?? "-");
                const lift = String(snapshot.lift ?? "-");
                const revenue = String(snapshot.revenue ?? "-");
                return (
                  <tr key={treatment.id} className="hover:bg-white/[0.03]">
                    <td className="px-4 py-4">
                      <Link className="font-medium text-white hover:text-cyan" href={`/app/creatives/${treatment.id}`}>
                        {treatment.name}
                      </Link>
                    </td>
                    <td className="px-4 py-4 text-slate-300">{type}</td>
                    <td className="px-4 py-4 text-slate-300">{experimentLabel}</td>
                    <td className="px-4 py-4 text-slate-300">{treatment.channel}</td>
                    <td className="px-4 py-4 text-slate-300">{spend}</td>
                    <td className={`px-4 py-4 ${lift.startsWith("-") && lift !== "-" ? "text-red-300" : "text-mint"}`}>{lift}</td>
                    <td className="px-4 py-4 text-slate-300">{revenue}</td>
                    <td className="px-4 py-4">
                      <StatusPill label={treatment.approval_status} />
                    </td>
                  </tr>
                );
              })}
          </tbody>
        </table>
      </div>
    </section>
  );
}
