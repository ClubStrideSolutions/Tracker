# 🧪 Testing Suite Documentation

Comprehensive testing suite for the Intern Hour Tracker application.

## 📋 Table of Contents

- [Overview](#overview)
- [Test Structure](#test-structure)
- [Installation](#installation)
- [Running Tests](#running-tests)
- [Test Coverage](#test-coverage)
- [Performance Testing](#performance-testing)
- [Load Testing](#load-testing)
- [CI/CD Integration](#cicd-integration)
- [Writing Tests](#writing-tests)

## 🎯 Overview

Our testing suite ensures:
- **Stability**: Catch bugs before production
- **Performance**: Maintain optimal response times
- **Scalability**: Handle growing user base
- **Security**: Protect user data and prevent vulnerabilities
- **Reliability**: Consistent behavior across environments

### Test Statistics
- **Unit Tests**: 50+ tests covering core functionality
- **Integration Tests**: 20+ end-to-end workflow tests
- **Performance Tests**: 15+ benchmarks and scalability tests
- **Code Coverage Target**: 85%+

## 📁 Test Structure

```
tests/
├── conftest.py                 # Pytest fixtures and configuration
├── __init__.py                 # Test package initialization
├── unit/                       # Unit tests (isolated component tests)
│   ├── test_database.py        # Database operations
│   └── test_auth.py            # Authentication module
├── integration/                # Integration tests (workflow tests)
│   └── test_workflows.py       # End-to-end user workflows
├── performance/                # Performance and load tests
│   └── test_performance.py     # Performance benchmarks
├── load_test.py               # Locust load testing scenarios
└── README.md                  # This file
```

## 🔧 Installation

### 1. Install Development Dependencies

```bash
# Using pip
pip install -r requirements-dev.txt

# Or install specific test tools
pip install pytest pytest-cov pytest-xdist locust
```

### 2. Verify Installation

```bash
pytest --version
```

## 🚀 Running Tests

### Run All Tests

```bash
# Run complete test suite
pytest

# Run with verbose output
pytest -v

# Run with detailed output and show print statements
pytest -v -s
```

### Run Specific Test Categories

```bash
# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# Performance tests only
pytest tests/performance/

# Specific test file
pytest tests/unit/test_database.py

# Specific test class
pytest tests/unit/test_database.py::TestUserManagement

# Specific test function
pytest tests/unit/test_database.py::TestUserManagement::test_create_account_request
```

### Run Tests in Parallel

```bash
# Run tests across multiple CPU cores
pytest -n auto

# Run on specific number of cores
pytest -n 4
```

### Run Tests with Timeout

```bash
# Set timeout for slow tests
pytest --timeout=300  # 5 minutes
```

## 📊 Test Coverage

### Generate Coverage Report

```bash
# Run tests with coverage
pytest --cov=. --cov-report=html --cov-report=term

# View HTML report
# Open htmlcov/index.html in browser

# Generate XML report (for CI/CD)
pytest --cov=. --cov-report=xml
```

### Coverage Goals

| Component | Target Coverage |
|-----------|----------------|
| database.py | 90%+ |
| auth.py | 90%+ |
| app.py | 75%+ |
| lead_intern_portal.py | 75%+ |
| **Overall** | **85%+** |

### View Coverage by Module

```bash
pytest --cov=database --cov-report=term-missing
```

## ⚡ Performance Testing

### Run Performance Benchmarks

```bash
# Run all performance tests
pytest tests/performance/ -v

# Run with performance profiling
pytest tests/performance/ --profile

# Run specific performance test
pytest tests/performance/test_performance.py::TestDatabasePerformance::test_bulk_user_creation_performance -v
```

### Performance Benchmarks

Our system maintains these performance targets:

| Operation | Target | Benchmark |
|-----------|--------|-----------|
| User Authentication | < 100ms | ✅ ~50ms |
| Create Account Request | < 50ms | ✅ ~30ms |
| Log Hours Entry | < 50ms | ✅ ~25ms |
| Query 500 Hours | < 500ms | ✅ ~200ms |
| Submit Deliverable | < 100ms | ✅ ~60ms |
| Complex Query (JOIN) | < 50ms | ✅ ~30ms |

### Continuous Benchmarking

Monitor performance over time:

```bash
# Save benchmark results
pytest tests/performance/ --benchmark-save=current

# Compare with previous run
pytest tests/performance/ --benchmark-compare=0001
```

## 🔥 Load Testing

### Using Locust

Load testing simulates real-world usage with multiple concurrent users.

#### 1. Start Locust

```bash
# Start Locust web interface
locust -f tests/load_test.py

# Start with specific host
locust -f tests/load_test.py --host=http://localhost:8501
```

#### 2. Access Web Interface

Open browser to `http://localhost:8089`

#### 3. Configure Load Test

- **Number of users**: Start with 10, increase gradually
- **Spawn rate**: 1-2 users per second
- **Run time**: 5-10 minutes for initial tests

#### 4. Load Test Scenarios

```bash
# Test with Core Interns
locust -f tests/load_test.py InternTrackerUser

# Test with Lead Interns
locust -f tests/load_test.py LeadInternUser

# Test with Admins
locust -f tests/load_test.py AdminUser

# Stress test
locust -f tests/load_test.py StressTestUser --users 100 --spawn-rate 10
```

### Headless Load Testing

```bash
# Run without web interface
locust -f tests/load_test.py --headless --users 50 --spawn-rate 5 --run-time 5m --host=http://localhost:8501
```

### Expected Load Test Results

| Metric | Target | Notes |
|--------|--------|-------|
| Response Time (median) | < 500ms | Under normal load |
| Response Time (95th percentile) | < 2s | Under normal load |
| Error Rate | < 1% | Under normal load |
| Max Users Supported | 100+ | Concurrent users |
| Requests per Second | 50+ | Sustained throughput |

## 🔄 CI/CD Integration

### GitHub Actions

Our CI/CD pipeline runs automatically on:
- Push to `main` or `develop` branches
- Pull requests
- Manual workflow dispatch

#### Pipeline Stages

1. **Test** (Python 3.9, 3.10, 3.11, 3.12)
   - Unit tests
   - Integration tests
   - Performance tests
   - Coverage report

2. **Lint**
   - flake8 (code quality)
   - black (formatting)
   - isort (import ordering)
   - mypy (type checking)

3. **Security**
   - bandit (security vulnerabilities)
   - safety (dependency vulnerabilities)

4. **Docker**
   - Build Docker image
   - Test containerization

5. **Performance Benchmark**
   - Run benchmarks
   - Store results as artifacts

### Running CI/CD Locally

```bash
# Install act (GitHub Actions local runner)
# https://github.com/nektos/act

# Run GitHub Actions locally
act -j test
```

### Badge Integration

Add to your README.md:

```markdown
![Tests](https://github.com/your-org/tracker/workflows/Test%20Suite/badge.svg)
![Coverage](https://codecov.io/gh/your-org/tracker/branch/main/graph/badge.svg)
```

## ✍️ Writing Tests

### Test Structure Guidelines

```python
import pytest

class TestFeatureName:
    """Test suite for specific feature"""

    def test_basic_functionality(self, fixture_name):
        """Test basic happy path"""
        # Arrange
        expected_result = True

        # Act
        result = function_under_test()

        # Assert
        assert result == expected_result

    def test_edge_case(self, fixture_name):
        """Test edge cases and error conditions"""
        with pytest.raises(ValueError):
            function_that_should_fail()

    def test_with_mock(self, mocker):
        """Test with mocked dependencies"""
        mock_db = mocker.patch('database.Database')
        # Test with mock...
```

### Using Fixtures

```python
def test_with_temp_database(temp_db):
    """Use temporary database fixture"""
    result = temp_db.create_account_request(...)
    assert result is True

def test_with_populated_db(db_with_users):
    """Use database with test users"""
    users = db_with_users.get_all_users()
    assert len(users) >= 2
```

### Naming Conventions

- Test files: `test_*.py`
- Test classes: `Test*`
- Test functions: `test_*`
- Be descriptive: `test_authentication_fails_with_invalid_password`

### Best Practices

1. **Isolation**: Each test should be independent
2. **Speed**: Unit tests should be fast (< 1s)
3. **Clarity**: Test names should describe what they test
4. **Coverage**: Test both happy paths and edge cases
5. **Fixtures**: Use fixtures to avoid repetition
6. **Assertions**: One logical assertion per test
7. **Documentation**: Add docstrings to complex tests

### Performance Test Guidelines

```python
def test_performance_metric():
    """Test should complete within time limit"""
    import time

    start = time.time()
    # Operation under test
    result = slow_operation()
    duration = time.time() - start

    assert duration < 1.0  # Should complete in < 1 second
    assert result is not None
```

## 🐛 Debugging Tests

### Run Failed Tests Only

```bash
# Run only tests that failed last time
pytest --lf

# Run failed tests first, then others
pytest --ff
```

### Debug with Print Statements

```bash
# Show print output
pytest -v -s

# Show local variables on failure
pytest -l
```

### Use Pytest Debugger

```bash
# Drop into debugger on failure
pytest --pdb

# Drop into debugger at start of test
pytest --trace
```

### Verbose Output

```bash
# Maximum verbosity
pytest -vv

# Show full diff on assertion failure
pytest -vv --tb=long
```

## 📈 Monitoring Test Health

### Key Metrics to Track

1. **Test Execution Time**
   - Total test suite runtime
   - Slowest tests
   - Trend over time

2. **Test Coverage**
   - Line coverage percentage
   - Branch coverage
   - Uncovered code

3. **Test Stability**
   - Flaky test detection
   - Failure rates
   - Success trends

4. **Performance Benchmarks**
   - Response time trends
   - Throughput metrics
   - Resource usage

### Generate Test Report

```bash
# Generate HTML test report
pytest --html=report.html --self-contained-html

# Generate JUnit XML (for CI/CD)
pytest --junitxml=junit.xml
```

## 🎯 Test Quality Checklist

- [ ] All tests pass consistently
- [ ] Code coverage ≥ 85%
- [ ] No test takes > 5 seconds (unit tests)
- [ ] Performance benchmarks meet targets
- [ ] Load tests pass with 50+ concurrent users
- [ ] Security scans show no vulnerabilities
- [ ] Docker build succeeds
- [ ] CI/CD pipeline passes
- [ ] Documentation is up to date

## 🤝 Contributing

When contributing new features:

1. Write tests first (TDD approach recommended)
2. Ensure all existing tests pass
3. Add tests for new functionality
4. Maintain or improve code coverage
5. Update documentation as needed
6. Run full test suite before submitting PR

## 📞 Support

For testing issues:
- Check test logs: `pytest -v --tb=short`
- Review fixtures: `pytest --fixtures`
- Consult pytest docs: https://docs.pytest.org/

---

**Remember**: Tests are your safety net. Keep them fast, reliable, and comprehensive! 🚀