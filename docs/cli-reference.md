# 📘 CLI Reference

Complete reference for all Sierra SDK command-line tools.

## 🚀 Quick Reference

| Command | Purpose | Example |
|---------|---------|---------|
| `init` | Create new environment | `sierra-sdk init my_project` |
| `build` | Compile invokers | `sierra-sdk build` |
| `check` | Run validation | `sierra-sdk check` |
| `health` | Environment status | `sierra-sdk health` |
| `repo add` | Add package source | `sierra-sdk repo add <url>` |
| `search` | Find packages | `sierra-sdk search osint` |
| `install` | Install package | `sierra-sdk install tool-name` |
| `update` | Update packages | `sierra-sdk update --all` |
| `list` | List packages | `sierra-sdk list --installed` |
| `remove` | Uninstall package | `sierra-sdk remove tool-name` |

---

## 🎯 Global Options

Available for most commands:

```bash
-h, --help          Show help message
-v, --verbose       Enable debug logging
--env ENV_NAME      Specify environment (default: default_env)
```

---

## 📂 Environment Commands

### `init` - Initialize Environment

Create a new Sierra environment for your projects.

**Syntax:**
```bash
sierra-sdk init [name] [--force]
```

**Arguments:**
- `name` - Environment name (default: `default_env`)
- `--force` - Overwrite existing environment

**Examples:**
```bash
# Create default environment
sierra-sdk init

# Create named environment
sierra-sdk init my_osint_tools

# Force recreate existing
sierra-sdk init my_project --force
```

**What It Creates:**
```
my_project/
├── scripts/        # Your source invokers
├── config.yaml     # Configuration file
└── source          # Package metadata
```

---

### `clean` - Clean Environment

Remove generated files from an environment.

**Syntax:**
```bash
sierra-sdk clean [--env ENV_NAME]
```

**What It Removes:**
- `config.yaml`
- `__pycache__` directories
- `.pytest_cache` directories

**Examples:**
```bash
# Clean default environment
sierra-sdk clean

# Clean specific environment
sierra-sdk clean --env test_env
```

---

## 🏗️ Build Commands

### `build` - Compile Invokers

Compile source invokers into standalone scripts.

**Syntax:**
```bash
sierra-sdk build [--env ENV_NAME] [-v]
```

**Options:**
- `--env` - Environment to build (default: `default_env`)
- `-v, --verbose` - Show detailed logs

**Examples:**
```bash
# Build with default settings
sierra-sdk build

# Build with debug output
sierra-sdk build --verbose

# Build specific environment
sierra-sdk build --env production
```

**Process:**

```mermaid
graph LR
    A[Source Scripts] -->|Validate| B[Type Check]
    B -->|Transform| C[Generate CLI]
    C -->|Bundle| D[Standalone Scripts]
    D --> E[Update config.yaml]
    
    style A fill:#bc13fe20
    style D fill:#00f3ff20
```

**Output:**
- Compiled scripts in `ENV/invokers/`
- Updated `ENV/config.yaml`
- Installed dependencies in `ENV/venv/`

---

### `check` - Validate Invokers

Run comprehensive validation checks without building.

**Syntax:**
```bash
sierra-sdk check [--env ENV_NAME] [-v]
```

**Checks:**
- ✅ Type annotations present
- ✅ Parameter validation rules
- ✅ YAML-safe names and descriptions
- ✅ Entry point exists
- ✅ Dependencies resolvable

**Examples:**
```bash
# Check current environment
sierra-sdk check

# Check with details
sierra-sdk check --verbose
```

**Output Example:**
```
✨ All checks passed! Your invokers are healthy.

# Or if issues found:
❌ ERRORS:
[ERROR] invoker: my-tool
  Invalid invoker name 'my-tool'
  💡 Suggestion: Use only lowercase letters, numbers, and underscores

⚠️ WARNINGS:
[WARNING] parameter: my_tool.target
  No description provided
```

---

### `health` - Environment Health

Check overall health of your Sierra environment.

**Syntax:**
```bash
sierra-sdk health [--env ENV_NAME] [-v]
```

**Checks:**
- Scripts directory exists
- Virtual environment valid
- Dependencies installed
- Config file valid

**Examples:**
```bash
sierra-sdk health
```

**Output:**
```
✅ Health Status: HEALTHY

Invokers: 5
Errors: 0
Warnings: 2

Environment Checks:
  ✅ Scripts Directory
  ✅ Virtual Environment
  ✅ Config File
  ✅ Dependencies
```

---

## 📦 Package Manager Commands

### `repo add` - Add Repository

Add a GitHub repository as a package source.

**Syntax:**
```bash
sierra-sdk repo add <url> [--name NAME] [--branch BRANCH] [--priority PRIORITY]
```

**Arguments:**
- `url` - GitHub repository URL
- `--name` - Custom name for source
- `--branch` - Git branch (default: `main`)
- `--priority` - Source priority (default: `10`, lower = higher priority)

**Examples:**
```bash
# Add official repository
sierra-sdk repo add https://github.com/xsyncio/sierra-invokers

# Add with custom name
sierra-sdk repo add https://github.com/user/tools --name custom-tools

# Add development branch
sierra-sdk repo add https://github.com/user/tools --branch dev
```

---

### `repo list` - List Repositories

Show all configured package sources.

**Syntax:**
```bash
sierra-sdk repo list
```

**Output:**
```
📦 Configured Repositories:

1. xsyncio/sierra-invokers (priority: 10) ✅ enabled
   URL: https://github.com/xsyncio/sierra-invokers
   Packages: 15
   Cached: 2024-11-26 10:30:15

2. custom-tools (priority: 20) ✅ enabled  
   URL: https://github.com/user/tools
   Packages: Not cached yet
```

---

### `repo update` - Update Registry

Update package registry from repositories.

**Syntax:**
```bash
sierra-sdk repo update [source]
```

**Arguments:**
- `source` - Specific source to update (optional)

**Examples:**
```bash
# Update all sources
sierra-sdk repo update

# Update specific source
sierra-sdk repo update xsyncio/sierra-invokers
```

---

### `repo remove` - Remove Repository

Remove a package source.

**Syntax:**
```bash
sierra-sdk repo remove <name>
```

**Examples:**
```bash
sierra-sdk repo remove custom-tools
```

---

### `search` - Search Packages

Find packages across all repositories.

**Syntax:**
```bash
sierra-sdk search <query> [--tag TAG] [--category CATEGORY] [--source SOURCE]
```

**Options:**
- `--tag` - Filter by tag
- `--category` - Filter by category
- `--source` - Filter by source

**Examples:**
```bash
# Search for domain tools
sierra-sdk search domain

# Filter by category
sierra-sdk search "" --category network

# Filter by tag
sierra-sdk search osint --tag investigation

# Combine filters
sierra-sdk search "" --category web --source xsyncio/sierra-invokers
```

**Output:**
```
📦 Search Results (3 packages):

whois-lookup v1.2.0
  Comprehensive WHOIS lookup for domains and IPs
  Category: domain | Tags: osint, whois

dns-analyzer v1.0.5
  Advanced DNS record analysis
  Category: domain | Tags: dns, investigation

subdomain-enum v2.0.1
  Subdomain enumeration tool
  Category: domain | Tags: recon, osint
```

---

### `info` - Package Information

Show detailed information about a package.

**Syntax:**
```bash
sierra-sdk info <package>
```

**Examples:**
```bash
sierra-sdk info whois-lookup
```

**Output:**
```
Package: whois-lookup
Version: 1.2.0
Category: domain
Source: xsyncio/sierra-invokers

Description:
  Comprehensive WHOIS information retrieval for
  domains and IP addresses.

Tags: osint, whois, domain, investigation

Dependencies:
  - requests
  - dnspython

Installation:
  sierra-sdk install whois-lookup
```

---

### `install` - Install Package

Install packages into your environment.

**Syntax:**
```bash
sierra-sdk install <packages...> [--env ENV] [--force] [--skip-validation]
```

**Options:**
- `--env` - Target environment (default: `test_env`)
- `--force` - Force reinstall
- `--skip-validation` - Skip type safety checks

**Examples:**
```bash
# Install single package
sierra-sdk install whois-lookup

# Install multiple packages
sierra-sdk install whois-lookup dns-analyzer port-scanner

# Force reinstall
sierra-sdk install whois-lookup --force

# Install to specific environment
sierra-sdk install whois-lookup --env production

# Skip validation (not recommended)
sierra-sdk install whois-lookup --skip-validation
```

**Process:**
1. Downloads package from source
2. Validates type safety (unless skipped)
3. Installs to `ENV/scripts/`
4. Updates package metadata

**Important:** After installing, run `sierra-sdk build` to compile!

---

### `list` - List Packages

List available or installed packages.

**Syntax:**
```bash
sierra-sdk list [--installed] [--env ENV]
```

**Options:**
- `--installed` - Show only installed packages
- `--env` - Environment to check (default: `test_env`)

**Examples:**
```bash
# List all available packages
sierra-sdk list

# List installed packages
sierra-sdk list --installed

# Check specific environment
sierra-sdk list --installed --env production
```

**Output (Available):**
```
📦 Available Packages (15 total):

DOMAIN:
  whois-lookup v1.2.0
  dns-analyzer v1.0.5
  subdomain-enum v2.0.1

NETWORK:
  port-scanner v3.1.0
  ip-intelligence v1.5.2
```

**Output (Installed):**
```
📦 Installed Packages (3):

whois-lookup v1.2.0
  Installed: 2024-11-26
  Source: xsyncio/sierra-invokers

dns-analyzer v1.0.5
  Installed: 2024-11-25
  Source: xsyncio/sierra-invokers
```

---

### `update` - Update Packages

Update installed packages to latest versions.

**Syntax:**
```bash
sierra-sdk update [package] [--all] [--env ENV]
```

**Options:**
- `--all` - Update all packages
- `--env` - Environment to update (default: `test_env`)

**Examples:**
```bash
# Update specific package
sierra-sdk update whois-lookup

# Update all packages
sierra-sdk update --all

# Update in specific environment
sierra-sdk update --all --env production
```

**Output:**
```
🔄 Checking for updates...

📦 Updating 2 package(s)...

whois-lookup: 1.2.0 → 1.3.0
  ✅ Updated

dns-analyzer: 1.0.5 (up to date)

✅ Successfully updated 1/2 packages
🔨 Run 'sierra-sdk build' to rebuild
```

---

### `upgradable` - List Upgradable

Show packages with available updates.

**Syntax:**
```bash
sierra-sdk upgradable [--env ENV]
```

**Examples:**
```bash
sierra-sdk upgradable
```

**Output:**
```
📦 Upgradable Packages (2):

whois-lookup
  Installed: 1.2.0
  Available: 1.3.0
  Source: xsyncio/sierra-invokers

port-scanner
  Installed: 3.0.0
  Available: 3.1.0
  Source: xsyncio/sierra-invokers

Run 'sierra-sdk update --all' to upgrade all packages
```

---

### `remove` - Uninstall Package

Remove an installed package.

**Syntax:**
```bash
sierra-sdk remove <package> [--env ENV]
```

**Examples:**
```bash
# Remove package
sierra-sdk remove whois-lookup

# Remove from specific environment
sierra-sdk remove whois-lookup --env production
```

**Output:**
```
🗑️  Removing whois-lookup...
✅ Removed successfully

🔨 Run 'sierra-sdk build' to rebuild
```

---

## 💡 Common Workflows

### Starting a New Project

```bash
# 1. Initialize environment
sierra-sdk init my_investigation

# 2. Add package sources
sierra-sdk repo add https://github.com/xsyncio/sierra-invokers

# 3. Search for tools
sierra-sdk search osint

# 4. Install tools
sierra-sdk install whois-lookup dns-analyzer

# 5. Build environment
sierra-sdk build --env my_investigation
```

### Developing an Invoker

```bash
# 1. Create environment
sierra-sdk init dev_env

# 2. Write invoker in dev_env/scripts/my_tool.py
# (use your text editor)

# 3. Validate
sierra-sdk check --env dev_env

# 4. Build
sierra-sdk build --env dev_env --verbose

# 5. Test
dev_env/venv/bin/python dev_env/invokers/my_tool.py --help
```

### Maintaining Packages

```bash
# Check for updates
sierra-sdk upgradable

# Update all
sierra-sdk update --all

# Rebuild
sierra-sdk build

# Verify health
sierra-sdk health
```

---

## 🔧 Advanced Usage

### Environment Variables

```bash
# Set default environment
export SIERRA_ENV=production

# Use custom config location
export SIERRA_CONFIG=/path/to/config
```

### Chaining Commands

```bash
# Install and build in one go
sierra-sdk install whois-lookup && sierra-sdk build
```

### Scripting

```bash
#!/bin/bash
# Auto-update script

sierra-sdk repo update
sierra-sdk update --all
sierra-sdk build
sierra-sdk check
```

---

## 🚨 Exit Codes

Commands return standard exit codes:

| Code | Meaning |
|------|---------|
| `0` | Success |
| `1` | Error |
| `130` | Interrupted (Ctrl+C) |

Use in scripts:
```bash
if sierra-sdk build --env prod; then
    echo "Build successful"
else
    echo "Build failed"
    exit 1
fi
```

---

## 📚 Related Documentation

- [Core Concepts](concepts.md) - Understand the terminology
- [Tutorial](quickstart.md) - Hands-on learning
- [Package Manager](package-manager/index.md) - Detailed package guide
- [Troubleshooting](installation.md#troubleshooting) - Fix common issues
