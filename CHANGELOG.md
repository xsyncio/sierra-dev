# Sierra SDK v2.0.0 - Changelog

All notable changes to Sierra SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.0] - 2024-11-26

### Added
- **Strict Output Control**: Introduced `sierra.respond(result)` for outputting results.
- **Result Constructors**: Result classes (`Table`, `Tree`, etc.) now accept constructor arguments for cleaner instantiation.

### Changed
- **Logging Policy**: Logging to `stdout` or `stderr` is now strictly prohibited in invoker scripts. All output must go through `sierra.respond()`.
- **Examples**: Updated all example invokers to comply with strict output rules.

## [2.0.0] - 2024-11-26

### 🎉 Major Release - Complete Rewrite

Sierra SDK v2.0 is a major release that transforms the framework into a comprehensive OSINT and investigation toolkit with package management capabilities.

### Added

#### Package Manager System
- 📦 APT-like package manager with GitHub integration
- Repository management (add, remove, update, list)
- Package installation with automatic dependency resolution
- Package search and discovery across multiple sources
- Update checking and automatic package upgrades
- Local caching and metadata tracking
- Type safety validation for all packages

#### CLI Commands (14 total)
- `sierra-sdk repo add` - Add GitHub repository as package source
- `sierra-sdk repo list` - List configured repositories
- `sierra-sdk repo update` - Update package registries
- `sierra-sdk repo remove` - Remove repository source
- `sierra-sdk search` - Search for packages
- `sierra-sdk info` - Show package information
- `sierra-sdk install` - Install packages
- `sierra-sdk update` - Update installed packages
- `sierra-sdk upgradable` - List packages with updates
- `sierra-sdk remove` - Uninstall packages
- `sierra-sdk list` - List available/installed packages
- `sierra-sdk build` - Build invoker environment
- `sierra-sdk check` - Run validation checks
- `sierra-sdk health` - Check environment health

#### OSINT Tools (15+ production-ready examples)
- **Domain & DNS**: subdomain_enumerator, dns_analyzer, whois_lookup, crt_sh
- **Network & IP**: ip_intelligence, port_scanner, ssl_cert_analyzer
- **Email**: email_breach_checker (HIBP integration)
- **Web**: tech_detector (50+ technologies), wayback_analyzer
- **Social**: username_checker (10+ platforms)
- **Identity**: digital_footprint, phone_number analysis

#### Comprehensive Logging
- Logging infrastructure across all 6 package_manager modules
- Debug, info, warning, and error log levels
- Structured logging with UniversalLogger
- ~100+ log statements throughout codebase

#### Testing Infrastructure
- Comprehensive test suite with 60+ tests
- pytest configuration with coverage reporting
- Shared fixtures and mocking utilities
- Unit tests for logger, results, repository, type_validator
- Integration tests for package workflows
- Test runner script (`run_tests.sh`)
- HTML coverage reports

#### Documentation
- Complete package manager documentation
- All 14 CLI commands documented
- OSINT tools usage guide
- API reference documentation
- MkDocs configuration with Material theme
- GitHub-ready README

### Changed

#### Core Framework
- Enhanced type checking with AST-based validation
- Improved error handling across all modules
- Rich result types (Table, Tree, Timeline, Chart)
- Better validation system (YAML, parameters, health)
- Modular package structure

#### Development
- Python 3.12+ required
- Comprehensive type annotations (100% coverage)
- Production-ready code quality
- Full test coverage for critical paths

### Technical Details

#### New Modules
- `sierra.package_manager.repository` - Repository management
- `sierra.package_manager.installer` - Package installation
- `sierra.package_manager.registry` - Package registry
- `sierra.package_manager.updater` - Update functionality
- `sierra.package_manager.type_validator` - Type safety
- `sierra.package_manager.search` - Package search

#### Dependencies Added
- `httpx` - HTTP client for package manager
- `dnspython` - DNS operations for OSINT
- `requests` - HTTP requests for tools
- `beautifulsoup4` - HTML parsing
- `pytest` - Testing framework

#### Files Added
- 11 new OSINT example tools
- 8 test files with 60+ tests
- Package manager module (6 files)
- Comprehensive documentation
- Test infrastructure

### Statistics

- **Lines of Code**: ~8,000+ (production code)
- **Test Coverage**: 60+ tests covering critical modules
- **OSINT Tools**: 15+ production-ready tools
- **CLI Commands**: 14 commands
- **Documentation**: 1,500+ lines
- **Features**: 6 major new systems

### Breaking Changes

⚠️ **Version 2.0 introduces breaking changes:**

1. **Python Version**: Now requires Python 3.12 or higher
2. **Package Name**: Changed from `sierra-dev` to `sierra-sdk`
3. **CLI Entry Point**: Changed from `sierra` to `sierra-sdk`
4. **Import Structure**: New package_manager module
5. **Configuration**: Enhanced config.yaml structure

### Migration Guide

#### From v1.x to v2.0

```bash
# Uninstall old version
pip uninstall sierra-dev

# Install new version
pip install sierra-sdk

# Update CLI usage
sierra build      # OLD
sierra-sdk build  # NEW

# Install packages
sierra-sdk repo add https://github.com/xsyncio/sierra-invokers
sierra-sdk install digital-footprint
```

### Contributors

- Xsyncio Team
- Community contributors

### Links

- [Documentation](https://xsyncio.github.io/sierra-dev/)
- [GitHub Repository](https://github.com/xsyncio/sierra-dev)
- [Issue Tracker](https://github.com/xsyncio/sierra-dev/issues)

---

## [1.x.x] - Previous Versions

See git history for changes in v1.x releases.

---

**Sierra SDK v2.0** - Modern investigation tooling made simple.
