#!/usr/bin/env python3
"""
Video to Meeting Minutes Orchestrator
Coordinates the microservices workflow for video transcription and meeting minutes generation.
"""

import os
import sys
import json
import time
import logging
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VideoToMeetingMinutesOrchestrator:
    def __init__(self, 
                 transcription_service_url: str = "http://localhost:5001",
                 meeting_minutes_service_url: str = "http://localhost:5002",
                 file_management_service_url: str = "http://localhost:5003"):
        self.transcription_service_url = transcription_service_url
        self.meeting_minutes_service_url = meeting_minutes_service_url
        self.file_management_service_url = file_management_service_url
        
        # Service health check
        self._check_services_health()
    
    def _check_services_health(self):
        """Check if all required services are running."""
        services = {
            "transcription": self.transcription_service_url,
            "meeting_minutes": self.meeting_minutes_service_url,
            "file_management": self.file_management_service_url
        }
        
        for service_name, url in services.items():
            try:
                response = requests.get(f"{url}/health", timeout=5)
                if response.status_code == 200:
                    logger.info(f"✅ {service_name} service is healthy")
                else:
                    logger.warning(f"⚠️ {service_name} service returned status {response.status_code}")
            except requests.exceptions.RequestException as e:
                logger.error(f"❌ {service_name} service is not available: {e}")
                raise Exception(f"Service {service_name} is not running. Please start it first.")
    
    def _call_transcription_service(self, video_path: str, language: Optional[str] = None) -> Dict[str, Any]:
        """Call the transcription service."""
        logger.info(f"🎬 Starting video transcription: {video_path}")
        
        payload = {
            "video_path": video_path,
            "language": language,
            "word_timestamps": True
        }
        
        try:
            response = requests.post(
                f"{self.transcription_service_url}/transcribe",
                json=payload,
                timeout=300  # 5 minutes timeout for transcription
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    logger.info("✅ Video transcription completed successfully")
                    return result
                else:
                    raise Exception(f"Transcription failed: {result.get('error')}")
            else:
                raise Exception(f"Transcription service error: {response.status_code}")
                
        except requests.exceptions.Timeout:
            raise Exception("Transcription service timeout - video may be too large")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to call transcription service: {e}")
    
    def _format_transcript_for_meeting_minutes(self, transcript_data: Dict[str, Any]) -> str:
        """Format transcript data for meeting minutes generation."""
        logger.info("📝 Formatting transcript for meeting minutes")
        
        payload = {
            "transcript_data": transcript_data
        }
        
        try:
            response = requests.post(
                f"{self.transcription_service_url}/format-transcript",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    return result.get("formatted_text")
                else:
                    raise Exception(f"Formatting failed: {result.get('error')}")
            else:
                raise Exception(f"Formatting service error: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to format transcript: {e}")
    
    def _call_meeting_minutes_service(self, transcription_text: str, meeting_title: str,
                                    meeting_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Call the meeting minutes generation service."""
        logger.info("📋 Generating Agile TPM meeting minutes")
        
        payload = {
            "transcription_text": transcription_text,
            "meeting_title": meeting_title,
            "meeting_date": meeting_date.isoformat() if meeting_date else None
        }
        
        try:
            response = requests.post(
                f"{self.meeting_minutes_service_url}/generate-minutes",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    logger.info("✅ Meeting minutes generated successfully")
                    return result.get("data")
                else:
                    raise Exception(f"Meeting minutes generation failed: {result.get('error')}")
            else:
                raise Exception(f"Meeting minutes service error: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to generate meeting minutes: {e}")
    
    def _create_dated_folder(self, meeting_title: str, meeting_date: Optional[datetime] = None) -> str:
        """Create a dated output folder."""
        logger.info("📁 Creating dated output folder")
        
        payload = {
            "meeting_title": meeting_title,
            "meeting_date": meeting_date.isoformat() if meeting_date else None
        }
        
        try:
            response = requests.post(
                f"{self.file_management_service_url}/create-dated-folder",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    folder_path = result.get("folder_path")
                    logger.info(f"✅ Created output folder: {folder_path}")
                    return folder_path
                else:
                    raise Exception(f"Folder creation failed: {result.get('error')}")
            else:
                raise Exception(f"File management service error: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to create output folder: {e}")
    
    def _save_transcript(self, transcript_text: str, output_folder: str) -> Dict[str, Any]:
        """Save transcript to text file."""
        logger.info("💾 Saving transcript to text file")
        
        payload = {
            "transcript_text": transcript_text,
            "output_folder": output_folder,
            "filename": "transcript.txt"
        }
        
        try:
            response = requests.post(
                f"{self.file_management_service_url}/save-transcript",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    logger.info(f"✅ Transcript saved: {result.get('file_path')}")
                    return result
                else:
                    raise Exception(f"Transcript save failed: {result.get('error')}")
            else:
                raise Exception(f"File management service error: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to save transcript: {e}")
    
    def _save_meeting_minutes_docx(self, meeting_data: Dict[str, Any], output_folder: str) -> Dict[str, Any]:
        """Save meeting minutes as DOCX file."""
        logger.info("📄 Saving meeting minutes as DOCX")
        
        payload = {
            "meeting_data": meeting_data,
            "output_folder": output_folder,
            "filename": "meeting_minutes.docx"
        }
        
        try:
            response = requests.post(
                f"{self.file_management_service_url}/save-meeting-minutes-docx",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    logger.info(f"✅ DOCX saved: {result.get('file_path')}")
                    return result
                else:
                    raise Exception(f"DOCX save failed: {result.get('error')}")
            else:
                raise Exception(f"File management service error: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to save DOCX: {e}")
    
    def _save_meeting_minutes_html(self, meeting_data: Dict[str, Any], output_folder: str) -> Dict[str, Any]:
        """Save meeting minutes as HTML file."""
        logger.info("🌐 Saving meeting minutes as HTML")
        
        payload = {
            "meeting_data": meeting_data,
            "output_folder": output_folder,
            "filename": "meeting_minutes.html"
        }
        
        try:
            response = requests.post(
                f"{self.file_management_service_url}/save-meeting-minutes-html",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    logger.info(f"✅ HTML saved: {result.get('file_path')}")
                    return result
                else:
                    raise Exception(f"HTML save failed: {result.get('error')}")
            else:
                raise Exception(f"File management service error: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to save HTML: {e}")
    
    def _copy_video_to_output(self, video_path: str, output_folder: str) -> Dict[str, Any]:
        """Copy original video to output folder."""
        logger.info("🎥 Copying original video to output folder")
        
        payload = {
            "video_path": video_path,
            "output_folder": output_folder
        }
        
        try:
            response = requests.post(
                f"{self.file_management_service_url}/copy-video",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    logger.info(f"✅ Video copied: {result.get('file_path')}")
                    return result
                else:
                    logger.warning(f"⚠️ Video copy failed: {result.get('error')}")
                    return result
            else:
                logger.warning(f"⚠️ File management service error: {response.status_code}")
                return {"success": False, "error": f"Service error: {response.status_code}"}
                
        except requests.exceptions.RequestException as e:
            logger.warning(f"⚠️ Failed to copy video: {e}")
            return {"success": False, "error": str(e)}
    
    def _create_workflow_summary(self, output_folder: str, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create workflow summary file."""
        logger.info("📊 Creating workflow summary")
        
        payload = {
            "output_folder": output_folder,
            "workflow_data": workflow_data
        }
        
        try:
            response = requests.post(
                f"{self.file_management_service_url}/create-workflow-summary",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    logger.info(f"✅ Workflow summary created: {result.get('file_path')}")
                    return result
                else:
                    logger.warning(f"⚠️ Workflow summary failed: {result.get('error')}")
                    return result
            else:
                logger.warning(f"⚠️ File management service error: {response.status_code}")
                return {"success": False, "error": f"Service error: {response.status_code}"}
                
        except requests.exceptions.RequestException as e:
            logger.warning(f"⚠️ Failed to create workflow summary: {e}")
            return {"success": False, "error": str(e)}
    
    def process_video_to_meeting_minutes(self, 
                                       video_path: str,
                                       meeting_title: str,
                                       meeting_date: Optional[datetime] = None,
                                       language: Optional[str] = None,
                                       copy_video: bool = True) -> Dict[str, Any]:
        """
        Complete workflow: Video -> Transcription -> Meeting Minutes -> Organized Output
        
        Args:
            video_path: Path to the input video file
            meeting_title: Title for the meeting
            meeting_date: Date of the meeting (default: today)
            language: Language code for transcription (optional)
            copy_video: Whether to copy original video to output folder
            
        Returns:
            Dictionary with workflow results and file paths
        """
        start_time = time.time()
        workflow_data = {
            "video_path": video_path,
            "meeting_title": meeting_title,
            "meeting_date": meeting_date.isoformat() if meeting_date else datetime.now().isoformat(),
            "language": language,
            "steps": []
        }
        
        try:
            logger.info("🚀 Starting Video to Meeting Minutes Workflow")
            logger.info(f"📹 Input Video: {video_path}")
            logger.info(f"📋 Meeting Title: {meeting_title}")
            
            # Step 1: Transcribe video
            step_start = time.time()
            transcription_result = self._call_transcription_service(video_path, language)
            workflow_data["steps"].append({
                "step": "transcription",
                "duration": time.time() - step_start,
                "success": True,
                "segments_count": len(transcription_result["data"]["segments"])
            })
            
            # Step 2: Format transcript
            step_start = time.time()
            formatted_transcript = self._format_transcript_for_meeting_minutes(transcription_result["data"])
            workflow_data["steps"].append({
                "step": "format_transcript",
                "duration": time.time() - step_start,
                "success": True
            })
            
            # Step 3: Generate meeting minutes
            step_start = time.time()
            meeting_data = self._call_meeting_minutes_service(formatted_transcript, meeting_title, meeting_date)
            workflow_data["steps"].append({
                "step": "generate_meeting_minutes",
                "duration": time.time() - step_start,
                "success": True,
                "epics_count": len(meeting_data["artifacts"]["epics"]),
                "risks_count": len(meeting_data["artifacts"]["risks"]),
                "action_items_count": len(meeting_data["artifacts"]["action_items"])
            })
            
            # Step 4: Create output folder
            step_start = time.time()
            output_folder = self._create_dated_folder(meeting_title, meeting_date)
            workflow_data["steps"].append({
                "step": "create_output_folder",
                "duration": time.time() - step_start,
                "success": True,
                "output_folder": output_folder
            })
            
            # Step 5: Save transcript
            step_start = time.time()
            transcript_save_result = self._save_transcript(formatted_transcript, output_folder)
            workflow_data["steps"].append({
                "step": "save_transcript",
                "duration": time.time() - step_start,
                "success": transcript_save_result["success"],
                "file_path": transcript_save_result.get("file_path"),
                "file_size": transcript_save_result.get("file_size")
            })
            
            # Step 6: Save meeting minutes as DOCX
            step_start = time.time()
            docx_save_result = self._save_meeting_minutes_docx(meeting_data, output_folder)
            workflow_data["steps"].append({
                "step": "save_meeting_minutes_docx",
                "duration": time.time() - step_start,
                "success": docx_save_result["success"],
                "file_path": docx_save_result.get("file_path"),
                "file_size": docx_save_result.get("file_size")
            })
            
            # Step 7: Save meeting minutes as HTML
            step_start = time.time()
            html_save_result = self._save_meeting_minutes_html(meeting_data, output_folder)
            workflow_data["steps"].append({
                "step": "save_meeting_minutes_html",
                "duration": time.time() - step_start,
                "success": html_save_result["success"],
                "file_path": html_save_result.get("file_path"),
                "file_size": html_save_result.get("file_size")
            })
            
            # Step 8: Copy original video (optional)
            if copy_video:
                step_start = time.time()
                video_copy_result = self._copy_video_to_output(video_path, output_folder)
                workflow_data["steps"].append({
                    "step": "copy_video",
                    "duration": time.time() - step_start,
                    "success": video_copy_result["success"],
                    "file_path": video_copy_result.get("file_path"),
                    "file_size": video_copy_result.get("file_size")
                })
            
            # Step 9: Create workflow summary
            step_start = time.time()
            summary_result = self._create_workflow_summary(output_folder, workflow_data)
            workflow_data["steps"].append({
                "step": "create_workflow_summary",
                "duration": time.time() - step_start,
                "success": summary_result["success"],
                "file_path": summary_result.get("file_path")
            })
            
            # Calculate total duration
            total_duration = time.time() - start_time
            workflow_data["total_duration"] = total_duration
            
            logger.info("🎉 Workflow completed successfully!")
            logger.info(f"⏱️ Total duration: {total_duration:.2f} seconds")
            logger.info(f"📁 Output folder: {output_folder}")
            
            return {
                "success": True,
                "output_folder": output_folder,
                "workflow_data": workflow_data,
                "files": {
                    "transcript": transcript_save_result.get("file_path"),
                    "meeting_minutes_docx": docx_save_result.get("file_path"),
                    "meeting_minutes_html": html_save_result.get("file_path"),
                    "original_video": video_copy_result.get("file_path") if copy_video else None,
                    "workflow_summary": summary_result.get("file_path")
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Workflow failed: {e}")
            workflow_data["error"] = str(e)
            workflow_data["total_duration"] = time.time() - start_time
            
            return {
                "success": False,
                "error": str(e),
                "workflow_data": workflow_data
            }


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Video to Meeting Minutes Orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python orchestrator.py "input/meeting.mp4" "Weekly Team Meeting"
    python orchestrator.py "input/meeting.mp4" "Sprint Planning" --date "2024-01-15" --language en
    python orchestrator.py "input/meeting.mp4" "Product Review" --no-copy-video
        """
    )
    
    parser.add_argument(
        'video_path',
        help='Path to the input video file'
    )
    
    parser.add_argument(
        'meeting_title',
        help='Title for the meeting'
    )
    
    parser.add_argument(
        '--date',
        help='Meeting date (YYYY-MM-DD format, default: today)'
    )
    
    parser.add_argument(
        '--language',
        help='Language code for transcription (e.g., en, es, fr)'
    )
    
    parser.add_argument(
        '--no-copy-video',
        action='store_true',
        help='Do not copy original video to output folder'
    )
    
    parser.add_argument(
        '--transcription-service',
        default='http://localhost:5001',
        help='Transcription service URL'
    )
    
    parser.add_argument(
        '--meeting-minutes-service',
        default='http://localhost:5002',
        help='Meeting minutes service URL'
    )
    
    parser.add_argument(
        '--file-management-service',
        default='http://localhost:5003',
        help='File management service URL'
    )
    
    args = parser.parse_args()
    
    # Validate input file
    if not os.path.exists(args.video_path):
        print(f"Error: Video file '{args.video_path}' does not exist.")
        sys.exit(1)
    
    # Parse meeting date
    meeting_date = None
    if args.date:
        try:
            meeting_date = datetime.strptime(args.date, '%Y-%m-%d')
        except ValueError:
            print("Error: Invalid date format. Use YYYY-MM-DD")
            sys.exit(1)
    
    # Initialize orchestrator
    orchestrator = VideoToMeetingMinutesOrchestrator(
        transcription_service_url=args.transcription_service,
        meeting_minutes_service_url=args.meeting_minutes_service,
        file_management_service_url=args.file_management_service
    )
    
    # Run workflow
    result = orchestrator.process_video_to_meeting_minutes(
        video_path=args.video_path,
        meeting_title=args.meeting_title,
        meeting_date=meeting_date,
        language=args.language,
        copy_video=not args.no_copy_video
    )
    
    if result["success"]:
        print("\n🎉 Workflow completed successfully!")
        print(f"📁 Output folder: {result['output_folder']}")
        print("\n📄 Generated files:")
        for file_type, file_path in result["files"].items():
            if file_path:
                print(f"  • {file_type}: {file_path}")
        
        print(f"\n⏱️ Total processing time: {result['workflow_data']['total_duration']:.2f} seconds")
    else:
        print(f"\n❌ Workflow failed: {result['error']}")
        sys.exit(1)


if __name__ == "__main__":
    main()
