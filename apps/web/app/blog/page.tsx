import { MarketingNav } from "@/components/marketing";

export const metadata = {
  title: "Blog",
  description: "CreativeLift AI essays on AI creative testing, incrementality, attribution, and open-source marketing measurement."
};

const posts = [
  "Why AI Marketing Needs Measurement, Not More Content",
  "What Is Creative Lift?",
  "How to Track AI-Generated Ads From Prompt to Revenue",
  "A Practical Guide to Incrementality Testing for AI Creatives",
  "Open Source vs Closed AI Marketing Platforms"
];

export default function BlogPage() {
  return (
    <>
      <MarketingNav />
      <main className="shell py-20">
        <h1 className="text-5xl font-semibold">Blog</h1>
        <div className="mt-10 grid gap-4">
          {posts.map((post) => (
            <article key={post} className="panel rounded-lg p-6">
              <h2 className="text-2xl font-semibold">{post}</h2>
              <p className="mt-3 text-slate-400">Seed post outline included for the v0.1.0 launch content calendar.</p>
            </article>
          ))}
        </div>
      </main>
    </>
  );
}
