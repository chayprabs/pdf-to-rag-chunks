"""Ephemeral per-job artifact storage."""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import uuid
import zipfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from ..core.chunking import ChunkRecord
from ..core.tables import ExtractedTable
from ..config import settings

JOB_ID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    re.I,
)


def validate_job_id(job_id: str) -> str:
    if not JOB_ID_RE.match(job_id):
        raise ValueError("invalid_job_id")
    return job_id


@dataclass
class JobArtifacts:
    job_id: str
    sha256: str
    page_count: int
    ocr_pages: list[int] = field(default_factory=list)
    markdown_path: Path | None = None
    chunks_path: Path | None = None
    manifest_path: Path | None = None
    tables: list[dict] = field(default_factory=list)
    images: list[dict] = field(default_factory=list)
    stats: dict = field(default_factory=dict)
    blocks_cache: list | None = None
    layout_path: Path | None = None


class JobStore:
    def __init__(self, base_dir: Path | None = None) -> None:
        self.base_dir = (base_dir or settings.jobs_dir).resolve()
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def job_dir(self, job_id: str) -> Path:
        job_id = validate_job_id(job_id)
        path = self.base_dir / job_id
        path.mkdir(parents=True, exist_ok=True)
        return path

    def create_job(self, pdf_bytes: bytes) -> tuple[str, str]:
        job_id = str(uuid.uuid4())
        sha = hashlib.sha256(pdf_bytes).hexdigest()
        pdf_path = self.job_dir(job_id) / "input.pdf"
        pdf_path.write_bytes(pdf_bytes)
        return job_id, sha

    def save_artifacts(
        self,
        job_id: str,
        sha256: str,
        markdown: str,
        chunks: list[ChunkRecord],
        tables: list[ExtractedTable],
        page_count: int,
        ocr_pages: list[int],
        images: list[dict],
        stats: dict,
    ) -> JobArtifacts:
        from ..core.chunking import chunks_to_jsonl
        from ..core.tables import table_to_csv, table_to_html, table_to_json, table_to_markdown

        job_id = validate_job_id(job_id)
        root = self.job_dir(job_id)
        md_path = root / "document.md"
        md_path.write_text(markdown, encoding="utf-8")

        chunks_path = root / "chunks.jsonl"
        chunks_path.write_text(chunks_to_jsonl(chunks), encoding="utf-8")

        tables_dir = root / "tables"
        tables_dir.mkdir(exist_ok=True)
        table_meta: list[dict] = []
        for table in tables:
            tdir = tables_dir / table.id
            tdir.mkdir(exist_ok=True)
            (tdir / "table.md").write_text(table_to_markdown(table), encoding="utf-8")
            (tdir / "table.csv").write_text(table_to_csv(table), encoding="utf-8")
            (tdir / "table.json").write_text(table_to_json(table), encoding="utf-8")
            (tdir / "table.html").write_text(table_to_html(table), encoding="utf-8")
            table_meta.append(
                {
                    "id": table.id,
                    "page": table.page,
                    "mdUrl": f"/v1/jobs/{job_id}/artifacts/tables/{table.id}/table.md",
                    "csvUrl": f"/v1/jobs/{job_id}/artifacts/tables/{table.id}/table.csv",
                    "jsonUrl": f"/v1/jobs/{job_id}/artifacts/tables/{table.id}/table.json",
                    "htmlUrl": f"/v1/jobs/{job_id}/artifacts/tables/{table.id}/table.html",
                    "quality": table.quality,
                }
            )

        images_dir = root / "images"
        images_dir.mkdir(exist_ok=True)
        for img in images:
            src = Path(img.get("path", ""))
            if src.exists():
                dest = images_dir / src.name
                shutil.copy(src, dest)
                img["url"] = f"/v1/jobs/{job_id}/artifacts/images/{src.name}"

        manifest = {
            "jobId": job_id,
            "sha256": sha256,
            "createdAt": datetime.now(timezone.utc).isoformat(),
            "pageCount": page_count,
            "ocrPages": ocr_pages,
            "stats": stats,
            "toc": stats.get("toc", []),
        }
        manifest_path = root / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

        zip_tables = root / "tables.zip"
        with zipfile.ZipFile(zip_tables, "w") as zf:
            for f in tables_dir.rglob("*"):
                if f.is_file():
                    zf.write(f, f.relative_to(tables_dir))

        return JobArtifacts(
            job_id=job_id,
            sha256=sha256,
            page_count=page_count,
            ocr_pages=ocr_pages,
            markdown_path=md_path,
            chunks_path=chunks_path,
            manifest_path=manifest_path,
            tables=table_meta,
            images=images,
            stats=stats,
        )

    def load_job_meta(self, job_id: str) -> JobArtifacts | None:
        try:
            validate_job_id(job_id)
        except ValueError:
            return None
        manifest = self.job_dir(job_id) / "manifest.json"
        if not manifest.exists():
            return None
        data = json.loads(manifest.read_text(encoding="utf-8"))
        root = self.job_dir(job_id)
        return JobArtifacts(
            job_id=job_id,
            sha256=data["sha256"],
            page_count=data["pageCount"],
            ocr_pages=data.get("ocrPages", []),
            markdown_path=root / "document.md",
            chunks_path=root / "chunks.jsonl",
            manifest_path=manifest,
            tables=[],
            images=[],
            stats=data.get("stats", {}),
        )

    def artifact_path(self, job_id: str, subpath: str) -> Path | None:
        try:
            validate_job_id(job_id)
        except ValueError:
            return None

        if ".." in subpath or subpath.startswith("/"):
            return None

        root = self.job_dir(job_id).resolve()
        candidate = (root / subpath).resolve()
        try:
            candidate.relative_to(root)
        except ValueError:
            return None

        if candidate.exists() and candidate.is_file():
            return candidate
        return None
