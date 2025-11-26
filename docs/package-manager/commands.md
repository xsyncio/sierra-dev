# CLI Commands Reference

This is the complete reference for all **14 Sierra SDK CLI commands**. These commands allow you to manage repositories, install packages, and maintain your environment.

## 📦 Repository Commands

Manage the sources where Sierra SDK looks for packages.

### `sierra-sdk repo add`
Add a GitHub repository as a package source.

**Syntax:**
```bash
sierra-sdk repo add <url> [options]
```

**Options:**
- `--name <name>`: Custom name for the source (e.g., "community").
- `--branch <branch>`: Git branch to use (default: `main`).
- `--priority <n>`: Priority level (lower number = higher priority). Default is 10.

**Examples:**
```bash
sierra-sdk repo add https://github.com/xsyncio/sierra-invokers
sierra-sdk repo add https://github.com/my-org/private-tools --name private --priority 1
```

---

### `sierra-sdk repo list`
List all configured repositories and their status.

**Syntax:**
```bash
sierra-sdk repo list
```

**Output:**
Displays a table of sources, their URLs, priorities, and enabled status.

---

### `sierra-sdk repo update`
Fetch the latest package registries from all configured sources.

**Syntax:**
```bash
sierra-sdk repo update [source]
```

**Arguments:**
- `source` (optional): Update only a specific source by name.

**Examples:**
```bash
sierra-sdk repo update          # Update all
sierra-sdk repo update official # Update only 'official'
```

---

### `sierra-sdk repo remove`
Remove a repository source.

**Syntax:**
```bash
sierra-sdk repo remove <name>
```

---

## 🔍 Discovery Commands

Find and explore available packages.

### `sierra-sdk search`
Search for packages across all repositories.

**Syntax:**
```bash
sierra-sdk search <query> [options]
```

**Options:**
- `--tag <tag>`: Filter by tag (e.g., "osint").
- `--category <cat>`: Filter by category.
- `--source <src>`: Filter by source repository.

**Examples:**
```bash
sierra-sdk search email
sierra-sdk search --tag vulnerability
```

---

### `sierra-sdk info`
Show detailed information about a specific package.

**Syntax:**
```bash
sierra-sdk info <package>
```

**Output:**
Displays description, author, version, source, tags, and installation instructions.

---

## 💿 Package Management

Install, update, and remove packages.

### `sierra-sdk install`
Install one or more packages into your environment.

**Syntax:**
```bash
sierra-sdk install <package>... [options]
```

**Options:**
- `--env <name>`: Target environment (default: `test_env`).
- `--force`: Force re-installation even if already installed.
- `--skip-validation`: Bypass type safety checks (use with caution).

**Examples:**
```bash
sierra-sdk install digital-footprint
sierra-sdk install pkg1 pkg2 pkg3 --env production
```

---

### `sierra-sdk update`
Update installed packages to the latest version.

**Syntax:**
```bash
sierra-sdk update [package] [--all]
```

**Options:**
- `--all`: Update ALL installed packages.
- `--env <name>`: Target environment.

**Examples:**
```bash
sierra-sdk update digital-footprint
sierra-sdk update --all
```

---

### `sierra-sdk upgradable`
List all packages that have updates available.

**Syntax:**
```bash
sierra-sdk upgradable
```

---

### `sierra-sdk remove`
Uninstall a package.

**Syntax:**
```bash
sierra-sdk remove <package>
```

---

### `sierra-sdk list`
List available or installed packages.

**Syntax:**
```bash
sierra-sdk list [options]
```

**Options:**
- `--installed`: Show only installed packages.
- `--env <name>`: Target environment.

---

## 🛠️ Development & Health

Maintain and validate your environment.

### `sierra-sdk init`
Initialize a new Sierra environment.

```bash
sierra-sdk init [name] [--force]
```

- `name`: Name of the environment directory (default: `default_env`)
- `--force`: Overwrite existing configuration if present

### `sierra-sdk clean`
Clean generated files from the environment.

```bash
sierra-sdk clean [--env ENV]
```

- `--env`: Target environment (default: `default_env`)

### `sierra-sdk build`
Compile invoker scripts and generate configuration.

**Syntax:**
```bash
sierra-sdk build [options]
```

**Options:**
- `--env <name>`: Target environment.
- `-v, --verbose`: Enable debug logging.

---

### `sierra-sdk check`
Run comprehensive validation checks on your invokers.

**Syntax:**
```bash
sierra-sdk check [options]
```

**Checks Performed:**
- YAML configuration validity
- Parameter definitions
- Type annotations
- Reserved keywords

---

### `sierra-sdk health`
Check the overall health of the Sierra SDK environment.

**Syntax:**
```bash
sierra-sdk health
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

- Use `sierra-sdk repo update` frequently to get the latest package versions.
- Use `sierra-sdk check` before building to catch errors early.
- Combine `sierra-sdk search` with tags for precise discovery.
