#!/usr/bin/env python3
"""
Service Startup Script
Starts all microservices for the video-to-meeting-minutes workflow.
"""

import os
import sys
import time
import subprocess
import signal
import logging
from pathlib import Path
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ServiceManager:
    def __init__(self):
        self.processes = {}
        self.services = {
            "transcription": {
                "script": "services/transcription_service.py",
                "port": 5001,
                # Allow env overrides for CI/happy path
                "args": [
                    "--model", os.environ.get("TRANSCRIPTION_MODEL", "small"),
                    "--device", os.environ.get("TRANSCRIPTION_DEVICE", "auto"),
                    "--compute-type", os.environ.get("TRANSCRIPTION_COMPUTE_TYPE", "auto")
                ]
            },
            "meeting_minutes": {
                "script": "services/meeting_minutes_service.py",
                "port": 5002,
                "args": []
            },
            "file_management": {
                "script": "services/file_management_service.py",
                "port": 5003,
                "args": ["--base-output-dir", "./output"]
            },
            "orchestrator": {
                "script": "services/orchestrator_service.py",
                "port": 5000,
                "args": []
            }
        }
    
    def start_service(self, service_name: str, api_key: str = None):
        """Start a specific service."""
        if service_name not in self.services:
            logger.error(f"Unknown service: {service_name}")
            return False
        
        service_config = self.services[service_name]
        script_path = Path(service_config["script"])
        
        if not script_path.exists():
            logger.error(f"Service script not found: {script_path}")
            return False
        
        # Build command
        cmd = [sys.executable, str(script_path), "--port", str(service_config["port"])]
        cmd.extend(service_config["args"])
        
        # Add API key for meeting minutes service
        if service_name == "meeting_minutes" and api_key:
            cmd.extend(["--api-key", api_key])
        
        try:
            logger.info(f"Starting {service_name} service on port {service_config['port']}")
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.processes[service_name] = process
            logger.info(f"✅ {service_name} service started (PID: {process.pid})")
            
            # Wait a moment for service to start
            time.sleep(2)
            
            # Check if process is still running
            if process.poll() is None:
                return True
            else:
                stdout, stderr = process.communicate()
                logger.error(f"❌ {service_name} service failed to start")
                logger.error(f"STDOUT: {stdout}")
                logger.error(f"STDERR: {stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to start {service_name} service: {e}")
            return False
    
    def stop_service(self, service_name: str):
        """Stop a specific service."""
        if service_name in self.processes:
            process = self.processes[service_name]
            try:
                process.terminate()
                process.wait(timeout=5)
                logger.info(f"✅ {service_name} service stopped")
                del self.processes[service_name]
            except subprocess.TimeoutExpired:
                process.kill()
                logger.info(f"🔪 {service_name} service killed")
                del self.processes[service_name]
            except Exception as e:
                logger.error(f"Error stopping {service_name} service: {e}")
    
    def start_all_services(self, api_key: str = None):
        """Start all services."""
        logger.info("🚀 Starting all microservices...")
        
        success_count = 0
        for service_name in self.services:
            if self.start_service(service_name, api_key):
                success_count += 1
            else:
                logger.error(f"Failed to start {service_name} service")
        
        if success_count == len(self.services):
            logger.info("🎉 All services started successfully!")
            logger.info("\n📋 Service URLs:")
            for service_name, config in self.services.items():
                logger.info(f"  • {service_name}: http://localhost:{config['port']}")
            return True
        else:
            logger.error(f"❌ Only {success_count}/{len(self.services)} services started")
            return False
    
    def stop_all_services(self):
        """Stop all services."""
        logger.info("🛑 Stopping all services...")
        
        for service_name in list(self.processes.keys()):
            self.stop_service(service_name)
        
        logger.info("✅ All services stopped")
    
    def check_services_health(self):
        """Check health of all running services."""
        import requests
        
        logger.info("🔍 Checking service health...")
        
        for service_name, config in self.services.items():
            try:
                response = requests.get(f"http://localhost:{config['port']}/health", timeout=5)
                if response.status_code == 200:
                    health_data = response.json()
                    logger.info(f"✅ {service_name}: {health_data.get('status', 'unknown')}")
                else:
                    logger.warning(f"⚠️ {service_name}: HTTP {response.status_code}")
            except requests.exceptions.RequestException as e:
                logger.error(f"❌ {service_name}: {e}")
    
    def wait_for_services(self, timeout: int = 30):
        """Wait for all services to be ready."""
        import requests
        
        logger.info(f"⏳ Waiting for services to be ready (timeout: {timeout}s)...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            all_ready = True
            
            for service_name, config in self.services.items():
                try:
                    response = requests.get(f"http://localhost:{config['port']}/health", timeout=2)
                    if response.status_code != 200:
                        all_ready = False
                        break
                except requests.exceptions.RequestException:
                    all_ready = False
                    break
            
            if all_ready:
                logger.info("✅ All services are ready!")
                return True
            
            time.sleep(1)
        
        logger.error("❌ Services not ready within timeout")
        return False


def signal_handler(signum, frame):
    """Handle shutdown signals."""
    logger.info("\n🛑 Received shutdown signal")
    if 'service_manager' in globals():
        service_manager.stop_all_services()
    sys.exit(0)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Start microservices for video-to-meeting-minutes workflow")
    parser.add_argument('--api-key', help='OpenAI API key for AI features')
    parser.add_argument('--check-only', action='store_true', help='Only check service health')
    parser.add_argument('--stop', action='store_true', help='Stop all services')
    parser.add_argument('--wait-timeout', type=int, default=30, help='Timeout for waiting services to be ready')
    
    args = parser.parse_args()
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    global service_manager
    service_manager = ServiceManager()
    
    if args.stop:
        service_manager.stop_all_services()
        return
    
    if args.check_only:
        service_manager.check_services_health()
        return
    
    # Start all services
    if service_manager.start_all_services(args.api_key):
        # Wait for services to be ready
        if service_manager.wait_for_services(args.wait_timeout):
            logger.info("\n🎯 Services are ready! You can now run the orchestrator.")
            logger.info("\nExample usage:")
            logger.info('python orchestrator.py "input/meeting.mp4" "Team Meeting"')
            
            # Keep running until interrupted
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                logger.info("\n🛑 Shutting down...")
                service_manager.stop_all_services()
        else:
            logger.error("❌ Services failed to start properly")
            service_manager.stop_all_services()
            sys.exit(1)
    else:
        logger.error("❌ Failed to start services")
        sys.exit(1)


if __name__ == "__main__":
    main()
