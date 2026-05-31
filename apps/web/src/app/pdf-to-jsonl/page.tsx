import { TopBar } from "@/components/TopBar";
import { ParsePlayground } from "@/components/ParsePlayground";
import { SeoBar } from "@/components/SeoBar";
import { SiteFooter } from "@/components/SiteFooter";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "PDF to JSONL Chunks — DoclingRAG",
  description: "Chunk PDFs into JSONL with page, bbox, and token metadata for RAG pipelines.",
};

export default function PdfToJsonlPage() {
  return (
    <div className="flex min-h-screen flex-col">
      <TopBar />
      <SeoBar />
      <main className="flex-1">
        <h1 className="sr-only">PDF to JSONL</h1>
        <ParsePlayground />
      </main>
      <SiteFooter />
    </div>
  );
}
