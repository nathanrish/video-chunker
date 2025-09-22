# Video Chunk Splitter

Automatically splits any video found in the `./input/` folder into chunks organized in folders.
Output will be created in the `./output/` folder.

## Features

- Automatically detects video files in the input directory
- Splits videos into configurable chunk durations
- Organizes chunks into folders for better management
- Supports multiple video formats (mp4, avi, mkv, mov, wmv, flv, webm, m4v, mpg, mpeg)
- Fast processing using copy mode (no re-encoding)

## Prerequisites

### 1. Python Requirements
Install the required Python package:
```bash
pip install ffmpeg-python
```

### 2. FFmpeg Installation (Required)

**The script requires FFmpeg to be installed on your system.** Choose one of the following methods:

#### Method 1: Automatic Installation Script
Run the provided batch script:
```bash
install_ffmpeg.bat
```

#### Method 2: Manual Installation
1. Go to [https://www.gyan.dev/ffmpeg/builds/](https://www.gyan.dev/ffmpeg/builds/)
2. Download "release builds" → "ffmpeg-release-essentials.zip"
3. Extract to `C:\ffmpeg\`
4. Add `C:\ffmpeg\bin` to your system PATH environment variable

#### Method 3: Package Managers
If you have a package manager installed:

**Chocolatey:**
```bash
choco install ffmpeg
```

**Winget (Windows 10/11):**
```bash
winget install ffmpeg
```

**Scoop:**
```bash
scoop install ffmpeg
```

### 3. Verify Installation
After installing FFmpeg, verify it works:
```bash
ffmpeg -version
```

## Usage

### Basic Usage
1. Place your video file in the `./input/` folder
2. Run the script:
```bash
python video_splitter.py
```

### Advanced Usage
```bash
# Custom chunk duration (30 seconds) and folder organization (5 chunks per folder)
python video_splitter.py --chunk-duration 30 --chunks-per-folder 5

# Short form
python video_splitter.py -d 120 -c 20
```

### Command Line Options
- `-d, --chunk-duration`: Duration of each chunk in seconds (default: 60)
- `-c, --chunks-per-folder`: Number of chunks per folder (default: 10)
- `--version`: Show version information

## Examples

```bash
# Split into 60-second chunks, 10 per folder (default)
python video_splitter.py

# Split into 30-second chunks, 5 per folder
python video_splitter.py --chunk-duration 30 --chunks-per-folder 5

# Split into 2-minute chunks, 20 per folder
python video_splitter.py -d 120 -c 20
```

## Output Structure

```
output/
└── video_name_chunks/
    ├── chunks_001/
    │   ├── video_name_chunk_001.mp4
    │   ├── video_name_chunk_002.mp4
    │   └── ...
    ├── chunks_002/
    │   ├── video_name_chunk_011.mp4
    │   ├── video_name_chunk_012.mp4
    │   └── ...
    └── ...
```

## Troubleshooting

### Error: "The system cannot find the file specified"
This error typically means FFmpeg is not installed or not in your system PATH. Follow the FFmpeg installation steps above.

### Error: "No video files found"
- Ensure your video file is in the `./input/` folder
- Check that your video file has a supported extension
- Supported formats: .mp4, .avi, .mkv, .mov, .wmv, .flv, .webm, .m4v, .mpg, .mpeg

### Multiple video files
If multiple video files are found in the input folder, the script will process the first one and display a warning. For best results, keep only one video file in the input folder.

## Technical Details

- Uses FFmpeg with copy mode for fast processing (no re-encoding)
- Automatically creates necessary directories
- Handles edge cases like partial final chunks
- Cross-platform compatible (Windows, macOS, Linux)

## Transcription & Documents

You can transcribe the generated chunks and produce documents:

- Full transcript (txt, json)
- Agile meeting minutes (markdown)
- Transcript snapshot (markdown)

### Install extra dependency

```
pip install -r requirements.txt
```

This adds `faster-whisper`, a fast Whisper transcription backend. The first run will download the selected model.

### Usage

```
python transcribe.py --chunks-dir ./output/<video_name>_chunks --model small --language en
```

Common model sizes: `tiny`, `base`, `small`, `medium`, `large` (larger = more accurate, slower). Omit `--language` to auto-detect.

Outputs will be written alongside the chunks directory:

```
output/<video_name>_chunks/
  transcripts/
    chunk_001.txt
    chunk_001.json
    ...
    full_transcript.txt
    full_transcript.json
  docs/
    meeting_minutes.md
    transcript_snapshot.md
```

### Notes

- Ensure FFmpeg is available (see earlier section). The transcriber uses FFmpeg for audio handling under the hood.
- GPU: If you have a CUDA GPU and drivers, you can try `--device cuda --compute-type float16`.

### Advanced options

```
# Include word-level timestamps and paragraph grouping
python transcribe.py --chunks-dir ./output/<video_name>_chunks \
  --word-timestamps --para-gap 3.0 --para-max-chars 600 \
  --facilitator "Your Name" --attendees "A, B, C"

# Refine outputs using OpenAI (set OPENAI_API_KEY)
python transcribe.py --chunks-dir ./output/<video_name>_chunks --use-llm
```

- `--word-timestamps` adds per-word timing in `chunk_XXX.json` and in the aggregated JSON.
- YAML header (title, datetime, facilitator, attendees) is included in `docs/meeting_minutes.md`.
- If `OPENAI_API_KEY` is present and `--use-llm` is set, minutes and snapshot will be refined.

### Exports

If libraries are present, the following are also generated:

- `docs/meeting_minutes.docx`, `docs/meeting_minutes.pdf`
- `docs/transcript_snapshot.docx`, `docs/transcript_snapshot.pdf`

Install with:

```
pip install python-docx reportlab
```

## Version

Video Splitter 1.2 (transcription, docs, advanced options, Docker)

## Docker

A `Dockerfile` is provided. This image includes Python dependencies and system `ffmpeg`.

Build the image:

```
docker build -t video-chunker:latest .
```

Run the splitter inside Docker (mount the project to access input/output):

```
docker run --rm -v %cd%:/app -w /app video-chunker:latest \
  python video_splitter.py -d 60 -c 10
```

Run the transcriber inside Docker:

```
docker run --rm -v %cd%:/app -w /app video-chunker:latest \
  python transcribe.py --chunks-dir ./output/<video_name>_chunks --model small --language en
```
