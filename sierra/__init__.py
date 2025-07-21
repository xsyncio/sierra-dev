"""
sierra-sdk.
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

import typing

from sierra.abc import *
from sierra.client import *
from sierra.core import *
from sierra.internal import *


def create_tree_result(
    results: list[typing.Union[str, dict[str, list[str]]]],
) -> dict[str, typing.Any]:
    """
    Create a Tree type result.

    Parameters
    ----------
    results : list[Union[str, dict[str, list[str]]]]
        The tree results.

    Returns
    -------
    TreeResult
        The formatted tree result.
    """
    result: dict[str, typing.Any] = {
        "type": "Tree",
        "results": results,
    }
    return result


def create_network_result(
    origins: list[str],
    nodes: list[dict[str, str]],
    edges: list[dict[str, str]],
) -> dict[str, str]:
    """
    Create a Network type result.

    Parameters
    ----------
    origins : list[str]
        List of origin node IDs.
    nodes : list[dict[str, str]]
        List of node definitions.
    edges : list[dict[str, str]]
        List of edge definitions.

    Returns
    -------
    NetworkResult
        The formatted network result.
    """
    result: dict[str, typing.Any] = {
        "type": "Network",
        "origins": origins,
        "nodes": nodes,
        "edges": edges,
    }
    return result


def create_error_result(message: str) -> dict[str, str]:
    """
    Create an Error type result.

    Parameters
    ----------
    message : str
        The error message.

    Returns
    -------
    ErrorResult
        The formatted error result.
    """
    result: dict[str, typing.Any] = {
        "type": "Error",
        "message": message,
    }

    return result
