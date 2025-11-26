# CLI Commands Reference

This is the complete reference for all **14 Sierra Dev CLI commands**. These commands allow you to manage repositories, install packages, and maintain your environment.

## 📦 Repository Commands

Manage the sources where Sierra Dev looks for packages.

### `sierra-dev repo add`
Add a GitHub repository as a package source.

**Syntax:**
```bash
sierra-dev repo add <url> [options]
```

**Options:**
- `--name <name>`: Custom name for the source (e.g., "community").
- `--branch <branch>`: Git branch to use (default: `main`).
- `--priority <n>`: Priority level (lower number = higher priority). Default is 10.

**Examples:**
```bash
sierra-dev repo add https://github.com/xsyncio/sierra-invokers
sierra-dev repo add https://github.com/my-org/private-tools --name private --priority 1
```

---

### `sierra-dev repo list`
List all configured repositories and their status.

**Syntax:**
```bash
sierra-dev repo list
```

**Output:**
Displays a table of sources, their URLs, priorities, and enabled status.

---

### `sierra-dev repo update`
Fetch the latest package registries from all configured sources.

**Syntax:**
```bash
sierra-dev repo update [source]
```

**Arguments:**
- `source` (optional): Update only a specific source by name.

**Examples:**
```bash
sierra-dev repo update          # Update all
sierra-dev repo update official # Update only 'official'
```

---

### `sierra-dev repo remove`
Remove a repository source.

**Syntax:**
```bash
sierra-dev repo remove <name>
```

---

## 🔍 Discovery Commands

Find and explore available packages.

### `sierra-dev search`
Search for packages across all repositories.

**Syntax:**
```bash
sierra-dev search <query> [options]
```

**Options:**
- `--tag <tag>`: Filter by tag (e.g., "osint").
- `--category <cat>`: Filter by category.
- `--source <src>`: Filter by source repository.

**Examples:**
```bash
sierra-dev search email
sierra-dev search --tag vulnerability
```

---

### `sierra-dev info`
Show detailed information about a specific package.

**Syntax:**
```bash
sierra-dev info <package>
```

**Output:**
Displays description, author, version, source, tags, and installation instructions.

---

## 💿 Package Management

Install, update, and remove packages.

### `sierra-dev install`
Install one or more packages into your environment.

**Syntax:**
```bash
sierra-dev install <package>... [options]
```

**Options:**
- `--env <name>`: Target environment (default: `test_env`).
- `--force`: Force re-installation even if already installed.
- `--skip-validation`: Bypass type safety checks (use with caution).

**Examples:**
```bash
sierra-dev install digital-footprint
sierra-dev install pkg1 pkg2 pkg3 --env production
```

---

### `sierra-dev update`
Update installed packages to the latest version.

**Syntax:**
```bash
sierra-dev update [package] [--all]
```

**Options:**
- `--all`: Update ALL installed packages.
- `--env <name>`: Target environment.

**Examples:**
```bash
sierra-dev update digital-footprint
sierra-dev update --all
```

---

### `sierra-dev upgradable`
List all packages that have updates available.

**Syntax:**
```bash
sierra-dev upgradable
```

---

### `sierra-dev remove`
Uninstall a package.

**Syntax:**
```bash
sierra-dev remove <package>
```

---

### `sierra-dev list`
List available or installed packages.

**Syntax:**
```bash
sierra-dev list [options]
```

**Options:**
- `--installed`: Show only installed packages.
- `--env <name>`: Target environment.

---

## 🛠️ Development & Health

Maintain and validate your environment.

### `sierra-dev init`
Initialize a new Sierra environment.

```bash
sierra-dev init [name] [--force]
```

- `name`: Name of the environment directory (default: `default_env`)
- `--force`: Overwrite existing configuration if present

### `sierra-dev clean`
Clean generated files from the environment.

```bash
sierra-dev clean [--env ENV]
```

- `--env`: Target environment (default: `default_env`)

### `sierra-dev build`
Compile invoker scripts and generate configuration.

**Syntax:**
```bash
sierra-dev build [options]
```

**Options:**
- `--env <name>`: Target environment.
- `-v, --verbose`: Enable debug logging.

---

### `sierra-dev check`
Run comprehensive validation checks on your invokers.

**Syntax:**
```bash
sierra-dev check [options]
```

**Checks Performed:**
- YAML configuration validity
- Parameter definitions
- Type annotations
- Reserved keywords

---

### `sierra-dev health`
Check the overall health of the Sierra Dev environment.

**Syntax:**
```bash
sierra-dev health
```

**Checks Performed:**
- Configuration existence
- Directory structure
- Virtual environment status
- Permission checks

---

## ℹ️ Global Options

These options apply to all commands:

- `-h, --help`: Show help message and exit.
- `-v, --verbose`: Enable verbose output (debug logs).

## 💡 Tips

- Use `sierra-dev repo update` frequently to get the latest package versions.
- Use `sierra-dev check` before building to catch errors early.
- Combine `sierra-dev search` with tags for precise discovery.
