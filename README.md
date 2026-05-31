# DoclingRAG (`pdf-to-rag-chunks`)

Parse PDFs into **RAG-ready Markdown and JSONL chunks** online with reading order, headings, tables, code blocks, captions, and OCR. Built for LangChain, LlamaIndex, and embedding pipelines.

## Features

- Layout-aware PDF parsing (reading order, headings, lists, code blocks)
- Table extraction (Markdown, CSV, JSON, HTML)
- OCR auto-routing for scanned pages (Tesseract, on-device)
- Chunking strategies: by heading, token budget (256–2048), semantic block, page, citation-aware, hybrid
- Downloads: `chunks.jsonl`, `document.md`, `manifest.json`, per-table files
- Self-host with Docker Compose

## Quick start

### Docker Compose

```bash
docker compose up -d
```

- Web: http://localhost:3000
- Worker health: http://localhost:8080/health

### Local development

```bash
pnpm install
pip install -r apps/worker/requirements.txt

# Terminal 1
cd apps/worker && PYTHONPATH=src uvicorn src.main:app --reload --port 8080

# Terminal 2
pnpm dev:web
```

## API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/parse` | POST | Upload PDF or URL; returns `ParseResult` |
| `/v1/rechunk` | POST | Re-chunk existing job without re-parse |
| `/v1/compare` | POST | Two-engine side-by-side compare |
| `/health` | GET | Worker health + engine version |

## SEO routes

- `/pdf-to-markdown`
- `/pdf-to-jsonl`
- `/pdf-table-extract`
- `/pdf-ocr`
- `/pdf-chunker`

## Samples

| File | Use case |
|------|----------|
| `minimal.pdf` | Smoke test |
| `attention-is-all-you-need.pdf` | Headings, lists, code |
| `financial-report-sample.pdf` | Tables |
| `scanned-manual.pdf` | OCR workflows |
| `multi-column-magazine.pdf` | Multi-column layout |

```bash
python3 scripts/generate_all_samples.py
```

Use the **Try a sample** chips on the homepage or `GET /v1/samples`.

## Pages

- `/` — main playground
- `/engines` — Markdown diff compare
- `/pdf-to-markdown`, `/pdf-to-jsonl`, `/pdf-table-extract`, `/pdf-ocr`, `/pdf-chunker` — SEO landings
- `/privacy`, `/terms`

## Source code (AGPL-3.0)

This service is licensed under the GNU Affero General Public License v3. Corresponding source is available at [https://github.com/chayprabs/pdf-to-rag-chunks](https://github.com/chayprabs/pdf-to-rag-chunks). If you run a modified networked version, you must offer users the complete corresponding source under the same license.

## Legal

| Document | Description |
|----------|-------------|
| [LICENSE](LICENSE) | AGPL-3.0 for the software |
| [NOTICE](NOTICE) | Copyright notice and output disclaimer |
| [docs/LEGAL_DISCLAIMER.md](docs/LEGAL_DISCLAIMER.md) | Important limits of these documents |
| Hosted [Privacy Policy](https://github.com/chayprabs/pdf-to-rag-chunks/blob/main/apps/web/src/app/privacy/page.tsx) | Data handling for the public playground (`/privacy`) |
| Hosted [Terms & Conditions](https://github.com/chayprabs/pdf-to-rag-chunks/blob/main/apps/web/src/app/terms/page.tsx) | Use of the hosted Service (`/terms`) |

**Disclaimer:** No policy or license can guarantee immunity from lawsuits in every jurisdiction. Some countries limit liability exclusions. Have a qualified attorney review these documents before commercial or high-risk use. Self-hosters must publish their own terms and privacy notice for their deployment.

## Security

See [SECURITY.md](SECURITY.md). Report issues via GitHub Security Advisories.

## Topics

`pdf` `rag` `pdf-to-markdown` `document-parsing` `ocr` `chunking` `table-extraction` `llm` `embeddings` `langchain` `llamaindex` `pdf-extraction` `online-tool`
