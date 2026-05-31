"""Shared request validation for API routes."""

from fastapi import HTTPException

VALID_OCR = frozenset({"auto", "force", "off"})
VALID_CHUNK_STRATEGIES = frozenset(
    {
        "by_heading",
        "token_budget",
        "semantic_block",
        "by_page",
        "citation_aware",
        "hybrid",
    }
)
VALID_TOKEN_BUDGETS = frozenset({256, 512, 1024, 2048})
VALID_ENGINES = frozenset({"pdfplumber"})


def validate_engine(engine: str) -> str:
    name = (engine or "pdfplumber").strip()
    if name not in VALID_ENGINES:
        raise HTTPException(
            status_code=400,
            detail="400_PDF_INVALID",
        )
    return name


def validate_ocr(ocr: str) -> str:
    mode = (ocr or "auto").strip().lower()
    if mode not in VALID_OCR:
        raise HTTPException(status_code=400, detail="400_PDF_INVALID")
    return mode


def validate_chunk_strategy(strategy: str) -> str:
    s = (strategy or "token_budget").strip()
    if s not in VALID_CHUNK_STRATEGIES:
        raise HTTPException(status_code=400, detail="400_PDF_INVALID")
    return s


def validate_token_budget(token_budget: int) -> int:
    if token_budget not in VALID_TOKEN_BUDGETS:
        raise HTTPException(status_code=400, detail="400_PDF_INVALID")
    return token_budget


def is_ocr_failure(exc: BaseException) -> bool:
    from ..core.ocr import OcrFailedError

    if isinstance(exc, OcrFailedError):
        return True
    if "OCR_FAILED" in str(exc).upper() or "OCR" in str(exc).upper():
        return True
    name = type(exc).__name__
    ocr_related = {
        "PDFInfoNotInstalledError",
        "TesseractError",
        "TesseractNotFoundError",
    }
    if name in ocr_related:
        return True
    cause = exc.__cause__
    if cause and is_ocr_failure(cause):
        return True
    return False
