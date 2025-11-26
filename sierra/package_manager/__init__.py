"""
Sierra Package Manager Module.

Provides APT-like package management for Sierra invoker scripts
with GitHub repositories as sources.
"""

from sierra.package_manager.repository import RepositoryManager
from sierra.package_manager.installer import PackageInstaller
from sierra.package_manager.registry import PackageRegistry
from sierra.package_manager.search import PackageSearch
from sierra.package_manager.updater import PackageUpdater
from sierra.package_manager.type_validator import TypeSafetyValidator, validate_invoker_script

__all__ = [
    "RepositoryManager",
    "PackageInstaller",
    "PackageRegistry",
    "PackageSearch",
    "PackageUpdater",
    "TypeSafetyValidator",
    "validate_invoker_script"
]
