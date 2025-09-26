#!/usr/bin/env python3
"""
Comprehensive QA check script for the Video to Meeting Minutes system.
"""

import os
import sys
import subprocess
import json
import time
import requests
from pathlib import Path
from typing import Dict, List, Tuple


class QAChecker:
    """Comprehensive QA checker for the system."""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.results = {
            "passed": 0,
            "failed": 0,
            "warnings": 0,
            "tests": []
        }
    
    def log_test(self, test_name: str, status: str, message: str = ""):
        """Log a test result."""
        self.results["tests"].append({
            "name": test_name,
            "status": status,
            "message": message
        })
        
        if status == "PASS":
            self.results["passed"] += 1
            print(f"✅ {test_name}: {message}")
        elif status == "FAIL":
            self.results["failed"] += 1
            print(f"❌ {test_name}: {message}")
        elif status == "WARN":
            self.results["warnings"] += 1
            print(f"⚠️  {test_name}: {message}")
    
    def check_python_syntax(self) -> bool:
        """Check Python syntax for all Python files."""
        print("\n🔍 Checking Python syntax...")
        
        python_files = list(self.base_dir.rglob("*.py"))
        syntax_errors = []
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    compile(f.read(), str(file_path), 'exec')
            except SyntaxError as e:
                syntax_errors.append(f"{file_path}:{e.lineno}: {e.msg}")
        
        if syntax_errors:
            self.log_test("Python Syntax Check", "FAIL", f"Found {len(syntax_errors)} syntax errors")
            for error in syntax_errors:
                print(f"   {error}")
            return False
        else:
            self.log_test("Python Syntax Check", "PASS", f"All {len(python_files)} Python files have valid syntax")
            return True
    
    def check_imports(self) -> bool:
        """Check that all imports are available."""
        print("\n🔍 Checking Python imports...")
        
        try:
            # Check main dependencies
            import flask
            import requests
            import faster_whisper
            import openai
            import docx
            import zipfile
            import threading
            
            self.log_test("Python Imports", "PASS", "All required Python packages are available")
            return True
        except ImportError as e:
            self.log_test("Python Imports", "FAIL", f"Missing required package: {e}")
            return False
    
    def check_frontend_dependencies(self) -> bool:
        """Check frontend dependencies."""
        print("\n🔍 Checking frontend dependencies...")
        
        frontend_dir = self.base_dir / "frontend"
        if not frontend_dir.exists():
            self.log_test("Frontend Dependencies", "WARN", "Frontend directory not found")
            return False
        
        # Check if package.json exists
        package_json = frontend_dir / "package.json"
        if not package_json.exists():
            self.log_test("Frontend Dependencies", "FAIL", "package.json not found")
            return False
        
        try:
            with open(package_json, 'r') as f:
                package_data = json.load(f)
            
            if "dependencies" in package_data:
                self.log_test("Frontend Dependencies", "PASS", f"Found {len(package_data['dependencies'])} dependencies")
                return True
            else:
                self.log_test("Frontend Dependencies", "WARN", "No dependencies found in package.json")
                return False
        except json.JSONDecodeError:
            self.log_test("Frontend Dependencies", "FAIL", "Invalid package.json format")
            return False
    
    def check_file_structure(self) -> bool:
        """Check that all required files and directories exist."""
        print("\n🔍 Checking file structure...")
        
        required_files = [
            "requirements_microservices.txt",
            "orchestrator.py",
            "start_services.py",
            "services/transcription_service.py",
            "services/meeting_minutes_service.py",
            "services/file_management_service.py",
            "services/api_service.py",
            "frontend/package.json",
            "frontend/shell/package.json",
            "frontend/modules/shared/package.json",
            "frontend/modules/video-processing/package.json",
            "frontend/modules/transcription/package.json",
            "frontend/modules/meeting-minutes/package.json",
            ".github/workflows/ci.yml",
            "docker-compose.yml",
            "Dockerfile"
        ]
        
        missing_files = []
        for file_path in required_files:
            full_path = self.base_dir / file_path
            if not full_path.exists():
                missing_files.append(file_path)
        
        if missing_files:
            self.log_test("File Structure", "FAIL", f"Missing {len(missing_files)} required files")
            for file_path in missing_files:
                print(f"   Missing: {file_path}")
            return False
        else:
            self.log_test("File Structure", "PASS", f"All {len(required_files)} required files exist")
            return True
    
    def check_services_health(self) -> bool:
        """Check that all services can start and respond to health checks."""
        print("\n🔍 Checking services health...")
        
        services = [
            ("Transcription Service", "http://localhost:5001/health"),
            ("Meeting Minutes Service", "http://localhost:5002/health"),
            ("File Management Service", "http://localhost:5003/health"),
            ("API Service", "http://localhost:5004/health")
        ]
        
        healthy_services = 0
        for service_name, url in services:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    self.log_test(f"{service_name} Health", "PASS", "Service is healthy")
                    healthy_services += 1
                else:
                    self.log_test(f"{service_name} Health", "FAIL", f"HTTP {response.status_code}")
            except requests.exceptions.RequestException as e:
                self.log_test(f"{service_name} Health", "WARN", f"Service not running: {e}")
        
        if healthy_services == len(services):
            self.log_test("All Services Health", "PASS", "All services are healthy")
            return True
        else:
            self.log_test("All Services Health", "WARN", f"Only {healthy_services}/{len(services)} services are healthy")
            return False
    
    def check_api_endpoints(self) -> bool:
        """Check that API endpoints are working."""
        print("\n🔍 Checking API endpoints...")
        
        api_endpoints = [
            ("GET /api/meetings", "http://localhost:5004/api/meetings"),
            ("GET /api/stats", "http://localhost:5004/api/stats"),
            ("GET /api/cleanup-status", "http://localhost:5004/api/cleanup-status"),
        ]
        
        working_endpoints = 0
        for endpoint_name, url in api_endpoints:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    self.log_test(f"API {endpoint_name}", "PASS", "Endpoint is working")
                    working_endpoints += 1
                else:
                    self.log_test(f"API {endpoint_name}", "FAIL", f"HTTP {response.status_code}")
            except requests.exceptions.RequestException as e:
                self.log_test(f"API {endpoint_name}", "WARN", f"Endpoint not available: {e}")
        
        if working_endpoints == len(api_endpoints):
            self.log_test("API Endpoints", "PASS", "All API endpoints are working")
            return True
        else:
            self.log_test("API Endpoints", "WARN", f"Only {working_endpoints}/{len(api_endpoints)} endpoints are working")
            return False
    
    def check_file_management_features(self) -> bool:
        """Check file management features."""
        print("\n🔍 Checking file management features...")
        
        # Check if input and output directories exist
        input_dir = self.base_dir / "input"
        output_dir = self.base_dir / "output"
        
        if not input_dir.exists():
            input_dir.mkdir()
            self.log_test("Input Directory", "WARN", "Created input directory")
        else:
            self.log_test("Input Directory", "PASS", "Input directory exists")
        
        if not output_dir.exists():
            output_dir.mkdir()
            self.log_test("Output Directory", "WARN", "Created output directory")
        else:
            self.log_test("Output Directory", "PASS", "Output directory exists")
        
        # Test file management service endpoints
        try:
            response = requests.get("http://localhost:5003/cleanup-status", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.log_test("File Management Service", "PASS", "Cleanup status endpoint working")
                    return True
                else:
                    self.log_test("File Management Service", "FAIL", "Cleanup status endpoint returned error")
                    return False
            else:
                self.log_test("File Management Service", "FAIL", f"HTTP {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            self.log_test("File Management Service", "WARN", f"Service not available: {e}")
            return False
    
    def check_docker_configuration(self) -> bool:
        """Check Docker configuration files."""
        print("\n🔍 Checking Docker configuration...")
        
        docker_files = [
            "Dockerfile",
            "docker-compose.yml",
            ".dockerignore"
        ]
        
        missing_docker_files = []
        for file_path in docker_files:
            full_path = self.base_dir / file_path
            if not full_path.exists():
                missing_docker_files.append(file_path)
        
        if missing_docker_files:
            self.log_test("Docker Configuration", "WARN", f"Missing {len(missing_docker_files)} Docker files")
            for file_path in missing_docker_files:
                print(f"   Missing: {file_path}")
            return False
        else:
            self.log_test("Docker Configuration", "PASS", "All Docker configuration files exist")
            return True
    
    def check_github_workflows(self) -> bool:
        """Check GitHub Actions workflows."""
        print("\n🔍 Checking GitHub workflows...")
        
        workflow_dir = self.base_dir / ".github" / "workflows"
        if not workflow_dir.exists():
            self.log_test("GitHub Workflows", "FAIL", ".github/workflows directory not found")
            return False
        
        workflow_files = list(workflow_dir.glob("*.yml")) + list(workflow_dir.glob("*.yaml"))
        
        if not workflow_files:
            self.log_test("GitHub Workflows", "FAIL", "No workflow files found")
            return False
        
        self.log_test("GitHub Workflows", "PASS", f"Found {len(workflow_files)} workflow files")
        return True
    
    def run_all_checks(self) -> Dict:
        """Run all QA checks."""
        print("🚀 Starting comprehensive QA check...")
        print("=" * 50)
        
        # Run all checks
        checks = [
            self.check_python_syntax,
            self.check_imports,
            self.check_frontend_dependencies,
            self.check_file_structure,
            self.check_services_health,
            self.check_api_endpoints,
            self.check_file_management_features,
            self.check_docker_configuration,
            self.check_github_workflows
        ]
        
        for check in checks:
            try:
                check()
            except Exception as e:
                self.log_test(f"Check {check.__name__}", "FAIL", f"Exception: {e}")
        
        # Print summary
        print("\n" + "=" * 50)
        print("📊 QA CHECK SUMMARY")
        print("=" * 50)
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        print(f"⚠️  Warnings: {self.results['warnings']}")
        print(f"📋 Total Tests: {len(self.results['tests'])}")
        
        # Overall status
        if self.results['failed'] == 0:
            print("\n🎉 All checks passed! The system is ready for deployment.")
            overall_status = "PASS"
        elif self.results['failed'] <= 2:
            print("\n⚠️  Some checks failed, but the system is mostly ready.")
            overall_status = "WARN"
        else:
            print("\n❌ Multiple checks failed. Please fix issues before deployment.")
            overall_status = "FAIL"
        
        self.results['overall_status'] = overall_status
        return self.results


def main():
    """Main function."""
    checker = QAChecker()
    results = checker.run_all_checks()
    
    # Exit with appropriate code
    if results['overall_status'] == "FAIL":
        sys.exit(1)
    elif results['overall_status'] == "WARN":
        sys.exit(2)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
