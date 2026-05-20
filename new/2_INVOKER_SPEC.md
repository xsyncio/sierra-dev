# 🧬 SIERRA Invoker Configurations & Protocols Specification

This document provides the exhaustive technical blueprint, output contracts, and YAML schema definitions for creating custom SIERRA Invoker integrations. 

---

## 🏗️ 1. Unified Configuration Schema (`invoker.yaml`)

Invoker configurations map local and remote command-line tools directly to graph nodes. SIERRA looks for `invoker.yaml` (or `config.yaml`) inside paths designated by the user.

```yaml
# ==============================================================================
# SIERRA Invoker Schema Definition
# ==============================================================================

# [Optional] PRIORITIZED EXECUTION CONTEXTS:
# Working directories SIERRA will search to resolve script paths or use as CWD.
PATHS:
  - /opt/scripts
  - /home/user/tools
  - ~/Documents/sierra-invokers

# [Mandatory] LIST OF REGISTERED SCRIPTS:
SCRIPTS:
  - Name: Subdomain Finder              # [Mandatory] Unique identifier for the canvas context menu
    Description: Looks up subdomains    # [Optional] Explanatory tooltip for the investigator
    Protocol: V2                        # [Optional] "V1" (Batch/Default) or "V2" (Streaming/Incremental)
    Params:                             # [Mandatory] Argument specifications mapped to variables
      - Name: Domain                    # [Mandatory] Parameter placeholder key
        Description: Target domain name # [Optional] Input box label helper
        Type: STRING                    # [Mandatory] "STRING", "FILE", or "IMAGE"
        Options:                        # [Optional] Parameter constraint flags
          - MANDATORY                   # Ensures execution is blocked if the parameter value is empty
          - PRIMARY                     # Designates the default target node property field
    Command: python subfinder.py {Domain} # [Mandatory] Shell execution template string
```

---

## 🧬 2. Parameter Data Types & Visual Pipelines

SIERRA manages raw inputs and maps them into localized values before executing your script. There are three core parameter data types:

| Type | YAML Identifier | Input Origin | Script Injection Value |
| :--- | :--- | :--- | :--- |
| **String** | `STRING` | Manual text entry or node value | Injected as standard escaped command-line text. |
| **File** | `FILE` | File picker or drag-and-drop file path | Injected as the absolute local path to the file. |
| **Image** | `IMAGE` | Clipboard paste, file upload, or screenshot | **[NEW]** Injected as an absolute local path to an auto-generated temporary PNG/JPG file. |

### 🖼️ Deep-Dive: The `IMAGE` Visual Pipeline

When an invoker declares `Type: IMAGE`, SIERRA's graphic processor automatically abstracts all visual asset logistics:

1. **Extraction**: The user right-clicks a node containing a visual asset, uploads an image, or references a URL.
2. **Buffering**: SIERRA downloads the asset, extracts the binary stream, and saves it into a secure temporary folder (e.g. `/tmp/sierra_image_3921.png`).
3. **Replacement**: The `{ParamName}` placeholder in your `Command` template is replaced with the absolute path on disk.
4. **Execution**: Your local script loads the path safely, completely unaware of whether the asset originated on the web or the clipboard.

#### Python Implementation Example for `IMAGE`:
```python
import sys
import json
from pathlib import Path

def process_image(temp_path_str: str):
    image_path = Path(temp_path_str)
    
    # 1. AST / File Validation
    if not image_path.exists() or not image_path.is_file():
        # Render clean V1 error block or V2 stream error
        print(json.dumps({"type": "Error", "message": f"Visual asset not accessible at: {temp_path_str}"}))
        sys.exit(1)
        
    # 2. Process image (e.g., OCR, metadata extraction, forensic checks)
    size = image_path.stat().st_size
    print(json.dumps({
        "type": "Tree",
        "results": [
            f"# Visual Asset Loaded Successfully",
            f"File Path: {image_path.name}",
            f"Size: {size} bytes"
        ]
    }))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"type": "Error", "message": "No visual asset path provided."}))
        sys.exit(1)
    process_image(sys.argv[1])
```

---

## ⚡ 3. The Protocol Contracts: V1 (Batch) vs V2 (Streaming)

SIERRA engines manage execution pipelines using one of two standard output protocols, dictated by the script's configuration.

```mermaid
graph TD
    subgraph V1: Batch Mode (Default)
        A[Launch Script] --> B[Block & Wait for Exit]
        B --> C[Read Entire stdout Buffer]
        C --> D[Parse Single JSON Object]
        D --> E[Render Canvas Nodes at Once]
    end
    
    subgraph V2: Streaming Mode (Real-Time)
        F[Launch Script] --> G[Read stdout Line-by-Line]
        G --> H{Parse JSON Event}
        H -->|type: progress| I[Update Progress Bar]
        H -->|type: result| J[Insert Node to Canvas]
        H -->|type: error| K[Render Error & Halt]
        H -->|type: end| L[Graceful Finish & Summary]
        G --> F
    end
```

---

### 📥 Protocol V1: Final Batch Formats

Batch Mode is built for fast utilities (DNS lookups, IP checks, local configuration parsers). The execution wraps, outputs a single block of JSON, and terminates.

#### 🌳 A. Tree Type
Used for rendering clean, nested hierarchical structures. Useful for categories, directory listings, or organized text outputs.
* **JSON Schema**:
  ```json
  {
    "type": "Tree",
    "results": [
      "Item 1",
      "Item 2",
      {
        "Group Title 1": [
          "Nested Leaf A",
          "Nested Leaf B"
        ]
      }
    ]
  }
  ```

* **Special Processing (Interactive Nodes)**:
  Strings starting with `#` are processed as bold header categories. All other plain text strings are interactive nodes. Double-clicking them in the SIERRA canvas automatically spawns contextual actions.

#### 🕸️ B. Network Type
Designed for representing relational graphs containing specific custom edges. Useful for transaction tracing, social profiles, and network infrastructure.
* **JSON Schema**:
  ```json
  {
    "type": "Network",
    "origins": ["SourceNodeId"],
    "nodes": [
      { "id": "UniqueNodeId1", "content": "### Header\nContent markdown for node" },
      { "id": "UniqueNodeId2", "content": "### Target\nMarkdown details here" }
    ],
    "edges": [
      { "source": "UniqueNodeId1", "target": "UniqueNodeId2", "label": "interacted_with" }
    ]
  }
  ```

#### ⚠️ C. Error Type
If the script encounters a critical exception before generating valid findings, returning an error structure allows SIERRA to flag the canvas gracefully.
* **JSON Schema**:
  ```json
  {
    "type": "Error",
    "message": "Detailed description of the API failure or environment error"
  }
  ```

---

### ⚡ Protocol V2: Incremental Streaming Events

Streaming Mode is built for long-running scripts (port scanning, active recon, recursively traversing social graphs). Instead of waiting minutes for an exit code, V2 outputs flushed JSON lines live to `stdout`.

> [!IMPORTANT]
> **V2 Streaming Constraints**:
> 1. Set `"Protocol": "V2"` in the YAML configuration.
> 2. Every event must be printed as a **single, compact, single-line JSON string** to `stdout`.
> 3. You must **flush `stdout` immediately** after each emission.
> 4. All debug messages, error logs, and warnings **must be directed to `stderr`**; otherwise, the JSON stream parser will crash.

#### V2 Stream Event Specifications:

```json
/* 1. Progress Indicator */
{ "version": 2, "type": "progress", "message": "Enumerating subdomain lists (45% complete)..." }

/* 2. Incremental Node Result */
{ "version": 2, "type": "result", "id": "sub_node_01", "parent": "root_node_id", "content": "### admin.target.com\nIP: `192.168.1.1`" }

/* 3. Graceful Termination */
{ "version": 2, "type": "end", "summary": "Successfully parsed 23 assets." }

/* 4. Stream Interruption / Error */
{ "version": 2, "type": "error", "message": "API key limit exceeded. Terminating thread." }
```

---

## 💡 Developer Guidelines & Best Practices

### 1. Directing Diagnostic Logs to Stderr
Never let raw output or standard library debug logs contaminate your stdout pipeline.
```python
import sys
# Correct approach:
sys.stderr.write("[DEBUG] Querying cloud providers...\n")
sys.stderr.flush()
```

### 2. Enforcing Buffer Flushing
In many runtime environments (including Python), `sys.stdout` is heavily buffered when piped. To guarantee real-time updates:
```python
import json
import sys

def emit_v2(event_type: str, **kwargs):
    event = {"version": 2, "type": event_type}
    event.update(kwargs)
    # Remove null elements
    payload = {k: v for k, v in event.items() if v is not None}
    
    # Dump to stdout and flush immediately
    print(json.dumps(payload), flush=True)
```

### 3. Canvas Node ID Consistency
Keep `id` attributes short, alphanumeric, and consistent. The `parent` key must reference an active, previously-emitted `id` to draw a connection line. Omit the `parent` key to anchor the result directly to the user's primary trigger node.
