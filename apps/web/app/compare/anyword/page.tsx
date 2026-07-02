import { ContentPage } from "@/components/content-page";
import { comparisons } from "@/lib/site-data";

export const metadata = { title: "CreativeLift AI vs Anyword" };

export default function Page() {
  const item = comparisons.anyword;
  return <ContentPage title={`CreativeLift AI and ${item.name}`} description={item.positioning} points={["Real experiment outcomes", "Revenue lift measurement", "Open-source data model"]} />;
}
