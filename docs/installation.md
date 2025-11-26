# 📥 Installation Guide

Get Sierra Dev up and running on your system in minutes.

## 🎯 Quick Installation

!!! tip "Copy-Paste Friendly"
    These commands will get you started. We'll explain what each does below!

=== "Linux / macOS"
    ```bash
    # Navigate to where you want Sierra
    cd ~/Projects  # or your preferred directory
    
    # Clone the repository
    git clone https://github.com/xsyncio/sierra-dev
    cd sierra-dev
    
    # Create virtual environment
    python3 -m venv venv
    source venv/bin/activate
    
    # Install Sierra Dev
    pip install -e .
    
    # Verify installation
    sierra-dev --help
    ```

=== "Windows"
    ```powershell
    # Navigate to where you want Sierra  
    cd C:\Projects  # or your preferred directory
    
    # Clone the repository
    git clone https://github.com/xsyncio/sierra-dev
    cd sierra-dev
    
    # Create virtual environment
    python -m venv venv
    venv\Scripts\activate
    
    # Install Sierra Dev
    pip install -e .
    
    # Verify installation
    sierra-dev --help
    ```

=== "Using conda"
    ```bash
    # Create conda environment
    conda create -n sierra python=3.10
    conda activate sierra
    
    # Clone and install
    git clone https://github.com/xsyncio/sierra-dev
    cd sierra-dev
    pip install -e .
    
    # Verify
    sierra-dev --help
    ```

---

## 📋 Prerequisites

Before installing, make sure you have:

### Required

| Requirement | Minimum Version | Check Command |
|-------------|-----------------|---------------|
| **Python** | 3.10+ | `python --version` |
| **pip** | 20.0+ | `pip --version` |
| **Git** | 2.0+ | `git --version` |

### Optional (but recommended)

- **Text Editor** - VS Code, PyCharm, or any code editor
- **Terminal** - Comfortable with command line basics

---

## 🔍 Detailed Installation Steps

### Step 1: Install Python

!!! question "Do I have Python installed?"
    Run `python --version` or `python3 --version` in your terminal.
    
    - ✅ Shows `Python 3.10.x` or higher → You're good!
    - ❌ Command not found → Install Python below

=== "Ubuntu/Debian"
    ```bash
    sudo apt update
    sudo apt install python3 python3-pip python3-venv
    ```

=== "macOS"
    ```bash
    # Using Homebrew
    brew install python@3.10
    ```

=== "Windows"
    1. Download from [python.org](https://www.python.org/downloads/)
    2. Run installer
    3. ✅ Check "Add Python to PATH"
    4. Click Install

### Step 2: Install Git

=== "Ubuntu/Debian"
    ```bash
    sudo apt install git
    ```

=== "macOS"
    ```bash
    # Using Homebrew
    brew install git
    ```

=== "Windows"
    Download from [git-scm.com](https://git-scm.com/download/win)

### Step 3: Clone Sierra Dev

```bash
# Choose a location (examples)
cd ~/Projects          # macOS/Linux
cd C:\Projects         # Windows

# Clone the repository
git clone https://github.com/xsyncio/sierra-dev
cd sierra-dev
```

**What This Does:**
- Downloads Sierra Dev source code
- Creates a `sierra-dev/` folder
- Changes into that folder

### Step 4: Create Virtual Environment

!!! info "Why Virtual Environment?"
    Keeps Sierra's dependencies separate from your system Python. This prevents conflicts and makes everything cleaner!

```bash
python3 -m venv venv  # Linux/macOS
python -m venv venv   # Windows
```

**Activate it:**

=== "Linux / macOS"
    ```bash
    source venv/bin/activate
    ```
    
    You should see `(venv)` in your terminal prompt.

=== "Windows CMD"
    ```cmd
    venv\Scripts\activate
    ```

=== "Windows PowerShell"
    ```powershell
    venv\Scripts\Activate.ps1
    ```
    
    If you get an error about execution policy:
    ```powershell
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
    ```

### Step 5: Install Sierra Dev

With your virtual environment **activated**:

```bash
pip install -e .
```

**What This Does:**
- Installs Sierra Dev in "editable" mode (`-e`)
- Installs all required dependencies
- Makes `sierra-dev` command available

**This will install:**
- Core Sierra framework
- Package manager
- CLI tools
- All dependencies (httpx, beautifulsoup4, etc.)

### Step 6: Verify Installation

```bash
sierra-dev --help
```

You should see:

```
usage: sierra-dev [-h] {init,clean,build,check,health,repo,search,info,install,update,upgradable,remove,list} ...

Sierra Dev - Invoker Package Manager

positional arguments:
  {init,clean,build,check,health,repo,search,info,install,update,upgradable,remove,list}
    init                Initialize a new project
    build               Build and compile invokers
    ...
```

✅ **Success!** Sierra Dev is installed.

---

## 🎨 Post-Installation Setup

### Optional: Add to System PATH

If you want to use `sierra-dev` from any directory without activating venv:

=== "Linux / macOS"
    Add to `~/.bashrc` or `~/.zshrc`:
    ```bash
    export PATH="$PATH:$HOME/Projects/sierra-dev/venv/bin"
    ```
    
    Then reload:
    ```bash
    source ~/.bashrc  # or ~/.zshrc
    ```

=== "Windows"
    1. Search "Environment Variables" in Start Menu
    2. Click "Environment Variables"
    3. Under "User variables", select `Path` → Edit
    4. Add New: `C:\Projects\sierra-dev\venv\Scripts`
    5. Click OK on all dialogs

### Create Your First Environment

```bash
sierra-dev init my_first_project
```

This creates:
```
my_first_project/
├── scripts/       # Your invoker source code goes here
├── config.yaml    # Auto-generated configuration
└── source         # Package source metadata
```

---

## 🔧 Troubleshooting

### Common Issues

??? error "Command not found: sierra-dev"
    **Problem:** Sierra Dev not in PATH or venv not activated
    
    **Solutions:**
    
    1. Make sure virtual environment is activated:
        ```bash
        source venv/bin/activate  # Linux/macOS
        venv\Scripts\activate     # Windows
        ```
    
    2. Or use full path:
        ```bash
        ./venv/bin/sierra-dev  # Linux/macOS
        venv\Scripts\sierra-dev # Windows
        ```

??? error "Python version too old"
    **Problem:** `ERROR: Python 3.10 or higher required`
    
    **Solution:** Install Python 3.10+
    
    Check current version:
    ```bash
    python --version
    ```
    
    Install newer version and recreate venv:
    ```bash
    python3.10 -m venv venv
    ```

??? error "Permission denied"
    **Problem:** Don't have write access
    
    **Solutions:**
    
    1. Don't use `sudo` with pip (bad practice)
    2. Install in your home directory instead
    3. Use virtual environment (recommended)

??? error "ModuleNotFoundError: No module named 'sierra'"
    **Problem:** Imported sierra in wrong context
    
    **Solution:**
    
    1. Make sure you're in the venv:
        ```bash
        which python  # Should show venv path
        ```
    
    2. Reinstall if needed:
        ```bash
        pip install -e .
        ```

??? error "git: command not found"
    **Problem:** Git not installed
    
    **Solution:** Install Git (see Step 2 above)

??? error "SSL Certificate Error"
    **Problem:** Corporate proxy or firewall
    
    **Solution:**
    
    1. Use `--trusted-host`:
        ```bash
        pip install -e . --trusted-host pypi.org --trusted-host files.pythonhosted.org
        ```
    
    2. Or configure proxy:
        ```bash
        export HTTP_PROXY=http://proxy.company.com:8080
        export HTTPS_PROXY=http://proxy.company.com:8080
        ```

### Getting More Help

#### Enable Debug Mode

For detailed installation logs:

```bash
pip install -e . --verbose
```

#### Check Dependencies

List installed packages:

```bash
pip list
```

Should include:
- sierra-dev (installed in editable mode)
- httpx
- beautifulsoup4
- dnspython
- And more...

#### Verify Python Environment

```bash
python -c "import sierra; print(sierra.__version__)"
```

Should print version number (e.g., `2.0.0`)

---

## 🔄 Updating Sierra Dev

Pull latest changes and reinstall:

```bash
cd sierra-dev
git pull
pip install -e . --upgrade
```

---

## 🗑️ Uninstalling

Remove Sierra Dev:

```bash
pip uninstall sierra-dev
```

Remove entire directory:
```bash
cd ..
rm -rf sierra-dev  # Linux/macOS
rmdir /s sierra-dev  # Windows
```

---

## ✅ Verification Checklist

Make sure everything works:

- [ ] `sierra-dev --help` shows help message
- [ ] `sierra-dev init test` creates a project
- [ ] `python -c "import sierra"` runs without error
- [ ] Virtual environment activates successfully

---

## 🚀 Next Steps

Now that Sierra Dev is installed:

1. **[Learn Core Concepts](concepts.md)** - Understand how it all works
2. **[Quick Start Tutorial](quickstart.md)** - Build your first invoker
3. **[CLI Reference](cli-reference.md)** - Master all commands

<div style="text-align: center; padding: 2em; background: linear-gradient(135deg, rgba(0,243,255,0.1), rgba(188,19,254,0.1)); border-radius: 8px; margin: 2em 0;">
    <p style="font-size: 1.2em; color: var(--neon-cyan);">
        🎉 Installation Complete!
    </p>
    <p style="margin-top: 1em;">
        <a href="../quickstart/" class="md-button md-button--primary">Start Building →</a>
    </p>
</div>
