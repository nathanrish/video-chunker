#!/bin/bash

# Deployment script for Video to Meeting Minutes system
# This script handles deployment to different environments

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${1:-staging}
VERSION=${2:-latest}
DOCKER_REGISTRY=${DOCKER_REGISTRY:-ghcr.io}
IMAGE_NAME=${IMAGE_NAME:-video-meeting-minutes}

# Functions
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
    exit 1
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed"
    fi
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose is not installed"
    fi
    
    # Check if required environment variables are set
    if [ -z "$OPENAI_API_KEY" ] && [ "$ENVIRONMENT" = "production" ]; then
        warning "OPENAI_API_KEY not set for production deployment"
    fi
    
    success "Prerequisites check passed"
}

# Run tests
run_tests() {
    log "Running tests..."
    
    # Run Python tests
    if [ -f "requirements_microservices.txt" ]; then
        pip install -r requirements_microservices.txt
        python -m pytest tests/ -v --cov=. --cov-report=html
    fi
    
    # Run frontend tests
    if [ -d "frontend" ]; then
        cd frontend
        npm ci
        npm run test -- --coverage --watchAll=false
        cd ..
    fi
    
    success "Tests completed"
}

# Build Docker images
build_images() {
    log "Building Docker images..."
    
    # Build main application image
    docker build -t ${DOCKER_REGISTRY}/${IMAGE_NAME}:${VERSION} .
    docker build -t ${DOCKER_REGISTRY}/${IMAGE_NAME}:latest .
    
    # Build frontend image
    if [ -d "frontend" ]; then
        cd frontend
        docker build -t ${DOCKER_REGISTRY}/${IMAGE_NAME}-frontend:${VERSION} .
        docker build -t ${DOCKER_REGISTRY}/${IMAGE_NAME}-frontend:latest .
        cd ..
    fi
    
    success "Docker images built"
}

# Push images to registry
push_images() {
    log "Pushing images to registry..."
    
    # Login to registry (if not already logged in)
    if [ "$DOCKER_REGISTRY" != "docker.io" ]; then
        echo "$DOCKER_TOKEN" | docker login $DOCKER_REGISTRY -u $DOCKER_USERNAME --password-stdin
    fi
    
    # Push images
    docker push ${DOCKER_REGISTRY}/${IMAGE_NAME}:${VERSION}
    docker push ${DOCKER_REGISTRY}/${IMAGE_NAME}:latest
    
    if [ -d "frontend" ]; then
        docker push ${DOCKER_REGISTRY}/${IMAGE_NAME}-frontend:${VERSION}
        docker push ${DOCKER_REGISTRY}/${IMAGE_NAME}-frontend:latest
    fi
    
    success "Images pushed to registry"
}

# Deploy to environment
deploy() {
    log "Deploying to $ENVIRONMENT environment..."
    
    # Create environment-specific configuration
    case $ENVIRONMENT in
        "staging")
            export COMPOSE_PROJECT_NAME=video-meeting-minutes-staging
            export REACT_APP_API_URL=http://localhost:5004
            ;;
        "production")
            export COMPOSE_PROJECT_NAME=video-meeting-minutes-prod
            export REACT_APP_API_URL=https://api.video-meeting-minutes.com
            ;;
        *)
            error "Unknown environment: $ENVIRONMENT"
            ;;
    esac
    
    # Stop existing containers
    docker-compose down --remove-orphans
    
    # Start services
    docker-compose up -d
    
    # Wait for services to be healthy
    log "Waiting for services to be healthy..."
    sleep 30
    
    # Check service health
    check_service_health
    
    success "Deployment to $ENVIRONMENT completed"
}

# Check service health
check_service_health() {
    log "Checking service health..."
    
    services=(
        "http://localhost:5001/health:Transcription Service"
        "http://localhost:5002/health:Meeting Minutes Service"
        "http://localhost:5003/health:File Management Service"
        "http://localhost:5004/health:API Service"
        "http://localhost:3000:Frontend"
    )
    
    for service in "${services[@]}"; do
        url=$(echo $service | cut -d: -f1-2)
        name=$(echo $service | cut -d: -f3)
        
        if curl -f -s $url > /dev/null; then
            success "$name is healthy"
        else
            error "$name is not responding"
        fi
    done
}

# Run database migrations
run_migrations() {
    log "Running database migrations..."
    
    # This would run any database migrations if needed
    # For now, the SQLite database is created automatically
    success "Database migrations completed"
}

# Cleanup old images
cleanup() {
    log "Cleaning up old Docker images..."
    
    # Remove dangling images
    docker image prune -f
    
    # Remove old versions (keep last 3)
    docker images ${DOCKER_REGISTRY}/${IMAGE_NAME} --format "table {{.Tag}}\t{{.ID}}" | \
        grep -v "latest" | \
        tail -n +4 | \
        awk '{print $2}' | \
        xargs -r docker rmi || true
    
    success "Cleanup completed"
}

# Rollback deployment
rollback() {
    log "Rolling back deployment..."
    
    # Stop current containers
    docker-compose down
    
    # Start previous version (this would need to be implemented based on your rollback strategy)
    warning "Rollback functionality needs to be implemented based on your specific requirements"
}

# Main deployment flow
main() {
    log "Starting deployment process..."
    log "Environment: $ENVIRONMENT"
    log "Version: $VERSION"
    log "Registry: $DOCKER_REGISTRY"
    
    # Run deployment steps
    check_prerequisites
    
    if [ "$SKIP_TESTS" != "true" ]; then
        run_tests
    fi
    
    build_images
    
    if [ "$PUSH_IMAGES" = "true" ]; then
        push_images
    fi
    
    run_migrations
    deploy
    
    if [ "$CLEANUP" = "true" ]; then
        cleanup
    fi
    
    success "Deployment completed successfully!"
    
    # Print access information
    echo ""
    log "Access Information:"
    echo "  Frontend: http://localhost:3000"
    echo "  API: http://localhost:5004"
    echo "  Health Check: http://localhost:5004/health"
    echo ""
    log "To view logs: docker-compose logs -f"
    log "To stop services: docker-compose down"
}

# Handle command line arguments
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "rollback")
        rollback
        ;;
    "health")
        check_service_health
        ;;
    "cleanup")
        cleanup
        ;;
    *)
        echo "Usage: $0 {deploy|rollback|health|cleanup} [environment] [version]"
        echo "  deploy: Deploy the application (default)"
        echo "  rollback: Rollback to previous version"
        echo "  health: Check service health"
        echo "  cleanup: Clean up old Docker images"
        echo ""
        echo "Environment variables:"
        echo "  OPENAI_API_KEY: OpenAI API key for AI features"
        echo "  DOCKER_REGISTRY: Docker registry URL (default: ghcr.io)"
        echo "  IMAGE_NAME: Docker image name (default: video-meeting-minutes)"
        echo "  SKIP_TESTS: Set to 'true' to skip tests"
        echo "  PUSH_IMAGES: Set to 'true' to push images to registry"
        echo "  CLEANUP: Set to 'true' to clean up old images"
        exit 1
        ;;
esac
