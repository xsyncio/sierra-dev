# Sierra‑SDK


🚀 **Overview**
---------------

Sierra‑SDK is a Python framework for building and managing invoker scripts that can be used across different nodes in Sierra during any investigation.

### Project Goals

*   Provide a robust and flexible framework for managing invoker scripts
*   Offer a simple and intuitive API for building and compiling Sierra applications
*   Support extensibility through plugins and custom configurations

### Key Features

*   **Modular Design**: Sierra‑SDK is built with a modular architecture, allowing for easy extension and customization
*   **Invoker Script Management**: Easily build, compile, and load invoker scripts across different nodes in Sierra
*   **Plugin Support**: Extend the functionality of Sierra‑SDK through custom plugins

## ⚙️ Installation
-----------------

### pip Installation

You can install Sierra‑SDK using pip:
```bash
pip install sierra-dev
```
### Installation from Source

To install Sierra‑SDK from source, clone the repository and run the following command:
```bash
git clone https://github.com/xsyncio/sierra-dev.git
cd sierra-dev
pip install .
```
## 🔧 Usage Examples
-------------------

### Building an Invoker Script
```python
import sierra

# ─── Define the Invoker ────────────────────────────────────────────────────────
invoker = sierra.InvokerScript(
    name="greet",
    description="Prints a personalized greeting message."
)


invoker.requirement(["requests"])


# ─── Dependency functions ──────────────────────────────────────────────────────
@invoker.dependancy
def random_function_one(param: int) -> int:
    return param * 2

@invoker.dependancy
def random_function_two(message: str) -> str:
    return message.upper()

@invoker.dependancy
def random_function_three(value: float) -> float:
    return value / 3.14

@invoker.dependancy
def random_function_four(flag: bool) -> bool:
    return not flag

# ─── Entry point ───────────────────────────────────────────────────────────────
@invoker.entry_point
def run(
    name: sierra.Param[
        str | None,
        sierra.SierraOption(
            description="The name of the person to greet.",
            mandatory="MANDATORY"
        )
    ],
    polite: sierra.Param[
        bool | None,
        sierra.SierraOption(
            description="Whether to include a polite phrase in the greeting.",
            mandatory=None
        )
    ] = False,
) -> None:
    """
    Greet the specified user by name, optionally politely.

    Parameters
    ----------
    name : str
        Name of the user (mandatory).
    polite : bool, optional
        If True, includes a polite prefix.
    """
    if name is None:
        # Missing mandatory parameter
        result = sierra.create_error_result("Missing mandatory parameter: name")
    else:
        # Build greeting
        greeting = f"Hello, {name}!"
        if polite:
            greeting = f"Good day to you, {name}!"
        # Wrap the greeting in a TreeResult
        result = sierra.create_tree_result([greeting])

    # Print the structured result
    print(result)

# ─── Loader ────────────────────────────────────────────────────────────────────
def load(client: sierra.SierraDevelopmentClient) -> None:
    """
    Register this invoker with the given Sierra client.

    Parameters
    ----------
    client : SierraDevelopmentClient
        The Sierra client instance.
    """
    client.load_invoker(invoker)
```

### Compiling
```python
import sierra

# Initialize Sierra client with DEBUG‑level logging
client = sierra.SierraDevelopmentClient(
    environment_name="idd",
    logger=sierra.UniversalLogger(
        name="Sierra",
        level=sierra.sierra_internal_logger.LogLevel.DEBUG,
    ),
)

# Discover and register all invoker scripts
client.load_invokers_from_scripts()

# Generate standalone scripts and config.yaml
client.compiler.compile()
```

## 📦 API Highlights
-------------------

*   `sierra.core.builder`: Builder for invoker scripts
*   `sierra.core.compiler`: Compiler for invoker scripts
*   `sierra.core.loader`: Loader for compiled scripts
*   `sierra.abc.sierra`: Abstract base classes for Sierra components
*   `sierra.invoker`: Invoker script definitions

## 🛠️ Configuration & Extensibility
------------------------------------

Sierra‑SDK supports extensibility through plugins and custom configurations. You can add custom plugins by creating a new folder in the `plugins/` directory and adding your plugin code.

### Plugin Folders

*   `plugins/`: Folder for custom plugins
*   `core/`: Folder for core Sierra‑SDK components
*   `abc/`: Folder for abstract base classes
*   `invoker/`: Folder for invoker script definitions

## 💡 Contributing Guidelines & Code of Conduct
---------------------------------------------

We welcome contributions to Sierra‑SDK! Please see our [CONTRIBUTING.md](CONTRIBUTING.md) file for guidelines on how to contribute.

### Code of Conduct

We follow the [Python Code of Conduct](https://www.python.org/psf/conduct/).

## 📝 License & Authors
-----------------------

Sierra‑SDK is licensed under the [GNU AFFERO GENERAL PUBLIC LICENSE](LICENSE).

### Authors

*   [Xsyncio](https://github.com/xsyncio)