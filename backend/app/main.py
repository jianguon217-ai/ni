from __future__ import annotations

import json
import os
import shutil
import sqlite3
import subprocess
import uuid
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, HttpUrl

APP_VERSION = "0.2.0"
DB_PATH = Path(os.getenv("MYCODEX_DB_PATH", "/data/jobs.sqlite3"))
app = FastAPI(
    title="MyCodex Studio API",
    version=APP_VERSION,
    description="Cloud-first orchestration API. Generation is dry-run only until a provider is explicitly configured.",
)


class JobStatus(str, Enum):
    planned = "planned"
    queued = "queued"
    running = "running"
    succeeded = "succeeded"
    failed = "failed"


class ReferenceImage(BaseModel):
    url: HttpUrl
    role: str = Field(default="identity", pattern="^(identity|environment|style)$")


class GenerateRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=8000)
    audio_url: HttpUrl | None = None
    reference_images: list[ReferenceImage] = Field(default_factory=list, max_length=10)
    aspect_ratio: str = Field(default="9:16", pattern="^(9:16|16:9|1:1|4:3|3:4)$")
    duration_seconds: float | None = Field(default=None, gt=0, le=600)
    provider: str = Field(default="vidmuse", pattern="^(vidmuse|seedance|local)$")
    dry_run: bool = True


class Job(BaseModel):
    id: str
    status: JobStatus
    created_at: datetime
    request: GenerateRequest
    message: str
    provider_task_id: str | None = None
    output_url: str | None = None


def _connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH, timeout=10)
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    with _connect() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                request_json TEXT NOT NULL,
                message TEXT NOT NULL,
                provider_task_id TEXT,
                output_url TEXT
            )
            """
        )


def _save_job(job: Job) -> None:
    with _connect() as connection:
        connection.execute(
            """
            INSERT OR REPLACE INTO jobs
            (id, status, created_at, request_json, message, provider_task_id, output_url)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                job.id,
                job.status.value,
                job.created_at.isoformat(),
                job.request.model_dump_json(),
                job.message,
                job.provider_task_id,
                job.output_url,
            ),
        )


def _load_job(job_id: str) -> Job | None:
    with _connect() as connection:
        row = connection.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
    if row is None:
        return None
    return Job(
        id=row["id"],
        status=row["status"],
        created_at=datetime.fromisoformat(row["created_at"]),
        request=GenerateRequest.model_validate_json(row["request_json"]),
        message=row["message"],
        provider_task_id=row["provider_task_id"],
        output_url=row["output_url"],
    )


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "mycodex-studio-api", "version": APP_VERSION}


@app.get("/v1/providers")
def providers() -> dict[str, Any]:
    return {
        "providers": [
            {"id": "vidmuse", "status": "cli_available" if shutil.which("vidmuse") else "not_configured",
             "generation_enabled": False, "reason": "Read-only discovery scaffold; generation adapter requires runtime verification."},
            {"id": "seedance", "status": "not_configured", "generation_enabled": False,
             "reason": "No verified provider credentials or API contract configured."},
            {"id": "local", "status": "planned", "generation_enabled": False,
             "reason": "Local rendering adapter is not implemented."},
        ]
    }


@app.get("/v1/providers/vidmuse/models")
def vidmuse_models() -> dict[str, Any]:
    """Read-only model discovery. Never submits a generation request."""
    executable = shutil.which("vidmuse")
    if not executable:
        raise HTTPException(status_code=503, detail="VidMuse CLI is not installed in this runtime.")
    try:
        result = subprocess.run(
            [executable, "model", "list", "--video", "--output", "json"],
            capture_output=True, text=True, timeout=30, check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise HTTPException(status_code=504, detail="VidMuse model discovery timed out.") from exc
    if result.returncode == 3:
        raise HTTPException(status_code=401, detail="VidMuse CLI is not authenticated. Authenticate interactively in the runtime.")
    if result.returncode != 0:
        raise HTTPException(status_code=502, detail=f"VidMuse model discovery failed (exit {result.returncode}).")
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=502, detail="VidMuse returned invalid JSON.") from exc
    return {"provider": "vidmuse", "models": payload}


@app.post("/v1/jobs", response_model=Job)
def create_job(request: GenerateRequest) -> Job:
    job_id = str(uuid.uuid4())
    if not request.dry_run:
        raise HTTPException(
            status_code=501,
            detail="Live generation is disabled until a provider adapter, verified model contract, and per-job credit approval are configured.",
        )
    job = Job(
        id=job_id,
        status=JobStatus.planned,
        created_at=datetime.now(timezone.utc),
        request=request,
        message="Dry-run accepted. No provider was called and no credits were consumed.",
    )
    _save_job(job)
    return job


@app.get("/v1/jobs/{job_id}", response_model=Job)
def get_job(job_id: str) -> Job:
    job = _load_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found.")
    return job
