"""
Shared fixtures and utilities for Sierra Dev tests.
"""
import pytest
import pathlib
import tempfile
import shutil
from unittest.mock import Mock, MagicMock

import sierra
from sierra.internal.logger import UniversalLogger, LogLevel


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    tmpdir = tempfile.mkdtemp()
    yield pathlib.Path(tmpdir)
    shutil.rmtree(tmpdir)


@pytest.fixture
def mock_logger():
    """Create a mock logger."""
    logger = Mock(spec=UniversalLogger)
    logger.log = Mock()
    return logger


@pytest.fixture
def sierra_client(temp_dir, mock_logger):
    """Create a Sierra client for testing."""
    # Create test environment structure
    env_path = temp_dir / "test_env"
    env_path.mkdir()
    (env_path / "scripts").mkdir()
    (env_path / "invokers").mkdir()
    (env_path / "config").mkdir()
    (env_path / "venv").mkdir()
    (env_path / "venv" / "bin").mkdir()
    
    # Create minimal config.yaml
    config_file = env_path / "config" / "config.yaml"
    config_file.write_text("invokers: {}")
    
    client = sierra.SierraDevelopmentClient(
        environment_path=temp_dir,
        environment_name="test_env",
        logger=mock_logger
    )
    
    return client


@pytest.fixture
def sample_invoker():
    """Create a sample invoker for testing."""
    invoker = sierra.InvokerScript(
        name="test-invoker",
        description="Test invoker for unit tests"
    )
    
    @invoker.entry_point
    def run(
        param1: sierra.Param[
            str | None,
            sierra.SierraOption(
                description="Test parameter",
                mandatory="MANDATORY"
            )
        ]
    ) -> None:
        """Test entry point."""
        print(f"Test: {param1}")
    
    return invoker


@pytest.fixture
def mock_requests(monkeypatch):
    """Mock requests library for network tests."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {}
    mock_response.text = ""
    mock_response.headers = {}
    
    mock_get = Mock(return_value=mock_response)
    monkeypatch.setattr("requests.get", mock_get)
    
    return mock_get


@pytest.fixture
def package_registry_data():
    """Sample package registry data."""
    return {
        "version": "1.0.0",
        "updated": "2024-11-26T10:00:00Z",
        "packages": {
            "test-package": {
                "name": "test-package",
                "version": "1.0.0",
                "description": "Test package",
                "author": "Test Author",
                "tags": ["test", "example"],
                "category": "testing",
                "path": "invokers/test-package"
            }
        }
    }


@pytest.fixture  
def installed_packages_data():
    """Sample installed packages data."""
    return {
        "packages": {
            "test-package": {
                "version": "1.0.0",
                "installed_date": "2024-11-26T10:00:00",
                "source": "test-repo",
                "path": "/test/path/test_package.py",
                "metadata": {
                    "description": "Test package",
                    "author": "Test Author",
                    "tags": ["test"]
                }
            }
        }
    }


# Helper functions

def create_mock_script(content: str, path: pathlib.Path) -> None:
    """Create a mock Python script file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def create_test_invoker_script(name: str = "test", has_types: bool = True) -> str:
    """Generate a test invoker script."""
    if has_types:
        return f'''
import sierra

invoker = sierra.InvokerScript(name="{name}", description="Test")

@invoker.entry_point
def run(param: str) -> None:
    """Test function."""
    print(param)

def load(client: sierra.SierraDevelopmentClient) -> None:
    client.load_invoker(invoker)
'''
    else:
        return f'''
import sierra

invoker = sierra.InvokerScript(name="{name}", description="Test")

@invoker.entry_point
def run(param):  # Missing type annotation
    print(param)

def load(client):
    client.load_invoker(invoker)
'''
