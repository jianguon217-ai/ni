from __future__ import annotations

import os
import shutil
import subprocess
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, HttpUrl

APP_VERSION = "0.1.0"
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


JOBS: dict[str, Job] = {}


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
        # Avoid returning stderr verbatim because it may contain sensitive runtime details.
        raise HTTPException(status_code=502, detail=f"VidMuse model discovery failed (exit {result.returncode}).")
    import json
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
    JOBS[job_id] = job
    return job


@app.get("/v1/jobs/{job_id}", response_model=Job)
def get_job(job_id: str) -> Job:
    job = JOBS.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found.")
    return job
