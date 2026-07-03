"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { GitBranch, RefreshCcw } from "lucide-react";
import { AuditLog, creativeLiftApi } from "@/lib/api-client";
import { toApiErrorMessage } from "./ui/data-source-notice";

function labelAction(action: string) {
  return action.replaceAll("_", " ").replaceAll(".", " ");
}

export function DashboardLineagePanel() {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadLogs = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      setLogs(await creativeLiftApi.listAuditLogs());
    } catch (err) {
      setLogs([]);
      setError(toApiErrorMessage(err, "Could not reach the API. Lineage unavailable."));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadLogs();
  }, [loadLogs]);

  return (
    <section className="panel rounded-lg p-5">
      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <GitBranch className="h-5 w-5 text-cyan" />
          <h2 className="text-lg font-semibold">Lineage</h2>
        </div>
        <button
          className="grid h-8 w-8 place-items-center rounded border border-white/15 text-slate-300 hover:border-cyan/50"
          onClick={loadLogs}
          type="button"
        >
          <RefreshCcw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
        </button>
      </div>
      <div className="mt-4 divide-y divide-white/10">
        {logs.slice(0, 5).map((log) => (
          <div key={log.id} className="grid grid-cols-[auto_1fr] gap-3 py-3">
            <span className="mt-1 h-2 w-2 rounded-full bg-cyan" />
            <div>
              <p className="text-sm capitalize text-white">{labelAction(log.action)}</p>
              <p className="mt-1 text-xs text-slate-500">
                {log.target_type}{log.target_id ? ` · ${log.target_id.slice(0, 8)}` : ""} · {new Date(log.created_at).toLocaleString()}
              </p>
            </div>
          </div>
        ))}
        {!logs.length ? (
          <p className={`py-3 text-sm ${error ? "text-yellow-200" : "text-slate-500"}`}>
            {error ?? "No audit events yet."}
          </p>
        ) : null}
      </div>
      <Link className="mt-4 inline-flex text-sm text-cyan" href="/app/settings">
        View audit log
      </Link>
    </section>
  );
}
