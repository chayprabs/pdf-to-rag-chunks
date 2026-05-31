export function SeoBar() {
  return (
    <div
      className="w-full border-b border-[var(--border)] bg-[#f5f5f5] px-4 py-3 text-center text-sm leading-relaxed text-[var(--muted)]"
      role="region"
      aria-label="Product description"
    >
      <p className="mx-auto max-w-3xl">
        Parse PDFs into RAG-ready Markdown and JSONL chunks with reading order, headings, tables,
        and OCR — built for LangChain, LlamaIndex, and embedding pipelines.
      </p>
      <p className="mx-auto mt-1 max-w-3xl">
        Drop a PDF below, choose chunking options, and download structured chunks in seconds.
      </p>
    </div>
  );
}
