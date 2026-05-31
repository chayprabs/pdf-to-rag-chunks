"""Ephemeral job TTL cleanup."""

from __future__ import annotations

import logging
import shutil
import time
from pathlib import Path

from ..config import settings

logger = logging.getLogger(__name__)


def purge_expired_jobs(jobs_dir: Path | None = None, ttl_seconds: int | None = None) -> int:
    base = (jobs_dir or settings.jobs_dir).resolve()
    ttl = ttl_seconds if ttl_seconds is not None else settings.job_ttl_seconds
    if not base.exists():
        return 0

    now = time.time()
    removed = 0
    for entry in base.iterdir():
        if not entry.is_dir():
            continue
        try:
            mtime = entry.stat().st_mtime
        except OSError:
            continue
        if now - mtime > ttl:
            shutil.rmtree(entry, ignore_errors=True)
            removed += 1
            logger.info("Purged expired job dir=%s", entry.name)
    return removed
