"""
Tests for RepositoryManager.
"""
import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from sierra.package_manager.repository import RepositoryManager, RepositorySource


class TestRepositorySource:
    """Test RepositorySource dataclass."""
    
    def test_repository_source_creation(self):
        """Test creating a repository source."""
        source = RepositorySource(
            name="test-repo",
            url="https://github.com/test/repo",
            branch="main",
            enabled=True,
            priority=10
        )
        assert source.name == "test-repo"
        assert source.url == "https://github.com/test/repo"
        assert source.branch == "main"
    
    def test_repository_source_to_dict(self): 
        """Test converting source to dict."""
        source = RepositorySource(name="test", url="https://test.com")
        data = source.to_dict()
        assert data["name"] == "test"
        assert data["url"] == "https://test.com"
    
    def test_repository_source_from_dict(self):
        """Test creating source from dict."""
        data = {
            "name": "test",
            "url": "https://test.com",
            "branch": "develop",
            "enabled": False,
            "priority": 5
        }
        source = RepositorySource.from_dict(data)
        assert source.name == "test"
        assert source.branch == "develop"
        assert source.enabled is False


class TestRepositoryManager:
    """Test RepositoryManager class."""
    
    def test_repository_manager_init(self, temp_dir, mock_logger):
        """Test initializing repository manager."""
        repo_mgr = RepositoryManager(temp_dir, logger=mock_logger)
        assert repo_mgr.config_dir == temp_dir
        assert (temp_dir / "cache" / "registry").exists()
    
    def test_load_sources_empty(self, temp_dir, mock_logger):
        """Test loading sources when file doesn't exist."""
        repo_mgr = RepositoryManager(temp_dir, logger=mock_logger)
        assert repo_mgr.sources == []
    
    def test_load_sources_with_data(self, temp_dir, mock_logger):
        """Test loading sources from file."""
        # Create sources file
        sources_file = temp_dir / "sources.json"
        sources_data = {
            "sources": [
                {
                    "name": "test-repo",
                    "url": "https://github.com/test/repo",
                    "branch": "main",
                    "enabled": True,
                    "priority": 10
                }
            ]
        }
        sources_file.write_text(json.dumps(sources_data))
        
        repo_mgr = RepositoryManager(temp_dir, logger=mock_logger)
        assert len(repo_mgr.sources) == 1
        assert repo_mgr.sources[0].name == "test-repo"
    
    def test_save_sources(self, temp_dir, mock_logger):
        """Test saving sources to file."""
        repo_mgr = RepositoryManager(temp_dir, logger=mock_logger)
        repo_mgr.sources.append(RepositorySource(
            name="test",
            url="https://test.com"
        ))
        repo_mgr.save_sources()
        
        # Load and verify
        sources_file = temp_dir / "sources.json"
        assert sources_file.exists()
        data = json.loads(sources_file.read_text())
        assert len(data["sources"]) == 1
    
    def test_add_source_valid_url(self, temp_dir, mock_logger):
        """Test adding a valid repository source."""
        repo_mgr = RepositoryManager(temp_dir, logger=mock_logger)
        source = repo_mgr.add_source("https://github.com/test/repo")
        
        assert source.name == "test/repo"
        assert len(repo_mgr.sources) == 1
    
    def test_add_source_invalid_url(self, temp_dir, mock_logger):
        """Test adding invalid URL raises error."""
        repo_mgr = RepositoryManager(temp_dir, logger=mock_logger)
        
        with pytest.raises(ValueError, match="Invalid GitHub URL"):
            repo_mgr.add_source("not-a-github-url")
    
    def test_add_source_duplicate(self, temp_dir, mock_logger):
        """Test adding duplicate source raises error."""
        repo_mgr = RepositoryManager(temp_dir, logger=mock_logger)
        repo_mgr.add_source("https://github.com/test/repo", name="test")
        
        with pytest.raises(ValueError, match="already exists"):
            repo_mgr.add_source("https://github.com/other/repo", name="test")
    
    def test_remove_source(self, temp_dir, mock_logger):
        """Test removing a source."""
        repo_mgr = RepositoryManager(temp_dir, logger=mock_logger)
        repo_mgr.add_source("https://github.com/test/repo", name="test")
        
        assert repo_mgr.remove_source("test") is True
        assert len(repo_mgr.sources) == 0
    
    def test_remove_nonexistent_source(self, temp_dir, mock_logger):
        """Test removing non-existent source."""
        repo_mgr = RepositoryManager(temp_dir, logger=mock_logger)
        assert repo_mgr.remove_source("nonexistent") is False
    
    def test_list_sources(self, temp_dir, mock_logger):
        """Test listing sources sorted by priority."""
        repo_mgr = RepositoryManager(temp_dir, logger=mock_logger)
        repo_mgr.add_source("https://github.com/a/repo", name="a", priority=20)
        repo_mgr.add_source("https://github.com/b/repo", name="b", priority=10)
        
        sources = repo_mgr.list_sources()
        assert sources[0].priority == 10
        assert sources[1].priority == 20
    
    def test_get_source(self, temp_dir, mock_logger):
        """Test getting a specific source."""
        repo_mgr = RepositoryManager(temp_dir, logger=mock_logger)
        repo_mgr.add_source("https://github.com/test/repo", name="test")
        
        source = repo_mgr.get_source("test")
        assert source is not None
        assert source.name == "test"
    
    def test_get_nonexistent_source(self, temp_dir, mock_logger):
        """Test getting non-existent source returns None."""
        repo_mgr = RepositoryManager(temp_dir, logger=mock_logger)
        assert repo_mgr.get_source("nonexistent") is None
    
    @patch('httpx.get')
    def test_fetch_registry(self, mock_get, temp_dir, mock_logger):
        """Test fetching registry from GitHub."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"packages": {}}
        mock_get.return_value = mock_response
        
        repo_mgr = RepositoryManager(temp_dir, logger=mock_logger)
        source = RepositorySource(name="test", url="https://github.com/test/repo")
        
        registry = repo_mgr._fetch_registry(source)
        assert "packages" in registry
    
    @patch('httpx.get')
    def test_update_registry(self, mock_get, temp_dir, mock_logger):
        """Test updating registry."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "packages": {
                "pkg1": {},
                "pkg2": {}
            }
        }
        mock_get.return_value = mock_response
        
        repo_mgr = RepositoryManager(temp_dir, logger=mock_logger)
        repo_mgr.add_source("https://github.com/test/repo", name="test")
        
        results = repo_mgr.update_registry()
        assert "test" in results
        assert results["test"] == 2


@pytest.mark.unit
class TestRepositoryURLParsing:
    """Test GitHub URL parsing."""
    
    def test_parse_https_url(self, temp_dir, mock_logger):
        """Test parsing HTTPS GitHub URL."""
        repo_mgr = RepositoryManager(temp_dir, logger=mock_logger)
        parsed = repo_mgr._parse_github_url("https://github.com/owner/repo")
        assert parsed == ("owner", "repo")
    
    def test_parse_git_url(self, temp_dir, mock_logger):
        """Test parsing .git URL."""
        repo_mgr = RepositoryManager(temp_dir, logger=mock_logger)
        parsed = repo_mgr._parse_github_url("https://github.com/owner/repo.git")
        assert parsed == ("owner", "repo")
    
    def test_parse_invalid_url(self, temp_dir, mock_logger):
        """Test parsing invalid URL returns None."""
        repo_mgr = RepositoryManager(temp_dir, logger=mock_logger)
        parsed = repo_mgr._parse_github_url("not-a-url")
        assert parsed is None
