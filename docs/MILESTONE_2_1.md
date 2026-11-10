# Milestone 2.1 — FastAPI cloud agent scaffold

## Delivered

- FastAPI service with health endpoint.
- Provider status endpoint.
- Read-only VidMuse video-model discovery endpoint (requires VidMuse CLI and interactive authentication in the runtime).
- Dry-run job creation and in-memory job lookup.
- Live generation explicitly blocked until a provider adapter and verified model contract exist.
- Dockerfile and GitHub Actions test workflow.
- API tests for health, dry-run behavior, blocked live generation, and job lookup.

## Run locally or in a cloud container

```bash
cd backend
python -m venv .venv
# activate the virtual environment
pip install -r requirements.txt
uvicorn app.main:app --reload
```

OpenAPI docs: `/docs`; health: `/health`.

## Important current limitations

- Jobs are held in process memory and disappear on restart; SQLite/PostgreSQL persistence is the next engineering step.
- No provider generation call is implemented. `dry_run=true` is the only supported job mode.
- VidMuse model discovery is read-only and requires the VidMuse CLI to be installed and authenticated in the deployed runtime.
- No API key or cloud secret is included in this repository.
- GitHub Actions validates tests; it does not deploy the service.

## Acceptance checks

1. `GET /health` returns 200.
2. `POST /v1/jobs` with dry_run true returns a planned job.
3. `POST /v1/jobs` with dry_run false returns 501 without calling a provider.
4. `GET /v1/jobs/{id}` returns the planned job.
5. CI runs the test suite on pushes and pull requests touching backend files.
