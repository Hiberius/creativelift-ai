import { ContentPage } from "@/components/content-page";
import { comparisons } from "@/lib/site-data";

export const metadata = { title: "CreativeLift AI vs Jasper" };

export default function Page() {
  const item = comparisons.jasper;
  return <ContentPage title={`CreativeLift AI and ${item.name}`} description={item.positioning} points={["Generation complements measurement", "Prompt lineage after creation", "Incrementality-first outcomes"]} />;
}
