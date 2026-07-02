"use client";

import { useEffect, useMemo, useState } from "react";
import { ExperimentInsight, ExperimentResult, creativeLiftApi } from "@/lib/api-client";
import { LiftChart } from "./mini-chart";
import { StatusPill } from "./status-pill";

const fallbackResult: ExperimentResult = {
  experiment_id: "demo",
  variants: {
    control: { key: "control", visitors: 12000, conversions: 720, revenue: 178000, conversion_rate: 0.06 },
    ai_video: { key: "ai_video", visitors: 12180, conversions: 862, revenue: 248000, conversion_rate: 0.0708 }
  },
  comparison: {
    control_rate: 0.06,
    treatment_rate: 0.0708,
    absolute_lift: 0.0108,
    relative_lift: 0.18,
    p_value: 0.0018,
    confidence_interval_low: 0.0043,
    confidence_interval_high: 0.0172,
    revenue_per_visitor_delta: 5.5,
    decision: "winner"
  },
  srm: { chi_square: 1.34, p_value: 0.98, passed: true },
  recommendation: "winner"
};

const fallbackInsight: ExperimentInsight = {
  experiment_id: "demo",
  recommendation: "winner",
  winning_variant_key: "ai_video",
  decision_summary: "ai_video is the current winner for signup.",
  recommended_action: "Promote the winning treatment and keep monitoring guardrails.",
  confidence_note: "Decision rule: 95% confidence, no SRM, positive guardrails",
  evidence: [
    "Control conversion rate: 6.00%",
    "Treatment conversion rate: 7.08%",
    "Absolute lift: 1.08%",
    "p-value: 0.0018"
  ],
  next_steps: [
    "Review event health before acting on the decision.",
    "Feed the winning and losing angles into the next brief."
  ]
};

function pct(value: unknown) {
  return typeof value === "number" ? `${(value * 100).toFixed(2)}%` : String(value ?? "-");
}

export function ExperimentResultsPanel({ experimentId }: { experimentId: string }) {
  const [result, setResult] = useState<ExperimentResult>(fallbackResult);
  const [insight, setInsight] = useState<ExperimentInsight>(fallbackInsight);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const summary = useMemo(
    () => [
      ["Control CR", pct(result.comparison.control_rate)],
      ["Treatment CR", pct(result.comparison.treatment_rate)],
      ["Absolute lift", pct(result.comparison.absolute_lift)],
      ["Relative lift", pct(result.comparison.relative_lift)],
      ["p-value", typeof result.comparison.p_value === "number" ? result.comparison.p_value.toFixed(4) : "-"],
      [
        "95% CI",
        `${pct(result.comparison.confidence_interval_low)} to ${pct(result.comparison.confidence_interval_high)}`
      ],
      ["SRM p-value", typeof result.srm.p_value === "number" ? result.srm.p_value.toFixed(3) : "-"]
    ],
    [result]
  );

  useEffect(() => {
    async function loadResult() {
      setLoading(true);
      setError(null);
      try {
        const [nextResult, nextInsight] = await Promise.all([
          creativeLiftApi.getExperimentResults(experimentId),
          creativeLiftApi.getExperimentInsights(experimentId)
        ]);
        setResult(nextResult);
        setInsight(nextInsight);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Could not load experiment result; showing demo result");
        setInsight(fallbackInsight);
      } finally {
        setLoading(false);
      }
    }
    void loadResult();
  }, [experimentId]);

  return (
    <div className="grid gap-4 lg:grid-cols-[1fr_360px]">
      <section className="panel rounded-lg p-6">
        <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
          <div>
            <h2 className="text-2xl font-semibold">Experiment result</h2>
            <p className="mt-2 text-slate-400">
              {loading ? "Loading latest result..." : "Decision recommendation and lift diagnostics from the measurement engine."}
            </p>
          </div>
          <StatusPill label={result.recommendation} />
        </div>
        {error ? <div className="mt-4 rounded-lg border border-yellow-400/30 bg-yellow-400/10 p-4 text-sm text-yellow-100">{error}</div> : null}
        <LiftChart />
      </section>
      <aside className="panel rounded-lg p-6">
        <h2 className="text-xl font-semibold">Statistical summary</h2>
        <dl className="mt-5 grid gap-3 text-sm">
          {summary.map(([label, value]) => (
            <div key={label} className="flex justify-between border-b border-white/10 pb-2">
              <dt className="text-slate-500">{label}</dt>
              <dd>{value}</dd>
            </div>
          ))}
        </dl>
      </aside>
      <section className="panel rounded-lg p-6 lg:col-span-2">
        <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
          <div>
            <h2 className="text-xl font-semibold">Decision insight</h2>
            <p className="mt-2 text-sm text-slate-400">{insight.decision_summary}</p>
          </div>
          <StatusPill label={insight.winning_variant_key ?? insight.recommendation} />
        </div>
        <div className="mt-5 grid gap-5 lg:grid-cols-[0.45fr_0.55fr]">
          <div className="rounded-md border border-white/10 bg-white/[0.03] p-4">
            <p className="text-sm font-semibold text-white">Recommended action</p>
            <p className="mt-3 text-sm leading-6 text-slate-300">{insight.recommended_action}</p>
            <p className="mt-4 text-xs text-slate-500">{insight.confidence_note}</p>
          </div>
          <div className="grid gap-4 md:grid-cols-2">
            <div className="rounded-md border border-white/10 bg-white/[0.03] p-4">
              <p className="text-sm font-semibold text-white">Evidence</p>
              <ul className="mt-3 grid gap-2 text-sm text-slate-300">
                {insight.evidence.slice(0, 6).map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </div>
            <div className="rounded-md border border-white/10 bg-white/[0.03] p-4">
              <p className="text-sm font-semibold text-white">Next steps</p>
              <ul className="mt-3 grid gap-2 text-sm text-slate-300">
                {insight.next_steps.slice(0, 4).map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
