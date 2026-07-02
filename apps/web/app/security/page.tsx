import { ShieldCheck } from "lucide-react";
import { MarketingNav } from "@/components/marketing";

export const metadata = {
  title: "Security",
  description: "Privacy-first, self-hosted, auth-ready architecture for AI marketing measurement."
};

export default function SecurityPage() {
  const items = ["API key hashing", "Tenant isolation", "RLS-ready schema", "Audit logs", "No non-essential cookies", "Rate limit hooks"];
  return (
    <>
      <MarketingNav />
      <main className="shell py-20">
        <ShieldCheck className="h-12 w-12 text-cyan" />
        <h1 className="mt-6 text-5xl font-semibold">Security and privacy are product requirements.</h1>
        <p className="mt-6 max-w-3xl text-lg leading-8 text-slate-400">
          CreativeLift AI is designed for self-hosted teams that need governance, auditability, data control, and secure defaults.
        </p>
        <div className="mt-10 grid gap-4 md:grid-cols-3">
          {items.map((item) => <div key={item} className="panel rounded-lg p-5">{item}</div>)}
        </div>
      </main>
    </>
  );
}
