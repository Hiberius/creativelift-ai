import { Github, Terminal } from "lucide-react";
import { MarketingNav } from "@/components/marketing";

export const metadata = {
  title: "GitHub",
  description: "CreativeLift AI GitHub repository description, topics, and local demo command."
};

export default function GitHubPage() {
  return (
    <>
      <MarketingNav />
      <main className="shell py-20">
        <Github className="h-12 w-12 text-cyan" />
        <h1 className="mt-6 text-5xl font-semibold">CreativeLift AI on GitHub</h1>
        <p className="mt-6 max-w-3xl text-lg leading-8 text-slate-400">
          Open-source AI marketing measurement platform. Track every creative from prompt to profit with experiments, incrementality, attribution-ready events, and creative lineage.
        </p>
        <pre className="mt-8 overflow-x-auto rounded-lg border border-white/10 bg-black/40 p-5 text-sm text-slate-200">
          <code>git clone https://github.com/Hiberius/creativelift-ai && cd creativelift-ai && docker compose up</code>
        </pre>
        <div className="mt-6 flex items-center gap-3 text-cyan">
          <Terminal className="h-5 w-5" />
          v0.1.0 "Prompt to Profit"
        </div>
      </main>
    </>
  );
}
