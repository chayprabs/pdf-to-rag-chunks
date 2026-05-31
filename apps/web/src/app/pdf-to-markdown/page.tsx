import { TopBar } from "@/components/TopBar";
import { ParsePlayground } from "@/components/ParsePlayground";
import { SeoBar } from "@/components/SeoBar";
import { SiteFooter } from "@/components/SiteFooter";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "PDF to Markdown — DoclingRAG",
  description: "Convert PDF documents to clean Markdown with headings, tables, and reading order.",
};

export default function PdfToMarkdownPage() {
  return (
    <div className="flex min-h-screen flex-col">
      <TopBar />
      <SeoBar />
      <main className="flex-1">
        <h1 className="sr-only">PDF to Markdown</h1>
        <ParsePlayground />
      </main>
      <SiteFooter />
    </div>
  );
}
