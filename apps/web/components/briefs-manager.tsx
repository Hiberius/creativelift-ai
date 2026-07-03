"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { RefreshCcw } from "lucide-react";
import { Brief, creativeLiftApi } from "@/lib/api-client";
import { ApiErrorBanner, DemoDataBadge, toApiErrorMessage } from "./ui/data-source-notice";

const fallbackBriefs: Brief[] = [
  {
    id: "demo-brief-1",
    organization_id: "demo",
    name: "Meta prospecting AI video test",
    objective: "Increase qualified demo requests",
    target_audience: "US B2B SaaS growth leaders",
    channel: "paid_social",
    primary_kpi: "signup",
    status: "draft"
  },
  {
    id: "demo-brief-2",
    organization_id: "demo",
    name: "Lifecycle subject line lift",
    objective: "Improve activation from trial users",
    target_audience: "Trial users who imported ad accounts",
    channel: "email",
    primary_kpi: "activation",
    status: "draft"
  },
  {
    id: "demo-brief-3",
    organization_id: "demo",
    name: "Landing page hero angle test",
    objective: "Lift visitor-to-demo conversion",
    target_audience: "Marketing teams comparing AI attribution tools",
    channel: "landing_page",
    primary_kpi: "demo_request",
    status: "draft"
  }
];

export function BriefsManager() {
  const [briefs, setBriefs] = useState<Brief[]>(fallbackBriefs);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isDemo, setIsDemo] = useState(true);

  const loadBriefs = useCallback(async () => {
    setLoading(true);
    try {
      const nextBriefs = await creativeLiftApi.listBriefs();
      setBriefs(nextBriefs);
      setIsDemo(false);
      setError(null);
    } catch (err) {
      setBriefs(fallbackBriefs);
      setIsDemo(true);
      setError(toApiErrorMessage(err, "Could not reach the API. Showing demo briefs."));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadBriefs();
  }, [loadBriefs]);

  return (
    <>
      <div className="mb-4 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div className="flex items-center gap-3">
          <div>
            <h2 className="text-xl font-semibold">Brief registry</h2>
            <p className="mt-1 text-sm text-slate-400">Plan the objective, audience, KPI, channel, and guardrails before generating variants.</p>
          </div>
          {isDemo ? <DemoDataBadge /> : null}
        </div>
        <div className="flex gap-3">
          <button
            className="inline-flex items-center rounded-md border border-white/15 px-3 py-2 text-sm text-slate-200 hover:border-cyan/50"
            onClick={loadBriefs}
            type="button"
          >
            <RefreshCcw className={`mr-2 h-4 w-4 ${loading ? "animate-spin" : ""}`} />
            {loading ? "Refreshing..." : "Refresh"}
          </button>
          <Link className="rounded-md bg-cyan px-4 py-2 text-sm font-semibold text-ink" href="/app/briefs/new">
            New brief
          </Link>
        </div>
      </div>

      {error ? (
        <div className="mb-4">
          <ApiErrorBanner message={error} onRetry={loadBriefs} retrying={loading} />
        </div>
      ) : null}

      <div className="grid gap-4">
        {briefs.map((brief) => (
          <article key={brief.id} className="panel rounded-lg p-5">
            <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
              <div>
                <p className="text-sm text-cyan">{brief.channel}</p>
                <h2 className="mt-2 text-xl font-semibold">{brief.name}</h2>
                <p className="mt-2 text-slate-400">{brief.objective}</p>
              </div>
              <span className="w-fit rounded-md border border-white/15 bg-white/[0.03] px-2 py-1 text-xs text-slate-300">
                {brief.primary_kpi}
              </span>
            </div>
            <p className="mt-4 text-sm leading-6 text-slate-500">{brief.target_audience}</p>
          </article>
        ))}
      </div>
    </>
  );
}
