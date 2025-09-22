# Multi-stage build for smaller final image
FROM python:3.10-slim AS base

# Install system dependencies and ffmpeg
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set workdir
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt ./

# Install Python deps
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY . .

# Default command prints help
CMD ["python", "video_splitter.py", "--help"]
