"""
Integration tests for Sierra package manager workflow.
"""
import pytest
import json
from pathlib import Path
from unittest.mock import patch, Mock

from sierra.package_manager import RepositoryManager, PackageRegistry, PackageInstaller


@pytest.mark.integration
class TestPackageManagerWorkflow:
    """Test complete package manager workflows."""
    
    @patch('httpx.get')
    def test_full_install_workflow(self, mock_get, temp_dir, mock_logger, package_registry_data):
        """Test complete package install workflow."""
        # Setup mock responses
        mock_registry_response = Mock()
        mock_registry_response.status_code = 200
        mock_registry_response.json.return_value = package_registry_data
        
        mock_script_response = Mock()
        mock_script_response.status_code = 200
        mock_script_response.text = '''
import sierra
invoker = sierra.InvokerScript(name="test", description="Test")
@invoker.entry_point
def run(param: str) -> None:
    print(param)
def load(client: sierra.SierraDevelopmentClient) -> None:
    client.load_invoker(invoker)
'''
        
        mock_get.side_effect = [mock_registry_response, mock_script_response]
        
        # Setup
        config_dir = temp_dir / "config"
        env_path = temp_dir / "env"
        env_path.mkdir()
        
        # Initialize components
        repo_mgr = RepositoryManager(config_dir, logger=mock_logger)
        repo_mgr.add_source("https://github.com/test/repo", name="test-repo")
        
        # Update registry
        results = repo_mgr.update_registry()
        assert "test-repo" in results
        
        # Get registry
        registry = PackageRegistry(repo_mgr, logger=mock_logger)
        registry.refresh()
        
        # Install package
        installer = PackageInstaller(repo_mgr, env_path, logger=mock_logger)
        success = installer.install("test-package", registry, skip_validation=True)
        
        assert success is True
        assert installer.is_installed("test-package")
    
    def test_install_remove_workflow(self, temp_dir, mock_logger):
        """Test installing and then removing a package."""
        config_dir = temp_dir / "config"
        env_path = temp_dir / "env"
        env_path.mkdir()
        (env_path / "scripts").mkdir()
        
        repo_mgr = RepositoryManager(config_dir, logger=mock_logger)
        installer = PackageInstaller(repo_mgr, env_path, logger=mock_logger)
        
        # Manually add to installed registry
        installer.installed["test-pkg"] = {
            "version": "1.0.0",
            "installed_date": "2024-11-26",
            "source": "test",
            "path": str(env_path / "scripts" / "test_pkg.py"),
            "metadata": {}
        }
        
        # Create the script file
        script_path = env_path / "scripts" / "test_pkg.py"
        script_path.write_text("# test")
        
        installer.save_installed()
        
        # Remove package
        success = installer.remove("test-pkg")
        assert success is True
        assert not installer.is_installed("test-pkg")
        assert not script_path.exists()


@pytest.mark.integration  
class TestCLIIntegration:
    """Test CLI command integration."""
    
    def test_build_check_workflow(self, temp_dir, mock_logger):
        """Test build and check workflow."""
        # This would test the full build process
        # Currently a placeholder for integration testing
        pass


@pytest.mark.integration
class TestEndToEnd:
    """End-to-end tests."""
    
    def test_complete_osint_tool_workflow(self, temp_dir):
        """Test complete workflow from script to execution."""
        # This would test creating a script, building, and running
        # Currently a placeholder
        pass
