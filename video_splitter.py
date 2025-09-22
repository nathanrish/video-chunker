#!/usr/bin/env python3
"""
Video Chunk Splitter Script
Automatically splits any video found in ./input/ folder into chunks organized in folders.
Output will be created in ./output/ folder.

Requirements:
    pip install ffmpeg-python

Usage:
    python video_splitter.py --chunk-duration 60 --chunks-per-folder 10
"""

import os
import sys
import argparse
import math
import ffmpeg
from pathlib import Path
import shutil


def get_video_duration(input_path):
    """Get the duration of the video in seconds."""
    try:
        probe = ffmpeg.probe(input_path)
        duration = None
        # Try to get duration from the video stream first
        for stream in probe.get('streams', []):
            if stream.get('codec_type') == 'video' and 'duration' in stream:
                duration = float(stream['duration'])
                break
        # Fallback to container duration
        if duration is None:
            duration = float(probe['format']['duration'])
        return duration
    except Exception as e:
        print(f"Error getting video duration: {e}")
        print("Tip: Ensure FFmpeg is installed and available in your PATH. See README.md or run install_ffmpeg.bat")
        return None


def ensure_ffmpeg_available():
    """Return True if ffmpeg binary is available; attempt to auto-detect winget install if missing."""
    # 1) Found in current PATH?
    if shutil.which('ffmpeg') and shutil.which('ffprobe'):
        return True

    # 2) Try to find a winget-installed FFmpeg and add it to PATH for this process
    try:
        local_appdata = os.environ.get('LOCALAPPDATA')
        if local_appdata:
            winget_pkgs = Path(local_appdata) / 'Microsoft' / 'WinGet' / 'Packages'
            if winget_pkgs.exists():
                # Search a couple of common package folders
                candidates = list(winget_pkgs.glob('Gyan.FFmpeg*/*/bin')) + \
                             list(winget_pkgs.glob('Gyan.FFmpeg*/bin'))
                for bin_dir in candidates:
                    ffmpeg_exe = bin_dir / 'ffmpeg.exe'
                    ffprobe_exe = bin_dir / 'ffprobe.exe'
                    if ffmpeg_exe.exists() and ffprobe_exe.exists():
                        # Prepend to PATH for current process
                        os.environ['PATH'] = str(bin_dir) + os.pathsep + os.environ.get('PATH', '')
                        if shutil.which('ffmpeg') and shutil.which('ffprobe'):
                            return True
    except Exception:
        # Silently continue to user guidance below
        pass

    # 3) Not available; show guidance
    print("\nError: FFmpeg is not installed or not found in your PATH.")
    print("This script relies on the FFmpeg binary to process videos.")
    print("\nHow to fix:")
    print("  - Option A: Run the helper script: install_ffmpeg.bat")
    print("  - Option B: Winget (Windows 10/11): winget install ffmpeg")
    print("  - Option C: Chocolatey: choco install ffmpeg")
    print("  - Option D: Manual: Download from https://www.gyan.dev/ffmpeg/builds/ (release essentials),")
    print("               extract to C:\\ffmpeg\\ and add C:\\ffmpeg\\bin to your PATH")
    return False


def create_output_folders(output_path, total_chunks, chunks_per_folder):
    """Create output folders for organizing chunks."""
    folders = []
    num_folders = math.ceil(total_chunks / chunks_per_folder)
    
    for i in range(num_folders):
        folder_name = f"chunks_{i+1:03d}"
        folder_path = os.path.join(output_path, folder_name)
        os.makedirs(folder_path, exist_ok=True)
        folders.append(folder_path)
    
    return folders


def find_video_files(input_dir):
    """Find all video files in the input directory."""
    video_extensions = {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.mpg', '.mpeg'}
    video_files = []
    
    for file in os.listdir(input_dir):
        if Path(file).suffix.lower() in video_extensions:
            video_files.append(file)
    
    return video_files


def split_video(chunk_duration=60, chunks_per_folder=10):
    """
    Split video into chunks and organize them into folders.
    Automatically processes any video file found in ./input/ folder.
    
    Args:
        chunk_duration (int): Duration of each chunk in seconds
        chunks_per_folder (int): Number of chunks per folder
    """
    
    # Set up fixed paths
    app_dir = os.path.dirname(os.path.abspath(__file__))
    input_dir = os.path.join(app_dir, "input")
    output_base = os.path.join(app_dir, "output")
    
    # Ensure input directory exists
    os.makedirs(input_dir, exist_ok=True)
    
    # Find video files in input directory
    video_files = find_video_files(input_dir)
    
    if not video_files:
        print(f"Error: No video files found in ./input/ folder.")
        print(f"Supported formats: .mp4, .avi, .mkv, .mov, .wmv, .flv, .webm, .m4v, .mpg, .mpeg")
        return False
    
    if len(video_files) > 1:
        print(f"Found multiple video files in ./input/ folder:")
        for i, file in enumerate(video_files, 1):
            print(f"  {i}. {file}")
        print(f"Processing the first one: {video_files[0]}")
        print("Please ensure only one video file is in the input folder for best results.\n")
    
    # Use the first video file found
    input_filename = video_files[0]
    input_path = os.path.join(input_dir, input_filename)
    
    # Create video-specific output folder
    video_name = Path(input_filename).stem
    output_path = os.path.join(output_base, f"{video_name}_chunks")
    
    # Validate input file
    if not os.path.exists(input_path):
        print(f"Error: Input file '{input_filename}' not found in ./input/ folder.")
        return False
    
    # Create output directory
    os.makedirs(output_path, exist_ok=True)
    
    print(f"Processing video: {input_filename}")
    print(f"Input file: {input_path}")
    print(f"Output directory: {output_path}")
    
    # Ensure ffmpeg is available before proceeding
    if not ensure_ffmpeg_available():
        return False

    # Get video duration
    duration = get_video_duration(input_path)
    if duration is None:
        return False
    
    print(f"Video duration: {duration:.2f} seconds")
    
    # Calculate number of chunks
    total_chunks = math.ceil(duration / chunk_duration)
    print(f"Total chunks to create: {total_chunks}")
    
    # Create folder structure
    folders = create_output_folders(output_path, total_chunks, chunks_per_folder)
    print(f"Created {len(folders)} folders for organization")
    
    # Get input file info
    input_name = Path(input_path).stem
    input_ext = Path(input_path).suffix
    
    # Split video into chunks
    for i in range(total_chunks):
        start_time = i * chunk_duration
        
        # Determine which folder this chunk belongs to
        folder_index = i // chunks_per_folder
        current_folder = folders[folder_index]
        
        # Create output filename
        chunk_filename = f"{input_name}_chunk_{i+1:03d}{input_ext}"
        output_file = os.path.join(current_folder, chunk_filename)
        
        try:
            print(f"Creating chunk {i+1}/{total_chunks}: {chunk_filename}")
            
            # Use ffmpeg to extract the chunk
            (
                ffmpeg
                .input(input_path, ss=start_time, t=chunk_duration)
                .output(output_file, c='copy')  # Copy without re-encoding for speed
                .overwrite_output()
                .run(quiet=True)
            )
            
        except ffmpeg.Error as e:
            print(f"Error creating chunk {i+1}: {e}")
            continue
    
    print(f"\nVideo splitting complete!")
    print(f"Output location: {output_path}")
    print(f"Total chunks created: {total_chunks}")
    print(f"Chunks organized into {len(folders)} folders")
    
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Split any video found in ./input/ folder into chunks organized in folders",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python video_splitter.py
    python video_splitter.py --chunk-duration 30 --chunks-per-folder 5
    python video_splitter.py -d 120 -c 20

Note: Place your video file in ./input/ folder before running the script.
        """
    )
    
    
    parser.add_argument(
        '-d', '--chunk-duration',
        type=int,
        default=60,
        help='Duration of each chunk in seconds (default: 60)'
    )
    
    parser.add_argument(
        '-c', '--chunks-per-folder',
        type=int,
        default=10,
        help='Number of chunks per folder (default: 10)'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='Video Splitter 1.0'
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.chunk_duration <= 0:
        print("Error: Chunk duration must be greater than 0")
        sys.exit(1)
    
    if args.chunks_per_folder <= 0:
        print("Error: Chunks per folder must be greater than 0")
        sys.exit(1)
    
    # Run the splitter
    success = split_video(
        args.chunk_duration,
        args.chunks_per_folder
    )
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()