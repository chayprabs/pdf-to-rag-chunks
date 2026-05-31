import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "DoclingRAG — PDF to RAG Chunks",
  description:
    "Parse PDFs into RAG-ready Markdown and JSONL chunks online with reading order, headings, tables, code blocks, captions and OCR.",
  keywords: [
    "pdf",
    "rag",
    "pdf-to-markdown",
    "document-parsing",
    "ocr",
    "chunking",
    "table-extraction",
    "llm",
    "embeddings",
    "langchain",
    "llamaindex",
    "pdf-extraction",
    "online-tool",
  ],
  openGraph: {
    title: "DoclingRAG — PDF to RAG Chunks",
    description:
      "Parse PDFs into RAG-ready Markdown and JSONL chunks online with reading order, headings, tables, and OCR.",
    type: "website",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
