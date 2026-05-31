import { TopBar } from "@/components/TopBar";
import { ParsePlayground } from "@/components/ParsePlayground";
import { SeoBar } from "@/components/SeoBar";
import { SiteFooter } from "@/components/SiteFooter";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "PDF OCR — DoclingRAG",
  description: "OCR scanned PDF pages with Tesseract and export RAG-ready text.",
};

export default function PdfOcrPage() {
  return (
    <div className="flex min-h-screen flex-col">
      <TopBar />
      <SeoBar />
      <main className="flex-1">
        <h1 className="sr-only">PDF OCR</h1>
        <ParsePlayground defaultOcr="force" />
      </main>
      <SiteFooter />
    </div>
  );
}
