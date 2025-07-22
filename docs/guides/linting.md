# Linting Guide (Ruff)

Sierra‑SDK enforces **strict, automated linting** using [Ruff](https://docs.astral.sh/ruff/). This ensures your code is readable, safe, PEP8-compliant, and production‑ready across all modules, plugins, invokers, and core logic.

---

## 🔧 Configuration Summary

The Ruff config is defined in `pyproject.toml`:

```toml
[tool.ruff]
extend-exclude = ["examples/*", ".venv/*"]
line-length = 79

[tool.ruff.lint]
select = [
    "E", "F", "I", "TCH", "C", "N",
    "D2", "D3", "D415", "D417", "D418", "D419",
    "ASYNC", "Q", "RSE", "SIM", "RUF"
]
ignore = [
    "F405", "F403", "E501", "D205", "D417", "C901"
]
fixable = ["I", "TCH", "D"]

[tool.ruff.lint.pydocstyle]
convention = "numpy"

[tool.ruff.lint.isort]
force-single-line = true

[tool.ruff.format]
docstring-code-format = true
```

---

## ✅ Enabled Rule Categories

| Code    | Category            | Purpose                                              |
| ------- | ------------------- | ---------------------------------------------------- |
| `E`     | Pycodestyle         | PEP8 syntax violations (indent, spacing, etc.)       |
| `F`     | Pyflakes            | Undefined vars, unused imports                       |
| `I`     | isort               | Enforces import order and grouping                   |
| `TCH`   | Type Checking       | Missing annotations, wrong type locations            |
| `C`     | Complexity          | Cyclomatic and McCabe complexity checks              |
| `N`     | Naming              | Naming style conventions (e.g. `snake_case`)         |
| `D2/D3` | Docstring Style     | Enforces formatting in multi-line docstrings         |
| `D415`  | Section Terminators | Ensures docstring sections end with colons           |
| `D417`  | Arg Match           | Arguments in docstring must match function signature |
| `D418`  | Capitalization      | Docstring sections must start with uppercase         |
| `D419`  | Final Line          | Docstring ends with newline                          |
| `ASYNC` | Async Rules         | Coroutine-specific patterns and misuse               |
| `Q`     | Quotes              | Consistent use of `'` or `"`                         |
| `RSE`   | Raise Statements    | Proper use of `raise` syntax                         |
| `SIM`   | Simplifications     | Unnecessary code, can be written more simply         |
| `RUF`   | Ruff Internals      | Ruff's own useful auto-checks                        |

---

## 🚫 Ignored Rules (Temporarily or Internally Allowed)

| Code   | Reason                                                      |
| ------ | ----------------------------------------------------------- |
| `F403` | `import *` allowed internally for auto‑loader code          |
| `F405` | Allow references from wildcard imports internally           |
| `E501` | Line length is tracked separately (`line-length = 79`)      |
| `D205` | One-line summary may be followed immediately by description |
| `D417` | Signature mismatches may occur in some CLI generators       |
| `C901` | High complexity allowed temporarily during refactor stages  |

---

## 🧹 Auto-Fixable Rules

Ruff can automatically fix:

* `I`: Import ordering
* `TCH`: Type-checking fixes (e.g. move annotations to stubs)
* `D`: Many docstring formatting errors

Run:

```bash
ruff check . --fix
```

---

## 📚 Docstrings: NumPy Convention

Use **NumPy-style docstrings** in all modules. Ruff validates your structure, spacing, and style.

### ✅ Correct

```python
def add(a: int, b: int) -> int:
    """
    Add two numbers.

    Parameters
    ----------
    a : int
        First number.
    b : int
        Second number.

    Returns
    -------
    int
        Sum of both.
    """
    return a + b
```

### ❌ Incorrect

```python
def add(a, b):
    """adds"""
    return a + b
```

---

## 📦 Import Order: One Per Line

```python
# Good
import os
import sys

# Bad
import os, sys
```

---

## 🧠 Best Practices Summary

| Do ✅                           | Avoid ❌                        |
| ------------------------------ | ------------------------------ |
| One import per line            | Multiple imports on same line  |
| Always annotate every function | Leaving return type off        |
| Use NumPy docstrings           | Google or plain docstrings     |
| Keep line length ≤ 79          | Long unwrapped lines           |
| Run `ruff check --fix` often   | Ignoring doc errors or imports |

---

## 🧪 Run Linting

Check your code:

```bash
ruff check .
```

Autofix common issues:

```bash
ruff check . --fix
```

---

## 📌 Reminder

Ruff runs **fast**, has no runtime cost, and gives **immediate feedback**. Use it constantly to enforce code health and Sierra‑SDK quality.
