# Plugin Development

Learn how to build and register a standalone invoker script using the Sierra‑SDK plugin system. This guide walks you through defining dependencies, input parameters, result outputs, and the plugin loader function.

## Step 1 — Import Sierra

```python
import sierra
```

Use the core `sierra` module to access all plugin interfaces, decorators, parameter wrappers, and result constructors.

---

## Step 2 — Define an `InvokerScript`

Start by creating an `InvokerScript` object. This acts as the root definition of your plugin logic.

```python
invoker = sierra.InvokerScript(
    name="greet",
    description="Prints a personalized greeting message."
)
```

---

## Step 3 — Register Dependencies

You can define helper functions that are not exposed as command-line parameters but are needed by your entry point.

```python
@invoker.dependency
def random_function_one(param: int) -> int:
    return param * 2

@invoker.dependency
def random_function_two(message: str) -> str:
    return message.upper()
```

---

## Step 4 — Define the Entry Point

Mark the main function using `@invoker.entry_point`. Input arguments should use `sierra.Param` and `sierra.SierraOption`.

```python
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
```

---

## Step 5 — Load the Plugin

The plugin must define a `load()` function. This hook is invoked by the Sierra plugin loader to register your invoker.

```python
def load(client: sierra.SierraDevelopmentClient) -> None:
    client.load_invoker(invoker)
```

---

## Summary

| Component               | Purpose                                            |
| ----------------------- | -------------------------------------------------- |
| `InvokerScript()`       | Defines a new plugin/invoker                       |
| `@invoker.dependency`   | Adds a helper function to the script               |
| `@invoker.entry_point`  | Marks the main callable                            |
| `sierra.Param[...]`     | Wraps a parameter with typing and options metadata |
| `load()`                | Registers the invoker into the plugin system       |
| `create_tree_result()`  | Generates structured tree output                   |
| `create_error_result()` | Returns a formatted error                          |

Once created, this invoker becomes discoverable by Sierra CLI or GUI runners.
