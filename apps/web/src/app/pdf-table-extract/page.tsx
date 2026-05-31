import { TopBar } from "@/components/TopBar";
import { ParsePlayground } from "@/components/ParsePlayground";
import { SeoBar } from "@/components/SeoBar";
import { SiteFooter } from "@/components/SiteFooter";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "PDF Table Extraction — DoclingRAG",
  description: "Extract tables from PDFs as Markdown, CSV, and JSON.",
};

export default function PdfTableExtractPage() {
  return (
    <div className="flex min-h-screen flex-col">
      <TopBar />
      <SeoBar />
      <main className="flex-1">
        <h1 className="sr-only">PDF Table Extract</h1>
        <ParsePlayground />
      </main>
      <SiteFooter />
    </div>
  );
}
