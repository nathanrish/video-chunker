#!/usr/bin/env python3
"""
Tests for file management service functionality.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from services.file_management_service import FileManagementService


class TestFileManagementService:
    """Test cases for FileManagementService."""
    
    @pytest.fixture
    def temp_dirs(self):
        """Create temporary directories for testing."""
        temp_dir = tempfile.mkdtemp()
        input_dir = Path(temp_dir) / "input"
        output_dir = Path(temp_dir) / "output"
        input_dir.mkdir()
        output_dir.mkdir()
        
        yield input_dir, output_dir
        
        # Cleanup
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def file_service(self, temp_dirs):
        """Create FileManagementService instance for testing."""
        input_dir, output_dir = temp_dirs
        return FileManagementService(
            base_output_dir=str(output_dir),
            input_dir=str(input_dir)
        )
    
    def test_create_dated_folder(self, file_service):
        """Test creating dated folders."""
        folder_path = file_service.create_dated_folder("Test Meeting")
        
        assert Path(folder_path).exists()
        assert "Test_Meeting" in folder_path
    
    def test_save_transcript(self, file_service):
        """Test saving transcript to file."""
        output_folder = file_service.create_dated_folder("Test Meeting")
        transcript_text = "This is a test transcript."
        
        result = file_service.save_transcript(
            transcript_text, 
            output_folder, 
            "test_transcript.txt"
        )
        
        assert result["success"] is True
        assert result["file_path"] is not None
        assert Path(result["file_path"]).exists()
        
        # Verify content
        with open(result["file_path"], 'r') as f:
            content = f.read()
        assert content == transcript_text
    
    def test_zip_output_folder(self, file_service):
        """Test creating ZIP archive of output folder."""
        output_folder = file_service.create_dated_folder("Test Meeting")
        
        # Create some test files
        test_file = Path(output_folder) / "test.txt"
        test_file.write_text("Test content")
        
        result = file_service.zip_output_folder(output_folder, "Test Meeting")
        
        assert result["success"] is True
        assert result["zip_path"] is not None
        assert Path(result["zip_path"]).exists()
        assert result["files_zipped"] > 0
    
    def test_delete_input_file_safety(self, file_service, temp_dirs):
        """Test that input file deletion only works on input directory files."""
        input_dir, output_dir = temp_dirs
        
        # Create a file in input directory
        input_file = input_dir / "test_video.mp4"
        input_file.write_text("fake video content")
        
        # Create a file outside input directory
        outside_file = output_dir / "important_file.txt"
        outside_file.write_text("important content")
        
        # Should succeed for input directory file
        result1 = file_service.delete_input_file(str(input_file))
        assert result1["success"] is True
        assert not input_file.exists()
        
        # Should fail for file outside input directory
        result2 = file_service.delete_input_file(str(outside_file))
        assert result2["success"] is False
        assert "not in input directory" in result2["error"]
        assert outside_file.exists()  # File should still exist
    
    def test_get_cleanup_status(self, file_service):
        """Test getting cleanup status information."""
        status = file_service.get_cleanup_status()
        
        assert status["success"] is True
        assert "total_folders" in status
        assert "old_folders" in status
        assert "total_size_mb" in status
        assert "cutoff_hours" in status
        assert status["cutoff_hours"] == 24


@pytest.mark.integration
class TestFileManagementIntegration:
    """Integration tests for file management."""
    
    def test_complete_workflow(self, temp_dirs):
        """Test complete file management workflow."""
        input_dir, output_dir = temp_dirs
        
        # Create test video file
        video_file = input_dir / "test_meeting.mp4"
        video_file.write_text("fake video content")
        
        # Initialize service
        file_service = FileManagementService(
            base_output_dir=str(output_dir),
            input_dir=str(input_dir)
        )
        
        # Create output folder
        output_folder = file_service.create_dated_folder("Integration Test")
        
        # Save transcript
        transcript_result = file_service.save_transcript(
            "Test transcript content",
            output_folder,
            "transcript.txt"
        )
        assert transcript_result["success"] is True
        
        # Create ZIP
        zip_result = file_service.zip_output_folder(
            output_folder,
            "Integration Test"
        )
        assert zip_result["success"] is True
        
        # Delete input file
        delete_result = file_service.delete_input_file(str(video_file))
        assert delete_result["success"] is True
        assert not video_file.exists()
        
        # Verify all files exist in output
        output_path = Path(output_folder)
        assert (output_path / "transcript.txt").exists()
        assert (output_path / "Integration_Test_output.zip").exists()
