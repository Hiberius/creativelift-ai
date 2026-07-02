"use client";

import { useEffect, useState } from "react";
import { creativeLiftApi, MeasurementSummary } from "@/lib/api-client";
import { metrics } from "@/lib/site-data";
import { MiniChart } from "./mini-chart";

function formatCard(metric: string, value: number, unit: string) {
  if (unit === "percent" || unit === "ratio") return `${(value * 100).toFixed(1)}%`;
  if (unit === "currency") return `$${value.toLocaleString()}`;
  if (unit === "score") return value.toFixed(2);
  return value.toLocaleString();
}

export function DashboardSummary() {
  const [summary, setSummary] = useState<MeasurementSummary | null>(null);

  useEffect(() => {
    async function loadSummary() {
      try {
        setSummary(await creativeLiftApi.getMeasurementSummary());
      } catch {
        setSummary(null);
      }
    }
    void loadSummary();
  }, []);

  const cards = summary
    ? summary.cards.map((card) => ({
        label: card.metric.replaceAll("_", " "),
        value: formatCard(card.metric, card.value, card.unit),
        hint: card.delta == null ? summary.window : `Delta ${formatCard(card.metric, card.delta, card.unit)}`,
        tone: card.delta == null || card.delta >= 0 ? "mint" : "warning"
      }))
    : metrics;

  return (
    <section className="grid gap-3 md:grid-cols-2 xl:grid-cols-6">
      {cards.map((metric) => (
        <article key={metric.label} className="panel rounded-lg p-4">
          <p className="capitalize text-sm text-slate-400">{metric.label}</p>
          <p className={`mt-2 text-3xl font-semibold ${metric.tone === "mint" ? "text-mint" : "text-white"}`}>
            {metric.value}
          </p>
          <p className={`mt-1 text-sm ${metric.tone === "warning" ? "text-yellow-300" : "text-slate-400"}`}>
            {metric.hint}
          </p>
          <MiniChart tone={metric.tone === "mint" ? "mint" : "cyan"} />
        </article>
      ))}
    </section>
  );
}
