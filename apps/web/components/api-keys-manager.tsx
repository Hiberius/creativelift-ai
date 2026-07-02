"use client";

import { useEffect, useMemo, useState } from "react";
import { KeyRound, RefreshCcw, Trash2 } from "lucide-react";
import { ApiKey, creativeLiftApi } from "@/lib/api-client";

export function ApiKeysManager() {
  const [keys, setKeys] = useState<ApiKey[]>([]);
  const [createdKey, setCreatedKey] = useState<ApiKey | null>(null);
  const [name, setName] = useState("Browser ingestion key");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const hasKeys = useMemo(() => keys.length > 0, [keys]);

  async function loadKeys() {
    setLoading(true);
    setError(null);
    try {
      setKeys(await creativeLiftApi.listApiKeys());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load API keys");
    } finally {
      setLoading(false);
    }
  }

  async function createKey() {
    setSaving(true);
    setError(null);
    try {
      const key = await creativeLiftApi.createApiKey(name || "Ingestion key");
      setCreatedKey(key);
      await loadKeys();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not create API key");
    } finally {
      setSaving(false);
    }
  }

  async function deleteKey(id: string) {
    setError(null);
    try {
      await creativeLiftApi.deleteApiKey(id);
      setKeys((current) => current.filter((key) => key.id !== id));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not delete API key");
    }
  }

  useEffect(() => {
    void loadKeys();
  }, []);

  return (
    <section className="panel max-w-5xl rounded-lg p-6">
      <div className="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <div className="flex items-center gap-3">
            <KeyRound className="h-6 w-6 text-cyan" />
            <h2 className="text-xl font-semibold">Scoped ingestion keys</h2>
          </div>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-400">
            Create keys for event ingestion. The raw key is only shown once after creation; lists only show prefixes.
          </p>
        </div>
        <button
          onClick={loadKeys}
          className="inline-flex w-fit items-center rounded-md border border-white/15 px-3 py-2 text-sm text-slate-200 hover:border-cyan/50"
          type="button"
        >
          <RefreshCcw className="mr-2 h-4 w-4" />
          Refresh
        </button>
      </div>

      <div className="mt-6 grid gap-3 rounded-lg border border-white/10 bg-black/20 p-4 md:grid-cols-[1fr_auto]">
        <label className="grid gap-2 text-sm text-slate-300">
          Key name
          <input
            className="rounded-md border border-white/10 bg-white/[0.03] px-3 py-3 text-white outline-none focus:border-cyan"
            onChange={(event) => setName(event.target.value)}
            value={name}
          />
        </label>
        <button
          className="self-end rounded-md bg-cyan px-5 py-3 text-sm font-semibold text-ink disabled:cursor-not-allowed disabled:opacity-50"
          disabled={saving}
          onClick={createKey}
          type="button"
        >
          {saving ? "Creating..." : "Create key"}
        </button>
      </div>

      {createdKey?.raw_key ? (
        <div className="mt-5 rounded-lg border border-mint/30 bg-mint/10 p-4">
          <p className="text-sm font-semibold text-mint">Copy this key now. It will not be shown again.</p>
          <code className="mt-3 block overflow-x-auto rounded bg-black/35 p-3 text-sm text-slate-100">{createdKey.raw_key}</code>
        </div>
      ) : null}

      {error ? (
        <div className="mt-5 rounded-lg border border-red-400/30 bg-red-400/10 p-4 text-sm text-red-200">
          {error}
        </div>
      ) : null}

      <div className="mt-6 divide-y divide-white/10">
        {loading ? <p className="py-4 text-sm text-slate-400">Loading keys...</p> : null}
        {!loading && !hasKeys ? (
          <div className="rounded-lg border border-white/10 bg-white/[0.03] p-5 text-sm text-slate-400">
            No API keys yet. Create one to ingest events from a website, app, or connector.
          </div>
        ) : null}
        {keys.map((key) => (
          <div key={key.id} className="grid gap-3 py-4 text-sm md:grid-cols-[1fr_auto_auto] md:items-center">
            <div>
              <p className="font-medium text-white">{key.name}</p>
              <p className="mt-1 font-mono text-xs text-slate-500">{key.prefix}••••••••••••</p>
            </div>
            <span className="text-slate-400">{key.scopes.join(", ")}</span>
            <button
              aria-label={`Delete ${key.name}`}
              className="grid h-9 w-9 place-items-center rounded-md border border-red-400/30 text-red-300 hover:bg-red-400/10"
              onClick={() => void deleteKey(key.id)}
              type="button"
            >
              <Trash2 className="h-4 w-4" />
            </button>
          </div>
        ))}
      </div>
    </section>
  );
}
