# Documentation & Docstring Standards

Maintaining clear and consistent documentation is a core principle of Sierra‑SDK. This guide walks you through how to document your code using **NumPy-style docstrings**, and how to generate clean developer documentation using **MkDocs** and **mkdocstrings**.

## Why Docstrings Matter

Sierra‑SDK enforces strict standards around function and class documentation. Every public-facing function, method, and class should use **NumPy-style docstrings** to:

* Improve code readability.
* Enable automated documentation generation.
* Ensure consistency across all plugins and modules.

## Docstring Format: NumPy Style

NumPy-style docstrings are clean, structured, and ideal for static parsing. Below is a canonical example for a function:

```python
def process_data(data: list[str], verbose: bool = False) -> dict[str, int]:
    """
    Processes a list of strings and returns word counts.

    Parameters
    ----------
    data : list of str
        The input list of strings to process.
    verbose : bool, optional
        If True, prints detailed logging output. Defaults to False.

    Returns
    -------
    dict of str to int
        A dictionary mapping each word to its occurrence count.
    """
```

### Section Ordering

Follow this order strictly:

1. Short Summary
2. Extended Description (optional)
3. Parameters
4. Returns
5. Raises (if applicable)
6. Examples (if useful)
7. See Also / Notes (optional)

### Required Fields

* Every parameter must include:

  * Name
  * Type
  * Description
* Every return value must include:

  * Type
  * Description

## Common Standards

* **Use `list[str]` not `List[str]`** – always use lowercase generics for modern typing.
* **Do not use Markdown inside docstrings.**
* **Start all descriptions with capital letters** and end sentences with periods.

---

## MkDocs Integration

Sierra‑SDK uses `mkdocstrings` to render docstrings into clean, searchable documentation pages.

In `mkdocs.yml`:

```yaml
plugins:
  - mkdocstrings:
      handlers:
        python:
          options:
            docstring_style: numpy
            show_root_heading: true
            show_root_full_path: false
            show_symbol_type_heading: true
            merge_init_into_class: true
            show_signature: true
```

### Folder Layout

Make sure your repo structure supports autodoc discovery:

```
📁 sierra
 ├─ __init__.py
 ├─ core/
 ├─ invoker/
 └─ plugins/
```

Each file should use properly formatted module-level docstrings:

```python
"""
Invoker module for Sierra Dev.

This module contains core logic for building and registering standalone invoker scripts.
"""
```

---

## Best Practices

* Document **every public function** and class.
* Avoid documenting private methods unless necessary.
* Keep summaries to a **single sentence**.
* Use **imperative voice**: “Return X”, not “Returns X”.

---

## Tools to Enforce Compliance

Use **Ruff** to enforce docstring rules:

```toml
[tool.ruff.lint]
select = ["D"]
ignore = ["D205", "D417"]
```

Use **MyPy** to catch undocumented return values or bad type hints.

---

## Example: Documented Invoker Entry Point

```python
@invoker.entry_point
def run(
    name: sierra.Param[str, sierra.SierraOption(description="Name to greet.", mandatory="MANDATORY")],
    polite: sierra.Param[bool, sierra.SierraOption(description="Use polite tone.")]
) -> None:
    """
    Entry point to execute the greeting logic.

    Parameters
    ----------
    name : str
        Name of the person to greet.
    polite : bool
        Whether to greet politely.

    Returns
    -------
    None
    """
```

---

## Summary

Using proper documentation practices ensures:

✅ Clean auto-generated docs
✅ Easier onboarding for contributors
✅ Long-term maintainability

Follow this guide strictly for all official and third-party Sierra‑SDK plugins.

---
