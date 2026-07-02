import { ContentPage } from "@/components/content-page";

export const metadata = {
  title: "AI Marketing Attribution",
  description: "Open-source marketing attribution architecture with creative lineage and experiment calibration."
};

export default function Page() {
  return (
    <ContentPage
      title="Attribution that knows which prompt created the outcome."
      description="Use CreativeLift AI events and experiment results to calibrate broader attribution and MMM workflows."
      points={["Attribution-ready events", "Incrementality calibration", "Warehouse-friendly schema"]}
    />
  );
}
