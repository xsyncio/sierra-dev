"""
Package update functionality for Sierra Package Manager.

Handles checking for updates and updating installed packages.
"""

import typing
from pathlib import Path

from sierra.package_manager.registry import PackageInfo
from sierra.internal.logger import UniversalLogger


class PackageUpdater:
    """
    Handles package update operations.
    
    Checks for available updates and performs upgrades.
    """
    
    def __init__(self, installer, registry, logger: UniversalLogger | None = None):
        """
        Initialize updater.
        
        Parameters
        ----------
        installer : PackageInstaller
            Package installer instance
        registry : PackageRegistry
            Package registry instance
        logger : UniversalLogger, optional
            Logger instance for tracking operations
        """
        self.logger = logger or UniversalLogger("PackageUpdater")
        self.logger.log("Initializing PackageUpdater", "debug")
        
        self.installer = installer
        self.registry = registry
        self.logger.log("Package Updater initialized", "info")
    
    def check_updates(self) -> list[dict[str, str]]:
        """
        Check for available updates.
        
        Returns
        -------
        list[dict]
            List of packages with updates available
            Each dict has: name, current_version, available_version
        """
        self.registry.refresh()
        updates = []
        
        for pkg_name, pkg_data in self.installer.installed.items():
            current_version = pkg_data.get('version', '0.0.0')
            
            # Get latest version from registry
            pkg_info = self.registry.get_package(pkg_name)
            if not pkg_info:
                continue
            
            available_version = pkg_info.version
            
            # Compare versions (simple string comparison for now)
            if available_version != current_version:
                updates.append({
                    'name': pkg_name,
                    'current_version': current_version,
                    'available_version': available_version,
                    'source': pkg_info.source
                })
        
        return updates
    
    def update_package(self, package_name: str) -> bool:
        """
        Update a single package.
        
        Parameters
        ----------
        package_name : str
            Package to update
        
        Returns
        -------
        bool
            True if successful
        
        Raises
        ------
        ValueError
            If package not installed or no update available
        """
        if not self.installer.is_installed(package_name):
            raise ValueError(f"Package '{package_name}' is not installed")
        
        # Check if update available
        updates = self.check_updates()
        pkg_update = next((u for u in updates if u['name'] == package_name), None)
        
        if not pkg_update:
            raise ValueError(f"No update available for '{package_name}'")
        
        # Perform update (reinstall with force=True)
        return self.installer.install(package_name, self.registry, force=True)
    
    def update_all(self) -> dict[str, bool]:
        """
        Update all packages that have available updates.
        
        Returns
        -------
        dict[str, bool]
            Map of package name to success status
        """
        updates = self.check_updates()
        results = {}
        
        for update in updates:
            try:
                self.update_package(update['name'])
                results[update['name']] = True
            except Exception:
                results[update['name']] = False
        
        return results
