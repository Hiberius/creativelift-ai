"use client";

import { useEffect, useState } from "react";
import { GitBranch, RefreshCcw } from "lucide-react";
import { CreativeTreatment, creativeLiftApi } from "@/lib/api-client";
import { StatusPill } from "./status-pill";

function fallbackTreatment(id: string): CreativeTreatment {
  return {
    id,
    organization_id: "demo",
    name: "AI Video - Sunset v3",
    objective: "Drive incremental conversion lift",
    target_audience: "US growth teams",
    channel: "Meta",
    placement: "EXP-2024-0521",
    angle: "proof-led",
    hook: "Stop trusting platform ROAS blindly.",
    cta: "Run a lift test",
    offer: "Open-source local demo",
    body_copy: "Track the chain from generated prompt to incremental revenue.",
    media_metadata: { prompt_lineage: "mock" },
    ai_generated: true,
    human_edited: true,
    compliance_status: "approved",
    approval_status: "approved",
    metrics_snapshot: { spend: "$312,402", lift: "+23.4%", revenue: "$734,210" }
  };
}

export function CreativeDetailPanel({ creativeId }: { creativeId: string }) {
  const [treatment, setTreatment] = useState<CreativeTreatment>(fallbackTreatment(creativeId));
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function loadTreatment() {
    setLoading(true);
    setError(null);
    try {
      setTreatment(await creativeLiftApi.getCreativeTreatment(creativeId));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load treatment; showing demo lineage");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadTreatment();
  }, [creativeId]);

  const lineage = [
    ["Brief", treatment.brief_id?.slice(0, 8) ?? "demo"],
    ["Prompt", String(treatment.media_metadata?.variant_id ?? "mock")],
    ["Variant", treatment.angle || "unclassified"],
    ["Experiment", treatment.placement || "unassigned"],
    ["Revenue", String(treatment.metrics_snapshot?.revenue ?? "-")]
  ];

  return (
    <div className="grid gap-4 lg:grid-cols-[0.68fr_0.32fr]">
      <section className="panel rounded-lg p-6">
        <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
          <div>
            <h2 className="text-2xl font-semibold">Prompt lineage</h2>
            <p className="mt-2 text-sm text-slate-400">{loading ? "Loading treatment..." : treatment.objective}</p>
          </div>
          <div className="flex items-center gap-2">
            <StatusPill label={treatment.approval_status} />
            <button className="grid h-9 w-9 place-items-center rounded-md border border-white/15 text-slate-300 hover:border-cyan/50" onClick={loadTreatment} type="button">
              <RefreshCcw className="h-4 w-4" />
            </button>
          </div>
        </div>
        {error ? <div className="mt-4 rounded-lg border border-yellow-400/30 bg-yellow-400/10 p-4 text-sm text-yellow-100">{error}</div> : null}
        <div className="mt-6 grid gap-3 md:grid-cols-5">
          {lineage.map(([node, value], index) => (
            <div key={node} className="relative rounded-md border border-cyan/30 bg-cyan/5 p-4 text-center">
              <GitBranch className="mx-auto mb-2 h-5 w-5 text-cyan" />
              <p className="text-sm font-semibold">{node}</p>
              <p className="mt-1 truncate text-xs text-slate-400">{value}</p>
              {index < lineage.length - 1 ? <span className="absolute -right-2 top-1/2 hidden text-cyan md:block">→</span> : null}
            </div>
          ))}
        </div>
      </section>
      <aside className="panel rounded-lg p-6">
        <h2 className="text-xl font-semibold">Treatment metadata</h2>
        <dl className="mt-4 grid gap-3 text-sm">
          {[
            ["Channel", treatment.channel],
            ["Audience", treatment.target_audience],
            ["Hook", treatment.hook || "-"],
            ["CTA", treatment.cta || "-"],
            ["Lift", String(treatment.metrics_snapshot?.lift ?? "-")],
            ["Revenue", String(treatment.metrics_snapshot?.revenue ?? "-")]
          ].map(([label, value]) => (
            <div key={label} className="grid gap-1 border-b border-white/10 pb-2">
              <dt className="text-slate-500">{label}</dt>
              <dd className="text-slate-200">{value}</dd>
            </div>
          ))}
        </dl>
      </aside>
    </div>
  );
}
