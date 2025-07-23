# ⚙️ Installation

## 📦 PyPI

Install from PyPI:
<!-- termynal -->
```bash
pip install sierra-dev
```

## 🛠️ From Source

<!-- termynal -->
```bash
git clone https://github.com/xsyncio/sierra-dev.git
cd sierra-dev
pip install .
```

---

## 🔧 Usage Examples

### 1. Building an Invoker Script

```python
import sierra
import requests
# Define an InvokerScript
invoker = sierra.InvokerScript(
    name="greet",
    description="Prints a personalized greeting message."
)

invoker.requirement(["requests"])

# Dependency functions
@invoker.dependency
def random_function_one(param: int) -> int:
    return param * 2

@invoker.dependency
def random_function_two(message: str) -> str:
    return message.upper()

# Entry point
@invoker.entry_point
def run(
    name: sierra.Param[
        str | None,
        sierra.SierraOption(description="Name of the person to greet.", mandatory="MANDATORY")
    ],
    polite: sierra.Param[
        bool | None,
        sierra.SierraOption(description="Include polite greeting?", mandatory=None)
    ] = False
) -> None:
    if name is None:
        result = sierra.create_error_result("Missing mandatory parameter: name")
    else:
        greeting = f"Hello, {name}!"
        if polite:
            greeting = f"Good day to you, {name}!"
        result = sierra.create_tree_result([greeting])
    print(result)

# Loader function
def load(client: sierra.SierraDevelopmentClient) -> None:
    client.load_invoker(invoker)
```

### 2. Compiling & Running

```python
import sierra

# Initialize the Sierra development client
client = sierra.SierraDevelopmentClient(
    environment_name="default_env",
    logger=sierra.UniversalLogger(
        name="Sierra",
        level=sierra.sierra_internal_logger.LogLevel.DEBUG
    ),
)

# Discover and register invokers
client.load_invokers_from_scripts()

# Compile all invoker scripts and generate config.yaml
client.compiler.compile()
```

---

## 📦 API Highlights

* `sierra.core.builder`: Build invoker scripts programmatically
* `sierra.core.compiler`: Compile and package scripts
* `sierra.core.loader`: Load compiled scripts into the runtime
* `sierra.invoker`: Define script actions, dependencies, and parameters
* `sierra.options`: Parameter and option definitions
* `sierra.SierraDevelopmentClient`: High-level orchestration client

---

## 🛠️ Configuration & Extensibility

* **Configuration File**: Customize paths, logging, and plugins via `sierra.config.yaml`
* **Plugin Directory**: Drop custom plugins into the `plugins/` folder
* **Abstract Base Classes**: Implement new Sierra components by extending `sierra.abc.sierra`

---

## 💡 Contributing & Code of Conduct

We welcome contributions! Please review [CONTRIBUTING.md](CONTRIBUTING.md) and adhere to the [Python Code of Conduct](https://www.python.org/psf/conduct/).

---

## 📝 License & Authors

sierra-dev is released under the [GNU Affero General Public License](LICENSE).

**Authors:**

* [Xsyncio](https://github.com/xsyncio)
