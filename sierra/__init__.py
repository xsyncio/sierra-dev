"""
sierra-dev.
==========

A framework for building and managing invoker scripts that can be used across different nodes in Sierra during any investigation.

# Overview
--------

This package provides a comprehensive framework for building, compiling, and loading Sierra applications, including abstract base classes, core components, and internal utilities.

# Exposed Components
-----------------

- `create_error_result`: Function to create an error result.
- `create_tree_result`: Function to create a tree result.
- `SierraABC`: Abstract base class for Sierra components.
- `SierraBuilder`: Base class for building Sierra components.
- `SierraCompiler`: Base class for compiling Sierra components.
- `SierraConfig`: Top-level configuration for SIERRA invoker scripts.
- `SierraCoreObject`: Base class for all Sierra components.
- `SierraDevelopmentEnvironment`: Environment configuration class for Sierra development.
- `SierraInvokerBuilder`: Builder for Sierra invoker scripts.
- `SierraLoader`: Base class for loading Sierra components.
- `SierraSideloader`: Base class for side-loading Sierra components.
- `UniversalLogger`: Logger class for logging Sierra events.
- `StreamEmitter`: V2 streaming event emitter with context manager support.
- `stream_context`: Convenience context manager for V2 streaming sessions.

# V2 Streaming
-----------

For V2 invokers that stream results in real-time, use the ``StreamEmitter``:

    >>> from sierra.stream import StreamEmitter
    >>> with StreamEmitter() as stream:
    ...     stream.progress("Scanning targets...")
    ...     stream.result(id="node_1", content="### Target Found")
    ...     stream.end(summary="Scan complete.")

# Integration Notes
-----------------

This package is designed to be used as a foundation for building complex Sierra applications, providing a robust and flexible framework for managing invoker scripts across different nodes.
"""

import json
import os
import pathlib
import typing

from sierra._about import (
    FEATURES,
    RELEASE_NOTES,
    VERSION_INFO,
    VERSION_MAJOR,
    VERSION_MINOR,
    VERSION_PATCH,
    __author__,
    __author_email__,
    __copyright__,
    __description__,
    __license__,
    __title__,
    __url__,
    __version__,
)
from sierra.abc import (
    SierraABC,
    SierraConfig,
    SierraInvokerParam,
    SierraInvokerScript,
)
from sierra.client import SierraDevelopmentClient
from sierra.core import (
    SierraCompiler,
    SierraCoreObject,
    SierraDevelopmentEnvironment,
    SierraInvokerBuilder,
    SierraSideloader,
)
from sierra.internal import (
    BaseSierraError,
    CacheManager,
    CompressionType,
    SierraCacheError,
    SierraClientLoadError,
    SierraExecutionError,
    SierraHTTPError,
    SierraPathError,
    SierraPathNotFoundError,
    UniversalLogger,
)
from sierra.invoker import InvokerScript
from sierra.options import Param, SierraOption
from sierra.results import Chart, Network, Table, Timeline, Tree
from sierra.stream import StreamEmitter, stream_context
from sierra.validators import (
    InvokerValidationResult,
    sanitize_description,
    validate_invoker_name,
    validate_node_id,
    validate_param_type,
    validate_protocol,
    validate_yaml_safe,
)


def create_tree_result(
    results: list[str | dict[str, list[str]]],
) -> str:
    """
    Create a tree result containing a list of results.

    Parameters
    ----------
    results : list[Union[str, dict[str, list[str]]]]
        List of results, where each result is either a string or a dictionary with a single key-value pair.
        The key in the dictionary must be "children" and the value is a list of strings.

    Returns
    -------
    str
        A JSON-formatted string containing the tree result.
    """
    result: dict[str, typing.Any] = {
        "type": "Tree",
        "results": results,
    }
    return json.dumps(result, indent=4)


def create_network_result(
    origins: list[str],
    nodes: list[dict[str, str]],
    edges: list[dict[str, str]],
) -> str:
    """
    Create a network result containing a list of nodes and edges.

    Parameters
    ----------
    origins : list[str]
        List of origin node IDs.
    nodes : list[dict[str, str]]
        List of node definitions, where each node is a dictionary with a single key-value pair.
        The key in the dictionary must be "id" and the value is a string representing the node ID.
    edges : list[dict[str, str]]
        List of edge definitions, where each edge is a dictionary with two key-value pairs.
        The keys in the dictionary must be "from" and "to", and the values are strings representing the node IDs.

    Returns
    -------
    str
        A JSON-formatted string containing the network result.
    """
    result: dict[str, typing.Any] = {
        "type": "Network",
        "origins": origins,
        "nodes": nodes,
        "edges": edges,
    }
    return json.dumps(result, indent=4)


def create_error_result(message: str) -> str:
    """Create an error JSON result."""
    return json.dumps({"type": "Error", "message": message}, indent=4)


def respond(result: typing.Any) -> None:
    """
    Print the result to stdout.

    Handles both string and object results. If the result has a ``__str__``
    method (e.g., ``Tree``, ``Network``, ``Table``), it is automatically
    stringified.

    Parameters
    ----------
    result : Any
        The result to print. Can be a JSON string, a result builder object,
        or any printable value.
    """
    print(result)


# ---------------------------------------------------------------------------
# Cross-platform Image parameter class
# ---------------------------------------------------------------------------

if os.name == "nt":

    class Image(pathlib.WindowsPath):
        """Represents an image parameter path in SIERRA (Windows)."""

        pass
else:

    class Image(pathlib.PosixPath):
        """Represents an image parameter path in SIERRA (Unix/macOS)."""

        pass

# ---------------------------------------------------------------------------
# V2 Event Emission Helpers (module-level convenience functions)
# ---------------------------------------------------------------------------


def emit(event_type: str, **kwargs: typing.Any) -> None:
    """
    Emit a Protocol V2 streaming event to stdout.

    Parameters
    ----------
    event_type : str
        One of ``"progress"``, ``"result"``, ``"end"``, ``"error"``.
    **kwargs
        Additional event fields. ``None`` values are stripped.
    """
    event: dict[str, typing.Any] = {"version": 2, "type": event_type}
    event.update(kwargs)
    filtered = {k: v for k, v in event.items() if v is not None}
    print(json.dumps(filtered), flush=True)


def emit_progress(message: str) -> None:
    """Emit a Protocol V2 progress update."""
    emit("progress", message=message)


def emit_result(content: str, id: str | None = None, parent: str | None = None) -> None:
    """Emit a Protocol V2 incremental graph node."""
    emit("result", id=id, content=content, parent=parent)


def emit_end(summary: str | None = None) -> None:
    """Emit a Protocol V2 end event."""
    emit("end", summary=summary)


def emit_error(message: str) -> None:
    """Emit a Protocol V2 error event."""
    emit("error", message=message)


# ---------------------------------------------------------------------------
# Convenience error class
# ---------------------------------------------------------------------------


class SierraError(Exception):
    """
    Convenience exception that auto-formats as a SIERRA error result.

    When raised inside an invoker entry point, the builder's exception
    handler will catch it and emit either a V1 error JSON or a V2
    stream error event, depending on the protocol.

    Parameters
    ----------
    message : str
        Human-readable error description.

    Examples
    --------
    >>> raise sierra.SierraError("API key expired")
    """

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)

    def to_json(self) -> str:
        """Serialize to a V1 error result JSON string."""
        return create_error_result(self.message)

    def to_v2_json(self) -> str:
        """Serialize to a V2 stream error event JSON string."""
        event = {"version": 2, "type": "error", "message": self.message}
        return json.dumps(event)


__all__ = [
    # Core invoker
    "InvokerScript",
    "Param",
    "SierraOption",
    # Result builders
    "Tree",
    "Network",
    "Table",
    "Timeline",
    "Chart",
    # Client & infrastructure
    "SierraDevelopmentClient",
    "SierraError",
    # Result helpers
    "create_error_result",
    "create_tree_result",
    "create_network_result",
    "respond",
    # Image type
    "Image",
    # V2 streaming
    "emit",
    "emit_progress",
    "emit_result",
    "emit_end",
    "emit_error",
    "StreamEmitter",
    "stream_context",
    # Validators
    "InvokerValidationResult",
    "validate_node_id",
    "validate_yaml_safe",
    "validate_param_type",
    "validate_protocol",
    "validate_invoker_name",
    "sanitize_description",
]
