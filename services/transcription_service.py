#!/usr/bin/env python3
"""
Video Transcription Microservice
Handles video transcription using faster-whisper with REST API interface.
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

try:
    from faster_whisper import WhisperModel
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False

try:
    from flask import Flask, request, jsonify
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TranscriptionService:
    def __init__(self, model_size='small', device='auto', compute_type='auto'):
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self.model = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the Whisper model."""
        if not WHISPER_AVAILABLE:
            logger.error("faster-whisper not available")
            return
        
        try:
            # Auto-select compute type if requested
            if self.compute_type == 'auto':
                if self.device == 'cuda':
                    self.compute_type = 'float16'
                else:
                    self.compute_type = 'int8'
            
            self.model = WhisperModel(
                self.model_size, 
                device=self.device, 
                compute_type=self.compute_type
            )
            logger.info(f"Whisper model {self.model_size} initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Whisper model: {e}")
            self.model = None
    
    def transcribe_video(self, video_path: str, language: Optional[str] = None, 
                        word_timestamps: bool = True) -> Dict[str, Any]:
        """
        Transcribe a video file and return structured data.
        
        Args:
            video_path: Path to the video file
            language: Language code (optional, auto-detect if None)
            word_timestamps: Include word-level timestamps
            
        Returns:
            Dictionary with transcription data
        """
        if not self.model:
            return {
                "success": False,
                "error": "Whisper model not initialized",
                "data": None
            }
        
        if not os.path.exists(video_path):
            return {
                "success": False,
                "error": f"Video file not found: {video_path}",
                "data": None
            }
        
        try:
            logger.info(f"Starting transcription of: {video_path}")
            
            # Transcribe with timestamps
            segments, info = self.model.transcribe(
                video_path,
                language=language,
                beam_size=1,
                vad_filter=True,
                word_timestamps=word_timestamps
            )
            
            # Collect segments
            transcript_data = {
                'language': info.language,
                'duration': info.duration,
                'segments': []
            }
            
            for segment in segments:
                segment_data = {
                    'start': segment.start,
                    'end': segment.end,
                    'text': segment.text.strip()
                }
                
                # Add word-level timestamps if available
                if word_timestamps and hasattr(segment, 'words') and segment.words:
                    segment_data['words'] = [
                        {
                            'start': word.start,
                            'end': word.end,
                            'text': word.word.strip()
                        }
                        for word in segment.words if word.word
                    ]
                
                transcript_data['segments'].append(segment_data)
            
            logger.info(f"Transcription completed. Found {len(transcript_data['segments'])} segments")
            
            return {
                "success": True,
                "error": None,
                "data": transcript_data
            }
            
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "data": None
            }
    
    def format_transcript_for_meeting_minutes(self, transcript_data: Dict[str, Any]) -> str:
        """Format transcript data for meeting minutes generator."""
        lines = []
        
        for segment in transcript_data['segments']:
            start_time = segment['start']
            text = segment['text']
            
            # Format timestamp as HH:MM:SS
            hours = int(start_time // 3600)
            minutes = int((start_time % 3600) // 60)
            seconds = int(start_time % 60)
            timestamp = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            
            # Use generic speaker since we don't have speaker diarization
            lines.append(f"[{timestamp}] Speaker: {text}")
        
        return '\n'.join(lines)


# Flask API Service
if FLASK_AVAILABLE:
    app = Flask(__name__)
    transcription_service = TranscriptionService()

    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint."""
        return jsonify({
            "status": "healthy",
            "service": "transcription",
            "model_loaded": transcription_service.model is not None,
            "whisper_available": WHISPER_AVAILABLE
        })

    @app.route('/transcribe', methods=['POST'])
    def transcribe():
        """Transcribe a video file."""
        try:
            data = request.get_json()
            
            if not data or 'video_path' not in data:
                return jsonify({
                    "success": False,
                    "error": "video_path is required"
                }), 400
            
            video_path = data['video_path']
            language = data.get('language')
            word_timestamps = data.get('word_timestamps', True)
            
            result = transcription_service.transcribe_video(
                video_path, language, word_timestamps
            )
            
            if result['success']:
                return jsonify(result)
            else:
                return jsonify(result), 500
                
        except Exception as e:
            logger.error(f"API error: {e}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500

    @app.route('/format-transcript', methods=['POST'])
    def format_transcript():
        """Format transcript for meeting minutes."""
        try:
            data = request.get_json()
            
            if not data or 'transcript_data' not in data:
                return jsonify({
                    "success": False,
                    "error": "transcript_data is required"
                }), 400
            
            formatted_text = transcription_service.format_transcript_for_meeting_minutes(
                data['transcript_data']
            )
            
            return jsonify({
                "success": True,
                "formatted_text": formatted_text
            })
            
        except Exception as e:
            logger.error(f"Format error: {e}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500

    def run_service(host='localhost', port=5001, debug=False):
        """Run the transcription service."""
        logger.info(f"Starting Transcription Service on {host}:{port}")
        app.run(host=host, port=port, debug=debug)

else:
    def run_service(host='localhost', port=5001, debug=False):
        """Fallback when Flask is not available."""
        logger.error("Flask not available. Cannot run as web service.")
        sys.exit(1)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Video Transcription Microservice")
    parser.add_argument('--host', default='localhost', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5001, help='Port to bind to')
    parser.add_argument('--model', default='small', help='Whisper model size')
    parser.add_argument('--device', default='auto', help='Device to use')
    parser.add_argument('--compute-type', default='auto', help='Compute type')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    # Initialize service with custom parameters
    transcription_service = TranscriptionService(
        model_size=args.model,
        device=args.device,
        compute_type=args.compute_type
    )
    
    run_service(host=args.host, port=args.port, debug=args.debug)
