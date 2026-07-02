import Link from "next/link";
import { ArrowRight, Check, Database, FlaskConical, Github, GitBranch, ShieldCheck, Terminal } from "lucide-react";
import { heroBullets, navItems } from "@/lib/site-data";
import { Logo } from "./logo";

export function MarketingNav() {
  return (
    <header className="sticky top-0 z-40 border-b border-white/10 bg-ink/78 backdrop-blur-xl">
      <nav className="shell flex h-20 items-center justify-between">
        <Link href="/" aria-label="CreativeLift AI home">
          <Logo />
        </Link>
        <div className="hidden items-center gap-8 text-sm text-slate-300 lg:flex">
          {navItems.map((item) => (
            <Link key={item.href} href={item.href} className="hover:text-white">
              {item.label}
            </Link>
          ))}
        </div>
        <div className="flex items-center gap-3">
          <Link className="hidden rounded-md border border-white/15 px-4 py-2 text-sm text-slate-200 sm:inline-flex" href="/github">
            <Github className="mr-2 h-4 w-4" />
            Star on GitHub
          </Link>
          <Link className="rounded-md bg-gradient-to-r from-cyan to-lime px-4 py-2 text-sm font-semibold text-ink" href="/github">
            View on GitHub
          </Link>
        </div>
      </nav>
    </header>
  );
}

export function HeroLineage() {
  const columns = [
    { title: "Prompt", items: ["SaaS growth prompt", "Brand guardrails", "Model: GPT-4o"] },
    { title: "Generated Variants", items: ["V1 proof angle", "V2 governance", "V3 revenue hook", "+24 variants"] },
    { title: "Experiments", items: ["Meta prospecting", "Search hero", "Email lifecycle"] },
    { title: "Channels", items: ["Meta Ads", "Google Ads", "LinkedIn", "Email"] },
    { title: "Outcomes", items: ["Spend $1.26M", "CVR 3.21%", "ROAS 4.37x"] },
    { title: "Revenue", items: ["$5.51M", "+23.6% lift", "Tracked"] }
  ];
  return (
    <div className="relative min-h-[470px] overflow-hidden rounded-lg border border-white/12 bg-black/20 p-5 shadow-glow">
      <div className="grid-glow absolute inset-x-0 bottom-0 h-48 opacity-70" />
      <div className="relative grid grid-cols-2 gap-3 md:grid-cols-3 xl:grid-cols-6">
        {columns.map((column, index) => (
          <div key={column.title} className="relative">
            <p className="mb-3 text-[10px] font-semibold uppercase tracking-[0.18em] text-slate-500">{column.title}</p>
            <div className="rounded-md border border-white/15 bg-panel/80 p-3">
              {column.items.map((item) => (
                <div key={item} className="mb-2 rounded border border-white/10 bg-white/[0.03] px-2 py-2 text-xs text-slate-200 last:mb-0">
                  {item}
                </div>
              ))}
            </div>
            {index < columns.length - 1 ? (
              <div className="absolute -right-3 top-28 hidden h-px w-6 bg-cyan/70 xl:block" />
            ) : null}
          </div>
        ))}
      </div>
      <div className="absolute bottom-6 left-1/2 hidden w-[78%] -translate-x-1/2 items-center justify-between rounded-md border border-white/15 bg-ink/85 px-4 py-3 font-mono text-xs text-slate-300 md:flex">
        <span>$ creativelift track --prompt-id pr_8F2a --variant v3 --channel meta --revenue 1280.45</span>
        <span className="rounded bg-mint/10 px-2 py-1 text-mint">Tracked</span>
      </div>
    </div>
  );
}

export function HomePage() {
  return (
    <>
      <MarketingNav />
      <main>
        <section className="shell grid min-h-[calc(100vh-80px)] items-center gap-10 py-14 lg:grid-cols-[0.82fr_1.18fr]">
          <div>
            <h1 className="max-w-3xl text-balance text-5xl font-semibold leading-[1.04] text-white md:text-7xl">
              Stop guessing which AI creatives work<span className="text-cyan">.</span>
            </h1>
            <p className="mt-7 max-w-2xl text-xl leading-8 text-slate-300">
              CreativeLift AI tracks every ad, email, landing page, and prompt from generation to experiment to incremental revenue — open source, self-hostable, and built for serious growth teams.
            </p>
            <div className="mt-7 grid gap-4">
              {heroBullets.map((bullet) => (
                <div key={bullet} className="flex items-center gap-3 text-base text-slate-100">
                  <Check className="h-5 w-5 text-cyan" />
                  {bullet}
                </div>
              ))}
            </div>
            <div className="mt-10 flex flex-wrap gap-4">
              <Link className="inline-flex items-center rounded-md bg-gradient-to-r from-cyan to-lime px-6 py-4 font-semibold text-ink" href="/github">
                <Github className="mr-3 h-5 w-5" />
                View on GitHub
                <ArrowRight className="ml-3 h-5 w-5" />
              </Link>
              <Link className="inline-flex items-center rounded-md border border-white/18 px-6 py-4 font-semibold text-white" href="/app/dashboard">
                <Terminal className="mr-3 h-5 w-5" />
                Run local demo
                <ArrowRight className="ml-3 h-5 w-5" />
              </Link>
            </div>
            <div className="mt-7 flex gap-6 text-sm text-slate-400">
              <span>8.6k+ GitHub stars</span>
              <span>Apache 2.0 License</span>
            </div>
          </div>
          <HeroLineage />
        </section>

        <section className="border-t border-white/10 bg-white/[0.02] py-20">
          <div className="shell">
            <div className="grid gap-8 lg:grid-cols-[0.9fr_1.1fr]">
              <div>
                <h2 className="text-4xl font-semibold text-white">The AI marketing problem</h2>
                <p className="mt-5 max-w-xl text-lg leading-8 text-slate-400">
                  AI has made it easy to create. It has not made it easy to measure. Most teams cannot connect what they prompt to what pays.
                </p>
              </div>
              <div className="grid gap-4 sm:grid-cols-2">
                {[
                  ["Too many tools", "14+", "Tools in the average marketing stack", FlaskConical],
                  ["Lost context", ">90%", "Of AI creatives lack traceable lineage", GitBranch],
                  ["Vanity metrics", "<20%", "Of reported lift is actually incremental", Database],
                  ["Slow to learn", "2-4 weeks", "To run a test and act on results", ShieldCheck]
                ].map(([title, value, body, Icon]) => (
                  <div key={String(title)} className="panel rounded-lg p-5">
                    <Icon className="h-7 w-7 text-cyan" />
                    <p className="mt-5 text-sm text-slate-300">{String(title)}</p>
                    <p className="mt-2 text-4xl font-semibold text-white">{String(value)}</p>
                    <p className="mt-2 text-sm leading-6 text-slate-400">{String(body)}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        <MarketingSections />
      </main>
    </>
  );
}

export function MarketingSections() {
  const sections = [
    ["Why dashboards lie", "Platform dashboards optimize for platform credit. CreativeLift AI stores experiment-ready exposure, conversion, and revenue events so lift can be checked instead of assumed."],
    ["From prompt to profit", "Track the full chain: brief, prompt, variant, approval, exposure, conversion, revenue."],
    ["Creative Treatment Registry", "A versioned record for every AI-generated or human-edited marketing asset, including claims, guardrails, copy, channel, placement, and lineage."],
    ["Experiment and lift measurement", "Run A/B tests with SRM checks, confidence intervals, revenue per visitor, and decision recommendations."],
    ["Attribution and MMM-ready architecture", "Use incrementality experiments to calibrate attribution and future marketing mix models."],
    ["Governance, approvals, and compliance", "Review claims, mark AI-generated creative, store evidence URLs, and keep an audit trail."],
    ["Open-source stack", "Next.js, FastAPI, PostgreSQL, Redis, Python measurement services, Docker, and connector scaffolds."]
  ];
  return (
    <section className="shell py-20">
      <div className="grid gap-5 md:grid-cols-2">
        {sections.map(([title, body]) => (
          <article key={title} className="panel rounded-lg p-6">
            <h2 className="text-2xl font-semibold text-white">{title}</h2>
            <p className="mt-4 leading-7 text-slate-400">{body}</p>
          </article>
        ))}
      </div>
      <div className="mt-10 rounded-lg border border-cyan/30 bg-cyan/8 p-8 text-center">
        <h2 className="text-3xl font-semibold text-white">Open source. Self-hostable. Incrementality-first.</h2>
        <p className="mx-auto mt-3 max-w-2xl text-slate-300">
          Built for teams that do not trust platform ROAS blindly.
        </p>
        <Link className="mt-6 inline-flex rounded-md bg-cyan px-5 py-3 font-semibold text-ink" href="/github">
          View on GitHub
        </Link>
      </div>
    </section>
  );
}
