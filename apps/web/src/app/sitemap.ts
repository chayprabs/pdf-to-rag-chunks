import type { MetadataRoute } from "next";

const base = process.env.NEXT_PUBLIC_SITE_URL || "https://github.com/chayprabs/pdf-to-rag-chunks";

export default function sitemap(): MetadataRoute.Sitemap {
  const routes = [
    "",
    "/pdf-to-markdown",
    "/pdf-to-jsonl",
    "/pdf-table-extract",
    "/pdf-ocr",
    "/pdf-chunker",
    "/engines",
    "/privacy",
    "/terms",
  ];
  return routes.map((path) => ({
    url: `${base.replace(/\/$/, "")}${path || "/"}`,
    lastModified: new Date(),
  }));
}
