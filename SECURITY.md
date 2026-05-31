# Security Policy

## Supported versions

| Version | Supported |
|---------|-----------|
| 1.x     | Yes       |

## Reporting a vulnerability

Please report security issues via [GitHub Security Advisories](https://github.com/chayprabs/pdf-to-rag-chunks/security/advisories/new).

Do not disclose sensitive PDF content in public issues.

## Practices

- Uploads stored in ephemeral job directories with TTL
- No PDF content in application logs
- OCR runs locally (Tesseract) by default
- Signed artifact URLs with path traversal checks
