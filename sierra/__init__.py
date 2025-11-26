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

# Integration Notes
-----------------

This package is designed to be used as a foundation for building complex Sierra applications, providing a robust and flexible framework for managing invoker scripts across different nodes.
"""

import json
import typing

from sierra._about import *
from sierra.abc import *
from sierra.client import *
from sierra.core import *
from sierra.internal import *
from sierra.invoker import *
from sierra.options import *
from sierra.results import Tree, Network, Table, Timeline, Chart


def create_tree_result(
    results: list[typing.Union[str, dict[str, list[str]]]],
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

def respond(result: str) -> None:
    """Print the result to stdout."""
    print(result)

__all__ = [
    "InvokerScript",
    "Param",
    "SierraOption",
    "dependancy",
    "entry_point",
    "Tree",
    "Network",
    "Table",
    "Timeline",
    "Chart",
    "SierraDevelopmentClient",
    "SierraError",
    "create_error_result",
    "respond",
]
