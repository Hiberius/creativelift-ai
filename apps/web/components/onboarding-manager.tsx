"use client";

import { FormEvent, useEffect, useState } from "react";
import { Building2, CheckCircle2, ShieldCheck } from "lucide-react";
import { BrandPack, creativeLiftApi, Organization } from "@/lib/api-client";

const steps = ["Create organization", "Add brand guardrails", "Create first brief", "Generate variants", "Ingest events"];

function slugify(value: string) {
  return value
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 120) || "growth-lab";
}

export function OnboardingManager() {
  const [organizationName, setOrganizationName] = useState("Growth Lab Inc.");
  const [organization, setOrganization] = useState<Organization | null>(null);
  const [brandPacks, setBrandPacks] = useState<BrandPack[]>([]);
  const [brandName, setBrandName] = useState("Growth Lab Core");
  const [voice, setVoice] = useState("Clear, evidence-led, direct, never hype-only.");
  const [prohibitedClaims, setProhibitedClaims] = useState("guaranteed revenue, risk free growth");
  const [savingOrg, setSavingOrg] = useState(false);
  const [savingBrand, setSavingBrand] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function loadWorkspace() {
    try {
      const [me, packs] = await Promise.all([creativeLiftApi.getMe(), creativeLiftApi.listBrandPacks()]);
      setOrganization(me.organization);
      setOrganizationName(me.organization.name);
      setBrandPacks(packs);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load workspace");
    }
  }

  async function createOrganization(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSavingOrg(true);
    setError(null);
    setMessage(null);
    try {
      const nextOrganization = await creativeLiftApi.createOrganization(organizationName, slugify(organizationName));
      setOrganization(nextOrganization);
      setMessage("Organization saved.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not create organization");
    } finally {
      setSavingOrg(false);
    }
  }

  async function createBrandPack(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSavingBrand(true);
    setError(null);
    setMessage(null);
    try {
      const claims = prohibitedClaims.split(",").map((claim) => claim.trim()).filter(Boolean);
      const pack = await creativeLiftApi.createBrandPack({
        name: brandName,
        voice,
        prohibited_claims: claims,
        guardrails: {
          claims_require_evidence: true,
          tone: "premium technical"
        },
        regulated_category: false
      });
      setBrandPacks((current) => [pack, ...current]);
      setMessage("Brand pack created.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not create brand pack");
    } finally {
      setSavingBrand(false);
    }
  }

  useEffect(() => {
    void loadWorkspace();
  }, []);

  return (
    <div className="grid gap-5">
      <section className="grid gap-4 md:grid-cols-5">
        {steps.map((step, index) => (
          <article key={step} className="panel rounded-lg p-5">
            <p className="text-sm text-cyan">Step {index + 1}</p>
            <h2 className="mt-3 text-lg font-semibold">{step}</h2>
            {index < 2 ? <CheckCircle2 className="mt-4 h-5 w-5 text-mint" /> : null}
          </article>
        ))}
      </section>

      {error ? <div className="rounded-lg border border-red-400/30 bg-red-400/10 p-4 text-sm text-red-100">{error}</div> : null}
      {message ? <div className="rounded-lg border border-mint/30 bg-mint/10 p-4 text-sm text-mint">{message}</div> : null}

      <div className="grid gap-5 xl:grid-cols-2">
        <form className="panel rounded-lg p-6" onSubmit={createOrganization}>
          <div className="flex items-center gap-3">
            <Building2 className="h-6 w-6 text-cyan" />
            <h2 className="text-xl font-semibold">Workspace</h2>
          </div>
          <label className="mt-5 grid gap-2 text-sm text-slate-300">
            Organization name
            <input className="rounded-md border border-white/10 bg-white/[0.03] px-3 py-3 text-white outline-none focus:border-cyan" onChange={(event) => setOrganizationName(event.target.value)} value={organizationName} />
          </label>
          <p className="mt-3 text-sm text-slate-500">Slug: {slugify(organizationName)}</p>
          {organization ? <p className="mt-2 text-sm text-slate-400">Current workspace: {organization.name} ({organization.plan})</p> : null}
          <button className="mt-5 rounded-md bg-cyan px-5 py-3 text-sm font-semibold text-ink disabled:opacity-50" disabled={savingOrg || !organizationName} type="submit">
            {savingOrg ? "Saving..." : "Save organization"}
          </button>
        </form>

        <form className="panel rounded-lg p-6" onSubmit={createBrandPack}>
          <div className="flex items-center gap-3">
            <ShieldCheck className="h-6 w-6 text-cyan" />
            <h2 className="text-xl font-semibold">Brand guardrails</h2>
          </div>
          <div className="mt-5 grid gap-4">
            <label className="grid gap-2 text-sm text-slate-300">
              Brand pack name
              <input className="rounded-md border border-white/10 bg-white/[0.03] px-3 py-3 text-white outline-none focus:border-cyan" onChange={(event) => setBrandName(event.target.value)} value={brandName} />
            </label>
            <label className="grid gap-2 text-sm text-slate-300">
              Voice
              <textarea className="min-h-24 rounded-md border border-white/10 bg-white/[0.03] px-3 py-3 text-white outline-none focus:border-cyan" onChange={(event) => setVoice(event.target.value)} value={voice} />
            </label>
            <label className="grid gap-2 text-sm text-slate-300">
              Prohibited claims
              <input className="rounded-md border border-white/10 bg-white/[0.03] px-3 py-3 text-white outline-none focus:border-cyan" onChange={(event) => setProhibitedClaims(event.target.value)} value={prohibitedClaims} />
            </label>
          </div>
          <button className="mt-5 rounded-md bg-cyan px-5 py-3 text-sm font-semibold text-ink disabled:opacity-50" disabled={savingBrand || !brandName} type="submit">
            {savingBrand ? "Creating..." : "Create brand pack"}
          </button>
        </form>
      </div>

      <section className="panel rounded-lg p-6">
        <h2 className="text-xl font-semibold">Brand packs</h2>
        <div className="mt-4 grid gap-3 md:grid-cols-2">
          {brandPacks.map((pack) => (
            <article key={pack.id} className="rounded-md border border-white/10 bg-white/[0.03] p-4">
              <h3 className="font-semibold">{pack.name}</h3>
              <p className="mt-2 text-sm text-slate-400">{pack.voice || "No voice rules yet."}</p>
            </article>
          ))}
        </div>
      </section>
    </div>
  );
}
