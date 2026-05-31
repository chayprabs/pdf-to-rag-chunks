# Changelog

## [1.0.0] - 2026-05-31

### Added

- DoclingRAG web playground with PDF upload, URL ingest, and sample picker
- FastAPI worker: layout parsing, tables, OCR routing, chunking strategies
- Artifact downloads: `chunks.jsonl`, `document.md`, `manifest.json`, table/image ZIPs
- Live rechunk without re-parse (layout-aware when `layout.json` present)
- Engine comparison page at `/engines`
- SEO landing routes and dynamic sitemap
- Docker Compose self-host stack with Tesseract language packs
- CI: lint, typecheck, unit tests, golden tests, Docker build, Playwright E2E, CodeQL
- AGPL-3.0 license, privacy policy, terms of service
