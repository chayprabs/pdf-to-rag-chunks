"use client";

import type { ParseResult } from "@pdf-to-rag-chunks/shared-types";
import { FileText, Loader2, Upload } from "lucide-react";
import { useCallback, useState } from "react";
import ReactMarkdown from "react-markdown";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "/api/v1";

type ChunkStrategy =
  | "by_heading"
  | "token_budget"
  | "semantic_block"
  | "by_page"
  | "citation_aware"
  | "hybrid";

export function ParsePlayground() {
  const [file, setFile] = useState<File | null>(null);
  const [url, setUrl] = useState("");
  const [ocr, setOcr] = useState<"auto" | "force" | "off">("auto");
  const [strategy, setStrategy] = useState<ChunkStrategy>("token_budget");
  const [tokenBudget, setTokenBudget] = useState<256 | 512 | 1024 | 2048>(512);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ParseResult | null>(null);
  const [markdown, setMarkdown] = useState<string>("");
  const [chunksPreview, setChunksPreview] = useState<string>("");

  const onDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    const f = e.dataTransfer.files[0];
    if (f?.type === "application/pdf") setFile(f);
  }, []);

  const runParse = async () => {
    if (!file && !url.trim()) {
      setError("Upload a PDF or paste a URL.");
      return;
    }
    setLoading(true);
    setError(null);
    setResult(null);
    setMarkdown("");
    setChunksPreview("");

    try {
      const form = new FormData();
      if (file) form.append("file", file);
      else form.append("url", url.trim());
      form.append("ocr", ocr);
      form.append("chunkStrategy", strategy);
      form.append("tokenBudget", String(tokenBudget));

      const res = await fetch(`${API_BASE}/parse`, { method: "POST", body: form });
      if (!res.ok) {
        const detail = await res.text();
        throw new Error(detail || `Parse failed (${res.status})`);
      }
      const data = (await res.json()) as ParseResult;
      setResult(data);

      const mdRes = await fetch(`${API_BASE}${data.markdownUrl.replace("/v1", "")}`);
      if (mdRes.ok) setMarkdown(await mdRes.text());

      const chRes = await fetch(`${API_BASE}${data.chunksUrl.replace("/v1", "")}`);
      if (chRes.ok) {
        const text = await chRes.text();
        setChunksPreview(text.split("\n").slice(0, 5).join("\n"));
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Parse failed");
    } finally {
      setLoading(false);
    }
  };

  const download = (path: string, filename: string) => {
    const href = `${API_BASE}${path.replace("/v1", "")}`;
    const a = document.createElement("a");
    a.href = href;
    a.download = filename;
    a.click();
  };

  return (
    <section className="mx-auto max-w-5xl px-4 py-8" aria-label="PDF parser">
      <div
        onDragOver={(e) => e.preventDefault()}
        onDrop={onDrop}
        className="rounded-xl border-2 border-dashed border-[var(--border)] bg-white p-8 text-center transition-colors hover:border-[var(--accent)]"
      >
        <Upload className="mx-auto mb-3 text-[var(--muted)]" size={32} aria-hidden />
        <p className="mb-4 text-[var(--muted)]">Drag and drop a PDF, or choose a file</p>
        <label className="inline-flex cursor-pointer items-center gap-2 rounded-lg bg-[var(--accent)] px-5 py-2.5 text-sm font-medium text-white hover:opacity-90">
          <FileText size={16} aria-hidden />
          Select PDF
          <input
            type="file"
            accept="application/pdf"
            className="sr-only"
            onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          />
        </label>
        {file && (
          <p className="mt-3 text-sm text-[var(--foreground)]">
            Selected: <strong>{file.name}</strong>
          </p>
        )}
      </div>

      <div className="mt-4">
        <label htmlFor="pdf-url" className="mb-1 block text-sm text-[var(--muted)]">
          Or paste a PDF URL
        </label>
        <input
          id="pdf-url"
          type="url"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="https://example.com/paper.pdf"
          className="w-full rounded-lg border border-[var(--border)] bg-white px-3 py-2 text-sm"
        />
      </div>

      <div className="mt-6 grid gap-4 sm:grid-cols-3">
        <label className="text-sm">
          <span className="mb-1 block text-[var(--muted)]">OCR</span>
          <select
            value={ocr}
            onChange={(e) => setOcr(e.target.value as typeof ocr)}
            className="w-full rounded-lg border border-[var(--border)] bg-white px-3 py-2"
          >
            <option value="auto">Auto</option>
            <option value="force">Force</option>
            <option value="off">Off</option>
          </select>
        </label>
        <label className="text-sm">
          <span className="mb-1 block text-[var(--muted)]">Chunk strategy</span>
          <select
            value={strategy}
            onChange={(e) => setStrategy(e.target.value as ChunkStrategy)}
            className="w-full rounded-lg border border-[var(--border)] bg-white px-3 py-2"
          >
            <option value="token_budget">Token budget</option>
            <option value="by_heading">By heading</option>
            <option value="semantic_block">Semantic block</option>
            <option value="by_page">By page</option>
            <option value="citation_aware">Citation-aware</option>
            <option value="hybrid">Hybrid</option>
          </select>
        </label>
        <label className="text-sm">
          <span className="mb-1 block text-[var(--muted)]">Token budget</span>
          <select
            value={tokenBudget}
            onChange={(e) => setTokenBudget(Number(e.target.value) as typeof tokenBudget)}
            className="w-full rounded-lg border border-[var(--border)] bg-white px-3 py-2"
          >
            <option value={256}>256</option>
            <option value={512}>512</option>
            <option value={1024}>1024</option>
            <option value={2048}>2048</option>
          </select>
        </label>
      </div>

      <button
        type="button"
        onClick={runParse}
        disabled={loading}
        className="mt-6 flex w-full items-center justify-center gap-2 rounded-lg bg-[var(--accent)] py-3 text-sm font-semibold text-white disabled:opacity-60"
      >
        {loading ? (
          <>
            <Loader2 className="animate-spin" size={18} aria-hidden />
            Parsing…
          </>
        ) : (
          "Parse PDF"
        )}
      </button>

      {error && (
        <p className="mt-4 rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700" role="alert">
          {error}
        </p>
      )}

      {result && (
        <div className="mt-8 space-y-6">
          <div className="grid grid-cols-2 gap-3 rounded-lg border border-[var(--border)] bg-white p-4 text-sm sm:grid-cols-5">
            <Stat label="Pages" value={result.document.pageCount} />
            <Stat label="Headings" value={result.stats.headings} />
            <Stat label="Tables" value={result.stats.tables} />
            <Stat label="Figures" value={result.stats.figures} />
            <Stat label="Chunks" value={result.stats.chunks} />
          </div>

          <div className="flex flex-wrap gap-3">
            <button
              type="button"
              onClick={() => download(result.chunksUrl, "chunks.jsonl")}
              className="rounded-lg border border-[var(--border)] bg-white px-4 py-2 text-sm hover:border-[var(--accent)]"
            >
              Download chunks.jsonl
            </button>
            <button
              type="button"
              onClick={() => download(result.markdownUrl, "document.md")}
              className="rounded-lg border border-[var(--border)] bg-white px-4 py-2 text-sm hover:border-[var(--accent)]"
            >
              Download document.md
            </button>
          </div>

          {markdown && (
            <article className="rounded-lg border border-[var(--border)] bg-white p-6 prose prose-sm max-w-none">
              <h2 className="mb-4 text-base font-semibold">Extracted Markdown</h2>
              <ReactMarkdown>{markdown.slice(0, 8000)}</ReactMarkdown>
              {markdown.length > 8000 && (
                <p className="mt-2 text-xs text-[var(--muted)]">Preview truncated — download full file.</p>
              )}
            </article>
          )}

          {chunksPreview && (
            <pre className="overflow-x-auto rounded-lg border border-[var(--border)] bg-[#f9f9f9] p-4 text-xs">
              {chunksPreview}
            </pre>
          )}
        </div>
      )}
    </section>
  );
}

function Stat({ label, value }: { label: string; value: number }) {
  return (
    <div>
      <div className="text-[var(--muted)]">{label}</div>
      <div className="text-lg font-semibold">{value}</div>
    </div>
  );
}
