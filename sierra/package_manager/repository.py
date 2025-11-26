"""
Repository management for Sierra Package Manager.

Handles adding, removing, and updating GitHub repository sources.
"""

import json
import typing
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path

import httpx

from sierra.internal.logger import UniversalLogger


@dataclass
class RepositorySource:
    """Represents a package repository source."""
    
    name: str
    url: str
    branch: str = "main"
    enabled: bool = True
    priority: int = 10
    
    def to_dict(self) -> dict[str, typing.Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> "RepositorySource":
        """Create from dictionary."""
        return cls(**data)


class RepositoryManager:
    """
    Manages GitHub repository sources for package discovery.
    
    Handles:
    - Adding/removing repository sources
    - Updating package registries  
    - Caching registry data
    - Validating repository structure
    """
    
    def __init__(self, config_dir: Path, logger: UniversalLogger | None = None):
        """
        Initialize repository manager.
        
        Parameters
        ----------
        config_dir : Path
            Directory for storing configuration and cache
        logger : UniversalLogger, optional
            Logger instance for tracking operations
        """
        self.logger = logger or UniversalLogger("RepositoryManager")
        self.logger.log("Initializing RepositoryManager", "debug")
        
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.logger.log(f"Config directory: {self.config_dir}", "debug")
        
        self.sources_file = self.config_dir / "sources.json"
        self.cache_dir = self.config_dir / "cache" / "registry"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.logger.log(f"Cache directory: {self.cache_dir}", "debug")
        
        self.sources: list[RepositorySource] = []
        self.load_sources()
        self.logger.log(f"Repository Manager initialized with {len(self.sources)} sources", "info")
    
    def load_sources(self) -> None:
        """Load repository sources from disk."""
        self.logger.log("Loading repository sources from disk", "debug")
        if not self.sources_file.exists():
            self.logger.log("No sources file found, starting with empty list", "debug")
            self.sources = []
            return
        
        try:
            with open(self.sources_file, 'r') as f:
                data = json.load(f)
                self.sources = [
                    RepositorySource.from_dict(s) 
                    for s in data.get('sources', [])
                ]
            self.logger.log(f"Loaded {len(self.sources)} sources from disk", "debug")
        except Exception as e:
            self.logger.log(f"Error loading sources file: {e}", "error")
            self.sources = []
    
    def save_sources(self) -> None:
        """Save repository sources to disk."""
        data = {
            'sources': [s.to_dict() for s in self.sources]
        }
        with open(self.sources_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def add_source(
        self,
        url: str,
        name: str | None = None,
        branch: str = "main",
        priority: int = 10
    ) -> RepositorySource:
        """
        Add a new repository source.
        
        Parameters
        ----------
        url : str
            GitHub repository URL
        name : str, optional
            Custom name for the source
        branch : str
            Git branch to use
        priority : int
            Priority for package resolution (lower = higher priority)
        
        Returns
        -------
        RepositorySource
            The created source
        
        Raises
        ------
        ValueError
            If source already exists or URL is invalid
        """
        self.logger.log(f"Adding new repository source: {url}", "info")
        
        # Parse GitHub URL to extract owner/repo
        parsed = self._parse_github_url(url)
        if not parsed:
            self.logger.log(f"Invalid GitHub URL: {url}", "error")
            raise ValueError(f"Invalid GitHub URL: {url}")
        
        owner, repo = parsed
        self.logger.log(f"Parsed URL - Owner: {owner}, Repo: {repo}", "debug")
        
        # Generate name if not provided
        if not name:
            name = f"{owner}/{repo}"
        
        # Check if already exists
        if any(s.name == name for s in self.sources):
            self.logger.log(f"Source '{name}' already exists", "error")
            raise ValueError(f"Source '{name}' already exists")
        
        # Create and add source
        source = RepositorySource(
            name=name,
            url=url,
            branch=branch,
            priority=priority
        )
        
        self.sources.append(source)
        self.save_sources()
        self.logger.log(f"Successfully added source: {name}", "info")
        
        return source
    
    def remove_source(self, name: str) -> bool:
        """
        Remove a repository source.
        
        Parameters
        ----------
        name : str
            Name of the source to remove
        
        Returns
        -------
        bool
            True if removed, False if not found
        """
        original_count = len(self.sources)
        self.sources = [s for s in self.sources if s.name != name]
        
        if len(self.sources) < original_count:
            self.save_sources()
            # Remove cached registry
            cache_file = self.cache_dir / f"{name}.json"
            if cache_file.exists():
                cache_file.unlink()
            return True
        
        return False
    
    def list_sources(self) -> list[RepositorySource]:
        """
        Get all configured sources.
        
        Returns
        -------
        list[RepositorySource]
            List of repository sources sorted by priority
        """
        return sorted(self.sources, key=lambda s: s.priority)
    
    def get_source(self, name: str) -> RepositorySource | None:
        """
        Get a specific source by name.
        
        Parameters
        ----------
        name : str
            Source name
        
        Returns
        -------
        RepositorySource | None
            The source if found, None otherwise
        """
        for source in self.sources:
            if source.name == name:
                return source
        return None
    
    def update_registry(self, source_name: str | None = None) -> dict[str, int]:
        """
        Update package registries from sources.
        
        Parameters
        ----------
        source_name : str, optional
            Update specific source, or all if None
        
        Returns
        -------
        dict[str, int]
            Map of source name to package count
        """
        self.logger.log(f"Updating registries for: {source_name or 'all sources'}", "info")
        results = {}
        
        sources_to_update = (
            [self.get_source(source_name)] if source_name
            else self.list_sources()
        )
        self.logger.log(f"Updating {len(sources_to_update)} source(s)", "debug")
        
        for source in sources_to_update:
            if source is None or not source.enabled:
                continue
            
            self.logger.log(f"Fetching registry for source: {source.name}", "debug")
            try:
                registry = self._fetch_registry(source)
                self._cache_registry(source.name, registry)
                pkg_count = len(registry.get('packages', {}))
                results[source.name] = pkg_count
                self.logger.log(f"Updated {source.name}: {pkg_count} packages", "info")
            except Exception as e:
                self.logger.log(f"Failed to update {source.name}: {e}", "error")
                results[source.name] = 0
        
        return results
    
    def get_cached_registry(self, source_name: str) -> dict[str, typing.Any] | None:
        """
        Get cached registry for a source.
        
        Parameters
        ----------
        source_name : str
            Source name
        
        Returns
        -------
        dict | None
            Cached registry data or None if not cached
        """
        cache_file = self.cache_dir / f"{source_name}.json"
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r') as f:
                return json.load(f)
        except Exception:
            return None
    
    def _parse_github_url(self, url: str) -> tuple[str, str] | None:
        """
        Parse GitHub URL to extract owner and repo.
        
        Parameters
        ----------
        url : str
            GitHub URL (https://github.com/owner/repo)
        
        Returns
        -------
        tuple[str, str] | None
            (owner, repo) if valid, None otherwise
        """
        import re
        
        # Match https://github.com/owner/repo or github.com/owner/repo
        pattern = r'(?:https?://)?github\.com/([^/]+)/([^/]+?)(?:\.git)?/?$'
        match = re.match(pattern, url.strip())
        
        if match:
            return match.group(1), match.group(2)
        
        return None
    
    def _fetch_registry(self, source: RepositorySource) -> dict[str, typing.Any]:
        """
        Fetch registry.json from GitHub repository.
        
        Parameters
        ----------
        source : RepositorySource
            Repository source
        
        Returns
        -------
        dict
            Registry data
        
        Raises
        ------
        Exception
            If fetch fails
        """
        self.logger.log(f"Fetching registry from GitHub for: {source.name}", "debug")
        owner, repo = self._parse_github_url(source.url) or ("", "")
        
        # GitHub raw content URL
        raw_url = (
            f"https://raw.githubusercontent.com/{owner}/{repo}/"
            f"{source.branch}/registry.json"
        )
        
        self.logger.log(f"Fetching from: {raw_url}", "debug")
        response = httpx.get(raw_url, timeout=10.0)
        response.raise_for_status()
        self.logger.log(f"Successfully fetched registry for: {source.name}", "debug")
        
        return response.json()
    
    def _cache_registry(self, source_name: str, registry: dict) -> None:
        """
        Cache registry data to disk.
        
        Parameters
        ----------
        source_name : str
            Source name
        registry : dict
            Registry data to cache
        """
        cache_file = self.cache_dir / f"{source_name}.json"
        
        # Add cache metadata
        registry['_cached_at'] = datetime.now().isoformat()
        
        with open(cache_file, 'w') as f:
            json.dump(registry, f, indent=2)
