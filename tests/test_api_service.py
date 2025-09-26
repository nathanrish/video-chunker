#!/usr/bin/env python3
"""
Tests for API service functionality.
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from services.api_service import APIService, Meeting, Transcription, MeetingMinutes


class TestAPIService:
    """Test cases for APIService."""
    
    @pytest.fixture
    def api_service(self):
        """Create APIService instance for testing."""
        with patch('services.api_service.DATABASE_AVAILABLE', True):
            return APIService(db_path=":memory:")
    
    def test_create_meeting(self, api_service):
        """Test creating a meeting."""
        meeting_data = {
            "title": "Test Meeting",
            "date": "2024-01-15",
            "status": "pending"
        }
        
        result = api_service.db.create_meeting(Meeting(
            id="test-id",
            title=meeting_data["title"],
            date=meeting_data["date"],
            status=meeting_data["status"]
        ))
        
        assert result.title == "Test Meeting"
        assert result.date == "2024-01-15"
        assert result.status == "pending"
    
    def test_get_meeting(self, api_service):
        """Test retrieving a meeting."""
        # Create a meeting first
        meeting = Meeting(
            id="test-id",
            title="Test Meeting",
            date="2024-01-15",
            status="pending"
        )
        api_service.db.create_meeting(meeting)
        
        # Retrieve it
        retrieved = api_service.db.get_meeting("test-id")
        
        assert retrieved is not None
        assert retrieved.title == "Test Meeting"
        assert retrieved.id == "test-id"
    
    def test_get_meetings_with_filters(self, api_service):
        """Test retrieving meetings with filters."""
        # Create test meetings
        meetings = [
            Meeting(id="1", title="Meeting 1", date="2024-01-15", status="completed"),
            Meeting(id="2", title="Meeting 2", date="2024-01-16", status="pending"),
            Meeting(id="3", title="Meeting 3", date="2024-01-17", status="completed"),
        ]
        
        for meeting in meetings:
            api_service.db.create_meeting(meeting)
        
        # Test without filter
        all_meetings = api_service.db.get_meetings()
        assert len(all_meetings) == 3
        
        # Test with status filter
        completed_meetings = api_service.db.get_meetings(status="completed")
        assert len(completed_meetings) == 2
        
        # Test with limit
        limited_meetings = api_service.db.get_meetings(limit=2)
        assert len(limited_meetings) == 2
    
    def test_create_transcription(self, api_service):
        """Test creating a transcription."""
        transcription = Transcription(
            id="trans-1",
            meeting_id="meeting-1",
            text="Test transcription text",
            language="en",
            duration=120.5,
            segments=[{"start": 0, "end": 120.5, "text": "Test transcription text"}]
        )
        
        result = api_service.db.create_transcription(transcription)
        
        assert result.id == "trans-1"
        assert result.meeting_id == "meeting-1"
        assert result.text == "Test transcription text"
        assert result.duration == 120.5
    
    def test_create_meeting_minutes(self, api_service):
        """Test creating meeting minutes."""
        minutes = MeetingMinutes(
            id="minutes-1",
            meeting_id="meeting-1",
            transcription_id="trans-1",
            title="Test Meeting Minutes",
            summary="Test summary",
            artifacts={"epics": [], "risks": [], "action_items": []},
            sprint_info={"sprint_number": 1},
            speakers=["Speaker 1", "Speaker 2"]
        )
        
        result = api_service.db.create_meeting_minutes(minutes)
        
        assert result.id == "minutes-1"
        assert result.title == "Test Meeting Minutes"
        assert result.summary == "Test summary"
        assert len(result.speakers) == 2
    
    def test_delete_meeting_cascade(self, api_service):
        """Test that deleting a meeting cascades to related records."""
        # Create meeting
        meeting = Meeting(
            id="meeting-1",
            title="Test Meeting",
            date="2024-01-15",
            status="pending"
        )
        api_service.db.create_meeting(meeting)
        
        # Create related transcription
        transcription = Transcription(
            id="trans-1",
            meeting_id="meeting-1",
            text="Test text",
            language="en",
            duration=60.0,
            segments=[]
        )
        api_service.db.create_transcription(transcription)
        
        # Create related meeting minutes
        minutes = MeetingMinutes(
            id="minutes-1",
            meeting_id="meeting-1",
            transcription_id="trans-1",
            title="Test Minutes",
            summary="Test summary",
            artifacts={},
            sprint_info={},
            speakers=[]
        )
        api_service.db.create_meeting_minutes(minutes)
        
        # Delete meeting
        success = api_service.db.delete_meeting("meeting-1")
        assert success is True
        
        # Verify all related records are deleted
        assert api_service.db.get_meeting("meeting-1") is None
        assert api_service.db.get_transcription("trans-1") is None
        assert api_service.db.get_meeting_minutes("minutes-1") is None


@pytest.mark.api
class TestAPIServiceEndpoints:
    """Test API service endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        with patch('services.api_service.FLASK_AVAILABLE', True):
            from services.api_service import APIService
            service = APIService(db_path=":memory:")
            service.app.config['TESTING'] = True
            return service.app.test_client()
    
    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get('/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert data['service'] == 'api'
    
    def test_create_meeting_endpoint(self, client):
        """Test creating a meeting via API."""
        meeting_data = {
            "title": "API Test Meeting",
            "date": "2024-01-15",
            "status": "pending"
        }
        
        response = client.post('/api/meetings', 
                             data=json.dumps(meeting_data),
                             content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['title'] == "API Test Meeting"
    
    def test_get_meetings_endpoint(self, client):
        """Test retrieving meetings via API."""
        response = client.get('/api/meetings')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'data' in data
        assert 'count' in data
    
    def test_get_stats_endpoint(self, client):
        """Test statistics endpoint."""
        response = client.get('/api/stats')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'data' in data
        assert 'total_meetings' in data['data']
