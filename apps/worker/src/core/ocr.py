"""OCR routing for scanned PDF pages."""

from __future__ import annotations

import logging
from pathlib import Path

import pdfplumber

logger = logging.getLogger(__name__)

SUPPORTED_LANGUAGES = [
    "eng",
    "fra",
    "deu",
    "spa",
    "ita",
    "por",
    "nld",
    "chi_sim",
    "jpn",
    "ara",
    "rus",
    "hin",
]


def detect_scanned_pages(pdf_path: Path) -> list[int]:
    scanned: list[int] = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            text = (page.extract_text() or "").strip()
            chars = page.chars
            images = page.images
            if len(text) < 30 and (images or not chars):
                scanned.append(i)
    return scanned


def run_ocr(
    pdf_path: Path,
    pages: list[int] | None = None,
    language: str = "eng",
    mode: str = "auto",
) -> dict[int, str]:
    if mode == "off":
        return {}

    try:
        import pytesseract
        from pdf2image import convert_from_path
    except ImportError:
        logger.warning("OCR dependencies not installed; skipping OCR")
        return {}

    scanned = detect_scanned_pages(pdf_path) if mode == "auto" else []
    if mode == "force":
        with pdfplumber.open(pdf_path) as pdf:
            target_pages = pages or list(range(1, len(pdf.pages) + 1))
    else:
        target_pages = pages or scanned

    if not target_pages:
        return {}

    lang = language.replace("-", "_")
    if lang not in SUPPORTED_LANGUAGES and lang != "chi-sim":
        lang = "eng"

    results: dict[int, str] = {}
    try:
        images = convert_from_path(
            str(pdf_path),
            first_page=min(target_pages),
            last_page=max(target_pages),
            dpi=200,
        )
        page_map = list(range(min(target_pages), max(target_pages) + 1))
        for img, page_num in zip(images, page_map):
            if page_num not in target_pages:
                continue
            text = pytesseract.image_to_string(img, lang=lang)
            results[page_num] = text
    except Exception as exc:
        logger.error("OCR failed: %s", exc)
        raise

    return results


def ocr_confidence_by_page(ocr_text: dict[int, str]) -> dict[int, float]:
    conf: dict[int, float] = {}
    for page, text in ocr_text.items():
        alnum = sum(1 for c in text if c.isalnum())
        ratio = alnum / max(len(text), 1)
        conf[page] = round(min(0.99, 0.5 + ratio * 0.5), 2)
    return conf
