"use client";

import { FormEvent, useCallback, useEffect, useState } from "react";
import { Plug, RefreshCcw } from "lucide-react";
import { Connector, creativeLiftApi } from "@/lib/api-client";
import { connectors as fallbackConnectors } from "@/lib/site-data";
import { StatusPill } from "./status-pill";
import { ApiErrorBanner, DemoDataBadge, toApiErrorMessage } from "./ui/data-source-notice";

function demoConnectors(): Connector[] {
  return fallbackConnectors.map((item) => ({
    id: item.name,
    organization_id: "demo",
    provider: item.name.toLowerCase().replaceAll(" ", "_"),
    display_name: item.name,
    status: item.status.toLowerCase(),
    config: { events: item.events, lag: item.lag },
    last_sync_at: null
  }));
}

export function ConnectorsManager() {
  const [items, setItems] = useState<Connector[]>([]);
  const [provider, setProvider] = useState("posthog");
  const [displayName, setDisplayName] = useState("PostHog demo connector");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isDemo, setIsDemo] = useState(false);

  const loadConnectors = useCallback(async () => {
    setLoading(true);
    try {
      const next = await creativeLiftApi.listConnectors();
      setItems(next);
      setIsDemo(false);
      setError(null);
    } catch (err) {
      setItems([]);
      setIsDemo(true);
      setError(toApiErrorMessage(err, "Could not reach the API. Showing demo connectors."));
    } finally {
      setLoading(false);
    }
  }, []);

  async function createConnector(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving(true);
    setError(null);
    try {
      const connector = await creativeLiftApi.createConnector(provider, displayName, { mode: "scaffold" });
      setItems((current) => [connector, ...current]);
      setIsDemo(false);
    } catch (err) {
      setError(toApiErrorMessage(err, "Could not create connector"));
    } finally {
      setSaving(false);
    }
  }

  useEffect(() => {
    void loadConnectors();
  }, [loadConnectors]);

  const displayItems: Connector[] = isDemo ? demoConnectors() : items;

  return (
    <div className="grid gap-5 xl:grid-cols-[0.68fr_0.32fr]">
      <section>
        <div className="mb-4 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <div className="flex items-center gap-3">
            <div>
              <h2 className="text-xl font-semibold">Connector registry</h2>
              <p className="mt-1 text-sm text-slate-400">Track external systems that will feed events, metadata, leads, or revenue.</p>
            </div>
            {isDemo ? <DemoDataBadge /> : null}
          </div>
          <button className="inline-flex w-fit items-center rounded-md border border-white/15 px-3 py-2 text-sm text-slate-200 hover:border-cyan/50" onClick={loadConnectors} type="button">
            <RefreshCcw className={`mr-2 h-4 w-4 ${loading ? "animate-spin" : ""}`} />
            {loading ? "Refreshing..." : "Refresh"}
          </button>
        </div>
        {error ? (
          <div className="mb-4">
            <ApiErrorBanner message={error} onRetry={loadConnectors} retrying={loading} />
          </div>
        ) : null}
        {!loading && !isDemo && displayItems.length === 0 ? (
          <p className="mb-4 text-sm text-slate-500">No connectors yet. Add one below to start syncing.</p>
        ) : null}
        <div className="grid gap-4 md:grid-cols-2">
          {displayItems.map((connector) => (
            <article key={connector.id} className="panel rounded-lg p-5">
              <div className="flex items-center justify-between gap-3">
                <h3 className="text-xl font-semibold">{connector.display_name}</h3>
                <StatusPill label={connector.status} />
              </div>
              <p className="mt-4 text-sm text-slate-400">Provider: {connector.provider}</p>
              <p className="mt-2 text-sm text-slate-500">Last sync: {connector.last_sync_at ?? "not synced"}</p>
            </article>
          ))}
        </div>
      </section>

      <form className="panel h-fit rounded-lg p-6" onSubmit={createConnector}>
        <div className="flex items-center gap-3">
          <Plug className="h-6 w-6 text-cyan" />
          <h2 className="text-xl font-semibold">Add connector</h2>
        </div>
        <div className="mt-5 grid gap-4">
          <label className="grid gap-2 text-sm text-slate-300">
            Provider
            <select className="rounded-md border border-white/10 bg-ink px-3 py-3 text-white outline-none focus:border-cyan" onChange={(event) => setProvider(event.target.value)} value={provider}>
              {["posthog", "rudder", "snowplow", "google_ads", "meta_ads", "hubspot", "webhook_generic"].map((option) => (
                <option key={option} value={option}>{option}</option>
              ))}
            </select>
          </label>
          <label className="grid gap-2 text-sm text-slate-300">
            Display name
            <input className="rounded-md border border-white/10 bg-white/[0.03] px-3 py-3 text-white outline-none focus:border-cyan" onChange={(event) => setDisplayName(event.target.value)} value={displayName} />
          </label>
        </div>
        <button className="mt-5 rounded-md bg-cyan px-5 py-3 text-sm font-semibold text-ink disabled:opacity-50" disabled={saving} type="submit">
          {saving ? "Adding..." : "Add scaffold connector"}
        </button>
      </form>
    </div>
  );
}
