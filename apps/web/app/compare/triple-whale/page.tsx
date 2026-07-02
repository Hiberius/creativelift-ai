import { ContentPage } from "@/components/content-page";
import { comparisons } from "@/lib/site-data";

export const metadata = { title: "CreativeLift AI vs Triple Whale" };

export default function Page() {
  const item = comparisons["triple-whale"];
  return <ContentPage title={`CreativeLift AI and ${item.name}`} description={item.positioning} points={["Prompt-to-profit lineage", "Experiment calibration", "Creative governance"]} />;
}
