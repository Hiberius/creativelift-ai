import { ContentPage } from "@/components/content-page";

export const metadata = {
  title: "For B2B SaaS",
  description: "Creative testing and attribution for B2B SaaS growth teams."
};

export default function Page() {
  return (
    <ContentPage
      title="Measure AI creative impact across the SaaS funnel."
      description="Track messages from paid social, search, lifecycle email, and landing pages to signup, activation, and revenue events."
      points={["Pipeline-aware events", "Audience and angle analysis", "Governance for claims"]}
    />
  );
}
