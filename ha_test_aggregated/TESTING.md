# Fortnite Integration Testing Guide

This document provides comprehensive testing strategies and guidelines for the Fortnite Home Assistant integration.

## 🧪 Testing Framework Overview

The testing framework is built using:
- **pytest**: Main testing framework
- **pytest-asyncio**: Async test support
- **pytest-mock**: Mocking utilities
- **pytest-cov**: Coverage reporting
- **aioresponses**: HTTP response mocking

## 📁 Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Pytest fixtures and configuration
├── unit/                    # Unit tests
│   ├── test_coordinator.py  # Coordinator tests
│   ├── test_sensor.py       # Sensor tests
│   └── test_config_flow.py  # Config flow tests
├── integration/             # Integration tests
│   └── test_api_integration.py  # API integration tests
├── fixtures/                # Test data fixtures
│   └── api_responses.json   # Mock API responses
└── utils/                   # Test utilities
    └── mock_api.py          # API mocking helpers
```

## 🚀 Running Tests

### Quick Start
```bash
# Install test dependencies
pip install -r requirements-test.txt

# Run all tests
python run_tests.py

# Run with coverage
python run_tests.py --coverage

# Run unit tests only
python run_tests.py --unit

# Run integration tests only
python run_tests.py --integration

# Run with verbose output
python run_tests.py --verbose

# Skip slow tests
python run_tests.py --fast
```

### Using pytest directly
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_coordinator.py

# Run specific test
pytest tests/unit/test_coordinator.py::TestFortniteDataUpdateCoordinator::test_init

# Run with coverage
pytest --cov=custom_components.fortnite --cov-report=html

# Run with specific markers
pytest -m unit
pytest -m integration
pytest -m "not slow"
```

## 🧩 Test Categories

### Unit Tests (`@pytest.mark.unit`)
- **Purpose**: Test individual components in isolation
- **Scope**: Single functions, methods, or classes
- **Mocking**: Heavy use of mocks and fixtures
- **Speed**: Fast execution (< 1 second per test)

#### Key Unit Test Areas:
1. **Coordinator Tests**:
   - Rate limiting logic
   - Data transformation
   - Error handling
   - Circuit breaker functionality
   - Exponential backoff

2. **Sensor Tests**:
   - Sensor initialization
   - Data value calculation
   - State attributes
   - Aggregated sensor logic

3. **Config Flow Tests**:
   - Form validation
   - API connection testing
   - Error handling
   - User input validation

### Integration Tests (`@pytest.mark.integration`)
- **Purpose**: Test component interactions and real API behavior
- **Scope**: Multiple components working together
- **Mocking**: Minimal mocking, focus on real behavior
- **Speed**: Slower execution (1-5 seconds per test)

#### Key Integration Test Areas:
1. **API Integration**:
   - Full data flow from API to sensors
   - Rate limiting in real scenarios
   - Error recovery mechanisms
   - Connection pooling

2. **Home Assistant Integration**:
   - Sensor creation and updates
   - Configuration flow
   - Error handling in HA context

## 🔧 Test Fixtures

### Core Fixtures (`conftest.py`)
- `mock_hass`: Mock Home Assistant instance
- `mock_config_entry`: Mock configuration entry
- `coordinator`: Fortnite coordinator instance
- `mock_api_response`: Valid API response data
- `mock_error_response`: API error response
- `mock_rate_limit_response`: Rate limit response

### Usage Example:
```python
def test_sensor_initialization(coordinator, mock_config_entry):
    """Test sensor initialization."""
    sensor = FortniteSensor(
        coordinator,
        mock_config_entry,
        "eliminations",
        SENSOR_TYPES["eliminations"],
        "gamepad",
        "solo"
    )
    assert sensor._sensor_key == "eliminations"
```

## 📊 Test Coverage

### Coverage Goals
- **Overall**: ≥ 80%
- **Critical Paths**: ≥ 95%
- **Error Handling**: ≥ 90%
- **API Integration**: ≥ 85%

### Coverage Reports
```bash
# Generate HTML coverage report
pytest --cov=custom_components.fortnite --cov-report=html

# View coverage report
open htmlcov/index.html
```

## 🐛 Test Data Management

### Mock API Responses
- **Valid Responses**: Complete, realistic API data
- **Error Responses**: Various error scenarios
- **Edge Cases**: Empty data, malformed responses
- **Rate Limiting**: 429 responses with retry headers

### Test Data Validation
- **Input Validation**: Player IDs, API keys
- **Output Validation**: Data transformation accuracy
- **Error Scenarios**: Network failures, API errors
- **Edge Cases**: Empty responses, invalid data

## 🔄 Continuous Integration

### GitHub Actions Workflow
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: |
          pip install -r requirements-test.txt
      - name: Run tests
        run: python run_tests.py --coverage
```

## 🚨 Error Testing

### Common Error Scenarios
1. **Network Errors**:
   - Connection timeouts
   - DNS resolution failures
   - SSL certificate errors

2. **API Errors**:
   - Rate limiting (429)
   - Authentication failures (401)
   - Resource not found (404)
   - Server errors (500)

3. **Data Errors**:
   - Malformed responses
   - Missing required fields
   - Invalid data types
   - Negative values

### Error Recovery Testing
- **Retry Logic**: Exponential backoff
- **Circuit Breaker**: Failure threshold handling
- **Fallback Mechanisms**: Graceful degradation
- **User Feedback**: Clear error messages

## 📈 Performance Testing

### Load Testing
- **Concurrent Requests**: Multiple simultaneous API calls
- **Rate Limiting**: Staying within API limits
- **Memory Usage**: Long-running processes
- **Response Times**: API call performance

### Performance Benchmarks
- **API Response Time**: < 2 seconds
- **Sensor Update Time**: < 5 seconds
- **Memory Usage**: < 50MB per instance
- **CPU Usage**: < 10% during updates

## 🔍 Debugging Tests

### Debug Mode
```bash
# Run with debug output
pytest -v -s --tb=long

# Run specific failing test
pytest tests/unit/test_coordinator.py::TestFortniteDataUpdateCoordinator::test_rate_limiting -v -s

# Use pdb debugger
pytest --pdb tests/unit/test_coordinator.py
```

### Test Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)

def test_with_logging():
    """Test with detailed logging."""
    logger = logging.getLogger(__name__)
    logger.debug("Test starting")
    # Test code here
    logger.debug("Test completed")
```

## 📝 Writing New Tests

### Test Naming Convention
- **Test Classes**: `TestComponentName`
- **Test Methods**: `test_specific_functionality`
- **Test Files**: `test_component.py`

### Test Structure
```python
@pytest.mark.unit
class TestComponentName:
    """Test cases for ComponentName."""

    def test_specific_functionality(self, fixture1, fixture2):
        """Test specific functionality."""
        # Arrange
        expected = "expected_value"
        
        # Act
        result = component.method()
        
        # Assert
        assert result == expected
```

### Best Practices
1. **Arrange-Act-Assert**: Clear test structure
2. **Descriptive Names**: Clear test purpose
3. **Single Responsibility**: One test per scenario
4. **Mock External Dependencies**: Isolate units under test
5. **Test Edge Cases**: Boundary conditions and errors
6. **Maintain Test Data**: Keep fixtures up to date

## 🎯 Test Maintenance

### Regular Tasks
- **Update Fixtures**: Keep test data current
- **Review Coverage**: Ensure comprehensive testing
- **Refactor Tests**: Improve test quality
- **Update Dependencies**: Keep testing tools current

### Test Quality Metrics
- **Test Coverage**: Percentage of code covered
- **Test Execution Time**: Performance benchmarks
- **Test Reliability**: Flaky test identification
- **Test Maintainability**: Code complexity metrics

## 🚀 Advanced Testing

### Property-Based Testing
```python
from hypothesis import given, strategies as st

@given(st.text(min_size=3, max_size=16, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))))
def test_player_id_validation(player_id):
    """Test player ID validation with property-based testing."""
    assert coordinator._validate_player_id(player_id) is True
```

### Mutation Testing
```bash
# Install mutmut
pip install mutmut

# Run mutation testing
mutmut run --paths-to-mutate=custom_components.fortnite
```

### Contract Testing
```python
def test_api_contract():
    """Test API contract compliance."""
    # Verify API response structure
    # Check required fields
    # Validate data types
    # Ensure backward compatibility
```

## 📚 Additional Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-asyncio Documentation](https://pytest-asyncio.readthedocs.io/)
- [Home Assistant Testing](https://developers.home-assistant.io/docs/development_testing/)
- [API Testing Best Practices](https://restfulapi.net/testing-rest-apis/)

## 🤝 Contributing

When adding new tests:
1. Follow the existing test structure
2. Add appropriate test markers
3. Update test coverage goals
4. Document new test scenarios
5. Ensure tests are maintainable

## 📞 Support

For testing-related questions:
- Check existing test examples
- Review test documentation
- Ask in project discussions
- Create test-related issues
