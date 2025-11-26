# Sierra Dev - Modern Invoker Framework 🚀

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation](https://img.shields.io/badge/docs-mkdocs-blue)](https://xsyncio.github.io/sierra-dev/)

**Sierra Dev** is a modern, production-grade package manager and development framework for creating and managing investigation invoker scripts for the Sierra platform.

## ✨ Key Features

- **📦 APT-Like Package Manager** - Install invokers from GitHub repositories
- **🔍 Type Safety Validation** - Automatic AST-based type checking
- **✅ Comprehensive Validation** - YAML safety, parameter validation, health checks
- **🎨 Rich CLI** - 14 intuitive commands with emoji output
- **🔄 Auto-Updates** - Keep  your invokers up-to-date
- **📚 Built-in Documentation** - Self-documenting invoker scripts

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/xsyncio/sierra-dev
cd sierra-dev

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install Sierra Dev
pip install -e .
```

### Usage

```bash
# Add a package repository
sierra-dev repo add https://github.com/xsyncio/sierra-invokers

# Search for packages
sierra-dev search osint

# Install a package
sierra-dev install digital-footprint

# Build your environment
sierra-dev build --env test_env
```

## 📦 Package Manager

Sierra Dev provides an APT-like package management system:

### Repository Management
```bash
sierra-dev repo add <url>      # Add repository
sierra-dev repo list            # List sources
sierra-dev repo update          # Update registries
sierra-dev repo remove <name>   # Remove source
```

### Package Operations
```bash
sierra-dev search <query>       # Find packages
sierra-dev install <pkg>        # Install package
sierra-dev update --all         # Update all
sierra-dev remove <pkg>         # Uninstall
sierra-dev list --installed     # List installed
```

### Development
```bash
sierra-dev build                # Compile invokers
sierra-dev check                # Run validation
sierra-dev health               # Environment status
```

## 🏗️ Project Structure

```
sierra-dev/
├── sierra/                  # Main package
│   ├── package_manager/    # Package management
│   ├── core/               # Build & compile
│   ├── internal/           # Utilities
│   └── cli.py             # CLI interface
├── docs/                   # Documentation
├── test_env/              # Example env
└── mkdocs.yml            # Docs config
```

## 📚 Documentation

- **[Quick Start Guide](https://xsyncio.github.io/sierra-dev/quickstart/)** - Get started in 5 minutes
- **[Package Manager](https://xsyncio.github.io/sierra-dev/package-manager/)** - Learn the package system
- **[CLI Commands](https://xsyncio.github.io/sierra-dev/package-manager/commands/)** - Complete command reference
- **[API Reference](https://xsyncio.github.io/sierra-dev/api/client/)** - Python API documentation

## 🎯 Features

### Type Safety Enforcement
Automatic validation ensures all invokers have proper type annotations:

```python
# ✅ Valid - Will pass validation
def analyze_target(domain: str, check_breach: bool = False) -> dict:
    """Analyze a target domain."""
    return {"domain": domain, "found": True}

# ❌ Invalid - Will fail validation
def analyze_target(domain, check_breach=False):  # Missing type annotations
    return {"domain": domain}
```

### Rich Result Types
Built-in support for complex data visualization:

```python
from sierra import Table, Timeline, Chart, Tree, respond

# Output rich results
respond(Table(
    headers=["IP", "Port", "Service"],
    rows=[["192.168.1.1", "80", "HTTP"]]
))
```

### Comprehensive Validation
- YAML safety checks
- Parameter validation
- Type annotation enforcement
- Health diagnostics

## 🛠️ Development

### 1. Initialize Project
```bash
sierra-dev init my_project
cd my_project
```

### 2. Create an Invoker

```python
import sierra

invoker = sierra.InvokerScript(
    name="my_tool",
    description="Analyze a target"
)

@invoker.entry_point
def run(target: str) -> None:
    """Analyze a target."""
    result = {"target": target, "status": "analyzed"}
    sierra.respond(result)
```

### Building

```bash
# Validate your invokers
sierra-dev check --env test_env

# Build with verbose output
sierra-dev build --env test_env -v

# Check health
sierra-dev health --env test_env
```

## 📊 Statistics

- **14 CLI Commands** - Comprehensive package management
- **6 Package Manager Modules** - Full-featured package system
- **Type Safety Validation** - AST-based automatic checking
- **GitHub Integration** - Use existing infrastructure

## 🤝 Contributing

Contributions are welcome! Please see our [Contributing Guide](CONTRIBUTING.md).

### Development Setup

```bash
# Clone repository
git clone https://github.com/xsyncio/sierra-dev
cd sierra-dev

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Build documentation
mkdocs serve
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- **Documentation**: https://xsyncio.github.io/sierra-dev/
- **Repository**: https://github.com/xsyncio/sierra-dev
- **Issue Tracker**: https://github.com/xsyncio/sierra-dev/issues
- **Discussions**: https://github.com/xsyncio/sierra-dev/discussions


**Sierra Dev** - Modern investigation tooling made simple.
