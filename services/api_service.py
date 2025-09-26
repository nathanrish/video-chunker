#!/usr/bin/env python3
"""
CRUD API Service for Video-to-Meeting-Minutes System
Provides comprehensive REST API for frontend integration and testing.
"""

import os
import sys
import json
import uuid
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from enum import Enum

try:
    from flask import Flask, request, jsonify, send_file
    from flask_cors import CORS
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

try:
    import sqlite3
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MeetingStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class ProcessingStep(Enum):
    TRANSCRIPTION = "transcription"
    MINUTES_GENERATION = "minutes_generation"
    FILE_SAVING = "file_saving"
    COMPLETED = "completed"

@dataclass
class Meeting:
    id: str
    title: str
    date: str
    status: str
    video_path: Optional[str] = None
    language: Optional[str] = None
    participants: Optional[List[str]] = None
    created_at: str = None
    updated_at: str = None
    processing_step: str = ProcessingStep.TRANSCRIPTION.value
    error_message: Optional[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.updated_at is None:
            self.updated_at = datetime.now().isoformat()
        if self.participants is None:
            self.participants = []

@dataclass
class Transcription:
    id: str
    meeting_id: str
    text: str
    language: str
    duration: float
    segments: List[Dict[str, Any]]
    created_at: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()

@dataclass
class MeetingMinutes:
    id: str
    meeting_id: str
    transcription_id: str
    title: str
    summary: str
    artifacts: Dict[str, Any]
    sprint_info: Dict[str, Any]
    speakers: List[str]
    created_at: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()

class DatabaseManager:
    def __init__(self, db_path: str = "meetings.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the SQLite database with required tables."""
        if not DATABASE_AVAILABLE:
            logger.error("SQLite not available")
            return
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create meetings table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS meetings (
                        id TEXT PRIMARY KEY,
                        title TEXT NOT NULL,
                        date TEXT NOT NULL,
                        status TEXT NOT NULL,
                        video_path TEXT,
                        language TEXT,
                        participants TEXT,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL,
                        processing_step TEXT,
                        error_message TEXT
                    )
                ''')
                
                # Create transcriptions table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS transcriptions (
                        id TEXT PRIMARY KEY,
                        meeting_id TEXT NOT NULL,
                        text TEXT NOT NULL,
                        language TEXT NOT NULL,
                        duration REAL NOT NULL,
                        segments TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        FOREIGN KEY (meeting_id) REFERENCES meetings (id)
                    )
                ''')
                
                # Create meeting_minutes table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS meeting_minutes (
                        id TEXT PRIMARY KEY,
                        meeting_id TEXT NOT NULL,
                        transcription_id TEXT NOT NULL,
                        title TEXT NOT NULL,
                        summary TEXT NOT NULL,
                        artifacts TEXT NOT NULL,
                        sprint_info TEXT NOT NULL,
                        speakers TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        FOREIGN KEY (meeting_id) REFERENCES meetings (id),
                        FOREIGN KEY (transcription_id) REFERENCES transcriptions (id)
                    )
                ''')
                
                conn.commit()
                logger.info("Database initialized successfully")
                
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
    
    def create_meeting(self, meeting: Meeting) -> Meeting:
        """Create a new meeting record."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO meetings (id, title, date, status, video_path, language, 
                                        participants, created_at, updated_at, processing_step, error_message)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    meeting.id, meeting.title, meeting.date, meeting.status,
                    meeting.video_path, meeting.language, json.dumps(meeting.participants),
                    meeting.created_at, meeting.updated_at, meeting.processing_step, meeting.error_message
                ))
                conn.commit()
                return meeting
        except Exception as e:
            logger.error(f"Failed to create meeting: {e}")
            raise
    
    def get_meeting(self, meeting_id: str) -> Optional[Meeting]:
        """Get a meeting by ID."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM meetings WHERE id = ?', (meeting_id,))
                row = cursor.fetchone()
                
                if row:
                    return Meeting(
                        id=row[0], title=row[1], date=row[2], status=row[3],
                        video_path=row[4], language=row[5], 
                        participants=json.loads(row[6]) if row[6] else [],
                        created_at=row[7], updated_at=row[8], 
                        processing_step=row[9], error_message=row[10]
                    )
                return None
        except Exception as e:
            logger.error(f"Failed to get meeting: {e}")
            return None
    
    def get_meetings(self, limit: int = 50, offset: int = 0, status: Optional[str] = None) -> List[Meeting]:
        """Get meetings with optional filtering."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                query = 'SELECT * FROM meetings'
                params = []
                
                if status:
                    query += ' WHERE status = ?'
                    params.append(status)
                
                query += ' ORDER BY created_at DESC LIMIT ? OFFSET ?'
                params.extend([limit, offset])
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                meetings = []
                for row in rows:
                    meetings.append(Meeting(
                        id=row[0], title=row[1], date=row[2], status=row[3],
                        video_path=row[4], language=row[5],
                        participants=json.loads(row[6]) if row[6] else [],
                        created_at=row[7], updated_at=row[8],
                        processing_step=row[9], error_message=row[10]
                    ))
                
                return meetings
        except Exception as e:
            logger.error(f"Failed to get meetings: {e}")
            return []
    
    def update_meeting(self, meeting: Meeting) -> Optional[Meeting]:
        """Update a meeting record."""
        try:
            meeting.updated_at = datetime.now().isoformat()
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE meetings SET title = ?, date = ?, status = ?, video_path = ?,
                                       language = ?, participants = ?, updated_at = ?,
                                       processing_step = ?, error_message = ?
                    WHERE id = ?
                ''', (
                    meeting.title, meeting.date, meeting.status, meeting.video_path,
                    meeting.language, json.dumps(meeting.participants), meeting.updated_at,
                    meeting.processing_step, meeting.error_message, meeting.id
                ))
                conn.commit()
                return meeting
        except Exception as e:
            logger.error(f"Failed to update meeting: {e}")
            return None
    
    def delete_meeting(self, meeting_id: str) -> bool:
        """Delete a meeting and related records."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Delete related records first
                cursor.execute('DELETE FROM meeting_minutes WHERE meeting_id = ?', (meeting_id,))
                cursor.execute('DELETE FROM transcriptions WHERE meeting_id = ?', (meeting_id,))
                cursor.execute('DELETE FROM meetings WHERE id = ?', (meeting_id,))
                
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Failed to delete meeting: {e}")
            return False
    
    def create_transcription(self, transcription: Transcription) -> Transcription:
        """Create a new transcription record."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO transcriptions (id, meeting_id, text, language, duration, segments, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    transcription.id, transcription.meeting_id, transcription.text,
                    transcription.language, transcription.duration, json.dumps(transcription.segments),
                    transcription.created_at
                ))
                conn.commit()
                return transcription
        except Exception as e:
            logger.error(f"Failed to create transcription: {e}")
            raise
    
    def get_transcription(self, transcription_id: str) -> Optional[Transcription]:
        """Get a transcription by ID."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM transcriptions WHERE id = ?', (transcription_id,))
                row = cursor.fetchone()
                
                if row:
                    return Transcription(
                        id=row[0], meeting_id=row[1], text=row[2], language=row[3],
                        duration=row[4], segments=json.loads(row[5]), created_at=row[6]
                    )
                return None
        except Exception as e:
            logger.error(f"Failed to get transcription: {e}")
            return None
    
    def get_transcription_by_meeting(self, meeting_id: str) -> Optional[Transcription]:
        """Get transcription by meeting ID."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM transcriptions WHERE meeting_id = ?', (meeting_id,))
                row = cursor.fetchone()
                
                if row:
                    return Transcription(
                        id=row[0], meeting_id=row[1], text=row[2], language=row[3],
                        duration=row[4], segments=json.loads(row[5]), created_at=row[6]
                    )
                return None
        except Exception as e:
            logger.error(f"Failed to get transcription by meeting: {e}")
            return None
    
    def create_meeting_minutes(self, minutes: MeetingMinutes) -> MeetingMinutes:
        """Create a new meeting minutes record."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO meeting_minutes (id, meeting_id, transcription_id, title, 
                                               summary, artifacts, sprint_info, speakers, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    minutes.id, minutes.meeting_id, minutes.transcription_id, minutes.title,
                    minutes.summary, json.dumps(minutes.artifacts), json.dumps(minutes.sprint_info),
                    json.dumps(minutes.speakers), minutes.created_at
                ))
                conn.commit()
                return minutes
        except Exception as e:
            logger.error(f"Failed to create meeting minutes: {e}")
            raise
    
    def get_meeting_minutes(self, minutes_id: str) -> Optional[MeetingMinutes]:
        """Get meeting minutes by ID."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM meeting_minutes WHERE id = ?', (minutes_id,))
                row = cursor.fetchone()
                
                if row:
                    return MeetingMinutes(
                        id=row[0], meeting_id=row[1], transcription_id=row[2], title=row[3],
                        summary=row[4], artifacts=json.loads(row[5]), sprint_info=json.loads(row[6]),
                        speakers=json.loads(row[7]), created_at=row[8]
                    )
                return None
        except Exception as e:
            logger.error(f"Failed to get meeting minutes: {e}")
            return None
    
    def get_meeting_minutes_by_meeting(self, meeting_id: str) -> Optional[MeetingMinutes]:
        """Get meeting minutes by meeting ID."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM meeting_minutes WHERE meeting_id = ?', (meeting_id,))
                row = cursor.fetchone()
                
                if row:
                    return MeetingMinutes(
                        id=row[0], meeting_id=row[1], transcription_id=row[2], title=row[3],
                        summary=row[4], artifacts=json.loads(row[5]), sprint_info=json.loads(row[6]),
                        speakers=json.loads(row[7]), created_at=row[8]
                    )
                return None
        except Exception as e:
            logger.error(f"Failed to get meeting minutes by meeting: {e}")
            return None

class APIService:
    def __init__(self, db_path: str = "meetings.db"):
        self.db = DatabaseManager(db_path)
        self.app = Flask(__name__)
        CORS(self.app)  # Enable CORS for frontend integration
        
        # Register routes
        self._register_routes()
    
    def _register_routes(self):
        """Register all API routes."""
        
        # Health check
        @self.app.route('/health', methods=['GET'])
        def health_check():
            return jsonify({
                "status": "healthy",
                "service": "api",
                "database_available": DATABASE_AVAILABLE,
                "flask_available": FLASK_AVAILABLE
            })
        
        # Meetings CRUD
        @self.app.route('/api/meetings', methods=['GET'])
        def get_meetings():
            limit = request.args.get('limit', 50, type=int)
            offset = request.args.get('offset', 0, type=int)
            status = request.args.get('status')
            
            meetings = self.db.get_meetings(limit, offset, status)
            return jsonify({
                "success": True,
                "data": [asdict(meeting) for meeting in meetings],
                "count": len(meetings)
            })
        
        @self.app.route('/api/meetings', methods=['POST'])
        def create_meeting():
            try:
                data = request.get_json()
                
                if not data or 'title' not in data or 'date' not in data:
                    return jsonify({
                        "success": False,
                        "error": "title and date are required"
                    }), 400
                
                meeting = Meeting(
                    id=str(uuid.uuid4()),
                    title=data['title'],
                    date=data['date'],
                    status=data.get('status', MeetingStatus.PENDING.value),
                    video_path=data.get('video_path'),
                    language=data.get('language'),
                    participants=data.get('participants', [])
                )
                
                created_meeting = self.db.create_meeting(meeting)
                
                return jsonify({
                    "success": True,
                    "data": asdict(created_meeting)
                }), 201
                
            except Exception as e:
                logger.error(f"Failed to create meeting: {e}")
                return jsonify({
                    "success": False,
                    "error": str(e)
                }), 500
        
        @self.app.route('/api/meetings/<meeting_id>', methods=['GET'])
        def get_meeting(meeting_id):
            meeting = self.db.get_meeting(meeting_id)
            
            if meeting:
                return jsonify({
                    "success": True,
                    "data": asdict(meeting)
                })
            else:
                return jsonify({
                    "success": False,
                    "error": "Meeting not found"
                }), 404
        
        @self.app.route('/api/meetings/<meeting_id>', methods=['PUT'])
        def update_meeting(meeting_id):
            try:
                meeting = self.db.get_meeting(meeting_id)
                
                if not meeting:
                    return jsonify({
                        "success": False,
                        "error": "Meeting not found"
                    }), 404
                
                data = request.get_json()
                
                if not data:
                    return jsonify({
                        "success": False,
                        "error": "Request body is required"
                    }), 400
                
                # Update fields
                if 'title' in data:
                    meeting.title = data['title']
                if 'date' in data:
                    meeting.date = data['date']
                if 'status' in data:
                    meeting.status = data['status']
                if 'video_path' in data:
                    meeting.video_path = data['video_path']
                if 'language' in data:
                    meeting.language = data['language']
                if 'participants' in data:
                    meeting.participants = data['participants']
                if 'processing_step' in data:
                    meeting.processing_step = data['processing_step']
                if 'error_message' in data:
                    meeting.error_message = data['error_message']
                
                updated_meeting = self.db.update_meeting(meeting)
                
                if updated_meeting:
                    return jsonify({
                        "success": True,
                        "data": asdict(updated_meeting)
                    })
                else:
                    return jsonify({
                        "success": False,
                        "error": "Failed to update meeting"
                    }), 500
                    
            except Exception as e:
                logger.error(f"Failed to update meeting: {e}")
                return jsonify({
                    "success": False,
                    "error": str(e)
                }), 500
        
        @self.app.route('/api/meetings/<meeting_id>', methods=['DELETE'])
        def delete_meeting(meeting_id):
            success = self.db.delete_meeting(meeting_id)
            
            if success:
                return jsonify({
                    "success": True,
                    "message": "Meeting deleted successfully"
                })
            else:
                return jsonify({
                    "success": False,
                    "error": "Meeting not found or deletion failed"
                }), 404
        
        # Transcriptions CRUD
        @self.app.route('/api/transcriptions', methods=['POST'])
        def create_transcription():
            try:
                data = request.get_json()
                
                if not data or 'meeting_id' not in data or 'text' not in data:
                    return jsonify({
                        "success": False,
                        "error": "meeting_id and text are required"
                    }), 400
                
                transcription = Transcription(
                    id=str(uuid.uuid4()),
                    meeting_id=data['meeting_id'],
                    text=data['text'],
                    language=data.get('language', 'en'),
                    duration=data.get('duration', 0.0),
                    segments=data.get('segments', [])
                )
                
                created_transcription = self.db.create_transcription(transcription)
                
                return jsonify({
                    "success": True,
                    "data": asdict(created_transcription)
                }), 201
                
            except Exception as e:
                logger.error(f"Failed to create transcription: {e}")
                return jsonify({
                    "success": False,
                    "error": str(e)
                }), 500
        
        @self.app.route('/api/transcriptions/<transcription_id>', methods=['GET'])
        def get_transcription(transcription_id):
            transcription = self.db.get_transcription(transcription_id)
            
            if transcription:
                return jsonify({
                    "success": True,
                    "data": asdict(transcription)
                })
            else:
                return jsonify({
                    "success": False,
                    "error": "Transcription not found"
                }), 404
        
        @self.app.route('/api/meetings/<meeting_id>/transcription', methods=['GET'])
        def get_meeting_transcription(meeting_id):
            transcription = self.db.get_transcription_by_meeting(meeting_id)
            
            if transcription:
                return jsonify({
                    "success": True,
                    "data": asdict(transcription)
                })
            else:
                return jsonify({
                    "success": False,
                    "error": "Transcription not found for this meeting"
                }), 404
        
        # Meeting Minutes CRUD
        @self.app.route('/api/meeting-minutes', methods=['POST'])
        def create_meeting_minutes():
            try:
                data = request.get_json()
                
                required_fields = ['meeting_id', 'transcription_id', 'title', 'summary']
                if not data or not all(field in data for field in required_fields):
                    return jsonify({
                        "success": False,
                        "error": f"Required fields: {', '.join(required_fields)}"
                    }), 400
                
                minutes = MeetingMinutes(
                    id=str(uuid.uuid4()),
                    meeting_id=data['meeting_id'],
                    transcription_id=data['transcription_id'],
                    title=data['title'],
                    summary=data['summary'],
                    artifacts=data.get('artifacts', {}),
                    sprint_info=data.get('sprint_info', {}),
                    speakers=data.get('speakers', [])
                )
                
                created_minutes = self.db.create_meeting_minutes(minutes)
                
                return jsonify({
                    "success": True,
                    "data": asdict(created_minutes)
                }), 201
                
            except Exception as e:
                logger.error(f"Failed to create meeting minutes: {e}")
                return jsonify({
                    "success": False,
                    "error": str(e)
                }), 500
        
        @self.app.route('/api/meeting-minutes/<minutes_id>', methods=['GET'])
        def get_meeting_minutes(minutes_id):
            minutes = self.db.get_meeting_minutes(minutes_id)
            
            if minutes:
                return jsonify({
                    "success": True,
                    "data": asdict(minutes)
                })
            else:
                return jsonify({
                    "success": False,
                    "error": "Meeting minutes not found"
                }), 404
        
        @self.app.route('/api/meetings/<meeting_id>/minutes', methods=['GET'])
        def get_meeting_minutes_by_meeting(meeting_id):
            minutes = self.db.get_meeting_minutes_by_meeting(meeting_id)
            
            if minutes:
                return jsonify({
                    "success": True,
                    "data": asdict(minutes)
                })
            else:
                return jsonify({
                    "success": False,
                    "error": "Meeting minutes not found for this meeting"
                }), 404
        
        # Complete meeting data
        @self.app.route('/api/meetings/<meeting_id>/complete', methods=['GET'])
        def get_complete_meeting(meeting_id):
            meeting = self.db.get_meeting(meeting_id)
            
            if not meeting:
                return jsonify({
                    "success": False,
                    "error": "Meeting not found"
                }), 404
            
            transcription = self.db.get_transcription_by_meeting(meeting_id)
            minutes = self.db.get_meeting_minutes_by_meeting(meeting_id)
            
            return jsonify({
                "success": True,
                "data": {
                    "meeting": asdict(meeting),
                    "transcription": asdict(transcription) if transcription else None,
                    "minutes": asdict(minutes) if minutes else None
                }
            })
        
        # File download endpoints
        @self.app.route('/api/meetings/<meeting_id>/files/transcript', methods=['GET'])
        def download_transcript(meeting_id):
            meeting = self.db.get_meeting(meeting_id)
            
            if not meeting:
                return jsonify({
                    "success": False,
                    "error": "Meeting not found"
                }), 404
            
            # Look for transcript file in output folder
            output_folder = Path("output")
            meeting_folder = None
            
            for folder in output_folder.iterdir():
                if folder.is_dir() and meeting_id in folder.name:
                    meeting_folder = folder
                    break
            
            if not meeting_folder:
                return jsonify({
                    "success": False,
                    "error": "Transcript file not found"
                }), 404
            
            transcript_file = meeting_folder / "transcript.txt"
            
            if transcript_file.exists():
                return send_file(transcript_file, as_attachment=True, download_name=f"{meeting.title}_transcript.txt")
            else:
                return jsonify({
                    "success": False,
                    "error": "Transcript file not found"
                }), 404
        
        @self.app.route('/api/meetings/<meeting_id>/files/minutes', methods=['GET'])
        def download_meeting_minutes(meeting_id):
            meeting = self.db.get_meeting(meeting_id)
            
            if not meeting:
                return jsonify({
                    "success": False,
                    "error": "Meeting not found"
                }), 404
            
            # Look for minutes file in output folder
            output_folder = Path("output")
            meeting_folder = None
            
            for folder in output_folder.iterdir():
                if folder.is_dir() and meeting_id in folder.name:
                    meeting_folder = folder
                    break
            
            if not meeting_folder:
                return jsonify({
                    "success": False,
                    "error": "Meeting minutes file not found"
                }), 404
            
            format_type = request.args.get('format', 'docx')
            
            if format_type == 'docx':
                minutes_file = meeting_folder / "meeting_minutes.docx"
                download_name = f"{meeting.title}_minutes.docx"
            elif format_type == 'html':
                minutes_file = meeting_folder / "meeting_minutes.html"
                download_name = f"{meeting.title}_minutes.html"
            else:
                return jsonify({
                    "success": False,
                    "error": "Invalid format. Use 'docx' or 'html'"
                }), 400
            
            if minutes_file.exists():
                return send_file(minutes_file, as_attachment=True, download_name=download_name)
            else:
                return jsonify({
                    "success": False,
                    "error": f"Meeting minutes file ({format_type}) not found"
                }), 404
        
        # File management endpoints
        @self.app.route('/api/cleanup-status', methods=['GET'])
        def get_cleanup_status():
            """Get file cleanup status."""
            try:
                # This would typically call the file management service
                # For now, return a mock response
                return jsonify({
                    "success": True,
                    "data": {
                        "total_folders": 0,
                        "old_folders": 0,
                        "total_size_mb": 0,
                        "next_cleanup": "Every hour",
                        "cutoff_hours": 24
                    }
                })
            except Exception as e:
                logger.error(f"Failed to get cleanup status: {e}")
                return jsonify({
                    "success": False,
                    "error": str(e)
                }), 500

        @self.app.route('/api/meetings/<meeting_id>/zip', methods=['GET'])
        def download_meeting_zip(meeting_id):
            """Download meeting output as zip file."""
            meeting = self.db.get_meeting(meeting_id)
            
            if not meeting:
                return jsonify({
                    "success": False,
                    "error": "Meeting not found"
                }), 404
            
            # Look for zip file in output folder
            output_folder = Path("output")
            meeting_folder = None
            
            for folder in output_folder.iterdir():
                if folder.is_dir() and meeting_id in folder.name:
                    meeting_folder = folder
                    break
            
            if not meeting_folder:
                return jsonify({
                    "success": False,
                    "error": "Meeting output folder not found"
                }), 404
            
            # Look for zip file
            zip_files = list(meeting_folder.glob("*.zip"))
            if not zip_files:
                return jsonify({
                    "success": False,
                    "error": "Zip file not found"
                }), 404
            
            zip_file = zip_files[0]  # Take the first zip file found
            
            return send_file(zip_file, as_attachment=True, download_name=f"{meeting.title}_output.zip")

        # Statistics endpoint
        @self.app.route('/api/stats', methods=['GET'])
        def get_statistics():
            try:
                meetings = self.db.get_meetings(limit=1000)  # Get all meetings for stats
                
                stats = {
                    "total_meetings": len(meetings),
                    "meetings_by_status": {},
                    "meetings_by_month": {},
                    "total_duration": 0,
                    "average_duration": 0
                }
                
                for meeting in meetings:
                    # Count by status
                    status = meeting.status
                    stats["meetings_by_status"][status] = stats["meetings_by_status"].get(status, 0) + 1
                    
                    # Count by month
                    try:
                        meeting_date = datetime.fromisoformat(meeting.date)
                        month_key = meeting_date.strftime("%Y-%m")
                        stats["meetings_by_month"][month_key] = stats["meetings_by_month"].get(month_key, 0) + 1
                    except:
                        pass
                
                # Calculate duration stats
                durations = []
                for meeting in meetings:
                    transcription = self.db.get_transcription_by_meeting(meeting.id)
                    if transcription:
                        durations.append(transcription.duration)
                
                if durations:
                    stats["total_duration"] = sum(durations)
                    stats["average_duration"] = sum(durations) / len(durations)
                
                return jsonify({
                    "success": True,
                    "data": stats
                })
                
            except Exception as e:
                logger.error(f"Failed to get statistics: {e}")
                return jsonify({
                    "success": False,
                    "error": str(e)
                }), 500

def run_service(host='localhost', port=5004, debug=False, db_path='meetings.db'):
    """Run the API service."""
    if not FLASK_AVAILABLE:
        logger.error("Flask not available. Cannot run API service.")
        sys.exit(1)
    
    if not DATABASE_AVAILABLE:
        logger.error("SQLite not available. Cannot run API service.")
        sys.exit(1)
    
    api_service = APIService(db_path)
    
    logger.info(f"Starting API Service on {host}:{port}")
    logger.info(f"Database: {db_path}")
    logger.info("Available endpoints:")
    logger.info("  GET  /health")
    logger.info("  GET  /api/meetings")
    logger.info("  POST /api/meetings")
    logger.info("  GET  /api/meetings/{id}")
    logger.info("  PUT  /api/meetings/{id}")
    logger.info("  DELETE /api/meetings/{id}")
    logger.info("  GET  /api/meetings/{id}/complete")
    logger.info("  GET  /api/meetings/{id}/files/transcript")
    logger.info("  GET  /api/meetings/{id}/files/minutes")
    logger.info("  GET  /api/stats")
    
    api_service.app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="CRUD API Service for Video-to-Meeting-Minutes System")
    parser.add_argument('--host', default='localhost', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5004, help='Port to bind to')
    parser.add_argument('--db-path', default='meetings.db', help='SQLite database path')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    run_service(host=args.host, port=args.port, debug=args.debug, db_path=args.db_path)
