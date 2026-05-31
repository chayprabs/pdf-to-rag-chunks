export const ERROR_MAP: Record<string, string> = {
  "400_PDF_INVALID": "Invalid or missing PDF. Upload a valid file or URL.",
  "413_PDF_TOO_LARGE": "PDF is too large. Maximum size is 50 MB.",
  "424_OCR_FAILED": "OCR failed on this document.",
  "424_PARSE_TIMEOUT": "Parsing timed out. Try a smaller file or disable OCR.",
  "404_NOT_FOUND": "Download not found. Try parsing again.",
  "404_JOB_NOT_FOUND": "Job not found. Parse again first.",
  "500_PARSE_FAILED": "Server could not parse this PDF.",
};

export function parseErrorMessage(body: unknown, status: number): string {
  if (body && typeof body === "object" && "detail" in body) {
    const detail = (body as { detail: unknown }).detail;
    if (typeof detail === "string") {
      return ERROR_MAP[detail] || detail;
    }
    if (Array.isArray(detail)) {
      return "Invalid request. Check your inputs.";
    }
  }
  return `Request failed (${status})`;
}

export function artifactUrl(path: string, apiBase = "/api/v1"): string {
  const normalized = path.startsWith("/v1") ? path.slice(3) : path;
  return `${apiBase}${normalized}`;
}
