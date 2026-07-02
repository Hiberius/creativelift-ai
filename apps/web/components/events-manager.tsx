"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import { Activity, AlertTriangle, RefreshCcw, Send, Terminal } from "lucide-react";
import { creativeLiftApi, EventHealth, EventIngestResponse, EventName, EventRecord } from "@/lib/api-client";
import { treatments } from "@/lib/site-data";

const eventNames: EventName[] = ["impression", "click", "session_start", "signup", "lead", "purchase", "revenue", "custom_conversion"];

function nextIdempotencyKey() {
  return `evt_${Date.now()}`;
}

function formatPercent(value: number) {
  return `${Math.round(value * 100)}%`;
}

export function EventsManager() {
  const [eventName, setEventName] = useState<EventName>("purchase");
  const [creativeTreatmentId, setCreativeTreatmentId] = useState(treatments[0]?.id ?? "00000000-0000-0000-0000-000000000101");
  const [anonymousId, setAnonymousId] = useState("anon_demo_001");
  const [value, setValue] = useState("49");
  const [currency, setCurrency] = useState("USD");
  const [idempotencyKey, setIdempotencyKey] = useState(nextIdempotencyKey());
  const [saving, setSaving] = useState(false);
  const [loadingEvents, setLoadingEvents] = useState(false);
  const [result, setResult] = useState<EventIngestResponse | null>(null);
  const [events, setEvents] = useState<EventRecord[]>([]);
  const [health, setHealth] = useState<EventHealth | null>(null);
  const [error, setError] = useState<string | null>(null);

  const selectedTreatment = treatments.find((item) => item.id === creativeTreatmentId) ?? treatments[0];
  const payloadPreview = useMemo(() => {
    const numericValue = value.trim() ? Number(value) : null;
    return {
      events: [
        {
          event_name: eventName,
          timestamp: new Date().toISOString(),
          anonymous_id: anonymousId,
          creative_treatment_id: creativeTreatmentId,
          channel: selectedTreatment?.channel ?? "demo",
          placement: selectedTreatment?.experiment ?? "demo",
          value: Number.isFinite(numericValue) ? numericValue : null,
          currency: currency || null,
          properties: {
            source: "events_screen",
            treatment_name: selectedTreatment?.name ?? "Demo treatment"
          }
        }
      ]
    };
  }, [anonymousId, creativeTreatmentId, currency, eventName, selectedTreatment?.channel, selectedTreatment?.experiment, selectedTreatment?.name, value]);

  async function loadEvents() {
    setLoadingEvents(true);
    try {
      const [nextEvents, nextHealth] = await Promise.all([
        creativeLiftApi.listEvents(),
        creativeLiftApi.getEventHealth()
      ]);
      setEvents(nextEvents);
      setHealth(nextHealth);
    } catch {
      setEvents([]);
      setHealth(null);
    } finally {
      setLoadingEvents(false);
    }
  }

  async function submitEvent(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving(true);
    setError(null);
    setResult(null);
    try {
      const [payload] = payloadPreview.events;
      const nextResult = await creativeLiftApi.ingestEvents([payload], idempotencyKey);
      setResult(nextResult);
      setIdempotencyKey(nextIdempotencyKey());
      await loadEvents();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not ingest event");
    } finally {
      setSaving(false);
    }
  }

  useEffect(() => {
    void loadEvents();
  }, []);

  return (
    <div className="grid gap-5 xl:grid-cols-[0.58fr_0.42fr]">
      <form className="panel rounded-lg p-6" onSubmit={submitEvent}>
        <div className="flex items-center gap-3">
          <Send className="h-6 w-6 text-cyan" />
          <h2 className="text-xl font-semibold">Send demo event</h2>
        </div>
        <div className="mt-5 grid gap-4 md:grid-cols-2">
          <label className="grid gap-2 text-sm text-slate-300">
            Event
            <select className="rounded-md border border-white/10 bg-ink px-3 py-3 text-white outline-none focus:border-cyan" onChange={(event) => setEventName(event.target.value as EventName)} value={eventName}>
              {eventNames.map((name) => (
                <option key={name} value={name}>{name}</option>
              ))}
            </select>
          </label>
          <label className="grid gap-2 text-sm text-slate-300">
            Creative Treatment
            <select className="rounded-md border border-white/10 bg-ink px-3 py-3 text-white outline-none focus:border-cyan" onChange={(event) => setCreativeTreatmentId(event.target.value)} value={creativeTreatmentId}>
              {treatments.map((treatment) => (
                <option key={treatment.id} value={treatment.id}>{treatment.name}</option>
              ))}
            </select>
          </label>
          <label className="grid gap-2 text-sm text-slate-300">
            Anonymous ID
            <input className="rounded-md border border-white/10 bg-white/[0.03] px-3 py-3 text-white outline-none focus:border-cyan" onChange={(event) => setAnonymousId(event.target.value)} value={anonymousId} />
          </label>
          <label className="grid gap-2 text-sm text-slate-300">
            Idempotency Key
            <input className="rounded-md border border-white/10 bg-white/[0.03] px-3 py-3 text-white outline-none focus:border-cyan" onChange={(event) => setIdempotencyKey(event.target.value)} value={idempotencyKey} />
          </label>
          <label className="grid gap-2 text-sm text-slate-300">
            Value
            <input className="rounded-md border border-white/10 bg-white/[0.03] px-3 py-3 text-white outline-none focus:border-cyan" inputMode="decimal" onChange={(event) => setValue(event.target.value)} value={value} />
          </label>
          <label className="grid gap-2 text-sm text-slate-300">
            Currency
            <input className="rounded-md border border-white/10 bg-white/[0.03] px-3 py-3 uppercase text-white outline-none focus:border-cyan" maxLength={3} onChange={(event) => setCurrency(event.target.value.toUpperCase())} value={currency} />
          </label>
        </div>
        {error ? <div className="mt-5 rounded-lg border border-red-400/30 bg-red-400/10 p-4 text-sm text-red-100">{error}</div> : null}
        {result ? (
          <div className="mt-5 rounded-lg border border-mint/30 bg-mint/10 p-4 text-sm text-mint">
            Accepted {result.accepted} event{result.accepted === 1 ? "" : "s"}; deduplicated {result.deduplicated}.
          </div>
        ) : null}
        <button className="mt-5 rounded-md bg-cyan px-5 py-3 text-sm font-semibold text-ink disabled:opacity-50" disabled={saving || !anonymousId || !creativeTreatmentId || !idempotencyKey} type="submit">
          {saving ? "Sending..." : "Send event"}
        </button>
      </form>

      <section className="panel rounded-lg p-6">
        <div className="flex items-center gap-3">
          <Terminal className="h-6 w-6 text-cyan" />
          <h2 className="text-xl font-semibold">Request preview</h2>
        </div>
        <pre className="mt-5 overflow-x-auto rounded-lg border border-white/10 bg-black/40 p-4 text-xs text-slate-300">
          <code>{`POST /v1/events/ingest
X-API-Key: dev-api-key
Idempotency-Key: ${idempotencyKey}

${JSON.stringify(payloadPreview, null, 2)}`}</code>
        </pre>
      </section>

      <section className="panel rounded-lg p-6 xl:col-span-2">
        <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <div className="flex items-center gap-3">
            <Activity className="h-6 w-6 text-cyan" />
            <h2 className="text-xl font-semibold">Event health</h2>
          </div>
          <p className="text-sm text-slate-400">
            Last event {health?.last_event_at ? new Date(health.last_event_at).toLocaleString() : "-"}
          </p>
        </div>
        {health ? (
          <>
            <div className="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-6">
              {[
                ["Events", health.total_events.toLocaleString()],
                ["Actors", health.unique_actors.toLocaleString()],
                ["Experiment", formatPercent(health.experiment_coverage)],
                ["Variant", formatPercent(health.variant_coverage)],
                ["Quality", formatPercent(health.quality_score)],
                ["Value", health.revenue.toLocaleString(undefined, { maximumFractionDigits: 2 })]
              ].map(([label, value]) => (
                <div key={label} className="rounded-md border border-white/10 bg-white/[0.03] p-4">
                  <p className="text-xs uppercase text-slate-500">{label}</p>
                  <p className="mt-2 text-2xl font-semibold text-white">{value}</p>
                </div>
              ))}
            </div>
            <div className="mt-5 grid gap-4 lg:grid-cols-[0.45fr_0.55fr]">
              <div className="rounded-md border border-white/10 bg-white/[0.03] p-4">
                <p className="text-sm font-medium text-white">Event mix</p>
                <div className="mt-3 grid gap-2 text-sm">
                  {Object.entries(health.event_counts).sort((a, b) => b[1] - a[1]).slice(0, 5).map(([name, count]) => (
                    <div key={name} className="flex items-center justify-between gap-3 text-slate-300">
                      <span>{name}</span>
                      <span className="text-slate-500">{count}</span>
                    </div>
                  ))}
                </div>
              </div>
              <div className="rounded-md border border-white/10 bg-white/[0.03] p-4">
                <p className="text-sm font-medium text-white">Warnings</p>
                {health.warnings.length ? (
                  <div className="mt-3 grid gap-2">
                    {health.warnings.map((warning) => (
                      <div key={warning} className="flex items-start gap-2 text-sm text-yellow-200">
                        <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
                        <span>{warning}</span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="mt-3 text-sm text-mint">No warnings.</p>
                )}
              </div>
            </div>
          </>
        ) : (
          <p className="mt-5 text-sm text-slate-500">No event health loaded.</p>
        )}
      </section>

      <section className="panel overflow-hidden rounded-lg xl:col-span-2">
        <div className="flex flex-col gap-3 border-b border-white/10 p-5 md:flex-row md:items-center md:justify-between">
          <div>
            <h2 className="text-xl font-semibold">Recent events</h2>
            <p className="mt-1 text-sm text-slate-400">Latest events accepted by the local demo ingestion endpoint.</p>
          </div>
          <button className="inline-flex w-fit items-center rounded-md border border-white/15 px-3 py-2 text-sm text-slate-200 hover:border-cyan/50" onClick={loadEvents} type="button">
            <RefreshCcw className="mr-2 h-4 w-4" />
            {loadingEvents ? "Refreshing..." : "Refresh"}
          </button>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full min-w-[760px] text-left text-sm">
            <thead className="text-xs uppercase text-slate-500">
              <tr>
                {["Event", "Actor", "Treatment", "Value", "Timestamp"].map((heading) => (
                  <th key={heading} className="border-b border-white/10 px-4 py-3 font-medium">{heading}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-white/10">
              {events.length ? events.map((event, index) => (
                <tr key={`${event.timestamp}-${event.anonymous_id ?? event.user_id ?? index}`} className="hover:bg-white/[0.03]">
                  <td className="px-4 py-4 font-medium text-white">{event.event_name}</td>
                  <td className="px-4 py-4 text-slate-300">{event.user_id ?? event.anonymous_id ?? "-"}</td>
                  <td className="px-4 py-4 text-slate-300">{event.creative_treatment_id.slice(0, 8)}</td>
                  <td className="px-4 py-4 text-slate-300">{event.value == null ? "-" : `${event.value} ${event.currency ?? ""}`}</td>
                  <td className="px-4 py-4 text-slate-400">{new Date(event.timestamp).toLocaleString()}</td>
                </tr>
              )) : (
                <tr>
                  <td className="px-4 py-5 text-slate-500" colSpan={5}>No events loaded yet.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
