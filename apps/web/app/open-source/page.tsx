import { Github } from "lucide-react";
import Link from "next/link";
import { MarketingNav } from "@/components/marketing";

export const metadata = {
  title: "Open Source",
  description: "CreativeLift AI is Apache-2.0, self-hostable, and built for data teams that want transparent measurement."
};

export default function OpenSourcePage() {
  return (
    <>
      <MarketingNav />
      <main className="shell py-20">
        <h1 className="text-5xl font-semibold">Open source marketing measurement infrastructure.</h1>
        <p className="mt-6 max-w-3xl text-lg leading-8 text-slate-400">
          Run CreativeLift AI locally, inspect the statistical engine, keep event data in your stack, and extend connectors without waiting on a closed roadmap.
        </p>
        <div className="mt-10 grid gap-4 md:grid-cols-3">
          {["Apache-2.0", "Self-hostable", "API-first"].map((item) => (
            <div key={item} className="panel rounded-lg p-6 text-xl font-semibold">{item}</div>
          ))}
        </div>
        <Link href="/github" className="mt-8 inline-flex items-center rounded-md bg-cyan px-5 py-3 font-semibold text-ink">
          <Github className="mr-2 h-5 w-5" />
          View repo
        </Link>
      </main>
    </>
  );
}
