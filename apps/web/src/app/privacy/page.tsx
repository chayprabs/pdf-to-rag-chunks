import { TopBar } from "@/components/TopBar";
import { SiteFooter } from "@/components/SiteFooter";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Privacy Policy — DoclingRAG",
};

export default function PrivacyPage() {
  return (
    <div className="flex min-h-screen flex-col bg-[var(--background)]">
      <TopBar />
      <article className="mx-auto max-w-3xl flex-1 px-4 py-12 prose prose-sm">
        <h1>Privacy Policy</h1>
        <p>
          <strong>Last updated:</strong> May 31, 2026
        </p>
        <p>
          DoclingRAG (&quot;we&quot;, &quot;the service&quot;) is operated as an open-source tool. This policy
          explains how we handle information when you use the hosted playground or self-host the
          software.
        </p>
        <h2>Information we process</h2>
        <p>
          When you upload a PDF or provide a URL, the file is processed in ephemeral job storage on
          the server to produce Markdown and JSONL outputs. We do not require an account for basic
          use.
        </p>
        <h2>Retention</h2>
        <p>
          Uploaded PDFs and generated artifacts are stored only for a limited job TTL (default one
          hour) and are automatically deleted afterward unless you self-host with different
          settings.
        </p>
        <h2>Logging</h2>
        <p>
          We do not log PDF contents, passwords, or full filenames in application logs. Standard
          server access logs may record request metadata (timestamps, status codes, IP addresses) for
          security and reliability.
        </p>
        <h2>OCR and third parties</h2>
        <p>
          By default, OCR runs locally via Tesseract on the worker. No PDF content is sent to
          third-party OCR APIs unless you explicitly enable a cloud OCR option in a future release.
        </p>
        <h2>Cookies and tracking</h2>
        <p>
          The playground does not use third-party advertising or analytics trackers. Essential
          technical cookies may be used only if required for security or load balancing.
        </p>
        <h2>Your responsibilities</h2>
        <p>
          Do not upload confidential or personal data you are not authorized to process. You are
          responsible for complying with applicable laws when using this tool.
        </p>
        <h2>Contact</h2>
        <p>
          Questions:{" "}
          <a href="https://www.chaitanyaprabuddha.com">chaitanyaprabuddha.com</a> or the GitHub
          repository issue tracker.
        </p>
        <p className="text-xs text-[var(--muted)]">
          This policy is provided for informational purposes and does not constitute legal advice.
        </p>
      </article>
      <SiteFooter />
    </div>
  );
}
