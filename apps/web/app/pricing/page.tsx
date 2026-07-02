import { MarketingNav } from "@/components/marketing";

export const metadata = {
  title: "Pricing",
  description: "CreativeLift AI is open source and self-hostable. Cloud plans are coming soon."
};

export default function PricingPage() {
  const plans = [
    ["Open Source", "Free", "Self-host the core platform, API, dashboard, and measurement services."],
    ["Cloud Starter", "Coming soon", "Hosted workspace for small teams that want managed infrastructure."],
    ["Growth", "Coming soon", "Team workflows, agency reporting, and advanced connectors."],
    ["Enterprise", "Coming soon", "SSO, audit logs, governance, advanced security, and dedicated support."]
  ];
  return (
    <>
      <MarketingNav />
      <main className="shell py-20">
        <h1 className="text-5xl font-semibold">Open source first. Cloud plans coming soon.</h1>
        <p className="mt-5 text-lg text-slate-400">The core platform is open source.</p>
        <div className="mt-10 grid gap-4 lg:grid-cols-4">
          {plans.map(([name, price, body]) => (
            <article key={name} className="panel rounded-lg p-6">
              <h2 className="text-2xl font-semibold">{name}</h2>
              <p className="mt-4 text-3xl font-semibold text-cyan">{price}</p>
              <p className="mt-4 text-sm leading-6 text-slate-400">{body}</p>
            </article>
          ))}
        </div>
      </main>
    </>
  );
}
