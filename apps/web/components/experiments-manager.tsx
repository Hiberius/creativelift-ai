"use client";

import Link from "next/link";
import { FormEvent, useEffect, useState } from "react";
import { Beaker, Play, RefreshCcw, Square, Timer } from "lucide-react";
import { Experiment, ExperimentInput, creativeLiftApi } from "@/lib/api-client";
import { StatusPill } from "./status-pill";

const defaultExperiment: ExperimentInput = {
  name: "AI proof angle vs control",
  hypothesis: "A proof-led AI creative will improve signup conversion versus the current control.",
  primary_metric: "signup",
  guardrail_metric: "cost_per_signup",
  channel: "paid_social",
  variants: [
    { key: "control", creative_treatment_id: "00000000-0000-0000-0000-000000000105", allocation: 0.5, is_control: true },
    { key: "ai_proof_angle", creative_treatment_id: "00000000-0000-0000-0000-000000000101", allocation: 0.5 }
  ],
  randomization_unit: "anonymous_id",
  decision_rule: "95% confidence, healthy SRM, positive guardrails",
  notes: "Created from the local MVP experiment form."
};

export function ExperimentsManager() {
  const [experiments, setExperiments] = useState<Experiment[]>([]);
  const [draft, setDraft] = useState<ExperimentInput>(defaultExperiment);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [busyId, setBusyId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function loadExperiments() {
    setLoading(true);
    setError(null);
    try {
      setExperiments(await creativeLiftApi.listExperiments());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load experiments");
    } finally {
      setLoading(false);
    }
  }

  async function createExperiment(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving(true);
    setError(null);
    try {
      const experiment = await creativeLiftApi.createExperiment(draft);
      setExperiments((current) => [experiment, ...current]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not create experiment");
    } finally {
      setSaving(false);
    }
  }

  async function setStatus(id: string, status: "start" | "pause" | "complete") {
    setBusyId(id);
    setError(null);
    try {
      const updated = await creativeLiftApi.setExperimentStatus(id, status);
      setExperiments((current) => current.map((item) => (item.id === id ? updated : item)));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not update experiment status");
    } finally {
      setBusyId(null);
    }
  }

  useEffect(() => {
    void loadExperiments();
  }, []);

  return (
    <div className="grid gap-5 xl:grid-cols-[0.62fr_0.38fr]">
      <section className="grid gap-4">
        <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <div>
            <h2 className="text-xl font-semibold">Experiment registry</h2>
            <p className="mt-1 text-sm text-slate-400">Create, start, pause, complete, and inspect creative experiments.</p>
          </div>
          <button
            className="inline-flex w-fit items-center rounded-md border border-white/15 px-3 py-2 text-sm text-slate-200 hover:border-cyan/50"
            onClick={loadExperiments}
            type="button"
          >
            <RefreshCcw className="mr-2 h-4 w-4" />
            {loading ? "Refreshing..." : "Refresh"}
          </button>
        </div>
        {error ? <div className="rounded-lg border border-red-400/30 bg-red-400/10 p-4 text-sm text-red-200">{error}</div> : null}
        {experiments.map((experiment) => (
          <article key={experiment.id} className="panel grid gap-4 rounded-lg p-5 lg:grid-cols-[1fr_auto] lg:items-center">
            <div>
              <p className="text-sm text-cyan">{experiment.channel || "channel pending"} · {experiment.primary_metric}</p>
              <Link href={`/app/experiments/${experiment.id}`} className="mt-1 block text-xl font-semibold hover:text-cyan">
                {experiment.name}
              </Link>
              <p className="mt-2 text-sm leading-6 text-slate-400">{experiment.hypothesis}</p>
              <div className="mt-3 flex flex-wrap gap-2">
                <StatusPill label={experiment.status} />
                <span className="rounded-md border border-white/10 bg-white/[0.03] px-2 py-1 text-xs text-slate-400">
                  {experiment.variants.length} variants
                </span>
              </div>
            </div>
            <div className="flex flex-wrap gap-2">
              <button className="rounded-md border border-mint/30 px-3 py-2 text-sm text-mint disabled:opacity-50" disabled={busyId === experiment.id} onClick={() => void setStatus(experiment.id, "start")} type="button">
                <Play className="mr-1 inline h-4 w-4" />
                Start
              </button>
              <button className="rounded-md border border-yellow-400/30 px-3 py-2 text-sm text-yellow-300 disabled:opacity-50" disabled={busyId === experiment.id} onClick={() => void setStatus(experiment.id, "pause")} type="button">
                <Timer className="mr-1 inline h-4 w-4" />
                Pause
              </button>
              <button className="rounded-md border border-white/15 px-3 py-2 text-sm text-slate-200 disabled:opacity-50" disabled={busyId === experiment.id} onClick={() => void setStatus(experiment.id, "complete")} type="button">
                <Square className="mr-1 inline h-4 w-4" />
                Complete
              </button>
              <Link className="rounded-md bg-cyan px-3 py-2 text-sm font-semibold text-ink" href={`/app/experiments/${experiment.id}/results`}>
                Results
              </Link>
            </div>
          </article>
        ))}
      </section>

      <form className="panel h-fit rounded-lg p-6" onSubmit={createExperiment}>
        <div className="flex items-center gap-3">
          <Beaker className="h-6 w-6 text-cyan" />
          <h2 className="text-xl font-semibold">Create experiment</h2>
        </div>
        <div className="mt-5 grid gap-4">
          {[
            ["name", "Name"],
            ["hypothesis", "Hypothesis"],
            ["primary_metric", "Primary metric"],
            ["guardrail_metric", "Guardrail metric"],
            ["channel", "Channel"]
          ].map(([field, label]) => (
            <label key={field} className="grid gap-2 text-sm text-slate-300">
              {label}
              <input
                className="rounded-md border border-white/10 bg-white/[0.03] px-3 py-3 text-white outline-none focus:border-cyan"
                onChange={(event) => setDraft((current) => ({ ...current, [field]: event.target.value }))}
                value={String(draft[field as keyof ExperimentInput] ?? "")}
              />
            </label>
          ))}
        </div>
        <button className="mt-5 rounded-md bg-cyan px-5 py-3 text-sm font-semibold text-ink disabled:opacity-50" disabled={saving} type="submit">
          {saving ? "Creating..." : "Create draft experiment"}
        </button>
      </form>
    </div>
  );
}
