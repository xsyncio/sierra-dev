"""
Package registry for Sierra Package Manager.

Handles package metadata, search, and discovery.
"""

import typing
from dataclasses import dataclass
from pathlib import Path

from sierra.internal.logger import UniversalLogger


@dataclass
class PackageInfo:
    """Package metadata information."""
    
    name: str
    version: str
    description: str
    author: str = ""
    tags: list[str] = None
    category: str = ""
    source: str = ""
    path: str = ""
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
    
    def matches_query(self, query: str) -> bool:
        """Check if package matches search query."""
        query_lower = query.lower()
        
        # Search in name
        if query_lower in self.name.lower():
            return True
        
        # Search in description
        if query_lower in self.description.lower():
            return True
        
        # Search in tags
        for tag in self.tags:
            if query_lower in tag.lower():
                return True
        
        return False


class PackageRegistry:
    """
    Central registry for discovering and querying packages.
    
    Aggregates package information from all sources.
    """
    
    def __init__(self, repo_manager, logger: UniversalLogger | None = None):
        """
        Initialize package registry.
        
        Parameters
        ----------
        repo_manager : RepositoryManager
            Repository manager instance
        logger : UniversalLogger, optional
            Logger instance for tracking operations
        """
        self.logger = logger or UniversalLogger("PackageRegistry")
        self.logger.log("Initializing PackageRegistry", "debug")
        
        self.repo_manager = repo_manager
        self._packages: dict[str, PackageInfo] = {}
        self.logger.log("Package Registry initialized", "info")
    
    def refresh(self) -> None:
        """Refresh package list from all sources."""
        self.logger.log("Refreshing package registry from all sources", "debug")
        self._packages = {}
        
        for source in self.repo_manager.list_sources():
            if not source.enabled:
                continue
            
            self.logger.log(f"Loading packages from source: {source.name}", "debug")
            registry = self.repo_manager.get_cached_registry(source.name)
            if not registry:
                continue
            
            packages = registry.get('packages', {})
            for pkg_name, pkg_data in packages.items():
                # Create PackageInfo
                info = PackageInfo(
                    name=pkg_data.get('name', pkg_name),
                    version=pkg_data.get('version', '0.0.0'),
                    description=pkg_data.get('description', ''),
                    author=pkg_data.get('author', ''),
                    tags=pkg_data.get('tags', []),
                    category=pkg_data.get('category', ''),
                    source=source.name,
                    path=pkg_data.get('path', '')
                )
                
                # Store package (later sources override earlier ones)
                self._packages[pkg_name] = info
        
        self.logger.log(f"Registry refreshed with {len(self._packages)} total packages", "info")
    
    def search(
        self,
        query: str = "",
        tag: str | None = None,
        category: str | None = None,
        source: str | None = None
    ) -> list[PackageInfo]:
        """
        Search for packages.
        
        Parameters
        ----------
        query : str
            Search query string
        tag : str, optional
            Filter by tag
        category : str, optional
            Filter by category
        source : str, optional
            Filter by source
        
        Returns
        -------
        list[PackageInfo]
            Matching packages
        """
        self.logger.log(f"Searching packages: query='{query}', tag={tag}, category={category}, source={source}", "debug")
        results = []
        
        for pkg in self._packages.values():
            # Apply filters
            if source and pkg.source != source:
                continue
            
            if category and pkg.category != category:
                continue
            
            if tag and tag not in pkg.tags:
                continue
            
            # Apply query
            if query and not pkg.matches_query(query):
                continue
            
            results.append(pkg)
        
        self.logger.log(f"Search found {len(results)} matching packages", "debug")
        return results
    
    def get_package(self, name: str) -> PackageInfo | None:
        """
        Get package by name.
        
        Parameters
        ----------
        name : str
            Package name
        
        Returns
        -------
        PackageInfo | None
            Package info if found
        """
        return self._packages.get(name)
    
    def list_all(self) -> list[PackageInfo]:
        """Get all packages."""
        return list(self._packages.values())
    
    def list_by_category(self) -> dict[str, list[PackageInfo]]:
        """Group packages by category."""
        categories: dict[str, list[PackageInfo]] = {}
        
        for pkg in self._packages.values():
            cat = pkg.category or "Uncategorized"
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(pkg)
        
        return categories
    
    def get_stats(self) -> dict[str, int]:
        """Get registry statistics."""
        return {
            'total_packages': len(self._packages),
            'sources': len(set(p.source for p in self._packages.values())),
            'categories': len(set(p.category for p in self._packages.values() if p.category))
        }
