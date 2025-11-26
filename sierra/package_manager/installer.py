"""
Package installer for Sierra Package Manager.

Handles installing, updating, and removing packages.
"""

import json
import shutil
import typing
from datetime import datetime
from pathlib import Path

import httpx

from sierra.internal.logger import UniversalLogger


class PackageInstaller:
    """
    Handles package installation and management.
    
    Downloads packages from GitHub and installs them
    into the Sierra environment.
    """
    
    def __init__(self, repo_manager, environment_path: Path, logger: UniversalLogger | None = None):
        """
        Initialize installer.
        
        Parameters
        ----------
        repo_manager : RepositoryManager
            Repository manager instance
        environment_path : Path
            Path to Sierra environment
        logger : UniversalLogger, optional
            Logger instance for tracking operations
        """
        self.logger = logger or UniversalLogger("PackageInstaller")
        self.logger.log("Initializing PackageInstaller", "debug")
        
        self.repo_manager = repo_manager
        self.env_path = Path(environment_path)
        self.scripts_path = self.env_path / "scripts"
        self.scripts_path.mkdir(parents=True, exist_ok=True)
        self.logger.log(f"Environment path: {self.env_path}", "debug")
        self.logger.log(f"Scripts path: {self.scripts_path}", "debug")
        
        self.installed_file = self.repo_manager.config_dir / "installed.json"
        self.installed: dict[str, dict] = {}
        self.load_installed()
        self.logger.log(f"Package Installer initialized. {len(self.installed)} packages installed", "info")
    
    def load_installed(self) -> None:
        """Load installed packages registry."""
        self.logger.log("Loading installed packages registry", "debug")
        if not self.installed_file.exists():
            self.logger.log("No installed packages file found", "debug")
            self.installed = {}
            return
        
        try:
            with open(self.installed_file, 'r') as f:
                data = json.load(f)
                self.installed = data.get('packages', {})
            self.logger.log(f"Loaded {len(self.installed)} installed packages", "debug")
        except Exception as e:
            self.logger.log(f"Error loading installed packages: {e}", "error")
            self.installed = {}
    
    def save_installed(self) -> None:
        """Save installed packages registry."""
        data = {'packages': self.installed}
        with open(self.installed_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def is_installed(self, package_name: str) -> bool:
        """Check if package is installed."""
        return package_name in self.installed
    
    def get_installed_version(self, package_name: str) -> str | None:
        """Get installed version of a package."""
        pkg_data = self.installed.get(package_name)
        if pkg_data:
            return pkg_data.get('version')
        return None
    
    def install(
        self,
        package_name: str,
        registry,
        force: bool = False,
        skip_validation: bool = False
    ) -> bool:
        """
        Install a package.
        
        Parameters
        ----------
        package_name : str
            Name of package to install
        registry : PackageRegistry
            Package registry
        force : bool
            Force reinstall if already installed
        skip_validation : bool
            Skip type safety validation
        
        Returns
        -------
        bool
            True if successful
        
        Raises
        ------
        ValueError
            If package not found or validation fails
        Exception
            If installation fails
        """
        self.logger.log(f"Attempting to install package: {package_name}", "info")
        
        # Check if already installed
        if self.is_installed(package_name) and not force:
            self.logger.log(f"Package '{package_name}' is already installed", "warning")
            raise ValueError(f"Package '{package_name}' is already installed")
        
        # Get package info
        pkg_info = registry.get_package(package_name)
        if not pkg_info:
            self.logger.log(f"Package '{package_name}' not found in registry", "error")
            raise ValueError(f"Package '{package_name}' not found")
        
        self.logger.log(f"Found package: {pkg_info.name} v{pkg_info.version}", "debug")
        
        # Get source
        source = self.repo_manager.get_source(pkg_info.source)
        if not source:
            self.logger.log(f"Source '{pkg_info.source}' not found", "error")
            raise ValueError(f"Source '{pkg_info.source}' not found")
        
        # Download package file
        owner, repo = self._parse_github_url(source.url)
        file_url = (
            f"https://raw.githubusercontent.com/{owner}/{repo}/"
            f"{source.branch}/{pkg_info.path}/invoker.py"
        )
        
        self.logger.log(f"Downloading from: {file_url}", "debug")
        response = httpx.get(file_url, timeout=30.0)
        response.raise_for_status()
        self.logger.log(f"Downloaded {len(response.text)} bytes", "debug")
        
        # Convert package name to valid Python module name
        safe_name = package_name.replace('-', '_')
        script_file = self.scripts_path / f"{safe_name}.py"
        
        # Save temporarily for validation
        temp_file = script_file.with_suffix('.tmp')
        temp_file.write_text(response.text)
        self.logger.log(f"Saved temporary file: {temp_file}", "debug")
        
        # Type safety validation
        if not skip_validation:
            self.logger.log("Running type safety validation", "debug")
            from sierra.package_manager.type_validator import validate_invoker_script
            
            is_valid, report = validate_invoker_script(temp_file)
            
            if not is_valid:
                temp_file.unlink()  # Clean up
                self.logger.log(f"Type safety validation failed for {package_name}", "error")
                raise ValueError(f"Type safety validation failed:\n{report}")
            
            self.logger.log("Type safety validation passed", "debug")
        else:
            self.logger.log("Skipped type safety validation", "warning")
        
        # Move to final location
        if script_file.exists():
            script_file.unlink()
        temp_file.rename(script_file)
        self.logger.log(f"Installed script to: {script_file}", "debug")
        
        # Record installation
        self.installed[package_name] = {
            'version': pkg_info.version,
            'installed_date': datetime.now().isoformat(),
            'source': pkg_info.source,
            'path': str(script_file),
            'metadata': {
                'description': pkg_info.description,
                'author': pkg_info.author,
                'tags': pkg_info.tags
            }
        }
        
        self.save_installed()
        self.logger.log(f"Successfully installed {package_name} v{pkg_info.version}", "info")
        
        return True
    
    def remove(self, package_name: str) -> bool:
        """
        Remove an installed package.
        
        Parameters
        ----------
        package_name : str
            Package to remove
        
        Returns
        -------
        bool
            True if successful
        
        Raises
        ------
        ValueError
            If package not installed
        """
        self.logger.log(f"Attempting to remove package: {package_name}", "info")
        
        if not self.is_installed(package_name):
            self.logger.log(f"Package '{package_name}' is not installed", "error")
            raise ValueError(f"Package '{package_name}' is not installed")
        
        # Get package data
        pkg_data = self.installed[package_name]
        script_path = Path(pkg_data['path'])
        
        # Remove script file
        if script_path.exists():
            script_path.unlink()
            self.logger.log(f"Removed script file: {script_path}", "debug")
        
        # Remove from registry
        del self.installed[package_name]
        self.save_installed()
        self.logger.log(f"Successfully removed package: {package_name}", "info")
        
        return True
    
    def list_installed(self) -> list[dict]:
        """
        List all installed packages.
        
        Returns
        -------
        list[dict]
            List of installed package info
        """
        result = []
        for name, data in self.installed.items():
            result.append({
                'name': name,
                **data
            })
        return result
    
    def _parse_github_url(self, url: str) -> tuple[str, str]:
        """Parse GitHub URL to get owner/repo."""
        import re
        pattern = r'(?:https?://)?github\.com/([^/]+)/([^/]+?)(?:\.git)?/?$'
        match = re.match(pattern, url.strip())
        if match:
            return match.group(1), match.group(2)
        return ("", "")
