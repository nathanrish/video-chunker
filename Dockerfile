# Multi-stage build for microservices video-to-meeting-minutes system
FROM python:3.10-slim AS base

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set workdir
WORKDIR /app

# Copy requirements for microservices
COPY requirements_microservices.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements_microservices.txt

# Copy source code
COPY . .

# Create output directory
RUN mkdir -p /app/output

# Expose service ports (including orchestrator)
EXPOSE 5000 5001 5002 5003

# Health check for services
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health && \
        curl -f http://localhost:5001/health && \
        curl -f http://localhost:5002/health && \
        curl -f http://localhost:5003/health || exit 1

# Default command starts all microservices
CMD ["python", "start_services.py"]
