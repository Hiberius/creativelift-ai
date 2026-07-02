import { ContentPage } from "@/components/content-page";
import { comparisons } from "@/lib/site-data";

export const metadata = { title: "CreativeLift AI vs Optimizely" };

export default function Page() {
  const item = comparisons.optimizely;
  return <ContentPage title={`CreativeLift AI and ${item.name}`} description={item.positioning} points={["Creative-treatment native", "Prompt provenance", "Self-hostable stack"]} />;
}
