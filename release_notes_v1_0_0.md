# v1.0.0 - Initial release

- Video chunking via `video_splitter.py`
- Transcription, aggregation, Agile minutes & snapshot via `transcribe.py`
- Dockerfile with system ffmpeg
- CI, E2E workflow, and GHCR publish

## Docker Image

The Docker image is published to GitHub Container Registry (GHCR):

- Image (tagged): `ghcr.io/nathanrish/video-chunker:v1.0.0`
- Latest branch tag: `ghcr.io/nathanrish/video-chunker:master`

Pull commands:

```bash
# Tagged release image
docker pull ghcr.io/nathanrish/video-chunker:v1.0.0

# Latest from default branch
docker pull ghcr.io/nathanrish/video-chunker:master
```

## Usage (Docker)

```bash
# Split example
docker run --rm -v %cd%:/app -w /app ghcr.io/nathanrish/video-chunker:v1.0.0 \
  python video_splitter.py -d 60 -c 10

# Transcribe example
docker run --rm -v %cd%:/app -w /app ghcr.io/nathanrish/video-chunker:v1.0.0 \
  python transcribe.py --chunks-dir ./output/<video_name>_chunks --model small --language en --word-timestamps
```

## Notes
- Set `OPENAI_API_KEY` to enable `--use-llm` refinement in `transcribe.py`.
- For diarization support, provide `HUGGINGFACE_TOKEN` in future updates.

---

## Addendum: Microservices Orchestrator Service (Post v1.0.0)

A dedicated HTTP orchestrator service has been added to coordinate the microservices workflow, inspired by Camunda/Conductor.

### Endpoints (Port 5000)

```bash
# Health
GET /health

# Start workflow
POST /workflows
{
  "video_path": "input/meeting.mp4",
  "meeting_title": "Team Meeting",
  "meeting_date": "2024-01-15T10:00:00",  # optional ISO
  "language": "en",                         # optional
  "copy_video": true                         # default true
}

# Get workflow status
GET /workflows/{id}

# List workflows
GET /workflows?limit=50&status=running|completed|failed
```

### Local Run

```bash
python start_services.py

# In another shell, start a workflow via HTTP
curl -X POST http://localhost:5000/workflows \
  -H "Content-Type: application/json" \
  -d '{
        "video_path": "input/meeting.mp4",
        "meeting_title": "Team Meeting"
      }'
```

### Docker

The Dockerfile now exposes port 5000 and healthchecks include the orchestrator service.

```bash
docker run --rm -p 5000:5000 -p 5001:5001 -p 5002:5002 -p 5003:5003 \
  -v %cd%:/app -w /app ghcr.io/nathanrish/video-chunker:v1.0.0

# Start a workflow from host
curl -X POST http://localhost:5000/workflows \
  -H "Content-Type: application/json" \
  -d '{"video_path":"input/meeting.mp4","meeting_title":"Team Meeting"}'
```
