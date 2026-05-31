import { Github, Globe, Twitter } from "lucide-react";
import Link from "next/link";

const GITHUB_REPO = "https://github.com/chayprabs/pdf-to-rag-chunks";

export function TopBar() {
  return (
    <header className="border-b border-[var(--border)] bg-white">
      <div className="mx-auto flex max-w-5xl items-center justify-between px-4 py-4">
        <Link href="/" className="text-lg font-semibold tracking-tight text-[var(--foreground)]">
          DoclingRAG
        </Link>
        <nav className="flex items-center gap-5" aria-label="External links">
          <a
            href="https://x.com/chayprabs"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1.5 text-sm text-[var(--muted)] hover:text-[var(--accent)]"
            aria-label="Twitter / X"
          >
            <Twitter size={18} aria-hidden />
            <span className="sr-only sm:not-sr-only">@chayprabs</span>
          </a>
          <a
            href="https://www.chaitanyaprabuddha.com"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1.5 text-sm text-[var(--muted)] hover:text-[var(--accent)]"
            aria-label="Personal website"
          >
            <Globe size={18} aria-hidden />
            <span className="sr-only sm:not-sr-only">Website</span>
          </a>
          <a
            href={GITHUB_REPO}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1.5 text-sm text-[var(--muted)] hover:text-[var(--accent)]"
            aria-label="GitHub repository"
          >
            <Github size={18} aria-hidden />
            <span className="sr-only sm:not-sr-only">GitHub</span>
          </a>
        </nav>
      </div>
    </header>
  );
}
