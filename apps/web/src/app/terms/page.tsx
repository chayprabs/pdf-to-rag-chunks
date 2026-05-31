import { TopBar } from "@/components/TopBar";
import { SiteFooter } from "@/components/SiteFooter";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Terms & Conditions — DoclingRAG",
};

export default function TermsPage() {
  return (
    <div className="flex min-h-screen flex-col bg-[var(--background)]">
      <TopBar />
      <article className="mx-auto max-w-3xl flex-1 px-4 py-12 prose prose-sm">
        <h1>Terms &amp; Conditions</h1>
        <p>
          <strong>Last updated:</strong> May 31, 2026
        </p>
        <p>
          By using DoclingRAG you agree to these terms. If you do not agree, do not use the
          service.
        </p>
        <h2>Service provided &quot;as is&quot;</h2>
        <p>
          The software and hosted playground are provided without warranties of any kind, express
          or implied, including merchantability, fitness for a particular purpose, or
          non-infringement. Parsing quality may vary by PDF layout.
        </p>
        <h2>Limitation of liability</h2>
        <p>
          To the maximum extent permitted by law, the operators and contributors shall not be liable
          for any indirect, incidental, special, consequential, or punitive damages, or any loss of
          data, profits, or business arising from your use of the service.
        </p>
        <h2>Acceptable use</h2>
        <p>
          You may not use the service to process unlawful content, infringe intellectual property,
          distribute malware, or attempt to disrupt infrastructure. You must have rights to any PDFs
          you upload.
        </p>
        <h2>Open source license</h2>
        <p>
          Source code is licensed under AGPL-3.0. Self-hosting and modifications must comply with
          that license.
        </p>
        <h2>Changes</h2>
        <p>We may update these terms. Continued use after changes constitutes acceptance.</p>
        <p className="text-xs text-[var(--muted)]">
          These terms are a good-faith limitation of risk for a free tool and are not a substitute
          for professional legal counsel.
        </p>
      </article>
      <SiteFooter />
    </div>
  );
}
