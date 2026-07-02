import Link from "next/link";
import { MarketingNav } from "@/components/marketing";

export const metadata = {
  title: "Docs",
  description: "CreativeLift AI documentation for self-hosting, API usage, creative treatments, event ingestion, and measurement methodology."
};

export default function DocsPage() {
  const docs = ["Architecture", "Creative Treatment Model", "Event Ingestion", "Experiment Design", "Measurement Methodology", "Self-hosting", "Security", "Privacy"];
  return (
    <>
      <MarketingNav />
      <main className="shell py-20">
        <h1 className="text-5xl font-semibold">Docs</h1>
        <div className="mt-10 grid gap-4 md:grid-cols-2">
          {docs.map((doc) => (
            <Link key={doc} href="/docs" className="panel rounded-lg p-6 hover:border-cyan/40">
              <h2 className="text-xl font-semibold">{doc}</h2>
              <p className="mt-2 text-sm text-slate-400">Markdown documentation is included in the repository under `/docs`.</p>
            </Link>
          ))}
        </div>
      </main>
    </>
  );
}
