# v1.1.0 - Microservices Orchestrator, CI E2E, and Docs

## Highlights

- Orchestrator HTTP service (inspired by Camunda/Conductor) at `:5000`
- End-to-end microservices workflow with retries, step tracking, and background execution
- CI updates for health validation and E2E runs
- Architecture diagrams (Mermaid + auto-rendered SVG) and expanded docs

## New

- Orchestrator Service (`services/orchestrator_service.py`)
  - Endpoints:
    - `POST /workflows` — start a workflow
    - `GET /workflows/{id}` — inspect status and steps
    - `GET /workflows` — list workflows
    - `GET /health` — service and dependencies health
  - Steps: transcribe → format → minutes → create folder → save artifacts (TXT/DOCX/HTML) → optional copy video → workflow summary
  - Retries with backoff and per-step timings

- Launcher update (`start_services.py`)
  - Starts all services including orchestrator
  - Transcription service now supports env overrides for model/device/compute type

- Dockerfile
  - Exposes `5000 5001 5002 5003`
  - Healthcheck includes orchestrator `/health`
  - Installs `ffmpeg` for CI synthetic test videos

## CI/CD

- `.github/workflows/ci.yml`
  - Runs container, verifies health on `5000–5003`
  - Orchestrator E2E job: starts a failing workflow (missing input) and ensures terminal state

- `.github/workflows/orchestrator_happy.yml`
  - Happy path E2E: tiny CPU model, generates a 3-second test video, runs full workflow to completion, uploads output artifacts

- `.github/workflows/render_diagrams.yml`
  - Auto-renders Mermaid `diagrams/architecture.mmd` to `diagrams/architecture.svg` on push

## Documentation

- `README.md`
  - CI badges for main CI, Orchestrator Happy Path, and Render Diagrams
  - Architecture diagram (Mermaid) with static SVG fallback
  - Docker instructions updated to include orchestrator port 5000

- `README_Microservices.md`
  - Orchestrator endpoints, HTTP usage examples
  - Architecture diagram (Mermaid) with static SVG fallback

## Breaking Changes

- None. Existing CLI orchestrator `orchestrator.py` remains functional.

## Upgrade Notes

1. Pull latest changes and rebuild Docker image
2. If running locally, start via `python start_services.py`
3. Use orchestrator HTTP API (`:5000`) to start and monitor workflows

## Image

The publish workflow will push the new image to GHCR upon tag:

- `ghcr.io/nathanrish/video-chunker:v1.1.0`
- `ghcr.io/nathanrish/video-chunker:master`
