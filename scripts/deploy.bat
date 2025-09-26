@echo off
REM Deployment script for Video to Meeting Minutes system (Windows)
REM This script handles deployment to different environments

setlocal enabledelayedexpansion

REM Configuration
set ENVIRONMENT=%1
if "%ENVIRONMENT%"=="" set ENVIRONMENT=staging
set VERSION=%2
if "%VERSION%"=="" set VERSION=latest
set DOCKER_REGISTRY=%DOCKER_REGISTRY%
if "%DOCKER_REGISTRY%"=="" set DOCKER_REGISTRY=ghcr.io
set IMAGE_NAME=%IMAGE_NAME%
if "%IMAGE_NAME%"=="" set IMAGE_NAME=video-meeting-minutes

REM Functions
:log
echo [%date% %time%] %~1
goto :eof

:success
echo ✅ %~1
goto :eof

:warning
echo ⚠️  %~1
goto :eof

:error
echo ❌ %~1
exit /b 1

REM Check prerequisites
:check_prerequisites
call :log "Checking prerequisites..."

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    call :error "Docker is not installed"
)

REM Check if Docker Compose is installed
docker-compose --version >nul 2>&1
if errorlevel 1 (
    call :error "Docker Compose is not installed"
)

call :success "Prerequisites check passed"
goto :eof

REM Run tests
:run_tests
call :log "Running tests..."

REM Run Python tests
if exist "requirements_microservices.txt" (
    pip install -r requirements_microservices.txt
    python -m pytest tests/ -v --cov=. --cov-report=html
)

REM Run frontend tests
if exist "frontend" (
    cd frontend
    call npm ci
    call npm run test -- --coverage --watchAll=false
    cd ..
)

call :success "Tests completed"
goto :eof

REM Build Docker images
:build_images
call :log "Building Docker images..."

REM Build main application image
docker build -t %DOCKER_REGISTRY%/%IMAGE_NAME%:%VERSION% .
docker build -t %DOCKER_REGISTRY%/%IMAGE_NAME%:latest .

REM Build frontend image
if exist "frontend" (
    cd frontend
    docker build -t %DOCKER_REGISTRY%/%IMAGE_NAME%-frontend:%VERSION% .
    docker build -t %DOCKER_REGISTRY%/%IMAGE_NAME%-frontend:latest .
    cd ..
)

call :success "Docker images built"
goto :eof

REM Deploy to environment
:deploy
call :log "Deploying to %ENVIRONMENT% environment..."

REM Set environment-specific configuration
if "%ENVIRONMENT%"=="staging" (
    set COMPOSE_PROJECT_NAME=video-meeting-minutes-staging
    set REACT_APP_API_URL=http://localhost:5004
) else if "%ENVIRONMENT%"=="production" (
    set COMPOSE_PROJECT_NAME=video-meeting-minutes-prod
    set REACT_APP_API_URL=https://api.video-meeting-minutes.com
) else (
    call :error "Unknown environment: %ENVIRONMENT%"
)

REM Stop existing containers
docker-compose down --remove-orphans

REM Start services
docker-compose up -d

REM Wait for services to be healthy
call :log "Waiting for services to be healthy..."
timeout /t 30 /nobreak >nul

REM Check service health
call :check_service_health

call :success "Deployment to %ENVIRONMENT% completed"
goto :eof

REM Check service health
:check_service_health
call :log "Checking service health..."

REM Check each service
curl -f -s http://localhost:5001/health >nul 2>&1
if errorlevel 1 (
    call :error "Transcription Service is not responding"
) else (
    call :success "Transcription Service is healthy"
)

curl -f -s http://localhost:5002/health >nul 2>&1
if errorlevel 1 (
    call :error "Meeting Minutes Service is not responding"
) else (
    call :success "Meeting Minutes Service is healthy"
)

curl -f -s http://localhost:5003/health >nul 2>&1
if errorlevel 1 (
    call :error "File Management Service is not responding"
) else (
    call :success "File Management Service is healthy"
)

curl -f -s http://localhost:5004/health >nul 2>&1
if errorlevel 1 (
    call :error "API Service is not responding"
) else (
    call :success "API Service is healthy"
)

curl -f -s http://localhost:3000 >nul 2>&1
if errorlevel 1 (
    call :error "Frontend is not responding"
) else (
    call :success "Frontend is healthy"
)
goto :eof

REM Main deployment flow
:main
call :log "Starting deployment process..."
call :log "Environment: %ENVIRONMENT%"
call :log "Version: %VERSION%"
call :log "Registry: %DOCKER_REGISTRY%"

REM Run deployment steps
call :check_prerequisites

if not "%SKIP_TESTS%"=="true" (
    call :run_tests
)

call :build_images
call :deploy

call :success "Deployment completed successfully!"

REM Print access information
echo.
call :log "Access Information:"
echo   Frontend: http://localhost:3000
echo   API: http://localhost:5004
echo   Health Check: http://localhost:5004/health
echo.
call :log "To view logs: docker-compose logs -f"
call :log "To stop services: docker-compose down"
goto :eof

REM Handle command line arguments
if "%1"=="deploy" goto main
if "%1"=="rollback" goto rollback
if "%1"=="health" goto check_service_health
if "%1"=="cleanup" goto cleanup
if "%1"=="" goto main

echo Usage: %0 {deploy^|rollback^|health^|cleanup} [environment] [version]
echo   deploy: Deploy the application (default)
echo   rollback: Rollback to previous version
echo   health: Check service health
echo   cleanup: Clean up old Docker images
echo.
echo Environment variables:
echo   OPENAI_API_KEY: OpenAI API key for AI features
echo   DOCKER_REGISTRY: Docker registry URL (default: ghcr.io)
echo   IMAGE_NAME: Docker image name (default: video-meeting-minutes)
echo   SKIP_TESTS: Set to 'true' to skip tests
exit /b 1

:rollback
call :log "Rolling back deployment..."
docker-compose down
call :warning "Rollback functionality needs to be implemented based on your specific requirements"
goto :eof

:cleanup
call :log "Cleaning up old Docker images..."
docker image prune -f
call :success "Cleanup completed"
goto :eof
