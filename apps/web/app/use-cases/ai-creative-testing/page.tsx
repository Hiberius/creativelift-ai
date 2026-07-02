import { ContentPage } from "@/components/content-page";

export const metadata = {
  title: "AI Creative Testing",
  description: "AI creative testing software for prompt lineage, approvals, experiments, and lift measurement."
};

export default function Page() {
  return (
    <ContentPage
      title="AI creative testing that measures real lift."
      description="CreativeLift AI turns every generated ad, email, and landing page into a measurable treatment with prompt lineage and experiment results."
      points={["Creative Treatment registry", "A/B testing with SRM checks", "Prompt-to-revenue reporting"]}
    />
  );
}
