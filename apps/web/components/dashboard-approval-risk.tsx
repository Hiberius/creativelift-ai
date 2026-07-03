"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";
import { Check, RefreshCcw, X } from "lucide-react";
import { CreativeTreatment, creativeLiftApi } from "@/lib/api-client";
import { toApiErrorMessage } from "./ui/data-source-notice";

export function DashboardApprovalRisk() {
  const [treatments, setTreatments] = useState<CreativeTreatment[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadTreatments = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      setTreatments(await creativeLiftApi.listCreativeTreatments());
    } catch (err) {
      setTreatments([]);
      setError(toApiErrorMessage(err, "Could not reach the API. Approval data unavailable."));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadTreatments();
  }, [loadTreatments]);

  const summary = useMemo(() => {
    const counts = treatments.reduce<Record<string, number>>((current, treatment) => {
      current[treatment.approval_status] = (current[treatment.approval_status] ?? 0) + 1;
      return current;
    }, {});
    return {
      approved: counts.approved ?? 0,
      pending: (counts.pending_review ?? 0) + (counts.draft ?? 0),
      rejected: counts.rejected ?? 0,
      blocked: treatments.filter((treatment) => treatment.approval_status !== "approved").slice(0, 4)
    };
  }, [treatments]);

  return (
    <section className="panel rounded-lg p-5">
      <div className="mb-4 flex items-center justify-between gap-3">
        <h2 className="text-lg font-semibold">Approval Risk</h2>
        <button
          className="grid h-8 w-8 place-items-center rounded border border-white/15 text-slate-300 hover:border-cyan/50"
          onClick={loadTreatments}
          type="button"
        >
          <RefreshCcw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
        </button>
      </div>
      <div className="grid grid-cols-3 gap-2">
        {[
          ["Approved", summary.approved, "text-mint"],
          ["Pending", summary.pending, "text-yellow-300"],
          ["Rejected", summary.rejected, "text-red-300"]
        ].map(([label, value, tone]) => (
          <div key={label} className="rounded-md border border-white/10 bg-white/[0.03] p-3">
            <p className="text-xs uppercase text-slate-500">{label}</p>
            <p className={`mt-1 text-xl font-semibold ${tone}`}>{value}</p>
          </div>
        ))}
      </div>
      {error ? <p className="mt-4 text-xs text-yellow-200">{error}</p> : null}
      <div className="mt-4 divide-y divide-white/10">
        {summary.blocked.length ? summary.blocked.map((treatment) => (
          <Link key={treatment.id} className="grid grid-cols-[1fr_auto_auto] items-center gap-3 py-3" href={`/app/creatives/${treatment.id}`}>
            <div>
              <p className="text-sm text-white">{treatment.name}</p>
              <p className="text-xs text-slate-500">{treatment.channel || "channel pending"} · {treatment.approval_status}</p>
            </div>
            <span className="grid h-8 w-8 place-items-center rounded border border-mint/30 text-mint">
              <Check className="h-4 w-4" />
            </span>
            <span className="grid h-8 w-8 place-items-center rounded border border-red-400/30 text-red-300">
              <X className="h-4 w-4" />
            </span>
          </Link>
        )) : (
          <p className="py-3 text-sm text-mint">All loaded treatments are approved.</p>
        )}
      </div>
    </section>
  );
}
