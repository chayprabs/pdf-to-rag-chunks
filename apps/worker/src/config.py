from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="WORKER_")

    host: str = "0.0.0.0"
    port: int = 8080
    jobs_dir: Path = Path(__file__).resolve().parent.parent / "data" / "jobs"
    max_upload_bytes: int = 50 * 1024 * 1024
    job_ttl_seconds: int = 3600
    engine: str = "pdfplumber"
    engine_version: str = "0.11.4"
    memory_cap_mb: int = 6144
    parse_timeout_seconds: int = 300
    samples_dir: Path = Path(__file__).resolve().parent.parent.parent.parent / "samples"


settings = Settings()
settings.jobs_dir.mkdir(parents=True, exist_ok=True)
