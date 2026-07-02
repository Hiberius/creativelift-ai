import { ContentPage } from "@/components/content-page";

export const metadata = {
  title: "For E-commerce",
  description: "Creative lift measurement for DTC and e-commerce teams."
};

export default function Page() {
  return (
    <ContentPage
      title="Connect generated product creative to purchases and revenue."
      description="Measure offer, hook, CTA, image, and video variants against purchase and revenue-per-visitor outcomes."
      points={["Purchase/revenue events", "Guardrail metrics", "MMM-ready calibration"]}
    />
  );
}
