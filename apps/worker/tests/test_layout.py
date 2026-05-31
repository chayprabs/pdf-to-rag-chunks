from pathlib import Path

import pytest

from src.core.layout import extract_layout


def test_extract_layout_empty_pdf(tmp_path: Path):
    # Minimal valid PDF header only won't work; skip if no sample
    sample = Path(__file__).resolve().parents[3] / "samples" / "minimal.pdf"
    if not sample.exists():
        pytest.skip("no sample pdf")
    doc = extract_layout(sample)
    assert doc.page_count >= 1
