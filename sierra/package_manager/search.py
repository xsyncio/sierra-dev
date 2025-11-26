"""
Package search functionality.

Provides search with formatting and display.
"""

import typing
from sierra.package_manager.registry import PackageInfo
from sierra.internal.logger import UniversalLogger


class PackageSearch:
    """Search and format package results."""
    
    def __init__(self, registry, logger: UniversalLogger | None = None):
        """
        Initialize search.
        
        Parameters
        ----------
        registry : PackageRegistry
            Package registry instance
        logger : UniversalLogger, optional
            Logger instance
        """
        self.logger = logger or UniversalLogger("PackageSearch")
        self.registry = registry
    
    def search_and_format(
        self,
        query: str = "",
        **filters
    ) -> str:
        """
        Search and format results for display.
        
        Parameters
        ----------
        query : str
            Search query
        **filters
            Additional filters (tag, category, source)
        
        Returns
        -------
        str
            Formatted search results
        """
        results = self.registry.search(query, **filters)
        
        if not results:
            return f"\n🔍 No packages found matching '{query}'\n"
        
        lines = [f"\n🔍 Search results for '{query}':\n"]
        
        for pkg in results:
            lines.append(self._format_package_summary(pkg))
            lines.append("")
        
        lines.append(f"{len(results)} package(s) found\n")
        
        return "\n".join(lines)
    
    def format_package_info(self, pkg: PackageInfo, detailed: bool = True) -> str:
        """
        Format detailed package information.
        
        Parameters
        ----------
        pkg : PackageInfo
            Package to format
        detailed : bool
            Include detailed information
        
        Returns
        -------
        str
            Formatted package information
        """
        lines = [f"\n📦 {pkg.name} v{pkg.version}\n"]
        
        if detailed:
            lines.append("DESCRIPTION:")
            lines.append(f"  {pkg.description}\n")
            
            if pkg.author:
                lines.append(f"AUTHOR: {pkg.author}")
            
            if pkg.category:
                lines.append(f"CATEGORY: {pkg.category}")
            
            lines.append(f"SOURCE: {pkg.source}")
            
            if pkg.tags:
                lines.append(f"\nTAGS:")
                lines.append(f"  {', '.join(pkg.tags)}")
            
            lines.append(f"\nINSTALLATION:")
            lines.append(f"  sierra install {pkg.name}")
        
        return "\n".join(lines) + "\n"
    
    def _format_package_summary(self, pkg: PackageInfo) -> str:
        """Format package as one-line summary."""
        tags_str = f" [{', '.join(pkg.tags[:3])}]" if pkg.tags else ""
        return (
            f"📦 {pkg.name} ({pkg.source})\n"
            f"   Version: {pkg.version}\n"
            f"   {pkg.description}{tags_str}"
        )
