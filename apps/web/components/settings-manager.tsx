"use client";

import { FormEvent, useEffect, useState } from "react";
import { RefreshCcw } from "lucide-react";
import { AuditLog, BrandPack, ClaimEvidence, creativeLiftApi, MeResponse } from "@/lib/api-client";

const emptyEvidence = {
  claim: "",
  evidence_url: "",
  source_name: "",
  notes: "",
  status: "approved"
};

export function SettingsManager() {
  const [me, setMe] = useState<MeResponse | null>(null);
  const [brandPacks, setBrandPacks] = useState<BrandPack[]>([]);
  const [claimEvidence, setClaimEvidence] = useState<ClaimEvidence[]>([]);
  const [evidenceDraft, setEvidenceDraft] = useState(emptyEvidence);
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [savingEvidence, setSavingEvidence] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function loadSettings() {
    setLoading(true);
    setError(null);
    try {
      const [nextMe, packs, evidence, logs] = await Promise.all([
        creativeLiftApi.getMe(),
        creativeLiftApi.listBrandPacks(),
        creativeLiftApi.listClaimEvidence(),
        creativeLiftApi.listAuditLogs()
      ]);
      setMe(nextMe);
      setBrandPacks(packs);
      setClaimEvidence(evidence);
      setAuditLogs(logs);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load settings");
    } finally {
      setLoading(false);
    }
  }

  async function createEvidence(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSavingEvidence(true);
    setError(null);
    try {
      const evidence = await creativeLiftApi.createClaimEvidence({
        ...evidenceDraft,
        brand_pack_id: brandPacks[0]?.id ?? null
      });
      setClaimEvidence((current) => [evidence, ...current]);
      setEvidenceDraft(emptyEvidence);
      setAuditLogs(await creativeLiftApi.listAuditLogs());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not save claim evidence");
    } finally {
      setSavingEvidence(false);
    }
  }

  useEffect(() => {
    void loadSettings();
  }, []);

  return (
    <div className="grid gap-5 xl:grid-cols-[0.42fr_0.58fr]">
      <section className="panel rounded-lg p-6">
        <div className="flex items-center justify-between gap-3">
          <h2 className="text-xl font-semibold">Organization</h2>
          <button className="grid h-9 w-9 place-items-center rounded-md border border-white/15 text-slate-300 hover:border-cyan/50" onClick={loadSettings} type="button">
            <RefreshCcw className="h-4 w-4" />
          </button>
        </div>
        {error ? <div className="mt-4 rounded-lg border border-yellow-400/30 bg-yellow-400/10 p-4 text-sm text-yellow-100">{error}</div> : null}
        <dl className="mt-5 grid gap-3 text-sm">
          {[
            ["Name", me?.organization.name ?? (loading ? "Loading..." : "-")],
            ["Slug", me?.organization.slug ?? "-"],
            ["Plan", me?.organization.plan ?? "-"],
            ["Role", me?.principal.role ?? "-"],
            ["Scopes", me?.principal.scopes.join(", ") ?? "-"]
          ].map(([label, value]) => (
            <div key={label} className="grid gap-1 border-b border-white/10 pb-3">
              <dt className="text-slate-500">{label}</dt>
              <dd className="text-slate-200">{value}</dd>
            </div>
          ))}
        </dl>
      </section>

      <section className="panel rounded-lg p-6">
        <h2 className="text-xl font-semibold">Brand packs</h2>
        <div className="mt-4 grid gap-3">
          {brandPacks.map((pack) => (
            <article key={pack.id} className="rounded-md border border-white/10 bg-white/[0.03] p-4">
              <div className="flex flex-col gap-2 md:flex-row md:items-start md:justify-between">
                <div>
                  <h3 className="font-semibold">{pack.name}</h3>
                  <p className="mt-2 text-sm text-slate-400">{pack.voice || "No voice rules yet."}</p>
                </div>
                <span className="w-fit rounded-md border border-white/10 px-2 py-1 text-xs text-slate-400">
                  {pack.regulated_category ? "regulated" : "standard"}
                </span>
              </div>
              {pack.prohibited_claims?.length ? (
                <p className="mt-3 text-xs text-slate-500">Blocked claims: {pack.prohibited_claims.join(", ")}</p>
              ) : null}
            </article>
          ))}
        </div>
      </section>

      <section className="panel rounded-lg p-6 xl:col-span-2">
        <div className="grid gap-5 lg:grid-cols-[0.42fr_0.58fr]">
          <form className="grid gap-4" onSubmit={createEvidence}>
            <h2 className="text-xl font-semibold">Claim evidence</h2>
            <label className="grid gap-2 text-sm text-slate-300">
              Claim
              <input
                className="rounded-md border border-white/10 bg-white/[0.03] px-3 py-3 text-white outline-none focus:border-cyan"
                onChange={(event) => setEvidenceDraft((current) => ({ ...current, claim: event.target.value }))}
                value={evidenceDraft.claim}
              />
            </label>
            <label className="grid gap-2 text-sm text-slate-300">
              Evidence URL
              <input
                className="rounded-md border border-white/10 bg-white/[0.03] px-3 py-3 text-white outline-none focus:border-cyan"
                onChange={(event) => setEvidenceDraft((current) => ({ ...current, evidence_url: event.target.value }))}
                value={evidenceDraft.evidence_url}
              />
            </label>
            <div className="grid gap-4 md:grid-cols-2">
              <label className="grid gap-2 text-sm text-slate-300">
                Source
                <input
                  className="rounded-md border border-white/10 bg-white/[0.03] px-3 py-3 text-white outline-none focus:border-cyan"
                  onChange={(event) => setEvidenceDraft((current) => ({ ...current, source_name: event.target.value }))}
                  value={evidenceDraft.source_name}
                />
              </label>
              <label className="grid gap-2 text-sm text-slate-300">
                Status
                <select
                  className="rounded-md border border-white/10 bg-ink px-3 py-3 text-white outline-none focus:border-cyan"
                  onChange={(event) => setEvidenceDraft((current) => ({ ...current, status: event.target.value }))}
                  value={evidenceDraft.status}
                >
                  <option value="approved">approved</option>
                  <option value="needs_review">needs_review</option>
                  <option value="retired">retired</option>
                </select>
              </label>
            </div>
            <label className="grid gap-2 text-sm text-slate-300">
              Notes
              <textarea
                className="min-h-24 rounded-md border border-white/10 bg-white/[0.03] px-3 py-3 text-white outline-none focus:border-cyan"
                onChange={(event) => setEvidenceDraft((current) => ({ ...current, notes: event.target.value }))}
                value={evidenceDraft.notes}
              />
            </label>
            <button
              className="w-fit rounded-md bg-cyan px-5 py-3 text-sm font-semibold text-ink disabled:opacity-50"
              disabled={savingEvidence || !evidenceDraft.claim || !evidenceDraft.evidence_url}
              type="submit"
            >
              {savingEvidence ? "Saving..." : "Save evidence"}
            </button>
          </form>
          <div className="grid gap-3">
            {claimEvidence.map((evidence) => (
              <article key={evidence.id} className="rounded-md border border-white/10 bg-white/[0.03] p-4">
                <div className="flex flex-col gap-2 md:flex-row md:items-start md:justify-between">
                  <div>
                    <h3 className="font-semibold">{evidence.claim}</h3>
                    <p className="mt-2 text-sm text-slate-400">{evidence.source_name || "Source pending"}</p>
                  </div>
                  <span className="w-fit rounded-md border border-white/10 px-2 py-1 text-xs text-slate-400">
                    {evidence.status}
                  </span>
                </div>
                <a className="mt-3 block break-all text-sm text-cyan" href={evidence.evidence_url}>
                  {evidence.evidence_url}
                </a>
                {evidence.notes ? <p className="mt-3 text-xs text-slate-500">{evidence.notes}</p> : null}
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="panel overflow-hidden rounded-lg xl:col-span-2">
        <div className="border-b border-white/10 p-5">
          <h2 className="text-xl font-semibold">Governance audit</h2>
          <p className="mt-1 text-sm text-slate-400">Recent workspace actions recorded by the API.</p>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full min-w-[760px] text-left text-sm">
            <thead className="text-xs uppercase text-slate-500">
              <tr>
                {["Action", "Target", "Metadata", "Created"].map((heading) => (
                  <th key={heading} className="border-b border-white/10 px-4 py-3 font-medium">{heading}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-white/10">
              {auditLogs.length ? auditLogs.map((log) => (
                <tr key={log.id} className="hover:bg-white/[0.03]">
                  <td className="px-4 py-4 font-medium text-white">{log.action}</td>
                  <td className="px-4 py-4 text-slate-300">{log.target_type}:{log.target_id?.slice(0, 8) ?? "-"}</td>
                  <td className="px-4 py-4 text-slate-400">{Object.keys(log.metadata ?? {}).join(", ") || "-"}</td>
                  <td className="px-4 py-4 text-slate-400">{new Date(log.created_at).toLocaleString()}</td>
                </tr>
              )) : (
                <tr>
                  <td className="px-4 py-5 text-slate-500" colSpan={4}>No audit entries loaded yet.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
