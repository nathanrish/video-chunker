# Deployment Guide

This guide covers deploying the Video to Meeting Minutes system to different environments.

## 🚀 Quick Start

### Prerequisites

- **Docker** (20.10+)
- **Docker Compose** (2.0+)
- **Node.js** (18+) - for frontend development
- **Python** (3.8+) - for backend development
- **Git** - for version control

### Environment Variables

Create a `.env` file in the project root:

```bash
# OpenAI API Key (optional, for AI features)
OPENAI_API_KEY=your_openai_api_key_here

# Docker Configuration
DOCKER_REGISTRY=ghcr.io
IMAGE_NAME=video-meeting-minutes

# API Configuration
REACT_APP_API_URL=http://localhost:5004

# Database Configuration (optional)
DATABASE_URL=sqlite:///meetings.db
```

## 🏗️ Deployment Options

### 1. Local Development

```bash
# Clone the repository
git clone <repository-url>
cd video_chunks

# Install dependencies
pip install -r requirements_microservices.txt
cd frontend && npm run install:all && cd ..

# Start backend services
python start_services.py

# Start frontend (in another terminal)
cd frontend && npm run dev
```

**Access:**
- Frontend: http://localhost:3000
- API: http://localhost:5004

### 2. Docker Compose (Recommended)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

**Access:**
- Frontend: http://localhost:3000
- API: http://localhost:5004

### 3. Production Deployment

```bash
# Using deployment script
./scripts/deploy.sh production v1.2.0

# Or manually
docker-compose -f docker-compose.prod.yml up -d
```

## 🔧 Environment-Specific Configurations

### Staging Environment

```yaml
# docker-compose.staging.yml
version: '3.8'
services:
  frontend:
    environment:
      - REACT_APP_API_URL=http://staging-api.video-meeting-minutes.com
    ports:
      - "3000:80"
  
  api-service:
    environment:
      - ENVIRONMENT=staging
      - LOG_LEVEL=debug
```

### Production Environment

```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  frontend:
    environment:
      - REACT_APP_API_URL=https://api.video-meeting-minutes.com
    ports:
      - "80:80"
      - "443:443"
  
  api-service:
    environment:
      - ENVIRONMENT=production
      - LOG_LEVEL=info
    restart: unless-stopped
```

## 🐳 Docker Images

### Building Images

```bash
# Build all images
docker-compose build

# Build specific service
docker build -t video-meeting-minutes:latest .
docker build -t video-meeting-minutes-frontend:latest ./frontend
```

### Image Registry

```bash
# Tag for registry
docker tag video-meeting-minutes:latest ghcr.io/username/video-meeting-minutes:latest

# Push to registry
docker push ghcr.io/username/video-meeting-minutes:latest
```

## 🔄 CI/CD Pipeline

### GitHub Actions

The project includes automated CI/CD workflows:

1. **CI Pipeline** (`.github/workflows/ci.yml`)
   - Runs on every push and PR
   - Tests backend and frontend
   - Builds Docker images
   - Runs security scans

2. **Orchestrator Tests** (`.github/workflows/orchestrator_happy.yml`)
   - Tests complete workflow
   - Runs daily at 2 AM
   - Validates end-to-end functionality

3. **Diagram Rendering** (`.github/workflows/render_diagrams.yml`)
   - Renders Mermaid diagrams
   - Updates documentation

### Manual Deployment

```bash
# Run QA checks
python scripts/qa_check.py

# Deploy to staging
./scripts/deploy.sh staging v1.2.0

# Deploy to production
./scripts/deploy.sh production v1.2.0
```

## 📊 Monitoring and Health Checks

### Health Check Endpoints

- **API Service**: `GET /health`
- **Transcription Service**: `GET /health`
- **Meeting Minutes Service**: `GET /health`
- **File Management Service**: `GET /health`

### Monitoring Scripts

```bash
# Check all services
python scripts/qa_check.py

# Check specific service
curl http://localhost:5004/health

# View service logs
docker-compose logs -f api-service
```

## 🗄️ Database Management

### SQLite Database

The system uses SQLite by default:

```bash
# Database location
./meetings.db

# Backup database
cp meetings.db meetings_backup_$(date +%Y%m%d).db

# Restore database
cp meetings_backup_20240115.db meetings.db
```

### Database Migrations

```bash
# Run migrations (if any)
python -c "from services.api_service import APIService; APIService()"
```

## 🔒 Security Considerations

### Environment Variables

- Never commit `.env` files
- Use secure secret management in production
- Rotate API keys regularly

### Docker Security

```bash
# Run as non-root user
docker run --user 1000:1000 video-meeting-minutes

# Use specific image tags (not 'latest')
docker run ghcr.io/username/video-meeting-minutes:v1.2.0
```

### Network Security

```yaml
# docker-compose.yml
services:
  api-service:
    networks:
      - internal
    expose:
      - "5004"
  
  frontend:
    networks:
      - internal
      - external
    ports:
      - "80:80"
```

## 📈 Scaling

### Horizontal Scaling

```yaml
# Scale services
docker-compose up -d --scale transcription-service=3
docker-compose up -d --scale meeting-minutes-service=2
```

### Load Balancing

```yaml
# nginx.conf
upstream api {
    server api-service-1:5004;
    server api-service-2:5004;
    server api-service-3:5004;
}
```

## 🚨 Troubleshooting

### Common Issues

1. **Services won't start**
   ```bash
   # Check logs
   docker-compose logs
   
   # Check port conflicts
   netstat -tulpn | grep :5001
   ```

2. **Database connection issues**
   ```bash
   # Check database file permissions
   ls -la meetings.db
   
   # Recreate database
   rm meetings.db
   python start_services.py
   ```

3. **Frontend build issues**
   ```bash
   # Clear npm cache
   cd frontend
   npm cache clean --force
   rm -rf node_modules package-lock.json
   npm install
   ```

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=debug
python start_services.py

# Or with Docker
docker-compose -f docker-compose.debug.yml up
```

## 📋 Maintenance

### Regular Tasks

1. **Update dependencies**
   ```bash
   pip install -r requirements_microservices.txt --upgrade
   cd frontend && npm update
   ```

2. **Clean up old files**
   ```bash
   # The system auto-purges files after 24 hours
   # Manual cleanup if needed
   find output -type d -mtime +1 -exec rm -rf {} +
   ```

3. **Backup data**
   ```bash
   # Backup database
   cp meetings.db backup/meetings_$(date +%Y%m%d).db
   
   # Backup important output files
   tar -czf backup/output_$(date +%Y%m%d).tar.gz output/
   ```

### Performance Optimization

1. **Use GPU for transcription**
   ```bash
   docker run --gpus all video-meeting-minutes
   ```

2. **Optimize Docker images**
   ```dockerfile
   FROM python:3.9-slim
   # Use multi-stage builds
   # Minimize layers
   ```

## 🔄 Rollback Procedures

### Quick Rollback

```bash
# Stop current version
docker-compose down

# Start previous version
docker-compose -f docker-compose.previous.yml up -d
```

### Database Rollback

```bash
# Restore database backup
cp backup/meetings_20240114.db meetings.db

# Restart services
docker-compose restart api-service
```

## 📞 Support

For deployment issues:

1. Check the troubleshooting section
2. Review service logs
3. Run QA checks: `python scripts/qa_check.py`
4. Open an issue on GitHub

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [React Deployment Guide](https://create-react-app.dev/docs/deployment/)
- [Flask Deployment Guide](https://flask.palletsprojects.com/en/2.0.x/deploying/)
