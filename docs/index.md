# Sierra SDK - Modern Invoker Framework

**Sierra SDK** is a modern, production-grade package manager and development framework for creating and managing investigation invoker scripts for the Sierra platform.

!!! tip "First Time Here?"
    👋 **New to Sierra SDK?** Start with our [Welcome Guide](welcome.md) - it's designed for complete beginners!

## 🚀 Key Features

- **📦 APT-Like Package Manager** - Install invokers from GitHub repositories with dependency resolution.
- **🔍 Type Safety Validation** - Automatic AST-based type checking for robust scripts.
- **✅ Comprehensive Validation** - YAML safety, parameter validation, health checks.
- **🎨 Rich CLI** - 14 intuitive commands with emoji output and interactive feedback.
- **🔄 Auto-Updates** - Keep your invokers up-to-date with a single command.
- **📊 Rich Results** - Tables, trees, timelines, and charts for data visualization.
- **📝 Comprehensive Logging** - Detailed tracking of all operations with multiple log levels.
- **🧪 Test Infrastructure** - Built-in testing support with pytest fixtures and coverage.

## 🌟 New in v2.1

- **Strict Output Control** - Clean stdout with `sierra.respond()`
- **Enhanced Result Constructors** - Flexible APIs for all result types
- **15+ OSINT Tools** - Production-ready tools for domain, network, email analysis
- **Neon Cyberpunk Theme** - Extreme futuristic documentation theme
- **Comprehensive Beginner Docs** - Learn from zero to advanced

## 🎯 Quick Start

### For Beginners

New to programming or OSINT? Follow our progressive learning path:

1. **[Welcome Guide](welcome.md)** - Understand what Sierra SDK is
2. **[Installation](installation.md)** - Get set up in 5 minutes
3. **[Core Concepts](concepts.md)** - Learn the fundamentals
4. **[Your First 5 Minutes](quickstart.md)** - Build your first tool!

### For Developers

Already know Python? Jump right in:

```bash
# Install Sierra SDK
git clone https://github.com/xsyncio/sierra-dev
cd sierra-dev && python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e .

# Your first invoker in 3 commands
sierra-dev init my_project
cd my_project
sierra-dev build
```

[→ CLI Reference](cli-reference.md){ .md-button .md-button--primary }

### For OSINT Users

Want to use tools right away?

```bash
# Add package repository
sierra-dev repo add https://github.com/xsyncio/sierra-invokers

# Find tools
sierra-dev search domain

# Install and use
sierra-dev install whois_lookup
sierra-dev build
```

[→ OSINT Tools Guide](osint-tools.md){ .md-button }

## 📚 Documentation Structure

| Section | What You'll Find |
|---------|------------------|
| **[Welcome](welcome.md)** | Beginner-friendly intro and learning roadmap |
| **[Tutorials](quickstart.md)** | Hands-on guides and examples |
| **[Reference](cli-reference.md)** | Complete CLI and API documentation |
| **[Guides](guides/index.md)** | Best practices and advanced topics |

## 🎓 Learning Paths

Choose your path based on your goal:

=== "I Want to Learn"
    **Complete Learning Path:**
    
    1. [Welcome Guide](welcome.md) - Start here!
    2. [Core Concepts](concepts.md) - Understand fundamentals
    3. [Your First 5 Minutes](quickstart.md) - Build something
    4. [Results Guide](results-guide.md) - Master output formats
    5. [CLI Reference](cli-reference.md) - Learn all commands

=== "I Want to Build"
    **Quick Builder Track:**
    
    1. [Installation](installation.md)
    2. [Your First 5 Minutes](quickstart.md)  
    3. [Results Guide](results-guide.md)
    4. [CLI Reference](cli-reference.md)
    5. Start building!

=== "I Want to Use Tools"
    **OSINT User Track:**
    
    1. [Installation](installation.md)
    2. [OSINT Tools Guide](osint-tools.md)
    3. [Package Manager](package-manager/index.md)
    4. [CLI Commands](cli-reference.md)

## 🌟 Why Sierra SDK?

### For Users
- ✅ **Easy Discovery** - Find investigation tools quickly
- ⚡ **Quick Install** - One command to install
- 🔒 **Type Safe** - Automatic validation
- 📊 **Rich Results** - Beautiful tables, timelines, charts

### For Developers
- 📤 **Easy Distribution** - Host on GitHub
- 🏷️ **Metadata Support** - Rich package information
- 🔄 **Version Control** - Git-based versioning
- 🌐 **Community** - Share your tools

## 🚀 Next Steps

<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1em; margin: 2em 0;">
    <div style="padding: 1.5em; background: rgba(0,243,255,0.05); border: 1px solid rgba(0,243,255,0.2); border-radius: 4px;">
        <h3 style="margin-top: 0; color: var(--neon-cyan);">🎓 Learn</h3>
        <p>Start from the beginning</p>
        <a href="welcome/" class="md-button md-button--primary">Welcome Guide →</a>
    </div>
    <div style="padding: 1.5em; background: rgba(188,19,254,0.05); border: 1px solid rgba(188,19,254,0.2); border-radius: 4px;">
        <h3 style="margin-top: 0; color: var(--neon-purple);">⚡ Build</h3>
        <p>Create your first tool</p>
        <a href="quickstart/" class="md-button md-button--primary">5-Minute Tutorial →</a>
    </div>
    <div style="padding: 1.5em; background: rgba(10,255,0,0.05); border: 1px solid rgba(10,255,0,0.2); border-radius: 4px;">
        <h3 style="margin-top: 0; color: var(--neon-green);">🔍 Investigate</h3>
        <p>Use OSINT tools now</p>
        <a href="osint-tools/" class="md-button md-button--primary">Explore Tools →</a>
    </div>
</div>

## 💬 Community

- 📖 [Full Documentation](https://xsyncio.github.io/sierra-dev/)
- 🐛 [Issue Tracker](https://github.com/xsyncio/sierra-dev/issues)
- 💬 [Discussions](https://github.com/xsyncio/sierra-dev/discussions)

---

<div style="text-align: center; padding: 2em; background: linear-gradient(135deg, rgba(0,243,255,0.1), rgba(188,19,254,0.1)); border-radius: 8px; margin: 2em 0;">
    <p style="font-size: 1.3em; font-family: 'Orbitron', sans-serif; color: var(--neon-cyan);">
        🚀 Ready to build the future of investigation tools?
    </p>
    <p style="margin-top: 1em;">
        <a href="welcome/" class="md-button md-button--primary" style="margin: 0.5em;">Get Started</a>
        <a href="concepts/" class="md-button" style="margin: 0.5em;">Learn Concepts</a>
    </p>
</div>

**Built by Xsyncio**
