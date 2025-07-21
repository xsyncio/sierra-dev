"""
Sierra Internal.
================

🔒 Internal components of the Sierra SDK framework.

# Overview
--------

This package contains internal components of the Sierra SDK framework, including
cache management, error handling, logging, and utility functions.

# Exposed Components
-----------------

- [BaseSierraError](cci:2://file:///home/xsyncio/Downloads/sierra-dev/sierra/internal/errors.py:0:0-3:8): Base class for Sierra errors.
- `CacheManager`: Manager for caching Sierra components.
- [CompressionType](cci:2://file:///home/xsyncio/Downloads/sierra-dev/sierra/internal/cache.py:15:0-19:17): Enum for compression types.
- [SierraCacheError](cci:2://file:///home/xsyncio/Downloads/sierra-dev/sierra/internal/errors.py:49:0-52:8): Error class for cache-related errors.
- [SierraClientLoadError](cci:2://file:///home/xsyncio/Downloads/sierra-dev/sierra/internal/errors.py:34:0-40:8): Error class for client loading errors.
- [SierraExecutionError](cci:2://file:///home/xsyncio/Downloads/sierra-dev/sierra/internal/errors.py:28:0-31:8): Error class for execution errors.
- [SierraHTTPError](cci:2://file:///home/xsyncio/Downloads/sierra-dev/sierra/internal/errors.py:43:0-46:8): Error class for HTTP errors.
- [SierraPathError](cci:2://file:///home/xsyncio/Downloads/sierra-dev/sierra/internal/errors.py:6:0-9:8): Error class for path-related errors.
- [SierraPathNotFoundError](cci:2://file:///home/xsyncio/Downloads/sierra-dev/sierra/internal/errors.py:12:0-15:8): Error class for path not found errors.
- `UniversalLogger`: Logger class for logging Sierra events.

# Integration Notes
-----------------

This package is a fundamental part of the Sierra SDK framework, providing internal
components for managing cache, errors, logging, and utility functions.
"""

from sierra.internal.cache import CacheManager
from sierra.internal.cache import CompressionType
from sierra.internal.errors import BaseSierraError
from sierra.internal.errors import SierraCacheError
from sierra.internal.errors import SierraClientLoadError
from sierra.internal.errors import SierraExecutionError
from sierra.internal.errors import SierraHTTPError
from sierra.internal.errors import SierraPathError
from sierra.internal.errors import SierraPathNotFoundError
from sierra.internal.logger import UniversalLogger

__all__ = [
    "BaseSierraError",
    "CacheManager",
    "CompressionType",
    "SierraCacheError",
    "SierraClientLoadError",
    "SierraExecutionError",
    "SierraHTTPError",
    "SierraPathError",
    "SierraPathNotFoundError",
    "UniversalLogger",
]
