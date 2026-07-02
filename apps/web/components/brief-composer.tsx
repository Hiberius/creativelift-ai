"use client";

import { FormEvent, useState } from "react";
import { Sparkles } from "lucide-react";
import { Brief, BriefInput, CreativeTreatment, GeneratedVariant, creativeLiftApi } from "@/lib/api-client";

const initialBrief: BriefInput = {
  name: "Meta prospecting AI video test",
  objective: "Increase qualified demo requests from paid social",
  target_audience: "US B2B SaaS growth leaders at 50-500 employee companies",
  channel: "paid_social",
  primary_kpi: "signup",
  body: "Compare proof-led AI-generated hooks against static control creative."
};

export function BriefComposer() {
  const [brief, setBrief] = useState<BriefInput>(initialBrief);
  const [createdBrief, setCreatedBrief] = useState<Brief | null>(null);
  const [variants, setVariants] = useState<GeneratedVariant[]>([]);
  const [savedTreatments, setSavedTreatments] = useState<Record<string, CreativeTreatment>>({});
  const [saving, setSaving] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [savingVariant, setSavingVariant] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  function updateField(field: keyof BriefInput, value: string) {
    setBrief((current) => ({ ...current, [field]: value }));
  }

  async function createBrief(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving(true);
    setError(null);
    try {
      const nextBrief = await creativeLiftApi.createBrief(brief);
      setCreatedBrief(nextBrief);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not create brief");
    } finally {
      setSaving(false);
    }
  }

  async function generateVariants() {
    setGenerating(true);
    setError(null);
    try {
      setVariants(await creativeLiftApi.generateVariants(brief, 3));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not generate variants");
    } finally {
      setGenerating(false);
    }
  }

  async function saveAsTreatment(variant: GeneratedVariant) {
    setSavingVariant(variant.variant_id);
    setError(null);
    try {
      const treatment = await creativeLiftApi.createCreativeTreatment({
        brief_id: createdBrief?.id ?? null,
        name: variant.headline,
        objective: brief.objective,
        target_audience: brief.target_audience,
        channel: brief.channel,
        placement: "generated_variant",
        angle: variant.angle,
        hook: variant.headline,
        cta: variant.cta,
        offer: variant.landing_page_hero,
        body_copy: variant.primary_text,
        media_metadata: {
          variant_id: variant.variant_id,
          email_subject: variant.email_subject,
          landing_page_hero: variant.landing_page_hero,
          prompt_lineage: variant.prompt_lineage
        },
        ai_generated: true,
        human_edited: false
      });
      setSavedTreatments((current) => ({ ...current, [variant.variant_id]: treatment }));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not save Creative Treatment");
    } finally {
      setSavingVariant(null);
    }
  }

  return (
    <div className="grid gap-5 xl:grid-cols-[0.58fr_0.42fr]">
      <form className="panel grid gap-5 rounded-lg p-6" onSubmit={createBrief}>
        {[
          ["name", "Brief name"],
          ["objective", "Marketing objective"],
          ["target_audience", "Target audience"],
          ["channel", "Channel"],
          ["primary_kpi", "Primary KPI"]
        ].map(([field, label]) => (
          <label key={field} className="grid gap-2 text-sm text-slate-300">
            {label}
            <input
              className="rounded-md border border-white/10 bg-white/[0.03] px-3 py-3 text-white outline-none focus:border-cyan"
              onChange={(event) => updateField(field as keyof BriefInput, event.target.value)}
              value={String(brief[field as keyof BriefInput] ?? "")}
            />
          </label>
        ))}
        <label className="grid gap-2 text-sm text-slate-300">
          Brand guardrails and test notes
          <textarea
            className="min-h-28 rounded-md border border-white/10 bg-white/[0.03] px-3 py-3 text-white outline-none focus:border-cyan"
            onChange={(event) => updateField("body", event.target.value)}
            value={brief.body}
          />
        </label>
        <div className="flex flex-wrap gap-3">
          <button className="rounded-md bg-cyan px-5 py-3 font-semibold text-ink disabled:opacity-50" disabled={saving} type="submit">
            {saving ? "Creating..." : "Create draft brief"}
          </button>
          <button
            className="inline-flex items-center rounded-md border border-white/15 px-5 py-3 font-semibold text-white hover:border-cyan/50 disabled:opacity-50"
            disabled={generating}
            onClick={generateVariants}
            type="button"
          >
            <Sparkles className="mr-2 h-5 w-5 text-cyan" />
            {generating ? "Generating..." : "Generate mock variants"}
          </button>
        </div>
        {createdBrief ? (
          <div className="rounded-lg border border-mint/30 bg-mint/10 p-4 text-sm text-mint">
            Created brief: <span className="font-mono">{createdBrief.id}</span>
          </div>
        ) : null}
        {error ? (
          <div className="rounded-lg border border-red-400/30 bg-red-400/10 p-4 text-sm text-red-200">
            {error}
          </div>
        ) : null}
      </form>

      <section className="panel rounded-lg p-6">
        <h2 className="text-xl font-semibold">Generated variants</h2>
        <p className="mt-2 text-sm leading-6 text-slate-400">
          The local mock provider returns variants without requiring a real AI provider key.
        </p>
        <div className="mt-5 grid gap-4">
          {variants.length === 0 ? (
            <div className="rounded-lg border border-white/10 bg-white/[0.03] p-5 text-sm text-slate-400">
              Generate variants to preview headlines, CTA, angle, and hypothesis.
            </div>
          ) : null}
          {variants.map((variant) => (
            <article key={variant.variant_id} className="rounded-lg border border-white/10 bg-black/20 p-4">
              <p className="text-xs font-semibold uppercase text-cyan">{variant.angle}</p>
              <h3 className="mt-2 text-lg font-semibold text-white">{variant.headline}</h3>
              <p className="mt-3 text-sm leading-6 text-slate-400">{variant.primary_text}</p>
              <div className="mt-4 grid gap-2 text-xs text-slate-500">
                <span>CTA: {variant.cta}</span>
                <span>Subject: {variant.email_subject}</span>
                <span>Hypothesis: {variant.hypothesis}</span>
              </div>
              <button
                className="mt-4 rounded-md bg-cyan px-3 py-2 text-sm font-semibold text-ink disabled:opacity-50"
                disabled={Boolean(savedTreatments[variant.variant_id]) || savingVariant === variant.variant_id}
                onClick={() => void saveAsTreatment(variant)}
                type="button"
              >
                {savedTreatments[variant.variant_id]
                  ? `Saved as treatment ${savedTreatments[variant.variant_id].id.slice(0, 8)}`
                  : savingVariant === variant.variant_id
                    ? "Saving..."
                    : "Save as Creative Treatment"}
              </button>
            </article>
          ))}
        </div>
      </section>
    </div>
  );
}
