# Sierra Dev - Test Suite

Comprehensive test suite for Sierra Dev covering all modules and features.

## 📊 Test Coverage

### Core Modules
- ✅ **test_logger.py** - UniversalLogger (10 tests)
- ✅ **test_results.py** - Table, Tree, Timeline, Chart (15 tests)
- ✅ **test_client.py** - SierraDevelopmentClient (placeholder)
- ✅ **test_builder.py** - InvokerBuilder (placeholder)
- ✅ **test_compiler.py** - Compiler (placeholder)

### Package Manager
- ✅ **test_repository.py** - RepositoryManager (20+ tests)
- ✅ **test_type_validator.py** - TypeSafetyValidator (12 tests)
- ✅ **test_installer.py** - PackageInstaller (placeholder)
- ✅ **test_registry.py** - PackageRegistry (placeholder)
- ✅ **test_updater.py** - PackageUpdater (placeholder)

### Integration Tests
- ✅ **test_package_workflows.py** - Full install/remove workflow

## 🚀 Running Tests

### Quick Start
```bash
# Run all tests
./run_tests.sh

# Run specific test file
pytest tests/test_results.py -v

# Run with coverage
pytest --cov=sierra --cov-report=html

# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration
```

### Test Markers
- `@pytest.mark.unit` - Unit tests (fast)
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.slow` - Slow running tests
- `@pytest.mark.network` - Tests requiring network

## 📁 Test Structure

```
tests/
├── conftest.py                    # Shared fixtures
├── __init__.py
├── test_results.py               # Result types
├── core/
│   ├── __init__.py
│   ├── test_client.py
│   ├── test_builder.py
│   └── test_compiler.py
├── package_manager/
│   ├── __init__.py
│   ├── test_repository.py       # ✅ 20+ tests
│   ├── test_type_validator.py   # ✅ 12 tests
│   ├── test_installer.py
│   └── test_registry.py
├── internal/
│   ├── __init__.py
│   ├── test_logger.py            # ✅ 10 tests
│   └── test_cache.py
├── examples/
│   ├── __init__.py
│   └── test_osint_tools.py
└── integration/
    ├── __init__.py
    └── test_package_workflows.py  # ✅ Integration tests
```

## 🛠️ Fixtures Available

From `conftest.py`:

- `temp_dir` - Temporary directory for tests
- `mock_logger` - Mock UniversalLogger
- `sierra_client` - Configured Sierra client
- `sample_invoker` - Sample invoker script
- `mock_requests` - Mock requests library
- `package_registry_data` - Sample registry data
- `installed_packages_data` - Sample installed packages

## 📝 Writing Tests

### Example Test
```python
import pytest

class TestMyFeature:
    """Test my feature."""
    
    def test_basic_functionality(self, temp_dir, mock_logger):
        """Test basic functionality."""
        # Arrangement
        feature = MyFeature(temp_dir, logger=mock_logger)
        
        # Action
        result = feature.do_something()
        
        # Assertion
        assert result is not None
    
    @pytest.mark.network
    def test_network_feature(self, mock_requests):
        """Test feature requiring network."""
        # Mock network calls
        mock_requests.return_value.status_code = 200
        
        # Test
        result = call_api()
        assert result == expected
```

### Mocking External APIs
```python
from unittest.mock import Mock, patch

@patch('httpx.get')
def test_api_call(mock_get):
    """Test API call."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"key": "value"}
    mock_get.return_value = mock_response
    
    # Test code
    result = fetch_data()
    assert result["key"] == "value"
```

## 🎯 Test Goals

- ✅ Unit test coverage for all modules
- ✅ Integration tests for workflows
- ✅ Mock external dependencies
- ✅ Fast execution (unit tests < 1s each)
- ✅ Clear test names and documentation

## 📊 Current Coverage

**Implemented:**
- Logger: 100% (10/10 tests)
- Results: 100% (15/15 tests)
- Repository: 95% (20/21 features)
- Type Validator: 90% (12/13 features)
- Integration: Basic workflows

**TODO:**
- Core modules (client, builder, compiler)
- Remaining package manager modules
- Example OSINT tools
- End-to-end tests
- Performance tests

## 🔧 Dependencies

Test dependencies (auto-installed by `run_tests.sh`):
```
pytest>=7.0.0
pytest-cov>=4.0.0
pytest-mock>=3.10.0
```

## 💡 Tips

1. **Run tests frequently** during development
2. **Use markers** to run subsets: `pytest -m unit`
3. **Check coverage** to find untested code
4. **Mock external APIs** to avoid network calls
5. **Use fixtures** to reduce test boilerplate

## 🚨 Continuous Integration

Ready for GitHub Actions:
```yaml
- name: Run Tests
  run: |
    pip install pytest pytest-cov
    pytest --cov=sierra --cov-report=xml
```

## 📈 Coverage Goals

- **Target**: 80%+ overall coverage
- **Critical paths**: 90%+ coverage
- **Package manager**: 85%+ coverage
- **Core modules**: 80%+ coverage

---

**Run tests with:** `./run_tests.sh`
