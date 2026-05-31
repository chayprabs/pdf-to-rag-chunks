import { TopBar } from "@/components/TopBar";
import { ParsePlayground } from "@/components/ParsePlayground";
import { SeoBar } from "@/components/SeoBar";
import { SiteFooter } from "@/components/SiteFooter";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "PDF Chunker — DoclingRAG",
  description: "Chunk PDFs by heading, token budget, page, or citation-aware strategies.",
};

export default function PdfChunkerPage() {
  return (
    <div className="flex min-h-screen flex-col">
      <TopBar />
      <SeoBar />
      <main className="flex-1">
        <h1 className="sr-only">PDF Chunker</h1>
        <ParsePlayground />
      </main>
      <SiteFooter />
    </div>
  );
}
