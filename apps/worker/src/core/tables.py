"""Table detection and export."""

from __future__ import annotations

import csv
import io
import json
from dataclasses import dataclass
from pathlib import Path

import pdfplumber


@dataclass
class ExtractedTable:
    id: str
    page: int
    rows: list[list[str]]
    quality: float


def extract_tables(pdf_path: Path) -> list[ExtractedTable]:
    tables: list[ExtractedTable] = []
    table_idx = 0

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            found = page.find_tables() or []
            for raw in found:
                data = raw.extract()
                if not data or len(data) < 2:
                    continue
                cleaned = [
                    [str(c or "").strip() for c in row] for row in data if any(row)
                ]
                if len(cleaned) < 2:
                    continue
                table_idx += 1
                non_empty = sum(1 for row in cleaned for c in row if c)
                total = max(len(cleaned) * max(len(r) for r in cleaned), 1)
                quality = min(1.0, non_empty / total)
                tables.append(
                    ExtractedTable(
                        id=f"table-{table_idx}",
                        page=page_num,
                        rows=cleaned,
                        quality=round(quality, 2),
                    )
                )
    return tables


def table_to_markdown(table: ExtractedTable) -> str:
    rows = table.rows
    if not rows:
        return ""
    header = rows[0]
    lines = [
        "| " + " | ".join(header) + " |",
        "| " + " | ".join("---" for _ in header) + " |",
    ]
    for row in rows[1:]:
        padded = row + [""] * (len(header) - len(row))
        lines.append("| " + " | ".join(padded[: len(header)]) + " |")
    return "\n".join(lines)


def table_to_csv(table: ExtractedTable) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    for row in table.rows:
        writer.writerow(row)
    return buf.getvalue()


def table_to_json(table: ExtractedTable) -> str:
    if not table.rows:
        return "[]"
    header = table.rows[0]
    records = []
    for row in table.rows[1:]:
        record = {}
        for i, key in enumerate(header):
            record[key or f"col{i}"] = row[i] if i < len(row) else ""
        records.append(record)
    return json.dumps(records, indent=2)


def table_to_html(table: ExtractedTable) -> str:
    lines = ["<table>"]
    for i, row in enumerate(table.rows):
        tag = "th" if i == 0 else "td"
        lines.append("<tr>")
        for cell in row:
            lines.append(f"<{tag}>{cell}</{tag}>")
        lines.append("</tr>")
    lines.append("</table>")
    return "\n".join(lines)
