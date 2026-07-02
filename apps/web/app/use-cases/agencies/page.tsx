import { ContentPage } from "@/components/content-page";

export const metadata = {
  title: "For Agencies",
  description: "AI creative measurement for performance marketing agencies."
};

export default function Page() {
  return (
    <ContentPage
      title="Client-ready AI creative measurement for agencies."
      description="Standardize experiment planning, approvals, and prompt-to-profit reporting across client accounts."
      points={["Multi-tenant architecture", "Approval workflows", "Connector scaffolds"]}
    />
  );
}
