"use client";

import Link from "next/link";
import { FormEvent, useCallback, useEffect, useState } from "react";
import { ArrowRight, Pause, Play, RefreshCcw, Trophy } from "lucide-react";
import { creativeLiftApi, Experiment, ExperimentAssignment } from "@/lib/api-client";
import { experiments } from "@/lib/site-data";
import { StatusPill } from "./status-pill";
import { ApiErrorBanner, DemoDataBadge, toApiErrorMessage } from "./ui/data-source-notice";
import { DetailHeaderSkeleton } from "./ui/skeleton";

function fallbackExperiment(id: string): Experiment {
  const item = experiments.find((experiment) => experiment.id === id) ?? experiments[0];
  return {
    id,
    organization_id: "demo",
    name: item?.name ?? "AI video vs static control",
    hypothesis: "Proof-led generated creative creates higher signup conversion than static control.",
    primary_metric: "signup",
    guardrail_metric: "cost_per_signup",
    variants: [
      { key: "control", creative_treatment_id: "00000000-0000-0000-0000-000000000104", allocation: 0.5, is_control: true },
      { key: "ai_treatment", creative_treatment_id: "00000000-0000-0000-0000-000000000101", allocation: 0.5 }
    ],
    randomization_unit: "anonymous_id",
    channel: item?.channel ?? "paid_social",
    decision_rule: "frequentist_p_value_lt_0_05",
    minimum_detectable_effect: 0.05,
    notes: "Demo fallback until the API is running.",
    status: item?.status === "Running" ? "running" : "draft",
    starts_at: null,
    ends_at: null
  };
}

export function ExperimentDetailPanel({ experimentId }: { experimentId: string }) {
  const [experiment, setExperiment] = useState<Experiment | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState<string | null>(null);
  const [unitId, setUnitId] = useState("anon_demo_001");
  const [assignment, setAssignment] = useState<ExperimentAssignment | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isDemo, setIsDemo] = useState(false);

  const loadExperiment = useCallback(async () => {
    setLoading(true);
    try {
      const next = await creativeLiftApi.getExperiment(experimentId);
      setExperiment(next);
      setIsDemo(false);
      setError(null);
    } catch (err) {
      setExperiment(fallbackExperiment(experimentId));
      setIsDemo(true);
      setError(toApiErrorMessage(err, "Could not reach the API. Showing demo experiment details."));
    } finally {
      setLoading(false);
    }
  }, [experimentId]);

  async function transition(status: "start" | "pause" | "complete") {
    if (!experiment) return;
    setSaving(status);
    setError(null);
    try {
      setExperiment(await creativeLiftApi.setExperimentStatus(experiment.id, status));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not update experiment");
    } finally {
      setSaving(null);
    }
  }

  async function previewAssignment(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!experiment) return;
    setError(null);
    try {
      setAssignment(await creativeLiftApi.assignExperimentVariant(experiment.id, unitId));
    } catch (err) {
      setError(toApiErrorMessage(err, "Could not assign unit"));
    }
  }

  useEffect(() => {
    void loadExperiment();
  }, [loadExperiment]);

  if (loading && !experiment) {
    return (
      <div className="panel rounded-lg p-6">
        <DetailHeaderSkeleton />
      </div>
    );
  }

  if (!experiment) {
    return null;
  }

  return (
    <div className="grid gap-5">
      <section className="panel rounded-lg p-6">
        <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
          <div>
            <div className="flex items-center gap-3">
              <h2 className="text-2xl font-semibold">{experiment.name}</h2>
              <StatusPill label={experiment.status} />
              {isDemo ? <DemoDataBadge /> : null}
            </div>
            <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-400">{loading ? "Loading experiment..." : experiment.hypothesis}</p>
          </div>
          <div className="flex flex-wrap gap-2">
            <button className="grid h-9 w-9 place-items-center rounded-md border border-white/15 text-slate-300 hover:border-cyan/50" onClick={loadExperiment} type="button">
              <RefreshCcw className="h-4 w-4" />
            </button>
            <button className="inline-flex items-center rounded-md border border-mint/30 px-3 py-2 text-sm text-mint disabled:opacity-50" disabled={saving !== null} onClick={() => transition("start")} type="button">
              <Play className="mr-2 h-4 w-4" />
              {saving === "start" ? "Starting..." : "Start"}
            </button>
            <button className="inline-flex items-center rounded-md border border-yellow-300/30 px-3 py-2 text-sm text-yellow-200 disabled:opacity-50" disabled={saving !== null} onClick={() => transition("pause")} type="button">
              <Pause className="mr-2 h-4 w-4" />
              {saving === "pause" ? "Pausing..." : "Pause"}
            </button>
            <button className="inline-flex items-center rounded-md border border-cyan/30 px-3 py-2 text-sm text-cyan disabled:opacity-50" disabled={saving !== null} onClick={() => transition("complete")} type="button">
              <Trophy className="mr-2 h-4 w-4" />
              {saving === "complete" ? "Completing..." : "Complete"}
            </button>
          </div>
        </div>
        {error ? (
          <div className="mt-5">
            <ApiErrorBanner message={error} onRetry={loadExperiment} retrying={loading} />
          </div>
        ) : null}
      </section>

      <div className="grid gap-5 xl:grid-cols-[0.58fr_0.42fr]">
        <section className="panel overflow-hidden rounded-lg">
          <div className="border-b border-white/10 p-5">
            <h2 className="text-xl font-semibold">Variants</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full min-w-[620px] text-left text-sm">
              <thead className="text-xs uppercase text-slate-500">
                <tr>
                  {["Variant", "Creative Treatment", "Allocation", "Control"].map((heading) => (
                    <th key={heading} className="border-b border-white/10 px-4 py-3 font-medium">{heading}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-white/10">
                {experiment.variants.map((variant) => (
                  <tr key={variant.key} className="hover:bg-white/[0.03]">
                    <td className="px-4 py-4 font-medium text-white">{variant.key}</td>
                    <td className="px-4 py-4 text-slate-300">{variant.creative_treatment_id ?? "-"}</td>
                    <td className="px-4 py-4 text-slate-300">{Math.round(variant.allocation * 100)}%</td>
                    <td className="px-4 py-4 text-slate-300">{variant.is_control ? "Yes" : "No"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <aside className="panel rounded-lg p-6">
          <h2 className="text-xl font-semibold">Decision setup</h2>
          <dl className="mt-4 grid gap-3 text-sm">
            {[
              ["Primary metric", experiment.primary_metric],
              ["Guardrail metric", experiment.guardrail_metric || "-"],
              ["Randomization unit", experiment.randomization_unit || "anonymous_id"],
              ["Channel", experiment.channel || "-"],
              ["Decision rule", experiment.decision_rule || "-"],
              ["MDE", experiment.minimum_detectable_effect == null ? "-" : `${Math.round(experiment.minimum_detectable_effect * 100)}%`]
            ].map(([label, value]) => (
              <div key={label} className="grid gap-1 border-b border-white/10 pb-3">
                <dt className="text-slate-500">{label}</dt>
                <dd className="text-slate-200">{value}</dd>
              </div>
            ))}
          </dl>
          <Link className="mt-6 inline-flex items-center rounded-md bg-cyan px-4 py-3 text-sm font-semibold text-ink" href={`/app/experiments/${experiment.id}/results`}>
            View results
            <ArrowRight className="ml-2 h-4 w-4" />
          </Link>
        </aside>
      </div>

      <section className="panel rounded-lg p-6">
        <h2 className="text-xl font-semibold">Assignment preview</h2>
        <form className="mt-4 flex flex-col gap-3 md:flex-row" onSubmit={previewAssignment}>
          <input className="min-w-0 flex-1 rounded-md border border-white/10 bg-white/[0.03] px-3 py-3 text-white outline-none focus:border-cyan" onChange={(event) => setUnitId(event.target.value)} value={unitId} />
          <button className="rounded-md bg-cyan px-5 py-3 text-sm font-semibold text-ink" type="submit">
            Assign unit
          </button>
        </form>
        {assignment ? (
          <div className="mt-4 grid gap-3 text-sm md:grid-cols-4">
            {[
              ["Variant", assignment.variant_key],
              ["Creative", assignment.creative_treatment_id?.slice(0, 8) ?? "-"],
              ["Allocation", `${Math.round(assignment.allocation * 100)}%`],
              ["Control", assignment.is_control ? "Yes" : "No"]
            ].map(([label, value]) => (
              <div key={label} className="rounded-md border border-white/10 bg-white/[0.03] p-3">
                <p className="text-slate-500">{label}</p>
                <p className="mt-1 font-medium text-slate-100">{value}</p>
              </div>
            ))}
          </div>
        ) : null}
      </section>
    </div>
  );
}
