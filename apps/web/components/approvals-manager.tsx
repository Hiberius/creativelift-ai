"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { Check, RefreshCcw, X } from "lucide-react";
import { CreativeTreatment, creativeLiftApi } from "@/lib/api-client";
import { StatusPill } from "./status-pill";
import { ApiErrorBanner, toApiErrorMessage } from "./ui/data-source-notice";

export function ApprovalsManager() {
  const [treatments, setTreatments] = useState<CreativeTreatment[]>([]);
  const [evidenceUrls, setEvidenceUrls] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(true);
  const [busyId, setBusyId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const queue = useMemo(
    () => treatments.filter((item) => !["approved", "archived"].includes(item.approval_status)),
    [treatments]
  );

  const loadTreatments = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      setTreatments(await creativeLiftApi.listCreativeTreatments());
    } catch (err) {
      setError(toApiErrorMessage(err, "Could not reach the API. The approval queue is unavailable."));
    } finally {
      setLoading(false);
    }
  }, []);

  async function review(id: string, decision: "approve" | "reject") {
    setBusyId(id);
    setError(null);
    try {
      const updated =
        decision === "approve"
          ? await creativeLiftApi.approveCreativeTreatment(
              id,
              "Approved from approval queue",
              evidenceUrls[id]?.trim() ? [evidenceUrls[id].trim()] : []
            )
          : await creativeLiftApi.rejectCreativeTreatment(id);
      setTreatments((current) => current.map((item) => (item.id === id ? updated : item)));
      setEvidenceUrls((current) => ({ ...current, [id]: "" }));
    } catch (err) {
      setError(toApiErrorMessage(err, `Could not ${decision} treatment`));
    } finally {
      setBusyId(null);
    }
  }

  useEffect(() => {
    void loadTreatments();
  }, [loadTreatments]);

  return (
    <section className="panel rounded-lg p-6">
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h2 className="text-xl font-semibold">Creative review queue</h2>
          <p className="mt-2 text-sm text-slate-400">Review generated or edited Creative Treatments before they are promoted into experiments.</p>
        </div>
        <button
          className="inline-flex w-fit items-center rounded-md border border-white/15 px-3 py-2 text-sm text-slate-200 hover:border-cyan/50"
          onClick={loadTreatments}
          type="button"
        >
          <RefreshCcw className="mr-2 h-4 w-4" />
          {loading ? "Refreshing..." : "Refresh"}
        </button>
      </div>

      {error ? (
        <div className="mt-5">
          <ApiErrorBanner message={error} onRetry={loadTreatments} retrying={loading} />
        </div>
      ) : null}

      <div className="mt-6 divide-y divide-white/10">
        {loading ? <p className="py-4 text-sm text-slate-400">Loading treatments...</p> : null}
        {!loading && queue.length === 0 ? (
          <div className="rounded-lg border border-white/10 bg-white/[0.03] p-5 text-sm text-slate-400">
            No pending review items. Save generated variants as Creative Treatments to populate this queue.
          </div>
        ) : null}
        {queue.map((treatment) => (
          <div key={treatment.id} className="grid gap-4 py-4 md:grid-cols-[1fr_260px_auto_auto_auto] md:items-center">
            <div>
              <p className="text-sm text-cyan">{treatment.channel} · {treatment.angle || "unclassified"}</p>
              <h3 className="mt-1 font-semibold text-white">{treatment.name}</h3>
              <p className="mt-1 text-sm text-slate-500">{treatment.objective}</p>
              <p className="mt-1 text-xs text-slate-500">{treatment.compliance_status}</p>
            </div>
            <input
              className="rounded-md border border-white/10 bg-white/[0.03] px-3 py-2 text-sm text-white outline-none focus:border-cyan"
              onChange={(event) => setEvidenceUrls((current) => ({ ...current, [treatment.id]: event.target.value }))}
              placeholder="Evidence URL"
              value={evidenceUrls[treatment.id] ?? ""}
            />
            <StatusPill label={treatment.approval_status} />
            <button
              className="grid h-9 w-9 place-items-center rounded-md border border-mint/30 text-mint hover:bg-mint/10 disabled:opacity-50"
              disabled={busyId === treatment.id}
              onClick={() => void review(treatment.id, "approve")}
              type="button"
            >
              <Check className="h-4 w-4" />
            </button>
            <button
              className="grid h-9 w-9 place-items-center rounded-md border border-red-400/30 text-red-300 hover:bg-red-400/10 disabled:opacity-50"
              disabled={busyId === treatment.id}
              onClick={() => void review(treatment.id, "reject")}
              type="button"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        ))}
      </div>
    </section>
  );
}
