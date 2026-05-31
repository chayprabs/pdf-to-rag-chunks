import Link from "next/link";

export function SiteFooter() {
  return (
    <footer className="mt-auto border-t border-[var(--border)] bg-white py-8">
      <div className="mx-auto flex max-w-5xl flex-col items-center gap-3 px-4 text-center text-sm text-[var(--muted)]">
        <p>
          Source code (AGPL-3.0):{" "}
          <a
            href="https://github.com/chayprabs/pdf-to-rag-chunks"
            className="hover:text-[var(--accent)]"
            target="_blank"
            rel="noopener noreferrer"
          >
            github.com/chayprabs/pdf-to-rag-chunks
          </a>
        </p>
        <div className="flex gap-8">
          <Link href="/privacy" className="hover:text-[var(--accent)]">
            Privacy Policy
          </Link>
          <Link href="/terms" className="hover:text-[var(--accent)]">
            Terms &amp; Conditions
          </Link>
        </div>
      </div>
    </footer>
  );
}
