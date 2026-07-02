import type { MetadataRoute } from "next";

const routes = [
  "",
  "/product",
  "/use-cases/ai-creative-testing",
  "/use-cases/marketing-attribution",
  "/use-cases/agencies",
  "/use-cases/b2b-saas",
  "/use-cases/ecommerce",
  "/open-source",
  "/security",
  "/docs",
  "/blog",
  "/compare/jasper",
  "/compare/anyword",
  "/compare/optimizely",
  "/compare/triple-whale",
  "/compare/hockeystack",
  "/pricing",
  "/github"
];

export default function sitemap(): MetadataRoute.Sitemap {
  return routes.map((route) => ({
    url: `https://creativelift.ai${route}`,
    lastModified: new Date("2026-06-28")
  }));
}
