# API Documentation

Complete API reference for the Video to Meeting Minutes system.

## 🌐 Base URLs

- **Development**: `http://localhost:5004`
- **Staging**: `http://staging-api.video-meeting-minutes.com`
- **Production**: `https://api.video-meeting-minutes.com`

## 🔐 Authentication

Currently, the API does not require authentication. In production, consider implementing:

- API Key authentication
- JWT tokens
- OAuth 2.0

## 📋 API Endpoints

### Health Check

#### GET /health

Check if the API service is running.

**Response:**
```json
{
  "status": "healthy",
  "service": "api",
  "version": "1.2.0",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

### Meetings

#### GET /api/meetings

Retrieve a list of meetings.

**Query Parameters:**
- `status` (optional): Filter by status (`pending`, `processing`, `completed`, `failed`)
- `limit` (optional): Number of meetings to return (default: 50)
- `offset` (optional): Number of meetings to skip (default: 0)
- `search` (optional): Search in title and description

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "meeting-123",
      "title": "Sprint Planning Meeting",
      "date": "2024-01-15",
      "status": "completed",
      "duration": 3600,
      "created_at": "2024-01-15T09:00:00Z",
      "updated_at": "2024-01-15T10:00:00Z"
    }
  ],
  "count": 1,
  "total": 1
}
```

#### POST /api/meetings

Create a new meeting.

**Request Body:**
```json
{
  "title": "Sprint Planning Meeting",
  "date": "2024-01-15",
  "status": "pending",
  "description": "Weekly sprint planning session"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "meeting-123",
    "title": "Sprint Planning Meeting",
    "date": "2024-01-15",
    "status": "pending",
    "created_at": "2024-01-15T09:00:00Z"
  }
}
```

#### GET /api/meetings/{id}

Retrieve a specific meeting.

**Path Parameters:**
- `id`: Meeting ID

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "meeting-123",
    "title": "Sprint Planning Meeting",
    "date": "2024-01-15",
    "status": "completed",
    "duration": 3600,
    "transcription": {
      "id": "trans-456",
      "text": "Full transcription text...",
      "language": "en",
      "duration": 3600,
      "segments": [
        {
          "start": 0,
          "end": 30,
          "text": "Welcome to our sprint planning meeting"
        }
      ]
    },
    "meeting_minutes": {
      "id": "minutes-789",
      "title": "Sprint Planning Meeting Minutes",
      "summary": "Executive summary...",
      "artifacts": {
        "epics": [
          {
            "title": "User Authentication",
            "description": "Implement secure user authentication",
            "priority": "high"
          }
        ],
        "risks": [
          {
            "title": "API Integration Risk",
            "description": "Third-party API might be unavailable",
            "impact": "high",
            "probability": "medium"
          }
        ],
        "action_items": [
          {
            "action": "Review API documentation",
            "owner": "John Doe",
            "due_date": "2024-01-20",
            "priority": "high"
          }
        ]
      },
      "sprint_info": {
        "sprint_number": 1,
        "dates": ["2024-01-15", "2024-01-29"],
        "sprints": ["Sprint 1", "Sprint 2"]
      },
      "speakers": ["John Doe", "Jane Smith"]
    },
    "files": {
      "transcript": "/api/meetings/meeting-123/transcript",
      "meeting_minutes_docx": "/api/meetings/meeting-123/minutes/docx",
      "meeting_minutes_html": "/api/meetings/meeting-123/minutes/html",
      "zip_file": "/api/meetings/meeting-123/zip"
    }
  }
}
```

#### PUT /api/meetings/{id}

Update a meeting.

**Path Parameters:**
- `id`: Meeting ID

**Request Body:**
```json
{
  "title": "Updated Meeting Title",
  "status": "processing"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "meeting-123",
    "title": "Updated Meeting Title",
    "status": "processing",
    "updated_at": "2024-01-15T11:00:00Z"
  }
}
```

#### DELETE /api/meetings/{id}

Delete a meeting and all related data.

**Path Parameters:**
- `id`: Meeting ID

**Response:**
```json
{
  "success": true,
  "message": "Meeting deleted successfully"
}
```

---

### File Downloads

#### GET /api/meetings/{id}/transcript

Download meeting transcript as text file.

**Path Parameters:**
- `id`: Meeting ID

**Response:**
- Content-Type: `text/plain`
- File download with transcript content

#### GET /api/meetings/{id}/minutes/{format}

Download meeting minutes in specified format.

**Path Parameters:**
- `id`: Meeting ID
- `format`: File format (`docx` or `html`)

**Response:**
- Content-Type: `application/vnd.openxmlformats-officedocument.wordprocessingml.document` (for DOCX)
- Content-Type: `text/html` (for HTML)
- File download with meeting minutes

#### GET /api/meetings/{id}/zip

Download all meeting files as ZIP archive.

**Path Parameters:**
- `id`: Meeting ID

**Response:**
- Content-Type: `application/zip`
- ZIP file containing all meeting files

---

### Statistics

#### GET /api/stats

Get system statistics.

**Response:**
```json
{
  "success": true,
  "data": {
    "total_meetings": 150,
    "meetings_by_status": {
      "pending": 5,
      "processing": 2,
      "completed": 140,
      "failed": 3
    },
    "total_duration": 540000,
    "average_duration": 3600,
    "total_transcriptions": 140,
    "total_meeting_minutes": 140,
    "storage_usage": {
      "total_size_mb": 2500.5,
      "input_files": 50,
      "output_files": 300
    }
  }
}
```

---

### File Management

#### GET /api/cleanup-status

Get file cleanup status and statistics.

**Response:**
```json
{
  "success": true,
  "data": {
    "total_folders": 25,
    "old_folders": 3,
    "total_size_mb": 1250.75,
    "next_cleanup": "Every hour",
    "cutoff_hours": 24,
    "last_cleanup": "2024-01-15T09:00:00Z"
  }
}
```

---

## 🔄 Workflow Processing

### Video Processing Workflow

The system processes videos through the following workflow:

1. **Upload Video** → Input directory
2. **Transcription** → Generate transcript using faster-whisper
3. **Meeting Minutes** → Generate structured minutes using AI
4. **File Organization** → Create dated output folder
5. **File Saving** → Save all outputs (transcript, minutes, etc.)
6. **ZIP Creation** → Create compressed archive
7. **Input Cleanup** → Delete original video file
8. **Background Cleanup** → Auto-purge after 24 hours

### Processing Status

Meetings can have the following statuses:

- `pending`: Waiting to be processed
- `processing`: Currently being processed
- `completed`: Successfully processed
- `failed`: Processing failed

## 📊 Error Handling

### Error Response Format

```json
{
  "success": false,
  "error": "Error message",
  "code": "ERROR_CODE",
  "details": {
    "field": "Additional error details"
  }
}
```

### Common Error Codes

- `VALIDATION_ERROR`: Invalid request data
- `NOT_FOUND`: Resource not found
- `PROCESSING_ERROR`: Video processing failed
- `FILE_ERROR`: File operation failed
- `SERVICE_UNAVAILABLE`: Required service is down

### HTTP Status Codes

- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request data
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server error

## 🚀 Rate Limiting

Currently, no rate limiting is implemented. In production, consider:

- Request rate limiting per IP
- API key-based rate limiting
- Resource-based rate limiting

## 📝 Request/Response Examples

### Complete Workflow Example

```bash
# 1. Create a meeting
curl -X POST http://localhost:5004/api/meetings \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Sprint Planning Meeting",
    "date": "2024-01-15",
    "status": "pending"
  }'

# 2. Get meeting details
curl http://localhost:5004/api/meetings/meeting-123

# 3. Download transcript
curl -O http://localhost:5004/api/meetings/meeting-123/transcript

# 4. Download meeting minutes (DOCX)
curl -O http://localhost:5004/api/meetings/meeting-123/minutes/docx

# 5. Download all files as ZIP
curl -O http://localhost:5004/api/meetings/meeting-123/zip

# 6. Get statistics
curl http://localhost:5004/api/stats
```

### Error Handling Example

```bash
# Invalid meeting ID
curl http://localhost:5004/api/meetings/invalid-id

# Response:
{
  "success": false,
  "error": "Meeting not found",
  "code": "NOT_FOUND"
}
```

## 🔧 SDK Examples

### Python SDK

```python
import requests

class VideoMeetingMinutesAPI:
    def __init__(self, base_url="http://localhost:5004"):
        self.base_url = base_url
    
    def create_meeting(self, title, date, status="pending"):
        response = requests.post(f"{self.base_url}/api/meetings", json={
            "title": title,
            "date": date,
            "status": status
        })
        return response.json()
    
    def get_meeting(self, meeting_id):
        response = requests.get(f"{self.base_url}/api/meetings/{meeting_id}")
        return response.json()
    
    def download_transcript(self, meeting_id, filename=None):
        response = requests.get(f"{self.base_url}/api/meetings/{meeting_id}/transcript")
        if filename:
            with open(filename, 'wb') as f:
                f.write(response.content)
        return response.content

# Usage
api = VideoMeetingMinutesAPI()
meeting = api.create_meeting("Test Meeting", "2024-01-15")
print(meeting)
```

### JavaScript SDK

```javascript
class VideoMeetingMinutesAPI {
  constructor(baseUrl = 'http://localhost:5004') {
    this.baseUrl = baseUrl;
  }
  
  async createMeeting(title, date, status = 'pending') {
    const response = await fetch(`${this.baseUrl}/api/meetings`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ title, date, status }),
    });
    return response.json();
  }
  
  async getMeeting(meetingId) {
    const response = await fetch(`${this.baseUrl}/api/meetings/${meetingId}`);
    return response.json();
  }
  
  async downloadTranscript(meetingId) {
    const response = await fetch(`${this.baseUrl}/api/meetings/${meetingId}/transcript`);
    return response.blob();
  }
}

// Usage
const api = new VideoMeetingMinutesAPI();
const meeting = await api.createMeeting('Test Meeting', '2024-01-15');
console.log(meeting);
```

## 🔍 Testing the API

### Using curl

```bash
# Health check
curl http://localhost:5004/health

# Create meeting
curl -X POST http://localhost:5004/api/meetings \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Meeting", "date": "2024-01-15"}'

# Get meetings
curl http://localhost:5004/api/meetings

# Get statistics
curl http://localhost:5004/api/stats
```

### Using Postman

1. Import the API collection
2. Set the base URL to `http://localhost:5004`
3. Run the requests in sequence

### Using Swagger/OpenAPI

The API documentation can be viewed in Swagger UI at:
- `http://localhost:5004/docs` (if Swagger is enabled)

## 📚 Additional Resources

- [REST API Best Practices](https://restfulapi.net/)
- [HTTP Status Codes](https://httpstatuses.com/)
- [JSON API Specification](https://jsonapi.org/)
- [OpenAPI Specification](https://swagger.io/specification/)
