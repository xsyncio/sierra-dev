"""
Sierra Dev version and metadata.
"""

__version__ = "2.0.0"
__title__ = "Sierra Dev"
__description__ = "Modern framework for building and managing investigation invoker scripts for the Sierra platform"
__url__ = "https://github.com/xsyncio/sierra-dev"
__author__ = "Xsyncio"
__author_email__ = "dev@xsyncio.com"
__license__ = "AGPL-3.0"
__copyright__ = "Copyright 2024 Xsyncio"

# Version info
VERSION_MAJOR = 2
VERSION_MINOR = 0
VERSION_PATCH = 0
VERSION_INFO = (VERSION_MAJOR, VERSION_MINOR, VERSION_PATCH)

# Feature flags for v2.0
FEATURES = {
    "package_manager": True,
    "type_validation": True,
    "comprehensive_logging": True,
    "rich_cli": True,
    "osint_tools": True,
    "test_suite": True,
}

# Release notes
RELEASE_NOTES = """
Sierra Dev v2.0.0 - Major Release

New Features:
- 📦 APT-like package manager with GitHub integration
- 🔍 Type safety validation with AST-based checking
- ✅ Comprehensive validation system (YAML, parameters, health)
- 📊 14 CLI commands for package management
- 🚀 Auto-update functionality for installed packages
- 📚 15+ production-ready OSINT tools
- 🧪 Comprehensive test suite with 60+ tests
- 📝 Complete documentation with MkDocs

Package Manager:
- Repository management (add, remove, update)
- Package installation with type validation
- Update checking and package upgrades
- Search and discovery across repositories
- Local caching and metadata tracking

Improvements:
- Comprehensive logging across all modules
- Rich result types (Table, Tree, Timeline, Chart)
- Enhanced error handling and validation
- Production-ready code quality
- Full type annotations

Breaking Changes:
- Requires Python 3.12+
- New package structure with package_manager module
- Enhanced CLI interface with new commands
"""
