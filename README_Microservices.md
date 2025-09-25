# Video to Meeting Minutes - Microservices Architecture

A scalable microservices-based system that automatically transcribes videos and generates professional Agile TPM meeting minutes with organized output in dated folders.

## 🏗️ Architecture

The system consists of 4 microservices and a dedicated HTTP orchestrator service:

### Services

1. **Transcription Service** (Port 5001)
   - Handles video transcription using faster-whisper
   - Supports multiple languages and model sizes
   - Provides word-level timestamps

2. **Meeting Minutes Service** (Port 5002)
   - Generates Agile TPM style meeting minutes
   - Extracts epics, risks, action items, decisions
   - Supports AI-powered analysis with OpenAI
   - Exports to DOCX and HTML formats

3. **File Management Service** (Port 5003)
   - Creates dated output folders
   - Manages file operations and organization
   - Handles document generation and storage

4. **Orchestrator** (CLI)
   - Coordinates the entire workflow
   - Manages service communication
   - Provides error handling and logging

5. **Orchestrator Service** (Port 5000)
   - HTTP workflow engine inspired by Camunda/Conductor
   - Start workflows and query status over REST
   - Tracks steps, durations, retries, and errors
   - Executes workflows in the background

## 🗺️ Architecture Diagram

```mermaid
flowchart LR
    subgraph Client
      U[User / CLI / CI]
    end

    U -->|HTTP POST /workflows| ORCH[(Orchestrator Service\nPort 5000)]

    subgraph Services
      T[Transcription Service\nPort 5001]\n:::svc
      M[Meeting Minutes Service\nPort 5002]\n:::svc
      F[File Management Service\nPort 5003]\n:::svc
    end

    ORCH -->|/transcribe| T
    T -->|segments JSON| ORCH

    ORCH -->|/format-transcript| T
    T -->|formatted text| ORCH

    ORCH -->|/generate-minutes| M
    M -->|meeting data JSON| ORCH

    ORCH -->|/create-dated-folder| F
    ORCH -->|/save-transcript| F
    ORCH -->|/save-meeting-minutes-docx| F
    ORCH -->|/save-meeting-minutes-html| F
    ORCH -->|/copy-video (optional)| F
    ORCH -->|/create-workflow-summary| F

    subgraph Output
      O[(output/YYYY-MM-DD_Title/)]
    end

    F --> O
    ORCH -->|GET /workflows/{id}| U

    classDef svc fill:#eef,stroke:#446,stroke-width:1px;
```

The orchestrator coordinates the end-to-end workflow and persists step-by-step results (in-memory by default). Each microservice exposes health endpoints and task-specific APIs. Artifacts (transcript, DOCX, HTML, workflow summary, optional original video) are written under `output/<dated_folder>/`.

If your Markdown renderer does not support Mermaid, see the static diagram:

![Architecture SVG](diagrams/architecture.svg)

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements_microservices.txt
```

### 2. Start All Services

```bash
# Start all services (without AI features)
python start_services.py

# Start with OpenAI API key for enhanced AI features
python start_services.py --api-key your_openai_key
```

### 3. Run the Workflow

```bash
# Basic usage
python orchestrator.py "input/meeting.mp4" "Team Meeting"

# With custom date and language
python orchestrator.py "input/meeting.mp4" "Sprint Planning" --date "2024-01-15" --language en

# Without copying original video
python orchestrator.py "input/meeting.mp4" "Product Review" --no-copy-video
```

### 3a. Start the Workflow via Orchestrator Service (HTTP)

```bash
# Start a workflow (returns 202 with workflow id)
curl -X POST http://localhost:5000/workflows \
  -H "Content-Type: application/json" \
  -d '{
        "video_path": "input/meeting.mp4",
        "meeting_title": "Team Meeting",
        "meeting_date": "2024-01-15T10:00:00",
        "language": "en",
        "copy_video": true
      }'

# Get workflow status by id
curl http://localhost:5000/workflows/<workflow_id>

# List recent workflows
curl http://localhost:5000/workflows?limit=20
```

### Docker: Use prebuilt image (recommended)

```bash
# Pull the latest release image
docker pull ghcr.io/nathanrish/video-chunker:v1.1.0

# Run the container with all service ports
docker run -p 5000:5000 -p 5001:5001 -p 5002:5002 -p 5003:5003 \
  -v $(pwd)/output:/app/output ghcr.io/nathanrish/video-chunker:v1.1.0

# Check orchestrator health
curl http://localhost:5000/health
```

## 📁 Output Structure

The system creates organized, dated folders with all outputs:

```
output/
└── 2024-01-15_Team_Meeting/
    ├── transcript.txt                    # Full transcription
    ├── meeting_minutes.docx             # Professional DOCX minutes
    ├── meeting_minutes.html             # Web-viewable HTML minutes
    ├── original_meeting.mp4             # Copy of original video
    └── workflow_summary.json            # Processing details
```

## 🔧 Service Management

### Start Services Individually

```bash
# Transcription service
python services/transcription_service.py --model small --port 5001

# Meeting minutes service
python services/meeting_minutes_service.py --port 5002 --api-key your_key

# File management service
python services/file_management_service.py --port 5003 --base-output-dir ./output
```

### Check Service Health

```bash
# Check all services
python start_services.py --check-only

# Check individual service
curl http://localhost:5001/health
curl http://localhost:5002/health
curl http://localhost:5003/health
```

### Stop Services

```bash
# Stop all services
python start_services.py --stop

# Or use Ctrl+C when services are running
```

## 🎯 Features

### Video Transcription
- **Multiple Models**: tiny, base, small, medium, large
- **Language Support**: Auto-detection or manual specification
- **Word Timestamps**: Precise timing information
- **Format Support**: MP4, AVI, MKV, MOV, WMV, FLV, WebM, M4V

### Agile TPM Meeting Minutes
- **Epics & Initiatives**: Major program features
- **User Stories**: Business requirements
- **Technical Tasks**: Implementation work
- **Risk Management**: Impact and probability assessment
- **Dependencies**: Cross-team blockers
- **Decisions**: Technical and business decisions
- **Action Items**: With owners, due dates, priorities

### Output Formats
- **TXT**: Clean transcript with timestamps
- **DOCX**: Professional Word document
- **HTML**: Web-viewable with modern styling
- **JSON**: Machine-readable workflow data

### AI Enhancement (Optional)
- **Smart Analysis**: OpenAI GPT for better artifact extraction
- **Executive Summaries**: AI-generated program status
- **Risk Assessment**: Intelligent risk categorization
- **Action Item Extraction**: Automatic task identification

## 🔌 API Endpoints

### Orchestrator Service (Port 5000)

```bash
# Health check
GET /health

# Start workflow
POST /workflows
{
  "video_path": "path/to/video.mp4",
  "meeting_title": "Team Meeting",
  "meeting_date": "2024-01-15T10:00:00",   # optional ISO
  "language": "en",                          # optional
  "copy_video": true                          # default true
}

# Get workflow by id
GET /workflows/{id}

# List workflows
GET /workflows?limit=50&status=running|completed|failed
```

### Transcription Service (Port 5001)

```bash
# Health check
GET /health

# Transcribe video
POST /transcribe
{
  "video_path": "path/to/video.mp4",
  "language": "en",
  "word_timestamps": true
}

# Format transcript
POST /format-transcript
{
  "transcript_data": {...}
}
```

### Meeting Minutes Service (Port 5002)

```bash
# Health check
GET /health

# Generate meeting minutes
POST /generate-minutes
{
  "transcription_text": "...",
  "meeting_title": "Team Meeting",
  "meeting_date": "2024-01-15T10:00:00"
}

# Save as DOCX
POST /save-docx
{
  "meeting_data": {...},
  "output_path": "path/to/output.docx"
}

# Save as HTML
POST /save-html
{
  "meeting_data": {...},
  "output_path": "path/to/output.html"
}
```

### File Management Service (Port 5003)

```bash
# Health check
GET /health

# Create dated folder
POST /create-dated-folder
{
  "meeting_title": "Team Meeting",
  "meeting_date": "2024-01-15T10:00:00"
}

# Save transcript
POST /save-transcript
{
  "transcript_text": "...",
  "output_folder": "path/to/folder",
  "filename": "transcript.txt"
}

# Save meeting minutes DOCX
POST /save-meeting-minutes-docx
{
  "meeting_data": {...},
  "output_folder": "path/to/folder",
  "filename": "meeting_minutes.docx"
}
```

## 🛠️ Configuration

### Environment Variables

```bash
# OpenAI API key for AI features
export OPENAI_API_KEY="your_api_key_here"

# Service URLs (if running on different hosts)
export TRANSCRIPTION_SERVICE_URL="http://localhost:5001"
export MEETING_MINUTES_SERVICE_URL="http://localhost:5002"
export FILE_MANAGEMENT_SERVICE_URL="http://localhost:5003"
```

### Whisper Model Configuration

```bash
# Use different model sizes
python services/transcription_service.py --model large --device cuda

# Available models: tiny, base, small, medium, large
# Available devices: auto, cpu, cuda
# Available compute types: auto, int8, int8_float16, float16, float32
```

## 📊 Monitoring & Logging

### Service Logs
Each service provides detailed logging:
- **INFO**: Normal operations
- **WARNING**: Non-critical issues
- **ERROR**: Service failures
- **DEBUG**: Detailed debugging (when enabled)

### Workflow Tracking
The orchestrator tracks:
- Processing time for each step
- Success/failure status
- File sizes and paths
- Error messages and stack traces

### Health Monitoring
```bash
# Check all services
curl http://localhost:5001/health
curl http://localhost:5002/health
curl http://localhost:5003/health

# Service status includes:
# - Service name and version
# - Dependencies status
# - Model availability
# - Configuration details
```

## 🔧 Troubleshooting

### Common Issues

1. **Services won't start**
   ```bash
   # Check if ports are available
   netstat -an | grep :5001
   netstat -an | grep :5002
   netstat -an | grep :5003
   ```

2. **Transcription fails**
   ```bash
   # Check faster-whisper installation
   python -c "import faster_whisper; print('OK')"
   
   # Try smaller model
   python services/transcription_service.py --model tiny
   ```

3. **DOCX generation fails**
   ```bash
   # Check python-docx installation
   pip install python-docx
   ```

4. **AI features not working**
   ```bash
   # Check OpenAI API key
   python -c "import openai; print('OK')"
   
   # Verify API key
   python -c "import openai; openai.api_key='your_key'; print('OK')"
   ```

### Performance Optimization

1. **Use GPU for transcription**
   ```bash
   python services/transcription_service.py --device cuda --compute-type float16
   ```

2. **Use smaller models for faster processing**
   ```bash
   python services/transcription_service.py --model tiny
   ```

3. **Disable word timestamps for speed**
   ```bash
   # Modify transcription service call
   "word_timestamps": false
   ```

## 🚀 Production Deployment

### Docker Deployment
```dockerfile
# Example Dockerfile for production
FROM python:3.10-slim

WORKDIR /app
COPY requirements_microservices.txt .
RUN pip install -r requirements_microservices.txt

COPY . .
EXPOSE 5001 5002 5003

CMD ["python", "start_services.py"]
```

### Load Balancing
- Use nginx or similar for load balancing
- Scale transcription service for multiple videos
- Use Redis for session management
- Implement service discovery with Consul

### Security
- Use HTTPS for all service communication
- Implement API authentication
- Validate all input files
- Sanitize file paths and names

## 📈 Scaling Considerations

### Horizontal Scaling
- **Transcription Service**: Scale based on video processing load
- **Meeting Minutes Service**: Scale based on document generation
- **File Management Service**: Scale based on storage operations

### Resource Requirements
- **CPU**: Transcription is CPU-intensive
- **Memory**: Large models require significant RAM
- **Storage**: Video files and outputs need disk space
- **GPU**: Optional but significantly faster transcription

### Monitoring
- Service health endpoints
- Processing time metrics
- Error rate tracking
- Resource utilization monitoring

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all services pass health checks
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
