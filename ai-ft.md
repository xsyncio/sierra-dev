[AI Instruction Set: Absolute Compliance Required]

**Overview**  
The AI assistant must fully comply with the following rules in every response. No exceptions. Any violation constitutes non-compliance.

---

### 1. Imports and Namespace Management

- **No from Imports**  
  Under no circumstances should the AI use from module import X.  
- **Explicit Module References**  
  Always use import module and reference all attributes via module.attribute.

---

### 2. Documentation Standards

- **NumPy-Style Docstrings**  
  Every function, class, and module must include comprehensive NumPy-style docstrings with:
  - **Summary**  
  - **Parameters**  
  - **Returns**  
  - **Raises**  
  - **Examples**  
  - **Notes**  
- **Clarity**  
  Docstrings must clearly describe input types, output types, possible exceptions, and usage examples.

---

### 3. Code Completeness

- **Self-Contained**  
  Provide fully implemented, production-ready code. No placeholders or incomplete sections.  
- **Ready to Execute**  
  All dependencies and logic must be included; the user should not need to add or modify anything to run the code.

---

### 4. Library Usage

- **Permitted**  
  Any open-source Python library that does **not** require network access.  
- **Prohibited**  
  - HTTP or network-call libraries (requests, aiohttp, httpx, etc.).  
  - External APIs or internet-based services.

---

### 5. Precision, Performance, and Security

- **Concise Responses**  
  Focus on clarity, correctness, and efficiency; avoid unnecessary exposition.  
- **FinTech Best Practices**  
  Ensure code meets security, scalability, and data-integrity standards common in financial technology.  
- **Modularity**  
  Design with extendibility in mind—components should be loosely coupled and easily testable.

---

### 6. Style and Type Safety

- **PEP Compliance**  
  Follow PEP 8 (style), PEP 20 (Zen of Python), PEP 257 (docstrings), PEP 484 (type hints).  
- **Strict Typing**  
  Every function signature, variable, and return value must have accurate static type annotations.  
- **No Type Warnings**  
  Code must pass strict type checking (e.g., MyPy, VS Code strict mode) without errors.

---

### 7. Operational Constraints

- **Local Execution Only**  
  No reliance on third-party web services or cloud infrastructure.  
- **No Browser-Based Requests**  
  The solution must run entirely offline within the local environment.

---

### 8. Linting & Formatting Rules (Ruff Configuration)

Derived from pyproject.toml:

```toml
[tool.ruff]
extend-exclude = ["examples/*", ".venv/*"]
line-length = 79

[tool.ruff.lint]
select = [
  "E",    # Pycodestyle errors (PEP8)
  "F",    # Pyflakes (undefined names)
  "I",    # isort (import ordering)
  "TCH",  # Type-checking violations
  "C",    # Complexity (Cyclomatic, McCabe)
  "N",    # Naming conventions
  "D2",   # Pydocstyle: blank lines after summary
  "D3",   # Pydocstyle: multi-line docstring formatting
  "D415", # Sections end with colon
  "D417", # Docstring args match signature
  "D418", # Section capitalization
  "D419", # Final newline in docstring
  "ASYNC",# Async-specific linting
  "Q",    # Quotes consistency
  "RSE",  # Raise-statement correctness
  "SIM",  # Simplification rules
  "RUF",  # Ruff-specific rules
]
ignore = [
  "F405", # Allow wildcard imports internally
  "F403", # Allow from module import * internally
  "E501", # Disable strict line-length (handled above)
  "D205", # Disable one blank line after summary
  "D417", # Relax some arg-name mismatches
  "C901", # Temporarily allow high complexity
]
fixable = ["I", "TCH", "D"]

[tool.ruff.lint.pydocstyle]
convention = "numpy"

[tool.ruff.lint.isort]
force-single-line = true

[tool.ruff.format]
docstring-code-format = true
```