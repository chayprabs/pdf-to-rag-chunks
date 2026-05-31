#!/usr/bin/env python3
"""Generate PRD sample PDFs for tests and the sample picker."""

from __future__ import annotations

from pathlib import Path

from fpdf import FPDF

ROOT = Path(__file__).resolve().parents[1]
SAMPLES = ROOT / "samples"
WEB_SAMPLES = ROOT / "apps" / "web" / "public" / "samples"


class SamplePDF(FPDF):
    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")


def write_pdf(name: str, builder) -> None:
    pdf = SamplePDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    builder(pdf)
    out = SAMPLES / name
    out.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(out))
    WEB_SAMPLES.mkdir(parents=True, exist_ok=True)
    (WEB_SAMPLES / name).write_bytes(out.read_bytes())
    print(f"Wrote {out}")


def research_paper(pdf: FPDF) -> None:
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Attention Is All You Need", ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(0, 6, "Abstract\nWe propose the Transformer architecture for sequence transduction.")
    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, "1 Introduction", ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(
        0,
        6,
        "Recurrent models have been dominant. The Transformer relies entirely on attention [1].",
    )
    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, "2 Background", ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(0, 6, "- Autoregressive decoding\n- Encoder-decoder stacks\n- Scaled dot-product attention")
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, "3 Model Architecture", ln=True)
    pdf.set_font("Courier", "", 10)
    pdf.multi_cell(0, 5, "def attention(q, k, v):\n    return softmax(q @ k.T) @ v")


def financial_report(pdf: FPDF) -> None:
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "Financial Report - Q4 Sample", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.ln(4)
    col_w = 45
    pdf.set_font("Helvetica", "B", 10)
    for h in ["Metric", "Q3", "Q4", "YoY"]:
        pdf.cell(col_w, 8, h, border=1)
    pdf.ln()
    pdf.set_font("Helvetica", "", 10)
    rows = [
        ["Revenue", "$12.1M", "$14.8M", "+22%"],
        ["Operating income", "$2.1M", "$2.9M", "+38%"],
        ["Net margin", "12%", "15%", "+3pp"],
    ]
    for row in rows:
        for cell in row:
            pdf.cell(col_w, 8, cell, border=1)
        pdf.ln()
    pdf.ln(6)
    pdf.multi_cell(0, 6, "Figure 1: Revenue grew across all segments.")


def scanned_manual(pdf: FPDF) -> None:
    """Text layer present (simulates OCR output quality target)."""
    pdf.add_page()
    pdf.set_font("Helvetica", "", 12)
    pdf.multi_cell(
        0,
        7,
        "OPERATING MANUAL - MODEL 42\n\n"
        "Section 1: Safety\n"
        "Always disconnect power before servicing.\n\n"
        "Section 2: Maintenance\n"
        "Inspect belts monthly. Replace filter every 90 days.\n\n"
        "Figure 1: Control panel layout.",
    )


def multi_column_magazine(pdf: FPDF) -> None:
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Magazine Spread Sample", ln=True)
    pdf.set_font("Helvetica", "", 10)
    w = 90
    pdf.multi_cell(w, 5, "Column A: Urban design trends continue to reshape downtown cores worldwide.")
    pdf.set_xy(110, 30)
    pdf.multi_cell(w, 5, "Column B: Architects cite walkability and transit as top priorities for 2026.")
    pdf.set_xy(10, 80)
    pdf.multi_cell(0, 5, "Full width: This paragraph spans the page after columns.")


def minimal(pdf: FPDF) -> None:
    pdf.add_page()
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 10, "Hello DoclingRAG", ln=True)


def main() -> None:
    write_pdf("minimal.pdf", minimal)
    write_pdf("attention-is-all-you-need.pdf", research_paper)
    write_pdf("financial-report-sample.pdf", financial_report)
    write_pdf("scanned-manual.pdf", scanned_manual)
    write_pdf("multi-column-magazine.pdf", multi_column_magazine)
    print("All samples generated.")


if __name__ == "__main__":
    main()
