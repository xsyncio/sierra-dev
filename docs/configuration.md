# ⚙️ Configuration

Configure the **SierraDevelopmentClient** to get the most out of Sierra’s structured development workflow. This guide covers best practices around logging, caching, and environment layout.

---

## 🧱 Client Construction

At the core of every workflow is the `SierraDevelopmentClient`. You can instantiate it with custom logging, caching, and environment parameters.

### ✅ Recommended Client Setup

```python
import sierra
import pathlib
from sierra.internal.logger import LogLevel, UniversalLogger

# Create the logger
logger = UniversalLogger(
    name="Sierra",
    level=LogLevel.DEBUG,  # DEBUG or INFO for dev environments
)

# Build the client
client = sierra.SierraDevelopmentClient(
    environment_path=pathlib.Path.cwd(),       # Base directory for scripts/config
    environment_name="default_env",                    # Logical name for this dev env
    logger=logger,                             # Custom logger
    # Optional: pass `cache=...` if needed
)
```

This initializes:

* Environment paths and config files
* Logger with debug-level tracing
* HTTP client (e.g. for plugins or services)
* Script sideloader
* Compiler + Builder pipeline

---

## 📁 Project Layout

Here’s the standard folder structure Sierra expects:

```cmd
default_env/
├── scripts/              ← Your invoker source files
│   ├── greet.py
│   └── notify.py
├── invokers/             ← Auto‑compiled standalone invokers
├── config.yaml           ← Auto‑generated CLI config
├── cache/                ← (optional) Persistent build cache
├── compile.py            ← Client bootstrap / entry script
└── README.md
```

You can change the base path with `environment_path`, but `scripts/` must exist inside it.

---

## 🧠 Logging Best Practices

Use `UniversalLogger` to trace build, validation, or runtime errors.

### Available Log Levels

| Level     | Description                              |
| --------- | ---------------------------------------- |
| `DEBUG`   | Most verbose — useful during development |
| `INFO`    | Normal output — good for regular builds  |
| `WARNING` | Misconfiguration or redundancy           |
| `ERROR`   | Exceptions or halting errors             |

Set level during logger construction:

```python
UniversalLogger(name="Sierra", level=LogLevel.INFO)
```

Sierra uses structured messages for every phase:

* Environment init
* Sideloader source population
* Script discovery
* Invoker registration
* Compiler stages

---

## 💾 Caching (Optional)

You can pass a `CacheManager` instance to control how Sierra handles repeated compilation, YAML regeneration, and data reuse:

```python
from sierra.internal.cache import CacheManager

client = sierra.SierraDevelopmentClient(
    cache=CacheManager(cache_dir=pathlib.Path("default_env/cache"))
)
```

By default, caching is enabled unless disabled explicitly.

---

## 🔎 Script Auto‑Discovery

Call this in your entry script to load all `InvokerScript` instances from `scripts/`:

```python
client.load_invokers_from_scripts()
```

Each script must expose a `load()` function like this:

```python
def load(client: sierra.SierraDevelopmentClient) -> None:
    client.load_invoker(invoker)
```

Sierra uses Python’s `importlib` to dynamically load and validate each invoker module.

---

## 🧱 Environment Name

The `environment_name` is used for logical grouping. You can create multiple environments (e.g., `default_env`, `prod`, `test`) and Sierra will handle separate script and build trees per environment.

This affects:

* Generated YAML config name
* Build paths
* Contextual logging

---

## 🧪 Full Example

```python
import sierra
from sierra.internal.logger import UniversalLogger, LogLevel

client = sierra.SierraDevelopmentClient(
    environment_path="default_env",
    environment_name="default_env",
    logger=UniversalLogger(name="Sierra", level=LogLevel.DEBUG),
)

client.load_invokers_from_scripts()
client.compiler.compile()
```

---

## 🧵 Summary

| Config Field       | Purpose                             | Default                    |
| ------------------ | ----------------------------------- | -------------------------- |
| `environment_path` | Base path for scripts & builds      | `Path.cwd()`               |
| `environment_name` | Logical name for config/environment | `"default_env"`            |
| `logger`           | Structured logging output           | Built‑in `UniversalLogger` |
| `cache`            | Optional caching backend            | Enabled by default         |
| `http_client`      | Internal HTTP client (optional use) | `httpx.Client`             |
