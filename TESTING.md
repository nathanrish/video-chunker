# Testing Guide

This guide covers testing the Video to Meeting Minutes system at all levels.

## 🧪 Testing Strategy

### Test Pyramid

```
    /\
   /  \
  / E2E \     End-to-End Tests
 /______\
/        \
/Integration\  Integration Tests
/____________\
/              \
/    Unit Tests   \  Unit Tests
/__________________\
```

### Test Types

1. **Unit Tests** - Individual components and functions
2. **Integration Tests** - Service interactions
3. **End-to-End Tests** - Complete user workflows
4. **Performance Tests** - Load and stress testing
5. **Security Tests** - Vulnerability scanning

## 🔧 Test Setup

### Prerequisites

```bash
# Install test dependencies
pip install pytest pytest-cov pytest-mock flake8 black isort

# Install frontend test dependencies
cd frontend
npm install --save-dev jest @testing-library/react @testing-library/jest-dom
```

### Test Configuration

```ini
# pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --verbose
    --tb=short
    --strict-markers
    --disable-warnings
    --cov=.
    --cov-report=html
    --cov-report=xml
    --cov-report=term-missing
    --cov-fail-under=80
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow running tests
    api: API tests
    frontend: Frontend tests
```

## 🧩 Unit Tests

### Backend Unit Tests

#### Test File Management Service

```python
# tests/test_file_management.py
import pytest
from services.file_management_service import FileManagementService

def test_create_dated_folder():
    service = FileManagementService()
    folder_path = service.create_dated_folder("Test Meeting")
    assert Path(folder_path).exists()

def test_save_transcript():
    service = FileManagementService()
    result = service.save_transcript("Test text", "/tmp", "test.txt")
    assert result["success"] is True
```

#### Test API Service

```python
# tests/test_api_service.py
import pytest
from services.api_service import APIService

def test_create_meeting():
    service = APIService(db_path=":memory:")
    meeting = service.db.create_meeting(Meeting(...))
    assert meeting.title == "Test Meeting"
```

### Frontend Unit Tests

#### Test React Components

```javascript
// frontend/shell/src/__tests__/App.test.js
import React from 'react';
import { render, screen } from '@testing-library/react';
import App from '../App';

test('renders without crashing', () => {
  render(<App />);
  expect(screen.getByText('Video to Meeting Minutes')).toBeInTheDocument();
});
```

#### Test Shared Components

```javascript
// frontend/modules/shared/src/__tests__/StatusChip.test.js
import React from 'react';
import { render } from '@testing-library/react';
import { StatusChip } from '../StatusChip';

test('renders status chip with correct color', () => {
  const { getByText } = render(<StatusChip status="completed" />);
  expect(getByText('completed')).toBeInTheDocument();
});
```

## 🔗 Integration Tests

### Service Integration

```python
# tests/test_integration.py
import pytest
import requests
from services.file_management_service import FileManagementService

@pytest.mark.integration
def test_complete_workflow():
    # Start services
    # Process video
    # Verify outputs
    pass
```

### API Integration

```python
# tests/test_api_integration.py
import pytest
import requests

@pytest.mark.api
def test_meeting_crud_workflow():
    # Create meeting
    response = requests.post('http://localhost:5004/api/meetings', json={...})
    assert response.status_code == 201
    
    # Get meeting
    meeting_id = response.json()['data']['id']
    response = requests.get(f'http://localhost:5004/api/meetings/{meeting_id}')
    assert response.status_code == 200
```

## 🎯 End-to-End Tests

### Complete Workflow Test

```python
# tests/test_e2e.py
import pytest
import subprocess
import time

@pytest.mark.slow
def test_complete_video_processing():
    # Start all services
    subprocess.Popen(['python', 'start_services.py'])
    time.sleep(30)
    
    # Process test video
    result = subprocess.run([
        'python', 'orchestrator.py',
        'input/test_video.mp4',
        'Test Meeting'
    ], capture_output=True, text=True)
    
    assert result.returncode == 0
    assert 'success' in result.stdout.lower()
```

### Frontend E2E Tests

```javascript
// frontend/e2e/upload.test.js
import { test, expect } from '@playwright/test';

test('upload and process video', async ({ page }) => {
  await page.goto('http://localhost:3000');
  
  // Upload video
  await page.setInputFiles('input[type="file"]', 'test_video.mp4');
  await page.click('button[type="submit"]');
  
  // Wait for processing
  await expect(page.locator('[data-testid="processing-status"]')).toContainText('Processing');
  
  // Verify completion
  await expect(page.locator('[data-testid="success-message"]')).toBeVisible();
});
```

## ⚡ Performance Tests

### Load Testing

```python
# tests/test_performance.py
import pytest
import requests
import time
from concurrent.futures import ThreadPoolExecutor

@pytest.mark.slow
def test_concurrent_requests():
    def make_request():
        response = requests.get('http://localhost:5004/api/meetings')
        return response.status_code
    
    # Test with 10 concurrent requests
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(make_request) for _ in range(10)]
        results = [future.result() for future in futures]
    
    assert all(status == 200 for status in results)
```

### Memory Usage Test

```python
# tests/test_memory.py
import pytest
import psutil
import os

def test_memory_usage():
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss
    
    # Perform memory-intensive operations
    # ...
    
    final_memory = process.memory_info().rss
    memory_increase = final_memory - initial_memory
    
    # Should not use more than 100MB
    assert memory_increase < 100 * 1024 * 1024
```

## 🔒 Security Tests

### Input Validation

```python
# tests/test_security.py
import pytest
import requests

def test_sql_injection_protection():
    malicious_input = "'; DROP TABLE meetings; --"
    
    response = requests.post('http://localhost:5004/api/meetings', json={
        'title': malicious_input,
        'date': '2024-01-15'
    })
    
    # Should handle malicious input gracefully
    assert response.status_code in [400, 422]
```

### File Upload Security

```python
def test_malicious_file_upload():
    # Test with executable file
    with open('malicious.exe', 'wb') as f:
        f.write(b'MZ\x90\x00')  # PE header
    
    response = requests.post('http://localhost:5004/api/upload', files={
        'file': open('malicious.exe', 'rb')
    })
    
    # Should reject executable files
    assert response.status_code == 400
```

## 🚀 Running Tests

### Backend Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_file_management.py

# Run with coverage
pytest --cov=. --cov-report=html

# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run slow tests
pytest -m slow
```

### Frontend Tests

```bash
# Run all frontend tests
cd frontend
npm test

# Run with coverage
npm test -- --coverage

# Run specific test file
npm test -- App.test.js

# Run in watch mode
npm test -- --watch
```

### E2E Tests

```bash
# Install Playwright
npm install -D @playwright/test
npx playwright install

# Run E2E tests
npx playwright test

# Run specific E2E test
npx playwright test upload.test.js
```

## 📊 Test Coverage

### Coverage Reports

```bash
# Generate HTML coverage report
pytest --cov=. --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Coverage Goals

- **Unit Tests**: 90%+ coverage
- **Integration Tests**: 80%+ coverage
- **API Tests**: 95%+ coverage
- **Frontend Tests**: 85%+ coverage

## 🔄 Continuous Testing

### GitHub Actions

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          pip install -r requirements_microservices.txt
          pip install pytest pytest-cov
      - name: Run tests
        run: pytest --cov=. --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: pytest
        language: system
        pass_filenames: false
        always_run: true
      - id: flake8
        name: flake8
        entry: flake8
        language: system
        files: \.py$
```

## 🐛 Debugging Tests

### Debug Mode

```bash
# Run tests with debug output
pytest -s -v

# Run specific test with debug
pytest -s -v tests/test_file_management.py::test_create_dated_folder

# Run with pdb debugger
pytest --pdb
```

### Test Data

```python
# tests/fixtures.py
import pytest
import tempfile
from pathlib import Path

@pytest.fixture
def temp_video_file():
    """Create a temporary video file for testing."""
    temp_dir = tempfile.mkdtemp()
    video_file = Path(temp_dir) / "test_video.mp4"
    video_file.write_bytes(b"fake video content")
    yield video_file
    # Cleanup
    import shutil
    shutil.rmtree(temp_dir)
```

## 📈 Test Metrics

### Key Metrics

- **Test Coverage**: Percentage of code covered by tests
- **Test Execution Time**: How long tests take to run
- **Test Reliability**: Percentage of tests that pass consistently
- **Bug Detection Rate**: How many bugs are caught by tests

### Monitoring

```python
# tests/conftest.py
import pytest
import time

@pytest.fixture(autouse=True)
def test_timing():
    start_time = time.time()
    yield
    end_time = time.time()
    duration = end_time - start_time
    print(f"Test took {duration:.2f} seconds")
```

## 🎯 Best Practices

### Test Organization

1. **One test per behavior**
2. **Descriptive test names**
3. **Arrange-Act-Assert pattern**
4. **Independent tests**
5. **Fast feedback**

### Test Data Management

1. **Use fixtures for common data**
2. **Clean up after tests**
3. **Use factories for complex objects**
4. **Mock external dependencies**

### Test Maintenance

1. **Keep tests simple**
2. **Update tests when code changes**
3. **Remove obsolete tests**
4. **Regular test reviews**

## 🚨 Common Issues

### Flaky Tests

```python
# Bad: Depends on timing
def test_async_operation():
    start_async_operation()
    time.sleep(1)  # Unreliable
    assert operation_completed()

# Good: Wait for specific condition
def test_async_operation():
    start_async_operation()
    wait_for_condition(lambda: operation_completed(), timeout=10)
    assert operation_completed()
```

### Slow Tests

```python
# Use markers to skip slow tests
@pytest.mark.slow
def test_large_file_processing():
    # This test takes a long time
    pass

# Run without slow tests
pytest -m "not slow"
```

## 📚 Additional Resources

- [pytest Documentation](https://docs.pytest.org/)
- [Jest Documentation](https://jestjs.io/docs/getting-started)
- [Playwright Documentation](https://playwright.dev/)
- [Testing Library Documentation](https://testing-library.com/)
