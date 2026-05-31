import { TopBar } from "@/components/TopBar";
import { SiteFooter } from "@/components/SiteFooter";
import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Privacy Policy — DoclingRAG",
  description:
    "How DoclingRAG handles PDF uploads, ephemeral storage, logs, and your privacy rights.",
};

export default function PrivacyPage() {
  return (
    <div className="flex min-h-screen flex-col bg-[var(--background)]">
      <TopBar />
      <article className="mx-auto max-w-3xl flex-1 px-4 py-12 text-sm leading-relaxed text-[var(--foreground)]">
        <h1 className="mb-4 text-2xl font-semibold">Privacy Policy</h1>
        <p className="mb-6 text-[var(--muted)]">
          <strong>Effective date:</strong> May 31, 2026 ·{" "}
          <strong>Last updated:</strong> May 31, 2026
        </p>

        <p className="mb-4">
          This Privacy Policy describes how <strong>DoclingRAG</strong> (“Service”, “we”, “us”)
          operated by <strong>Chaitanya Prabuddha</strong> (“Operator”) processes information when
          you use the public playground at our website, interact with our APIs, or self-host the
          open-source software. By using the Service, you acknowledge this Policy and our{" "}
          <Link href="/terms" className="text-[var(--accent)] underline">
            Terms &amp; Conditions
          </Link>
          .
        </p>

        <h2 className="mb-2 mt-8 text-lg font-semibold">1. Who we are</h2>
        <p className="mb-4">
          <strong>Data controller</strong> (for the hosted Service): Chaitanya Prabuddha. Contact:{" "}
          <a
            href="https://www.chaitanyaprabuddha.com"
            className="text-[var(--accent)] underline"
            rel="noopener noreferrer"
            target="_blank"
          >
            https://www.chaitanyaprabuddha.com
          </a>{" "}
          or via the GitHub repository{" "}
          <a
            href="https://github.com/chayprabs/pdf-to-rag-chunks"
            className="text-[var(--accent)] underline"
            rel="noopener noreferrer"
            target="_blank"
          >
            chayprabs/pdf-to-rag-chunks
          </a>
          .
        </p>
        <p className="mb-4">
          If you self-host the software, <strong>you</strong> are the controller for processing you
          perform on your infrastructure. This Policy applies to the Operator&apos;s hosted
          instance only unless stated otherwise.
        </p>

        <h2 className="mb-2 mt-8 text-lg font-semibold">2. What we process</h2>
        <ul className="mb-4 list-disc space-y-2 pl-6">
          <li>
            <strong>PDF files and URLs you submit</strong> — processed to generate Markdown, JSONL
            chunks, tables, images, and related artifacts.
          </li>
          <li>
            <strong>Technical data</strong> — IP address, user-agent, request timestamps, HTTP
            status codes, and similar metadata in server or CDN logs for security and abuse
            prevention.
          </li>
          <li>
            <strong>We do not require an account</strong> for basic playground use and do not
            intentionally collect government ID numbers, payment cards, or passwords through the
            Service.
          </li>
        </ul>
        <p className="mb-4">
          <strong>We do not sell your personal information.</strong> We do not use third-party
          advertising trackers or behavioral profiling on the playground.
        </p>

        <h2 className="mb-2 mt-8 text-lg font-semibold">3. Purposes and legal bases</h2>
        <p className="mb-4">We process data to:</p>
        <ul className="mb-4 list-disc space-y-2 pl-6">
          <li>Provide parsing, chunking, OCR, and download features you request;</li>
          <li>Secure and operate the Service (fraud prevention, rate limits, debugging);</li>
          <li>Comply with law and enforce our Terms.</li>
        </ul>
        <p className="mb-4">
          Where the GDPR or similar laws apply, bases may include <strong>performance of a
          contract</strong> (providing the Service at your request), <strong>legitimate
          interests</strong> (security, improving reliability), and <strong>legal obligation</strong>
          . Where consent is required for a specific optional feature, we will ask separately.
        </p>

        <h2 className="mb-2 mt-8 text-lg font-semibold">4. Retention and deletion</h2>
        <p className="mb-4">
          Uploaded PDFs and generated job artifacts on the hosted Service are kept only in ephemeral
          storage for a limited period (default approximately one hour, configurable on self-hosted
          deployments) and are deleted automatically afterward unless a longer period is required
          by law or to resolve an active abuse investigation.
        </p>
        <p className="mb-4">
          Server logs may be retained for a limited period consistent with security needs, then
          rotated or deleted.
        </p>

        <h2 className="mb-2 mt-8 text-lg font-semibold">5. OCR and subprocessors</h2>
        <p className="mb-4">
          By default, OCR runs <strong>on the same worker</strong> using Tesseract. We do not send
          your PDF content to third-party OCR APIs in the default configuration. Infrastructure
          providers (e.g. hosting, CDN) may process network traffic metadata under their own
          policies.
        </p>

        <h2 className="mb-2 mt-8 text-lg font-semibold">6. International transfers</h2>
        <p className="mb-4">
          The hosted Service may be operated from servers in various regions. If you access the
          Service from outside that region, your data may be processed there. Where required, we
          rely on appropriate safeguards or derogations permitted by applicable law.
        </p>

        <h2 className="mb-2 mt-8 text-lg font-semibold">7. Your responsibilities</h2>
        <p className="mb-4">
          You must have a lawful basis to upload and process any PDF (including personal data of
          others). Do not upload illegal content, malware, or material you lack rights to use. You
          are solely responsible for compliance with employment, healthcare, financial, and sector
          rules (HIPAA, GDPR, etc.) that apply to <strong>your</strong> use case.
        </p>

        <h2 className="mb-2 mt-8 text-lg font-semibold">8. Your rights</h2>
        <p className="mb-4">
          Depending on your location, you may have rights to access, correct, delete, restrict, or
          object to processing of personal data, and to data portability or lodge a complaint with
          a supervisory authority. Because job data is ephemeral, deletion often occurs automatically
          when the job TTL expires. Contact us with reasonable requests; we may need to verify
          identity and may refuse manifestly unfounded or excessive requests as permitted by law.
        </p>
        <p className="mb-4">
          <strong>California residents (CCPA/CPRA):</strong> We do not sell or share personal
          information for cross-context behavioral advertising. You may contact us regarding
          applicable rights.
        </p>

        <h2 className="mb-2 mt-8 text-lg font-semibold">9. Children</h2>
        <p className="mb-4">
          The Service is not directed to children under 16 (or the age required in your country). We
          do not knowingly collect personal information from children. If you believe a child
          provided data, contact us for deletion.
        </p>

        <h2 className="mb-2 mt-8 text-lg font-semibold">10. Security</h2>
        <p className="mb-4">
          We use reasonable technical measures (HTTPS, ephemeral storage, access controls on
          self-hosted guidance). No method of transmission or storage is 100% secure; we do not
          guarantee absolute security.
        </p>

        <h2 className="mb-2 mt-8 text-lg font-semibold">11. Changes</h2>
        <p className="mb-4">
          We may update this Policy. The effective date at the top will change. Material changes
          may be noted on the website. Continued use after changes constitutes acceptance where
          permitted by law.
        </p>

        <h2 className="mb-2 mt-8 text-lg font-semibold">12. No legal advice</h2>
        <p className="mb-4 text-[var(--muted)]">
          This Policy is for transparency only and is not legal advice. Consult a qualified
          attorney in your jurisdiction for compliance with laws that apply to you.
        </p>
      </article>
      <SiteFooter />
    </div>
  );
}
