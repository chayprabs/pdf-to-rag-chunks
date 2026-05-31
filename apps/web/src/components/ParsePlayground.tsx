"use client";

import type { ParseResult, SampleMeta } from "@pdf-to-rag-chunks/shared-types";
import { FileText, Loader2, RefreshCw, Upload } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import { artifactUrl, parseErrorMessage } from "@/lib/api-errors";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "/api/v1";

type ChunkStrategy =
  | "by_heading"
  | "token_budget"
  | "semantic_block"
  | "by_page"
  | "citation_aware"
  | "hybrid";

type Tab = "markdown" | "chunks" | "tables" | "images";

function apiArtifact(path: string): string {
  return artifactUrl(path, API_BASE);
}

export function ParsePlayground({ defaultOcr }: { defaultOcr?: "auto" | "force" | "off" }) {
  const [file, setFile] = useState<File | null>(null);
  const [url, setUrl] = useState("");
  const [ocr, setOcr] = useState<"auto" | "force" | "off">(defaultOcr ?? "auto");
  const [strategy, setStrategy] = useState<ChunkStrategy>("token_budget");
  const [tokenBudget, setTokenBudget] = useState<256 | 512 | 1024 | 2048>(512);
  const [loading, setLoading] = useState(false);
  const [rechunking, setRechunking] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [warning, setWarning] = useState<string | null>(null);
  const [result, setResult] = useState<ParseResult | null>(null);
  const [markdown, setMarkdown] = useState("");
  const [chunksText, setChunksText] = useState("");
  const [tab, setTab] = useState<Tab>("markdown");
  const [samples, setSamples] = useState<SampleMeta[]>([]);
  const [sampleLoading, setSampleLoading] = useState(false);

  const clearStaleResults = () => {
    setResult(null);
    setMarkdown("");
    setChunksText("");
    setWarning(null);
    setError(null);
  };

  useEffect(() => {
    fetch(`${API_BASE}/samples`)
      .then(async (r) => {
        if (!r.ok) throw new Error("samples list failed");
        const d = await r.json();
        if (!d.samples?.length) throw new Error("empty samples");
        setSamples(d.samples);
      })
      .catch(() => {
        setSamples([
          {
            id: "minimal",
            filename: "minimal.pdf",
            title: "Minimal demo",
            description: "Smoke test",
            url: "/v1/samples/minimal.pdf",
          },
        ]);
      });
  }, []);

  const acceptFile = (f: File) => {
    const isPdf =
      f.type === "application/pdf" || f.name.toLowerCase().endsWith(".pdf");
    if (!isPdf) {
      setError("Please select a PDF file.");
      return;
    }
    setFile(f);
    setUrl("");
    clearStaleResults();
  };

  const onDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    const f = e.dataTransfer.files[0];
    if (f) acceptFile(f);
  }, []);

  const loadArtifacts = async (data: ParseResult) => {
    const mdRes = await fetch(apiArtifact(data.markdownUrl));
    if (mdRes.ok) setMarkdown(await mdRes.text());
    else setWarning("Markdown preview unavailable.");

    const chRes = await fetch(apiArtifact(data.chunksUrl));
    if (chRes.ok) setChunksText(await chRes.text());
    else setWarning((w) => w || "Chunks preview unavailable.");
  };

  const runParse = async (sampleFile?: File) => {
    const useFile = sampleFile || file;
    if (!useFile && !url.trim()) {
      setError("Upload a PDF, pick a sample, or paste a URL.");
      return;
    }
    setLoading(true);
    setError(null);
    setWarning(null);
    setResult(null);
    setMarkdown("");
    setChunksText("");

    try {
      const form = new FormData();
      if (useFile) form.append("file", useFile);
      else form.append("url", url.trim());
      form.append("ocr", ocr);
      form.append("chunkStrategy", strategy);
      form.append("tokenBudget", String(tokenBudget));

      const res = await fetch(`${API_BASE}/parse`, { method: "POST", body: form });
      const body = await res.json().catch(() => null);
      if (!res.ok) throw new Error(parseErrorMessage(body, res.status));
      const data = body as ParseResult;
      setResult(data);
      await loadArtifacts(data);
      setTab("markdown");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Parse failed");
    } finally {
      setLoading(false);
    }
  };

  const runSample = async (sample: SampleMeta) => {
    if (loading || sampleLoading || rechunking) return;
    setSampleLoading(true);
    setError(null);
    clearStaleResults();
    try {
      const sampleUrl = sample.url.startsWith("http")
        ? sample.url
        : apiArtifact(sample.url);
      const res = await fetch(sampleUrl);
      if (!res.ok) throw new Error("Could not load sample PDF");
      const blob = await res.blob();
      const f = new File([blob], sample.filename, { type: "application/pdf" });
      setFile(f);
      await runParse(f);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Sample load failed");
    } finally {
      setSampleLoading(false);
    }
  };

  const runRechunk = async () => {
    if (!result) return;
    setRechunking(true);
    setError(null);
    setWarning(null);
    try {
      const form = new FormData();
      form.append("jobId", result.jobId);
      form.append("chunkStrategy", strategy);
      form.append("tokenBudget", String(tokenBudget));
      const res = await fetch(`${API_BASE}/rechunk`, { method: "POST", body: form });
      const body = await res.json().catch(() => null);
      if (!res.ok) throw new Error(parseErrorMessage(body, res.status));
      const chRes = await fetch(apiArtifact((body as { chunksUrl: string }).chunksUrl));
      if (chRes.ok) {
        setChunksText(await chRes.text());
      } else {
        setWarning("Could not load updated chunks. Try downloading chunks.jsonl.");
      }
      if (result.stats) {
        setResult({
          ...result,
          stats: {
            ...result.stats,
            chunks: body.stats?.chunks ?? result.stats.chunks,
            tokens: body.stats?.tokens ?? result.stats.tokens,
          },
        });
      }
      setTab("chunks");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Rechunk failed");
    } finally {
      setRechunking(false);
    }
  };

  const download = async (path: string, filename: string) => {
    try {
      const res = await fetch(apiArtifact(path));
      if (!res.ok) throw new Error("Download failed");
      const blob = await res.blob();
      const href = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = href;
      a.download = filename;
      a.click();
      URL.revokeObjectURL(href);
    } catch {
      setError(`Could not download ${filename}.`);
    }
  };

  const tabs: { id: Tab; label: string }[] = [
    { id: "markdown", label: "Markdown" },
    { id: "chunks", label: "Chunks" },
    { id: "tables", label: "Tables" },
    { id: "images", label: "Images" },
  ];

  return (
    <section className="mx-auto max-w-5xl px-4 py-8" aria-label="PDF parser">
      {samples.length > 0 && (
        <div className="mb-6">
          <p className="mb-2 text-sm text-[var(--muted)]">Try a sample</p>
          <div className="flex flex-wrap gap-2">
            {samples.map((s) => (
              <button
                key={s.id}
                type="button"
                onClick={() => runSample(s)}
                disabled={loading || sampleLoading || rechunking}
                className="rounded-full border border-[var(--border)] bg-white px-3 py-1.5 text-xs hover:border-[var(--accent)]"
                title={s.description}
              >
                {s.title}
              </button>
            ))}
          </div>
        </div>
      )}

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
            accept="application/pdf,.pdf"
            className="sr-only"
            onChange={(e) => {
              const f = e.target.files?.[0];
              if (f) acceptFile(f);
            }}
          />
        </label>
        {file && (
          <p className="mt-3 flex items-center justify-center gap-2 text-sm">
            <span>
              Selected: <strong>{file.name}</strong>
            </span>
            <button
              type="button"
              className="text-xs text-[var(--accent)] underline"
              onClick={() => {
                setFile(null);
                clearStaleResults();
              }}
            >
              Clear file
            </button>
          </p>
        )}
      </div>

      <div className="mt-4">
        <label htmlFor="pdf-url" className="mb-1 block text-sm text-[var(--muted)]">
          Or paste a public PDF URL
        </label>
        <input
          id="pdf-url"
          type="url"
          value={url}
          onChange={(e) => {
            setUrl(e.target.value);
            if (e.target.value) setFile(null);
            clearStaleResults();
          }}
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
        {(strategy === "token_budget" || strategy === "hybrid") && (
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
        )}
      </div>

      <button
        type="button"
        onClick={() => runParse()}
        disabled={loading}
        className="mt-6 flex w-full items-center justify-center gap-2 rounded-lg bg-[var(--accent)] py-3 text-sm font-semibold text-white disabled:opacity-60"
      >
        {loading ? (
          <>
            <Loader2 className="animate-spin" size={18} />
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
      {warning && !error && (
        <p className="mt-4 rounded-lg bg-amber-50 px-4 py-3 text-sm text-amber-800">{warning}</p>
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

          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              onClick={() => download(result.chunksUrl, "chunks.jsonl")}
              className="rounded-lg border border-[var(--border)] bg-white px-3 py-2 text-sm hover:border-[var(--accent)]"
            >
              chunks.jsonl
            </button>
            <button
              type="button"
              onClick={() => download(result.markdownUrl, "document.md")}
              className="rounded-lg border border-[var(--border)] bg-white px-3 py-2 text-sm hover:border-[var(--accent)]"
            >
              document.md
            </button>
            {result.manifestUrl && (
              <button
                type="button"
                onClick={() => download(result.manifestUrl!, "manifest.json")}
                className="rounded-lg border border-[var(--border)] bg-white px-3 py-2 text-sm hover:border-[var(--accent)]"
              >
                manifest.json
              </button>
            )}
            {result.tablesZipUrl && result.stats.tables > 0 && (
              <button
                type="button"
                onClick={() => download(result.tablesZipUrl!, "tables.zip")}
                className="rounded-lg border border-[var(--border)] bg-white px-3 py-2 text-sm hover:border-[var(--accent)]"
              >
                tables.zip
              </button>
            )}
            {result.imagesZipUrl && result.stats.figures > 0 && (
              <button
                type="button"
                onClick={() => download(result.imagesZipUrl!, "images.zip")}
                className="rounded-lg border border-[var(--border)] bg-white px-3 py-2 text-sm hover:border-[var(--accent)]"
              >
                images.zip
              </button>
            )}
            <button
              type="button"
              onClick={runRechunk}
              disabled={rechunking}
              className="ml-auto flex items-center gap-1 rounded-lg border border-[var(--accent)] bg-white px-3 py-2 text-sm text-[var(--accent)]"
            >
              <RefreshCw size={14} className={rechunking ? "animate-spin" : ""} />
              Rechunk
            </button>
          </div>

          <div className="flex gap-1 border-b border-[var(--border)]" role="tablist">
            {tabs.map((t) => (
              <button
                key={t.id}
                type="button"
                role="tab"
                aria-selected={tab === t.id}
                onClick={() => setTab(t.id)}
                className={`px-4 py-2 text-sm ${
                  tab === t.id
                    ? "border-b-2 border-[var(--accent)] font-medium text-[var(--accent)]"
                    : "text-[var(--muted)]"
                }`}
              >
                {t.label}
              </button>
            ))}
          </div>

          {tab === "markdown" && (
            <article className="rounded-lg border border-[var(--border)] bg-white p-6 text-sm leading-relaxed">
              {markdown ? (
                <>
                  <ReactMarkdown>{markdown.slice(0, 12000)}</ReactMarkdown>
                  {markdown.length > 12000 && (
                    <p className="mt-2 text-xs text-[var(--muted)]">
                      Preview truncated — download document.md for the full file.
                    </p>
                  )}
                </>
              ) : (
                <p className="text-[var(--muted)]">No markdown preview loaded.</p>
              )}
            </article>
          )}

          {tab === "chunks" && (
            <pre className="max-h-96 overflow-auto rounded-lg border border-[var(--border)] bg-[#f9f9f9] p-4 text-xs">
              {chunksText || "No chunks preview loaded."}
            </pre>
          )}

          {tab === "tables" && (
            <div className="rounded-lg border border-[var(--border)] bg-white p-4 text-sm">
              {result.tables.length === 0 ? (
                <p className="text-[var(--muted)]">No tables detected.</p>
              ) : (
                <ul className="space-y-3">
                  {result.tables.map((t) => (
                    <li key={t.id} className="flex flex-wrap items-center gap-2">
                      <span>
                        {t.id} · page {t.page} · quality {t.quality}
                      </span>
                      <a href={apiArtifact(t.mdUrl)} className="text-[var(--accent)]">
                        MD
                      </a>
                      <a href={apiArtifact(t.csvUrl)} className="text-[var(--accent)]">
                        CSV
                      </a>
                      <a href={apiArtifact(t.jsonUrl)} className="text-[var(--accent)]">
                        JSON
                      </a>
                      {t.htmlUrl && (
                        <a href={apiArtifact(t.htmlUrl)} className="text-[var(--accent)]">
                          HTML
                        </a>
                      )}
                    </li>
                  ))}
                </ul>
              )}
            </div>
          )}

          {tab === "images" && (
            <div className="rounded-lg border border-[var(--border)] bg-white p-4 text-sm">
              {result.images.length === 0 ? (
                <p className="text-[var(--muted)]">No images extracted.</p>
              ) : (
                <ul className="space-y-2">
                  {result.images.map((img) => (
                    <li key={img.id}>
                      {img.id} · page {img.page}
                      {img.caption && ` — ${img.caption}`}
                      {img.url && (
                        <>
                          {" "}
                          <a href={apiArtifact(img.url)} className="text-[var(--accent)]">
                            View
                          </a>
                        </>
                      )}
                    </li>
                  ))}
                </ul>
              )}
            </div>
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
