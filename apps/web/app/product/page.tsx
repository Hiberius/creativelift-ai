import { MarketingNav, MarketingSections } from "@/components/marketing";

export const metadata = {
  title: "Product",
  description: "Creative Treatment registry, experiment measurement, approval workflows, and AI prompt lineage for marketing teams."
};

export default function ProductPage() {
  return (
    <>
      <MarketingNav />
      <main className="shell py-20">
        <h1 className="max-w-4xl text-5xl font-semibold leading-tight">The measurement operating system for AI-generated marketing.</h1>
        <p className="mt-6 max-w-3xl text-lg leading-8 text-slate-400">
          CreativeLift AI connects briefs, prompts, variants, approvals, experiments, events, revenue, and decision recommendations around one central object: the Creative Treatment.
        </p>
      </main>
      <MarketingSections />
    </>
  );
}
