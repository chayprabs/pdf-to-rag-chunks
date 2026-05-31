# QC Report — DoclingRAG v1.0.0

**Repo:** https://github.com/chayprabs/pdf-to-rag-chunks  
**Run at:** 2026-05-31  
**Verdict:** QUALIFIED (code/product) — hosted Lighthouse and Fly.io deploy are operator follow-ups.

## Passed

- Monorepo build, lint, typecheck
- Worker unit + API + golden + security tests (12 tests)
- All PRD sample PDFs generated
- Docker compose config + worker image build in CI
- Playwright E2E workflow (upload → parse)
- AGPL-3.0 full license text
- Privacy, terms, security.txt, Dependabot, CodeQL
- No third-party analytics; OCR on-device
- Job TTL cleanup, parse timeout, artifact path hardening

## Deferred (host/ops)

- Lighthouse ≥95 on production URL
- Fly.io / public hosted deployment
- p95 benchmarks on 30-page corpus
