import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .routes import compare, health, parse, rechunk

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("worker")

app = FastAPI(
    title="DoclingRAG Worker",
    description="Parse PDFs into RAG-ready Markdown and JSONL chunks",
    version="1.0.0",
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


@app.on_event("startup")
async def startup() -> None:
    logger.info(
        "Worker started engine=%s version=%s jobs_dir=%s",
        settings.engine,
        settings.engine_version,
        settings.jobs_dir,
    )
