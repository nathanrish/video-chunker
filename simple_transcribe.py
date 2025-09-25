#!/usr/bin/env python3
"""
Simple Video Transcriber
Transcribes a single video file using faster-whisper.

Requirements:
    pip install faster-whisper

Usage:
    python simple_transcribe.py input_video.mp4 --output transcription.txt
    python simple_transcribe.py input_video.mp4 --model small --language en
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


def transcribe_video(input_path, model_size='small', language=None, device='auto', compute_type='auto'):
    """Transcribe a video file using faster-whisper."""
    
    if not WHISPER_AVAILABLE:
        print("Error: faster-whisper not installed. Install with: pip install faster-whisper")
        return None
    
    # Initialize model
    try:
        model = WhisperModel(model_size, device=device, compute_type=compute_type)
    except Exception as e:
        print(f"Error initializing Whisper model: {e}")
        return None
    
    print(f"Transcribing {input_path}...")
    print("This may take a few minutes depending on video length...")
    
    try:
        # Transcribe with timestamps
        segments, info = model.transcribe(
            str(input_path),
            language=language,
            beam_size=1,
            vad_filter=True,
            word_timestamps=True
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
            if hasattr(segment, 'words') and segment.words:
                segment_data['words'] = [
                    {
                        'start': word.start,
                        'end': word.end,
                        'text': word.word.strip()
                    }
                    for word in segment.words if word.word
                ]
            
            transcript_data['segments'].append(segment_data)
        
        return transcript_data
        
    except Exception as e:
        print(f"Error during transcription: {e}")
        return None


def format_transcript_for_meeting_minutes(transcript_data):
    """Format transcript data for the meeting minutes generator."""
    lines = []
    
    for segment in transcript_data['segments']:
        start_time = segment['start']
        text = segment['text']
        
        # Format timestamp as HH:MM:SS
        hours = int(start_time // 3600)
        minutes = int((start_time % 3600) // 60)
        seconds = int(start_time % 60)
        timestamp = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        
        # For now, we'll use a generic speaker since we don't have speaker diarization
        # The meeting minutes generator can try to identify speakers from the text
        lines.append(f"[{timestamp}] Speaker: {text}")
    
    return '\n'.join(lines)


def save_transcript(transcript_data, output_path, format_type='txt'):
    """Save transcript in various formats."""
    output_path = Path(output_path)
    
    if format_type == 'txt':
        # Format for meeting minutes generator
        formatted_text = format_transcript_for_meeting_minutes(transcript_data)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(formatted_text)
    
    elif format_type == 'json':
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(transcript_data, f, indent=2, ensure_ascii=False)
    
    elif format_type == 'srt':
        # SubRip subtitle format
        with open(output_path, 'w', encoding='utf-8') as f:
            for i, segment in enumerate(transcript_data['segments'], 1):
                start_time = format_srt_time(segment['start'])
                end_time = format_srt_time(segment['end'])
                f.write(f"{i}\n")
                f.write(f"{start_time} --> {end_time}\n")
                f.write(f"{segment['text']}\n\n")
    
    print(f"Transcript saved to: {output_path}")


def format_srt_time(seconds):
    """Format time for SRT subtitle format."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millisecs = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"


def main():
    parser = argparse.ArgumentParser(
        description="Transcribe a single video file",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python simple_transcribe.py input_video.mp4
    python simple_transcribe.py input_video.mp4 --output meeting_transcript.txt
    python simple_transcribe.py input_video.mp4 --model small --language en --format json
    python simple_transcribe.py input_video.mp4 --format srt --output subtitles.srt
        """
    )
    
    parser.add_argument(
        'input_video',
        help='Path to input video file'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output file path (default: input_name_transcript.txt)'
    )
    
    parser.add_argument(
        '-f', '--format',
        choices=['txt', 'json', 'srt'],
        default='txt',
        help='Output format (default: txt)'
    )
    
    parser.add_argument(
        '-m', '--model',
        choices=['tiny', 'base', 'small', 'medium', 'large'],
        default='small',
        help='Whisper model size (default: small)'
    )
    
    parser.add_argument(
        '-l', '--language',
        help='Language code (e.g., en, es, fr). Leave empty for auto-detection'
    )
    
    parser.add_argument(
        '-d', '--device',
        choices=['auto', 'cpu', 'cuda'],
        default='auto',
        help='Device to use (default: auto)'
    )
    
    parser.add_argument(
        '--compute-type',
        choices=['auto', 'int8', 'int8_float16', 'float16', 'float32'],
        default='auto',
        help='Compute type (default: auto)'
    )
    
    args = parser.parse_args()
    
    # Validate input file
    if not os.path.exists(args.input_video):
        print(f"Error: Input video file '{args.input_video}' does not exist.")
        sys.exit(1)
    
    # Generate output filename if not provided
    if not args.output:
        input_path = Path(args.input_video)
        base_name = input_path.stem
        args.output = f"{base_name}_transcript.{args.format}"
    
    # Check if faster-whisper is available
    if not WHISPER_AVAILABLE:
        print("Error: faster-whisper is not installed.")
        print("Install it with: pip install faster-whisper")
        sys.exit(1)
    
    # Transcribe video
    transcript_data = transcribe_video(
        args.input_video,
        model_size=args.model,
        language=args.language,
        device=args.device,
        compute_type=args.compute_type
    )
    
    if transcript_data is None:
        print("Transcription failed.")
        sys.exit(1)
    
    # Save transcript
    save_transcript(transcript_data, args.output, args.format)
    
    # Print summary
    print(f"\nTranscription Summary:")
    print(f"Language detected: {transcript_data['language']}")
    print(f"Duration: {transcript_data['duration']:.2f} seconds")
    print(f"Segments: {len(transcript_data['segments'])}")
    
    # If txt format, suggest next step
    if args.format == 'txt':
        print(f"\nNext step: Generate meeting minutes with:")
        print(f"python meeting_minutes_generator.py {args.output}")


if __name__ == "__main__":
    main()
