import type { Metadata } from "next";
import "./globals.css";

const siteUrl = "https://creativelift.ai";

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title: {
    default: "CreativeLift AI - Open Source AI Marketing Measurement",
    template: "%s | CreativeLift AI"
  },
  description:
    "CreativeLift AI tracks every AI-generated creative from prompt to experiment to incremental revenue.",
  alternates: { canonical: "/" },
  openGraph: {
    type: "website",
    url: siteUrl,
    title: "CreativeLift AI",
    description: "From prompt to profit: measure which AI creatives actually lift revenue.",
    siteName: "CreativeLift AI"
  },
  twitter: {
    card: "summary_large_image",
    title: "CreativeLift AI",
    description: "Open-source AI marketing measurement platform."
  }
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
