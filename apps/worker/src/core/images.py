"""Image extraction and caption pairing."""

from __future__ import annotations

import re
from pathlib import Path

import pdfplumber
from pypdf import PdfReader


CAPTION_RE = re.compile(
    r"^(Figure|Fig\.?|Image|Illustration)\s*(\d+)[:\.]?\s*(.*)$",
    re.I,
)


def extract_images(pdf_path: Path, output_dir: Path) -> list[dict]:
    output_dir.mkdir(parents=True, exist_ok=True)
    images: list[dict] = []
    captions_by_page: dict[int, list[str]] = {}

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            caps = []
            for line in text.split("\n"):
                if CAPTION_RE.match(line.strip()):
                    caps.append(line.strip())
            captions_by_page[page_num] = caps

    try:
        reader = PdfReader(str(pdf_path))
        img_idx = 0
        for page_num, page in enumerate(reader.pages, start=1):
            resources = page.get("/Resources")
            if not resources:
                continue
            xobject = resources.get("/XObject")
            if not xobject:
                continue
            for name, obj in xobject.items():
                if obj.get("/Subtype") != "/Image":
                    continue
                img_idx += 1
                img_id = f"image-{img_idx}"
                ext = ".png"
                data = obj.get_data()
                out_path = output_dir / "images" / f"{img_id}{ext}"
                out_path.parent.mkdir(parents=True, exist_ok=True)
                try:
                    out_path.write_bytes(data)
                except Exception:
                    continue
                caps = captions_by_page.get(page_num, [])
                caption = caps[0] if caps else None
                images.append(
                    {
                        "id": img_id,
                        "page": page_num,
                        "path": str(out_path),
                        "caption": caption,
                        "altText": caption,
                    }
                )
    except Exception:
        pass

    return images
