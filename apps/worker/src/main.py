import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .routes import compare, health, parse, rechunk, samples
from .storage.cleanup import purge_expired_jobs

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("worker")


async def _ttl_loop() -> None:
    while True:
        await asyncio.sleep(300)
        try:
            n = purge_expired_jobs()
            if n:
                logger.info("TTL cleanup removed %s job(s)", n)
        except Exception:
            logger.exception("TTL cleanup failed")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(
        "Worker started engine=%s version=%s jobs_dir=%s ttl=%ss",
        settings.engine,
        settings.engine_version,
        settings.jobs_dir,
        settings.job_ttl_seconds,
    )
    purge_expired_jobs()
    task = asyncio.create_task(_ttl_loop())
    yield
    task.cancel()


app = FastAPI(
    title="DoclingRAG Worker",
    description="Parse PDFs into RAG-ready Markdown and JSONL chunks",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(parse.router, prefix="/v1")
app.include_router(rechunk.router, prefix="/v1")
app.include_router(compare.router, prefix="/v1")
app.include_router(samples.router, prefix="/v1")
