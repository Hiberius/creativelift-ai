import { ContentPage } from "@/components/content-page";
import { comparisons } from "@/lib/site-data";

export const metadata = { title: "CreativeLift AI vs HockeyStack" };

export default function Page() {
  const item = comparisons.hockeystack;
  return <ContentPage title={`CreativeLift AI and ${item.name}`} description={item.positioning} points={["Open-source architecture", "AI creative lineage", "Causal measurement"]} />;
}
