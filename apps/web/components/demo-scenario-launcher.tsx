"use client";

import Link from "next/link";
import { ArrowRight, CheckCircle2, Loader2, Play } from "lucide-react";
import { useState } from "react";
import { creativeLiftApi, DemoScenario } from "@/lib/api-client";

function pct(value: unknown) {
  return typeof value === "number" ? `${(value * 100).toFixed(1)}%` : "-";
}

export function DemoScenarioLauncher() {
  const [scenario, setScenario] = useState<DemoScenario | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function runScenario() {
    setLoading(true);
    setError(null);
    try {
      setScenario(await creativeLiftApi.runDemoScenario());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Demo scenario failed");
    } finally {
      setLoading(false);
    }
  }

  const control = scenario?.result.variants.control;
  const treatment = scenario?.result.variants.ai_proof;

  return (
    <section className="panel rounded-lg p-5">
      <div className="grid gap-4 lg:grid-cols-[1.1fr_1fr] lg:items-center">
        <div>
          <div className="flex flex-wrap items-center gap-3">
            <h2 className="text-lg font-semibold">Demo Lift Test</h2>
            {scenario ? (
              <span className="inline-flex items-center gap-2 rounded border border-mint/30 px-2.5 py-1 text-xs text-mint">
                <CheckCircle2 className="h-3.5 w-3.5" />
                {scenario.result.recommendation}
              </span>
            ) : null}
          </div>
          <p className="mt-2 max-w-2xl text-sm text-slate-400">
            Proof-led creative test with measured signup lift and evidence-backed approval.
          </p>
          {error ? <p className="mt-3 text-sm text-red-300">{error}</p> : null}
        </div>
        <div className="flex flex-wrap items-center gap-3 lg:justify-end">
          {scenario ? (
            <Link
              className="inline-flex items-center gap-2 rounded border border-white/10 px-4 py-2 text-sm text-cyan hover:bg-white/10"
              href={scenario.results_url}
            >
              Open results
              <ArrowRight className="h-4 w-4" />
            </Link>
          ) : null}
          <button
            className="inline-flex items-center gap-2 rounded bg-cyan px-4 py-2 text-sm font-semibold text-slate-950 hover:bg-mint disabled:cursor-not-allowed disabled:opacity-70"
            disabled={loading}
            onClick={runScenario}
            type="button"
          >
            {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4" />}
            {loading ? "Running" : scenario ? "Run again" : "Run demo"}
          </button>
        </div>
      </div>

      {scenario ? (
        <div className="mt-5 grid gap-3 md:grid-cols-4">
          <div className="rounded border border-white/10 p-3">
            <p className="text-xs text-slate-500">Events</p>
            <p className="mt-1 text-2xl font-semibold">{scenario.ingestion.accepted}</p>
          </div>
          <div className="rounded border border-white/10 p-3">
            <p className="text-xs text-slate-500">Control CVR</p>
            <p className="mt-1 text-2xl font-semibold">{pct(control?.conversion_rate)}</p>
          </div>
          <div className="rounded border border-white/10 p-3">
            <p className="text-xs text-slate-500">Treatment CVR</p>
            <p className="mt-1 text-2xl font-semibold text-mint">{pct(treatment?.conversion_rate)}</p>
          </div>
          <div className="rounded border border-white/10 p-3">
            <p className="text-xs text-slate-500">Event Quality</p>
            <p className="mt-1 text-2xl font-semibold">{scenario.event_health.quality_score.toFixed(2)}</p>
          </div>
        </div>
      ) : null}
    </section>
  );
}
