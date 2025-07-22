# Typing & Type Hinting

Sierra‑SDK uses **strict static typing** to ensure safety, clarity, and predictability in all components. This guide helps you apply best practices using `mypy`, `pyright`, and Python’s `typing` system across scripts, invokers, and plugins.

---

## ✅ Type Annotations: The Basics

Use fully annotated function signatures. Avoid implicit `Any`.

```python
def add(a: int, b: int) -> int:
    return a + b
```

✔️ Always declare return types
✔️ Prefer `str`, `int`, `bool`, `float`, `None`, `list[str]`, `dict[str, int]`, etc.

---

## ✅ Advanced Typing in Sierra

### `sierra.Param[...]`

Wrap input parameters using `Param[T, SierraOption]`. This supports type-checked command-line inputs.

```python
@invoker.entry_point
def run(
    name: sierra.Param[
        str | None,
        sierra.SierraOption(description="User name", mandatory="MANDATORY")
    ]
) -> None:
    ...
```

💡 Sierra type-wrappers are fully compatible with MyPy and Pyright.

---

## ✅ Callable Types

When registering dependencies, use explicit function signatures.

```python
@invoker.dependency
def compute(value: int) -> int:
    ...
```

Never leave them untyped—this breaks type checking across invoker dependency graphs.

---

## ✅ Use TypedDict for JSON-like Objects

For structured dicts (e.g. plugin config or JSON schemas), use `typing.TypedDict`.

```python
import typing

class PluginConfig(typing.TypedDict):
    name: str
    version: str
    enabled: bool
```

---

## ✅ Use Literal for Constrained Values

Use `typing.Literal` for fixed string options like `"MANDATORY"`, `"PRIMARY"`, etc.

```python
def set_flag(mode: typing.Literal["MANDATORY", "OPTIONAL"]) -> None:
    ...
```

---

## ✅ MyPy and Pyright

### Configure `mypy.ini`

```ini
[mypy]
strict = True
ignore_missing_imports = True
disallow_untyped_defs = True
check_untyped_defs = True
warn_unused_ignores = True
```

### Pyright config (`pyrightconfig.json`)

```json
{
  "typeCheckingMode": "strict",
  "reportMissingTypeStubs": false
}
```

---

## 🧠 Best Practices Summary

| Rule                        | Example or Tool           |
| --------------------------- | ------------------------- |
| Use full type signatures    | `def func(x: int) -> str` |
| Use `Param[T, Option]`      | For all invoker arguments |
| No implicit `Any`           | Use `mypy --strict`       |
| Wrap dicts with `TypedDict` | `class MyDict(TypedDict)` |
| Validate literals           | `Literal["A", "B", "C"]`  |

---

## 🔒 Static = Safe

Static typing helps Sierra:

* Prevent runtime errors
* Enable smart auto-complete
* Ensure plugin contracts are valid
* Document APIs without ambiguity

> ❗️ All contributions to Sierra‑SDK must pass `mypy` and `pyright` with zero errors.
