#!/usr/bin/env python3
"""
Simple Chunk-based Transcription
Transcribes a video by processing it in time-based chunks without requiring FFmpeg.
Uses faster-whisper's built-in segment processing.
"""

import os
import sys
import argparse
import json
from pathlib import Path
from datetime import datetime

try:
    from faster_whisper import WhisperModel
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False


def transcribe_video_chunks(input_path, model_size='tiny', language=None, chunk_duration=300):
    """Transcribe a video file in chunks using faster-whisper's segment processing."""
    
    if not WHISPER_AVAILABLE:
        print("Error: faster-whisper not installed. Install with: pip install faster-whisper")
        return None
    
    # Initialize model
    try:
        model = WhisperModel(model_size, device="cpu", compute_type="int8")
    except Exception as e:
        print(f"Error initializing Whisper model: {e}")
        return None
    
    print(f"Transcribing {input_path} in chunks of {chunk_duration} seconds...")
    print("This approach processes the video in segments for better memory management...")
    
    try:
        # Transcribe with timestamps
        segments, info = model.transcribe(
            str(input_path),
            language=language,
            beam_size=1,
            vad_filter=True,
            word_timestamps=True
        )
        
        # Collect segments and organize by time chunks
        all_segments = []
        current_chunk = 0
        chunk_segments = []
        
        for segment in segments:
            segment_data = {
                'start': segment.start,
                'end': segment.end,
                'text': segment.text.strip(),
                'chunk': int(segment.start // chunk_duration)
            }
            
            # Add word-level timestamps if available
            if hasattr(segment, 'words') and segment.words:
                segment_data['words'] = [
                    {
                        'start': word.start,
                        'end': word.end,
                        'text': word.word.strip()
                    }
                    for word in segment.words if word.word
                ]
            
            all_segments.append(segment_data)
            chunk_segments.append(segment_data)
            
            # Print progress for each chunk
            if segment_data['chunk'] > current_chunk:
                current_chunk = segment_data['chunk']
                print(f"Completed chunk {current_chunk} (up to {current_chunk * chunk_duration}s)")
        
        # Organize by chunks
        chunks = {}
        for segment in all_segments:
            chunk_id = segment['chunk']
            if chunk_id not in chunks:
                chunks[chunk_id] = []
            chunks[chunk_id].append(segment)
        
        transcript_data = {
            'language': info.language,
            'duration': info.duration,
            'chunk_duration': chunk_duration,
            'total_chunks': len(chunks),
            'chunks': chunks,
            'all_segments': all_segments
        }
        
        return transcript_data
        
    except Exception as e:
        print(f"Error during transcription: {e}")
        return None


def save_chunked_transcript(transcript_data, output_dir):
    """Save transcript organized by chunks."""
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    # Save individual chunk files
    for chunk_id, segments in transcript_data['chunks'].items():
        chunk_file = output_dir / f"chunk_{chunk_id:03d}.txt"
        with open(chunk_file, 'w', encoding='utf-8') as f:
            for segment in segments:
                start_time = segment['start']
                hours = int(start_time // 3600)
                minutes = int((start_time % 3600) // 60)
                seconds = int(start_time % 60)
                timestamp = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                f.write(f"[{timestamp}] Speaker: {segment['text']}\n")
    
    # Save combined transcript
    combined_file = output_dir / "full_transcript.txt"
    with open(combined_file, 'w', encoding='utf-8') as f:
        for segment in transcript_data['all_segments']:
            start_time = segment['start']
            hours = int(start_time // 3600)
            minutes = int((start_time % 3600) // 60)
            seconds = int(start_time % 60)
            timestamp = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            f.write(f"[{timestamp}] Speaker: {segment['text']}\n")
    
    # Save JSON data
    json_file = output_dir / "transcript_data.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(transcript_data, f, indent=2, ensure_ascii=False)
    
    print(f"Chunked transcript saved to: {output_dir}")
    print(f"Individual chunks: {len(transcript_data['chunks'])} files")
    print(f"Combined transcript: {combined_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Transcribe a video file in chunks for better memory management",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python simple_chunk_transcribe.py input_video.mp4
    python simple_chunk_transcribe.py input_video.mp4 --chunk-duration 180 --output-dir ./chunks
    python simple_chunk_transcribe.py input_video.mp4 --model small --language en
        """
    )
    
    parser.add_argument(
        'input_video',
        help='Path to input video file'
    )
    
    parser.add_argument(
        '--output-dir',
        default='./chunked_transcript',
        help='Output directory for chunked transcripts (default: ./chunked_transcript)'
    )
    
    parser.add_argument(
        '--chunk-duration',
        type=int,
        default=300,
        help='Chunk duration in seconds (default: 300 = 5 minutes)'
    )
    
    parser.add_argument(
        '-m', '--model',
        choices=['tiny', 'base', 'small', 'medium', 'large'],
        default='tiny',
        help='Whisper model size (default: tiny)'
    )
    
    parser.add_argument(
        '-l', '--language',
        help='Language code (e.g., en, es, fr). Leave empty for auto-detection'
    )
    
    args = parser.parse_args()
    
    # Validate input file
    if not os.path.exists(args.input_video):
        print(f"Error: Input video file '{args.input_video}' does not exist.")
        sys.exit(1)
    
    # Check if faster-whisper is available
    if not WHISPER_AVAILABLE:
        print("Error: faster-whisper is not installed.")
        print("Install it with: pip install faster-whisper")
        sys.exit(1)
    
    # Transcribe video in chunks
    transcript_data = transcribe_video_chunks(
        args.input_video,
        model_size=args.model,
        language=args.language,
        chunk_duration=args.chunk_duration
    )
    
    if transcript_data is None:
        print("Transcription failed.")
        sys.exit(1)
    
    # Save chunked transcript
    save_chunked_transcript(transcript_data, args.output_dir)
    
    # Print summary
    print(f"\nTranscription Summary:")
    print(f"Language detected: {transcript_data['language']}")
    print(f"Duration: {transcript_data['duration']:.2f} seconds")
    print(f"Total chunks: {transcript_data['total_chunks']}")
    print(f"Total segments: {len(transcript_data['all_segments'])}")
    
    # Suggest next step
    print(f"\nNext step: Generate meeting minutes with:")
    print(f"python meeting_minutes_generator.py {args.output_dir}/full_transcript.txt")


if __name__ == "__main__":
    main()
