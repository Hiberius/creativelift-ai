"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { RefreshCcw } from "lucide-react";
import { CreativeTreatment, creativeLiftApi } from "@/lib/api-client";
import { treatments } from "@/lib/site-data";
import { StatusPill } from "./status-pill";
import { ApiErrorBanner, DemoDataBadge, toApiErrorMessage } from "./ui/data-source-notice";

function fallbackTreatments(): CreativeTreatment[] {
  return treatments.map((item) => ({
    id: item.id,
    organization_id: "demo",
    name: item.name,
    objective: "Drive incremental conversion lift",
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
    metrics_snapshot: {
      spend: item.spend,
      lift: item.lift,
      revenue: item.revenue
    }
  }));
}

export function CreativesManager() {
  const [items, setItems] = useState<CreativeTreatment[]>(fallbackTreatments());
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isDemo, setIsDemo] = useState(true);

  const loadCreatives = useCallback(async () => {
    setLoading(true);
    try {
      const nextItems = await creativeLiftApi.listCreativeTreatments();
      setItems(nextItems);
      setIsDemo(false);
      setError(null);
    } catch (err) {
      setItems(fallbackTreatments());
      setIsDemo(true);
      setError(toApiErrorMessage(err, "Could not reach the API. Showing demo Creative Treatments."));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadCreatives();
  }, [loadCreatives]);

  return (
    <section className="panel overflow-hidden rounded-lg">
      <div className="flex flex-col gap-4 border-b border-white/10 p-5 md:flex-row md:items-center md:justify-between">
        <div className="flex items-center gap-3">
          <div>
            <h2 className="text-lg font-semibold">Creative Treatments</h2>
            <p className="mt-1 text-sm text-slate-400">The measurable registry for AI-generated and human-edited creative variants.</p>
          </div>
          {isDemo ? <DemoDataBadge /> : null}
        </div>
        <button
          className="inline-flex w-fit items-center rounded-md border border-white/15 px-3 py-2 text-sm text-slate-200 hover:border-cyan/50"
          onClick={loadCreatives}
          type="button"
        >
          <RefreshCcw className={`mr-2 h-4 w-4 ${loading ? "animate-spin" : ""}`} />
          {loading ? "Refreshing..." : "Refresh"}
        </button>
      </div>
      {error ? (
        <div className="m-5">
          <ApiErrorBanner message={error} onRetry={loadCreatives} retrying={loading} />
        </div>
      ) : null}
      <div className="overflow-x-auto">
        <table className="w-full min-w-[860px] text-left text-sm">
          <thead className="text-xs uppercase text-slate-500">
            <tr>
              {["Treatment", "Angle", "Channel", "CTA", "Approval", "Lift", "Revenue"].map((heading) => (
                <th key={heading} className="border-b border-white/10 px-4 py-3 font-medium">{heading}</th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-white/10">
            {items.map((item) => (
              <tr key={item.id} className="hover:bg-white/[0.03]">
                <td className="px-4 py-4">
                  <Link className="font-medium text-white hover:text-cyan" href={`/app/creatives/${item.id}`}>
                    {item.name}
                  </Link>
                  <p className="mt-1 max-w-md truncate text-xs text-slate-500">{item.objective}</p>
                </td>
                <td className="px-4 py-4 text-slate-300">{item.angle || "-"}</td>
                <td className="px-4 py-4 text-slate-300">{item.channel}</td>
                <td className="px-4 py-4 text-slate-300">{item.cta || "-"}</td>
                <td className="px-4 py-4"><StatusPill label={item.approval_status} /></td>
                <td className="px-4 py-4 text-mint">{String(item.metrics_snapshot?.lift ?? "-")}</td>
                <td className="px-4 py-4 text-slate-300">{String(item.metrics_snapshot?.revenue ?? "-")}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
