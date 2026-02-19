# Testing & Quality Assurance Guide

## Overview

This guide covers testing, code quality, and quality assurance practices for the Predictive Infrastructure Intelligence system.

## Table of Contents

1. [Unit Testing](#unit-testing)
2. [Integration Testing](#integration-testing)
3. [Code Quality](#code-quality)
4. [Performance Testing](#performance-testing)
5. [Security Testing](#security-testing)
6. [Continuous Integration](#continuous-integration)

## Unit Testing

### Running Unit Tests

```bash
# Install test dependencies
pip install pytest pytest-cov pytest-mock

# Run all tests
pytest

# Run with coverage report
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_health_scorer.py

# Run specific test
pytest tests/test_health_scorer.py::test_calculate_health_score

# Verbose output
pytest -v

# Show print statements
pytest -s
```

### Writing Unit Tests

```python
# tests/test_health_scorer.py
import pytest
from health_scorer import HealthScorer

class TestHealthScorer:
    """Test suite for HealthScorer class"""
    
    def test_calculate_overall_health_healthy_node(self):
        """Test health score calculation for healthy node"""
        node = {
            'cpu_usage': 30.0,
            'memory_usage': 40.0,
            'temperature': 50.0,
            'network_latency': 10.0,
            'disk_io': 20.0
        }
        
        result = HealthScorer.calculate_overall_health(node)
        
        assert result['status'] == 'healthy'
        assert result['overall_score'] >= 80
        assert len(result['component_scores']) == 5
    
    def test_calculate_overall_health_critical_node(self):
        """Test health score calculation for critical node"""
        node = {
            'cpu_usage': 95.0,
            'memory_usage': 90.0,
            'temperature': 85.0,
            'network_latency': 45.0,
            'disk_io': 85.0
        }
        
        result = HealthScorer.calculate_overall_health(node)
        
        assert result['status'] == 'critical'
        assert result['overall_score'] < 60
    
    @pytest.mark.parametrize("cpu,expected", [
        (30.0, 100),
        (50.0, 100),
        (75.0, 50),
        (85.0, 25),
        (90.0, 0),
    ])
    def test_component_health_cpu(self, cpu, expected):
        """Test CPU health score calculation"""
        score = HealthScorer.calculate_component_health('cpu', cpu)
        assert score == expected
```

## Integration Testing

### Testing API Endpoints

```python
# tests/test_api.py
import pytest
from app import app
import json

@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_endpoint(client):
    """Test health check endpoint"""
    response = client.get('/api/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'status' in data
    assert 'timestamp' in data

def test_stats_endpoint(client):
    """Test stats endpoint"""
    response = client.get('/api/stats')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'nodes_monitored' in data
    assert 'average_health' in data

def test_invalid_endpoint(client):
    """Test invalid endpoint returns 404"""
    response = client.get('/api/nonexistent')
    assert response.status_code == 404
```

### Running Integration Tests

```bash
# Run integration tests
pytest tests/integration/

# Run with database setup
pytest tests/integration/ --setup-show

# Run with specific marker
pytest -m integration
```

## Code Quality

### Code Style

```bash
# Format code with Black
black app.py config.py utils.py

# Check style with Flake8
flake8 app.py --max-line-length=100 --ignore=E501,W503

# Type checking with mypy
mypy app.py --ignore-missing-imports

# Run all quality checks
black --check .
flake8 . --max-line-length=100
mypy . --ignore-missing-imports
```

### Code Review Checklist

- [ ] Code follows PEP 8 style guidelines
- [ ] Functions have docstrings
- [ ] Complex logic has comments
- [ ] Error handling is present
- [ ] No hardcoded values
- [ ] No security vulnerabilities
- [ ] Performance is acceptable
- [ ] Tests are included
- [ ] Documentation updated

### Documentation Standards

```python
def fetch_node_metrics(node_id: str, timeout: int = 30) -> dict:
    """
    Fetch metrics for a specific node.
    
    Args:
        node_id: Unique identifier of the node
        timeout: Request timeout in seconds (default: 30)
    
    Returns:
        Dictionary containing node metrics:
        {
            'node_id': str,
            'cpu_usage': float (0-100),
            'memory_usage': float (0-100),
            'status': str ('healthy'|'degraded'|'critical')
        }
    
    Raises:
        ValueError: If node_id is invalid
        TimeoutError: If request exceeds timeout
        ConnectionError: If unable to connect to node
    
    Example:
        >>> metrics = fetch_node_metrics('node-01')
        >>> print(metrics['cpu_usage'])
        45.3
    """
    pass
```

## Performance Testing

### Benchmarking

```bash
# Install performance testing tools
pip install locust pytest-benchmark memory_profiler

# Run load test
locust -f locustfile.py --host=http://localhost:5000

# Memory profiling
python -m memory_profiler app.py

# CPU profiling
python -m cProfile -s cumulative app.py
```

### Performance Benchmarks

```python
# tests/test_performance.py
import pytest
import time

def test_stats_endpoint_performance(client, benchmark):
    """Benchmark stats endpoint performance"""
    def get_stats():
        response = client.get('/api/stats')
        return response.json
    
    result = benchmark(get_stats)
    assert result['nodes_monitored'] > 0

def test_health_calculation_performance():
    """Benchmark health score calculation"""
    from health_scorer import HealthScorer
    
    node = {
        'cpu_usage': 45.0,
        'memory_usage': 50.0,
        'temperature': 55.0,
        'network_latency': 15.0,
        'disk_io': 30.0
    }
    
    start = time.time()
    for _ in range(1000):
        HealthScorer.calculate_overall_health(node)
    elapsed = time.time() - start
    
    # Should complete 1000 calculations in < 1 second
    assert elapsed < 1.0, f"Performance degradation: {elapsed:.2f}s"
```

## Security Testing

### Input Validation

```bash
# Install security testing tools
pip install bandit safety

# Run security linter
bandit -r . -ll

# Check dependencies for vulnerabilities
safety check

# OWASP dependency check
npm install -g snyk
snyk test
```

### Security Test Cases

```python
# tests/test_security.py
def test_sql_injection_protection(client):
    """Test SQL injection protection"""
    payload = "'; DROP TABLE nodes; --"
    response = client.get(f'/api/nodes?id={payload}')
    assert response.status_code in [400, 422]  # Should reject

def test_xss_protection(client):
    """Test XSS attack prevention"""
    payload = "<script>alert('xss')</script>"
    response = client.post('/api/event', json={'message': payload})
    assert response.status_code in [400, 422]

def test_rate_limiting(client):
    """Test rate limiting"""
    responses = []
    for i in range(101):
        response = client.get('/api/stats')
        responses.append(response.status_code)
    
    # Should have at least one 429 (too many requests)
    assert 429 in responses

def test_cors_validation(client):
    """Test CORS validation"""
    response = client.get(
        '/api/stats',
        headers={'Origin': 'https://malicious.com'}
    )
    # Should have CORS headers for allowed origins only
    assert response.status_code == 200
```

## Continuous Integration

### GitHub Actions Example

```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.9', '3.10', '3.11']
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        pytest --cov=. --cov-report=xml
    
    - name: Code quality checks
      run: |
        black --check .
        flake8 . --max-line-length=100
        mypy . --ignore-missing-imports
    
    - name: Security checks
      run: |
        bandit -r . -ll
        safety check
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        files: ./coverage.xml
```

## Test Coverage Goals

- **Overall**: ≥ 80% code coverage
- **Critical paths**: ≥ 95%
- **Utils/Helpers**: ≥ 85%
- **API endpoints**: ≥ 90%

## Test Execution Strategy

1. **Pre-commit**: Run quick smoke tests (< 30s)
2. **Pull Request**: Run full test suite (< 5min)
3. **Staging**: Run integration tests with real cluster
4. **Production**: Health checks every 5 minutes

---

**Last Updated**: February 17, 2026
**Version**: 1.0
