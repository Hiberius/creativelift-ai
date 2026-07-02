import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { MarketingNav } from "./marketing";

export function ContentPage({
  title,
  description,
  points,
  cta = "Run local demo"
}: {
  title: string;
  description: string;
  points: string[];
  cta?: string;
}) {
  return (
    <>
      <MarketingNav />
      <main className="shell py-20">
        <h1 className="max-w-4xl text-5xl font-semibold leading-tight">{title}</h1>
        <p className="mt-6 max-w-3xl text-lg leading-8 text-slate-400">{description}</p>
        <div className="mt-10 grid gap-4 md:grid-cols-3">
          {points.map((point) => (
            <div key={point} className="panel rounded-lg p-6 text-slate-200">{point}</div>
          ))}
        </div>
        <Link className="mt-8 inline-flex items-center rounded-md bg-cyan px-5 py-3 font-semibold text-ink" href="/app/dashboard">
          {cta}
          <ArrowRight className="ml-2 h-5 w-5" />
        </Link>
      </main>
    </>
  );
}
