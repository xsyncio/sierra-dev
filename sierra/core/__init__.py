"""
Sierra Core.
============

🔩 Core components of the Sierra Dev framework.

# Overview
--------

This package contains the core components of the Sierra Dev framework, including
builders, compilers, environments, loaders, and base classes for Sierra objects.

# Exposed Components
-----------------

- `SierraBuilder`: Base class for building Sierra components.
- `SierraCompiler`: Base class for compiling Sierra components.
- [SierraCoreObject](cci:2://file:///home/xsyncio/Downloads/sierra-dev/sierra/core/base.py:14:0-50:9): Base class for all Sierra components.
- `SierraDevelopmentEnvironment`: Environment configuration class for Sierra development.
- `SierraInvokerBuilder`: Builder for Sierra invoker scripts.
- `SierraLoader`: Base class for loading Sierra components.
- `SierraSideloader`: Base class for side-loading Sierra components.

# Integration Notes
-----------------

This package is a fundamental part of the Sierra Dev framework, providing the core
components for building, compiling, and loading Sierra applications.
"""

from sierra.core.base import SierraCoreObject
from sierra.core.builder import SierraInvokerBuilder
from sierra.core.compiler import SierraCompiler
from sierra.core.environment import SierraDevelopmentEnvironment
from sierra.core.loader import SierraSideloader

__all__ = [
    "SierraCompiler",
    "SierraCoreObject",
    "SierraDevelopmentEnvironment",
    "SierraInvokerBuilder",
    "SierraSideloader",
]
