"use client";

import { useCallback, useEffect, useState } from "react";
import { Activity, AlertTriangle, RefreshCcw } from "lucide-react";
import { creativeLiftApi, EventHealth } from "@/lib/api-client";
import { toApiErrorMessage } from "./ui/data-source-notice";

function formatPercent(value: number) {
  return `${Math.round(value * 100)}%`;
}

export function DashboardIngestionHealth() {
  const [health, setHealth] = useState<EventHealth | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadHealth = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      setHealth(await creativeLiftApi.getEventHealth());
    } catch (err) {
      setHealth(null);
      setError(toApiErrorMessage(err, "Could not reach the API. Event health unavailable."));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadHealth();
  }, [loadHealth]);

  const cards = health
    ? [
        ["Events", health.total_events.toLocaleString()],
        ["Quality", formatPercent(health.quality_score)],
        ["Experiment", formatPercent(health.experiment_coverage)],
        ["Variant", formatPercent(health.variant_coverage)]
      ]
    : [
        ["Events", "-"],
        ["Quality", "-"],
        ["Experiment", "-"],
        ["Variant", "-"]
      ];

  return (
    <section className="panel rounded-lg p-5">
      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <Activity className="h-5 w-5 text-cyan" />
          <h2 className="text-lg font-semibold">Event Ingestion</h2>
        </div>
        <button
          className="grid h-8 w-8 place-items-center rounded border border-white/15 text-slate-300 hover:border-cyan/50"
          onClick={loadHealth}
          type="button"
        >
          <RefreshCcw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
        </button>
      </div>
      <div className="mt-4 grid grid-cols-2 gap-3">
        {cards.map(([label, value]) => (
          <div key={label} className="rounded-md border border-white/10 bg-white/[0.03] p-3">
            <p className="text-xs uppercase text-slate-500">{label}</p>
            <p className="mt-1 text-xl font-semibold text-white">{value}</p>
          </div>
        ))}
      </div>
      {health?.warnings.length ? (
        <div className="mt-4 grid gap-2">
          {health.warnings.slice(0, 2).map((warning) => (
            <div key={warning} className="flex items-start gap-2 text-xs text-yellow-200">
              <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
              <span>{warning}</span>
            </div>
          ))}
        </div>
      ) : (
        <p className={`mt-4 text-xs ${error ? "text-yellow-200" : "text-slate-500"}`}>
          {error ?? `Last event ${health?.last_event_at ? new Date(health.last_event_at).toLocaleString() : "-"}`}
        </p>
      )}
    </section>
  );
}
