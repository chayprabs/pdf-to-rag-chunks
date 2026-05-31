"use client";

import { SeoBar } from "@/components/SeoBar";
import { SiteFooter } from "@/components/SiteFooter";
import { TopBar } from "@/components/TopBar";
import { parseErrorMessage } from "@/lib/api-errors";
import { FileText, Loader2 } from "lucide-react";
import { useState } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "/api/v1";

export default function EnginesPage() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [diff, setDiff] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [hasCompared, setHasCompared] = useState(false);

  const runCompare = async () => {
    if (!file) {
      setError("Select a PDF first.");
      return;
    }
    setLoading(true);
    setError(null);
    setDiff([]);
    setHasCompared(false);
    try {
      const form = new FormData();
      form.append("file", file);
      form.append("engineA", "pdfplumber");
      form.append("engineB", "pdfplumber-alt");
      const res = await fetch(`${API_BASE}/compare`, { method: "POST", body: form });
      const body = await res.json().catch(() => null);
      if (!res.ok) throw new Error(parseErrorMessage(body, res.status));
      setDiff(body.diff || []);
      setHasCompared(true);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Compare failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen flex-col">
      <TopBar />
      <SeoBar />
      <main className="mx-auto max-w-5xl flex-1 px-4 py-8">
        <h1 className="mb-2 text-xl font-semibold">Engine comparison</h1>
        <p className="mb-6 text-sm text-[var(--muted)]">
          Run two parse passes and view a unified diff of Markdown output.
        </p>
        <label className="mb-4 inline-flex cursor-pointer items-center gap-2 rounded-lg border border-[var(--border)] bg-white px-4 py-2 text-sm">
          <FileText size={16} />
          Select PDF
          <input
            type="file"
            accept="application/pdf,.pdf"
            className="sr-only"
            onChange={(e) => {
              setFile(e.target.files?.[0] ?? null);
              setHasCompared(false);
              setDiff([]);
            }}
          />
        </label>
        {file && <p className="mb-4 text-sm">{file.name}</p>}
        <button
          type="button"
          onClick={runCompare}
          disabled={loading}
          className="flex items-center gap-2 rounded-lg bg-[var(--accent)] px-5 py-2.5 text-sm font-medium text-white"
        >
          {loading && <Loader2 className="animate-spin" size={16} />}
          Compare engines
        </button>
        {error && <p className="mt-4 text-sm text-red-600">{error}</p>}
        {diff.length > 0 && (
          <pre className="mt-6 max-h-96 overflow-auto rounded-lg border bg-[#f9f9f9] p-4 text-xs">
            {diff.join("\n")}
          </pre>
        )}
        {hasCompared && diff.length === 0 && !error && (
          <p className="mt-4 text-sm text-[var(--muted)]">
            Identical outputs — both runs use the same engine today.
          </p>
        )}
      </main>
      <SiteFooter />
    </div>
  );
}
