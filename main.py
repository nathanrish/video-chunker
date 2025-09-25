#!/usr/bin/env python3
"""
Video Chunk Splitter Script
Splits a video into chunks and organizes them into folders.

Requirements:
    pip install ffmpeg-python

Usage:
    python main.py input_video.mp4 output_directory --chunk-duration 60 --chunks-per-folder 10
"""

import os
import sys
import argparse
import math
import ffmpeg
from pathlib import Path


def get_video_duration(input_path):
    """Get the duration of the video in seconds."""
    try:
        probe = ffmpeg.probe(input_path)
        fmt = probe.get('format', {})
        if 'duration' in fmt and fmt['duration'] is not None:
            return float(fmt['duration'])
        for stream in probe.get('streams', []):
            if stream.get('codec_type') == 'video' and stream.get('duration'):
                return float(stream['duration'])
        return None
    except Exception as e:
        print(f"Error getting video duration: {e}")
        return None


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


def split_video(input_path, output_path, chunk_duration=60, chunks_per_folder=10):
    """
    Split video into chunks and organize them into folders.
    
    Args:
        input_path (str): Path to input video file
        output_path (str): Path to output directory
        chunk_duration (int): Duration of each chunk in seconds
        chunks_per_folder (int): Number of chunks per folder
    """
    
    # Validate input file
    if not os.path.exists(input_path):
        print(f"Error: Input file '{input_path}' does not exist.")
        return False
    
    # Create output directory
    os.makedirs(output_path, exist_ok=True)
    
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
    pad_width = len(str(total_chunks))
    
    # Split video into chunks
    for i in range(total_chunks):
        start_time = i * chunk_duration
        segment_duration = min(chunk_duration, max(0, duration - start_time))
        if segment_duration <= 0:
            break
        
        # Determine which folder this chunk belongs to
        folder_index = i // chunks_per_folder
        current_folder = folders[folder_index]
        
        # Create output filename
        chunk_index_str = f"{i+1:0{pad_width}d}"
        chunk_filename = f"{input_name}_chunk_{chunk_index_str}{input_ext}"
        output_file = os.path.join(current_folder, chunk_filename)
        
        try:
            print(f"Creating chunk {i+1}/{total_chunks}: {chunk_filename}")
            
            # Use ffmpeg to extract the chunk
            (
                ffmpeg
                .input(input_path, ss=start_time, t=segment_duration)
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
        description="Split a video into chunks organized in folders",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python main.py input.mp4 ./output
    python main.py input.mp4 ./output --chunk-duration 30 --chunks-per-folder 5
    python main.py "long movie.mp4" "/path/to/output" -d 120 -c 20
        """
    )
    
    parser.add_argument(
        'input_path',
        help='Path to the input video file'
    )
    
    parser.add_argument(
        'output_path',
        help='Path to the output directory'
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
        args.input_path,
        args.output_path,
        args.chunk_duration,
        args.chunks_per_folder
    )
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()