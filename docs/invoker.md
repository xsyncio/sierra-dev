# SIERRA Invoker

This document walks you through creating custom Invoker scripts to extend SIERRA’s functionality and automate tasks in your investigations.

---

## 1. Overview

Invoker scripts in SIERRA allow you to integrate external tools and scripts (Python, Bash, PowerShell, etc.) into the SIERRA interface. You define each script with a simple YAML configuration file that describes:

* Where to find your script files (`PATHS`)
* Which scripts to load (`SCRIPTS`)
* What parameters each script accepts
* How to execute the command

Once invoked, your script must return JSON-formatted results in a prescribed structure so SIERRA can visualize them in the investigation graph.

---

## 2. Invoker Script Structure

Each Invoker script is configured via a YAML file with the following sections:

```yaml
# Optional: directories SIERRA searches for your script files
PATHS:
  - /path/to/script/directory
  - /another/path

# Mandatory: list of Invoker scripts to register
SCRIPTS:
  - Name: Subdomain Finder           # Unique script name
    Description: "Lookup subdomains of a domain"
    Params:
      - Name: Domain                 # Parameter name
        Description: "Domain to query" # Optional description
        Type: STRING                 # Supported: STRING, FILE
        Options:
          - MANDATORY                # Options: PRIMARY, MANDATORY
    Command: python subfinder.py {Domain}
```

* **PATHS** (optional): A prioritized list of directories where SIERRA locates your script file.
* **Name** (mandatory): Unique identifier for your Invoker script.
* **Description** (optional): Brief summary of what the script does.
* **Params** (mandatory): List of parameters:

  * **Name** (mandatory)
  * **Description** (optional)
  * **Type** (mandatory): `STRING` or `FILE`
  * **Options** (optional): e.g. `PRIMARY`, `MANDATORY`
* **Command** (mandatory): The shell command to execute, with parameter placeholders like `{Domain}`.

---

## 3. Result Formats

Your script must output a JSON object that SIERRA can parse. There are three supported formats:

### 3.1 Tree Type

Use for hierarchical results.

```json
{
  "type": "Tree",
  "results": [
    "Entity A",
    {
      "Parent C": ["Child D", "Child E"]
    }
  ]
}
```

* `type`: must be `Tree`
* `results`: array of strings or nested objects (parent � children)

### 3.2 Network Type

Use for graph/network relationships.

```json
{
  "type": "Network",
  "origins": ["AliceID"],
  "nodes": [
    {"id": "AliceID",   "content": "Alice"},
    {"id": "BobID",     "content": "Bob"},
    {"id": "CharlieID", "content": "Charlie"}
  ],
  "edges": [
    {"source": "AliceID", "target": "BobID",     "label": "friend"},
    {"source": "AliceID", "target": "CharlieID", "label": "colleague"}
  ]
}
```

* `type`: must be `Network`
* `origins`: list of origin node IDs
* `nodes`: array of `{id, content}` objects
* `edges`: array of `{source, target, label}`

### 3.3 Error Type

On errors, return:

```json
{ "type": "Error", "message": "Error description" }
```

SIERRA will display the error and halt the script execution gracefully.

---

## 4. Example Invoker Configuration

Below is a full example of a subdomain lookup Invoker:

```yaml
PATHS:
  - /opt/scripts
  - /home/user/tools

SCRIPTS:
  - Name: Subdomain Finder
    Description: "Looks up subdomains using crt.sh"
    Params:
      - Name: Domain
        Description: "Domain to query"
        Type: STRING
        Options:
          - PRIMARY
          - MANDATORY
    Command: python subfinder.py {Domain}
```

When invoked, SIERRA will locate `subfinder.py` in the given `PATHS`, pass the `{Domain}` argument, and expect a Tree or Network JSON output.

---

## 5. Tips & Best Practices

* **Validate Input**: Check parameter presence and types, returning an `Error` JSON if invalid.
* **Timeouts**: Ensure long-running scripts implement timeouts to avoid blocking SIERRA.
* **Strict Output**: Use `sierra.respond(result)` to output the final JSON result. Do NOT use `print()` or `sys.stderr.write()` for logging or debugging, as this will break the integration.
* **Reusability**: Modularize code so dependency functions can be shared across multiple Invokers.

---

## 6. Advanced Validation Constraints & Async Invokers

### 6.1 Asynchronous Entry Points
SIERRA natively supports asynchronous entry point functions. If your invoker script is non-blocking or uses `async`/`await` (e.g. for concurrent web scraping or API calls), simply define the entry point with `async def`:

```python
import asyncio
import sierra

invoker = sierra.InvokerScript(name="async_scanner", protocol="V2")

@invoker.entry_point
async def run(target: str) -> None:
    # Run async tasks concurrently
    await asyncio.sleep(1)
    sierra.emit_progress("Scanning target...")
```
SIERRA automatically compiles async scripts to use `asyncio.run()` in their standalone CLI scripts.

### 6.2 Parameter Constraints Validation
You can define compile-time and runtime value assertions for parameters using `SierraOption` metadata parameters:

* `min_value` (int/float): The minimum numeric threshold.
* `max_value` (int/float): The maximum numeric threshold.
* `choices` (list): Enforces that the parameter value is one of the listed options.
* `pattern` (str): Regular expression pattern that the parameter value must match.

#### Example

```python
from sierra import InvokerScript, SierraOption, Param

invoker = InvokerScript(name="port_scanner")

@invoker.entry_point
def run(
    port: Param[int, SierraOption(description="Port to scan", min_value=1, max_value=65535)],
    protocol: Param[str, SierraOption(description="Network protocol", choices=["TCP", "UDP"])],
    target: Param[str, SierraOption(description="Target hostname", pattern="^[a-zA-Z0-9.-]+$")],
) -> None:
    pass
```

SIERRA compiled standalone scripts will automatically:
1. Enforce these constraints at runtime before executing the entry point.
2. Terminate execution with an `Error` JSON payload if the input values violate any of these validations.

---

Harness the power of SIERRA Invoker scripts to automate your investigative workflows and integrate your favorite tools seamlessly into the SIERRA platform.
