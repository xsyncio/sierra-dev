# 🚀 Quickstart

This guide helps you go from zero to a working **Sierra Dev** setup — where you can write structured invokers, generate standalone scripts, and produce CLI-ready YAML configs.

---

## 📁 1. Create Your First Invoker

In a file like `scripts/greet.py`, define an invoker:

```python
import sierra

# Define the invoker
invoker = sierra.InvokerScript(
    name="greet",
    description="Prints a personalized greeting message."
)

# Dependency functions
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

# Main entrypoint
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
            description="Whether to include a polite phrase in the greeting."
        )
    ] = False,
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

---

## ⚙️ 2. Load the Client

In your driver script (e.g. `compile.py`):

```python
import sierra

client = sierra.SierraDevelopmentClient(
    environment_name="default_env",
    logger=sierra.UniversalLogger(
        name="Sierra",
        level=sierra.sierra_internal_logger.LogLevel.DEBUG,
    ),
)

# Load all scripts from the environment
client.load_invokers_from_scripts()

# Compile to standalone Python + YAML config
client.compiler.compile()
```

---

## 🏗️ 3. What `compile()` Does

It auto-generates:

* A **standalone script** (e.g. `invokers/greet.py`)
* A **YAML entry** for your CLI or automation config
* Command-line argument parsing and runtime validation

Example compiled script:

```bash
python invokers/greet.py Alice true
```

Example output:

```json
{
  "type": "tree",
  "tree": ["Good day to you, Alice!"]
}
```

---

## 📂 4. Environment Layout

Your project directory might look like:

```cmd
📁 default_env/
 ├─ scripts/
 │   └─ greet.py
 ├─ invokers/
 │   └─ greet.py  ← auto‑compiled
 ├─ venv/
 ├─ config.yaml   ← auto‑generated
 └─ source
```

---

## 🧪 5. Run & Test

After compilation:

* CLI works with basic Python execution
* All validations (types, required params) are automatically checked
* Error and tree results are structured and JSON-compatible

---

## 📌 Notes

* Use `@invoker.entry_point` for the main logic
* Use `@invoker.dependancy` to register helpers
* Use `Param[...]` with `SierraOption(...)` for typed + validated inputs
* Client will pick up all scripts inside the `scripts/` directory

---

## 🧠 Learn More

Check out:

* [Plugin Development Guide](./guides/plugins.md)
* [Typing & Linting](./guides/typing.md)
* [Docstring & Documentation](./guides/documentation.md)
