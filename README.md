# Video to Meeting Minutes - Microservices System

A comprehensive microservices-based system that automatically transcribes videos and generates professional Agile TPM meeting minutes with organized output in dated folders.

## 🏗️ Architecture Overview

This system consists of multiple components:

### 🎬 Video Processing
- **Video Splitter**: Splits large videos into manageable chunks
- **Video Transcription**: Converts video to text using faster-whisper

### 📋 Meeting Minutes Generation
- **Agile TPM Format**: Professional Technical Program Manager style minutes
- **AI-Powered Analysis**: OpenAI GPT integration for enhanced extraction
- **Multiple Output Formats**: DOCX, HTML, and JSON

### 🏢 Microservices Architecture
- **Transcription Service** (Port 5001): Handles video transcription
- **Meeting Minutes Service** (Port 5002): Generates structured minutes
- **File Management Service** (Port 5003): Manages output organization
- **Orchestrator**: Coordinates the entire workflow

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd video_chunks

# Install dependencies
pip install -r requirements_microservices.txt
```

### 2. Start Microservices

```bash
# Start all services
python start_services.py

# With AI features (optional)
python start_services.py --api-key your_openai_key
```

### 3. Run Complete Workflow

```bash
# Basic usage
python orchestrator.py "input/meeting.mp4" "Team Meeting"

# With custom date and language
python orchestrator.py "input/meeting.mp4" "Sprint Planning" --date "2024-01-15" --language en
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

## 🎯 Features

### Video Processing
- **Multiple Formats**: MP4, AVI, MKV, MOV, WMV, FLV, WebM, M4V
- **Chunking Support**: Splits large videos for better processing
- **Language Detection**: Auto-detect or specify language
- **Word Timestamps**: Precise timing information

### Agile TPM Meeting Minutes
- **Epics & Initiatives**: Major program features
- **User Stories**: Business requirements
- **Technical Tasks**: Implementation work
- **Risk Management**: Impact and probability assessment
- **Dependencies**: Cross-team blockers
- **Decisions**: Technical and business decisions
- **Action Items**: With owners, due dates, priorities

### AI Enhancement (Optional)
- **Smart Analysis**: OpenAI GPT for better artifact extraction
- **Executive Summaries**: AI-generated program status
- **Risk Assessment**: Intelligent risk categorization
- **Action Item Extraction**: Automatic task identification

## 🔧 Service Management

### Start Services
```bash
# Start all services
python start_services.py

# Start with OpenAI API key
python start_services.py --api-key your_openai_key

# Check service health
python start_services.py --check-only

# Stop all services
python start_services.py --stop
```

### Individual Services
```bash
# Transcription service
python services/transcription_service.py --model small --port 5001

# Meeting minutes service
python services/meeting_minutes_service.py --port 5002 --api-key your_key

# File management service
python services/file_management_service.py --port 5003
```

## 🐳 Docker Deployment

### Build and Run
```bash
# Build the Docker image
docker build -t video-meeting-minutes .

# Run the container
docker run -p 5001:5001 -p 5002:5002 -p 5003:5003 -v $(pwd)/output:/app/output video-meeting-minutes

# Run with environment variables
docker run -e OPENAI_API_KEY=your_key -p 5001:5001 -p 5002:5002 -p 5003:5003 video-meeting-minutes
```

### Docker Compose
```yaml
version: '3.8'
services:
  video-meeting-minutes:
    build: .
    ports:
      - "5001:5001"
      - "5002:5002"
      - "5003:5003"
    volumes:
      - ./output:/app/output
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5001/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

## 🔌 API Endpoints

### Transcription Service (Port 5001)
```bash
GET  /health                    # Health check
POST /transcribe               # Transcribe video
POST /format-transcript        # Format transcript
```

### Meeting Minutes Service (Port 5002)
```bash
GET  /health                   # Health check
POST /generate-minutes         # Generate meeting minutes
POST /save-docx               # Save as DOCX
POST /save-html               # Save as HTML
```

### File Management Service (Port 5003)
```bash
GET  /health                   # Health check
POST /create-dated-folder      # Create output folder
POST /save-transcript          # Save transcript
POST /save-meeting-minutes-docx # Save DOCX
POST /save-meeting-minutes-html # Save HTML
```

## 📊 Usage Examples

### Basic Workflow
```bash
# 1. Start services
python start_services.py

# 2. Process video
python orchestrator.py "input/meeting.mp4" "Weekly Team Meeting"

# 3. Check output
ls output/
```

### Advanced Usage
```bash
# With custom parameters
python orchestrator.py \
  "input/meeting.mp4" \
  "Sprint Planning Meeting" \
  --date "2024-01-15" \
  --language en \
  --no-copy-video
```

### Service Health Monitoring
```bash
# Check all services
curl http://localhost:5001/health
curl http://localhost:5002/health
curl http://localhost:5003/health

# Or use the health check script
python start_services.py --check-only
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

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all services pass health checks
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review service health endpoints
3. Check the logs for detailed error messages
4. Open an issue on GitHub

## 🔄 Migration from Legacy

If you're upgrading from the previous single-script version:

1. **Install new dependencies**: `pip install -r requirements_microservices.txt`
2. **Start services**: `python start_services.py`
3. **Use orchestrator**: `python orchestrator.py "video.mp4" "Meeting Title"`
4. **Check output**: Files are now organized in dated folders

The legacy scripts (`meeting_minutes_generator.py`, `simple_transcribe.py`) are still available for backward compatibility.