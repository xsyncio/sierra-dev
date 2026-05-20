"""
Sierra Parameter Validators.
=============================

Strict, reusable validation utilities for invoker parameters, YAML safety,
node IDs, and protocol constraints. Used by the checker, builder, and
compiler to ensure invoker scripts are safe and well-formed.

Usage
-----
    from sierra.validators import (
        validate_node_id,
        validate_yaml_safe,
        validate_param_type,
        validate_protocol,
        sanitize_description,
    )
"""

import re
import typing
from dataclasses import dataclass, field

__all__ = [
    "InvokerValidationResult",
    "validate_node_id",
    "validate_yaml_safe",
    "validate_param_type",
    "validate_protocol",
    "validate_invoker_name",
    "sanitize_description",
    "SUPPORTED_PARAM_TYPES",
    "YAML_UNSAFE_PATTERN",
]

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

#: All parameter types the framework natively supports.
SUPPORTED_PARAM_TYPES: typing.Final[frozenset[str]] = frozenset(
    {"str", "int", "float", "bool", "Path", "Image"}
)

#: Pattern matching YAML-unsafe characters in descriptions/names.
YAML_UNSAFE_PATTERN: typing.Final[re.Pattern[str]] = re.compile(r'[:{}\[\],&*#!|>\'"%@`]')

#: Valid Python identifier pattern (for parameter and invoker names).
_PYTHON_IDENT: typing.Final[re.Pattern[str]] = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")

#: Valid V2 node ID pattern: alphanumeric and underscores only.
_NODE_ID_PATTERN: typing.Final[re.Pattern[str]] = re.compile(r"^[a-zA-Z0-9_]+$")

#: Reserved parameter names that conflict with framework internals.
RESERVED_PARAM_NAMES: typing.Final[frozenset[str]] = frozenset(
    {
        "self",
        "cls",
        "client",
        "args",
        "kwargs",
        "config",
        "environment",
        "logger",
        "result",
        "output",
        "input",
        "type",
        "name",
        "sierra",
        "emit",
        "respond",
    }
)

#: Valid protocol versions.
VALID_PROTOCOLS: typing.Final[frozenset[str]] = frozenset({"V1", "V2"})


# ---------------------------------------------------------------------------
# Result container
# ---------------------------------------------------------------------------


@dataclass
class InvokerValidationResult:
    """
    Container for validation results with structured errors and warnings.

    Attributes
    ----------
    is_valid : bool
        ``True`` if no errors were found (warnings are OK).
    errors : list[str]
        Critical issues that must be fixed.
    warnings : list[str]
        Non-critical suggestions for improvement.
    """

    is_valid: bool = True
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def add_error(self, msg: str) -> "InvokerValidationResult":
        """Add an error and mark result as invalid."""
        self.errors.append(msg)
        self.is_valid = False
        return self

    def add_warning(self, msg: str) -> "InvokerValidationResult":
        """Add a non-critical warning."""
        self.warnings.append(msg)
        return self

    def merge(self, other: "InvokerValidationResult") -> "InvokerValidationResult":
        """Merge another result into this one."""
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)
        if not other.is_valid:
            self.is_valid = False
        return self

    def __str__(self) -> str:
        """Human-readable summary."""
        parts: list[str] = []
        if self.errors:
            parts.append(f"❌ {len(self.errors)} error(s):")
            for e in self.errors:
                parts.append(f"  • {e}")
        if self.warnings:
            parts.append(f"⚠️  {len(self.warnings)} warning(s):")
            for w in self.warnings:
                parts.append(f"  • {w}")
        if self.is_valid and not self.warnings:
            parts.append("✅ All validations passed.")
        return "\n".join(parts)


# ---------------------------------------------------------------------------
# Validation functions
# ---------------------------------------------------------------------------


def validate_node_id(node_id: str) -> InvokerValidationResult:
    """
    Validate a V2 streaming node ID.

    Parameters
    ----------
    node_id : str
        The node identifier to validate.

    Returns
    -------
    InvokerValidationResult
        Validation result with any errors/warnings.
    """
    result = InvokerValidationResult()

    if not node_id or not node_id.strip():
        return result.add_error("Node ID must not be empty.")

    if not _NODE_ID_PATTERN.match(node_id):
        result.add_error(f"Node ID '{node_id}' must be alphanumeric with underscores only.")

    if len(node_id) > 64:
        result.add_warning(
            f"Node ID '{node_id}' is very long ({len(node_id)} chars). "
            "Keep IDs short and compact for best canvas performance."
        )

    return result


def validate_yaml_safe(text: str, context: str = "text") -> InvokerValidationResult:
    """
    Check if text is safe for YAML embedding without quotes.

    Parameters
    ----------
    text : str
        The text to validate.
    context : str
        Human-readable context (e.g. "description", "invoker name").

    Returns
    -------
    InvokerValidationResult
        Validation result with any unsafe character warnings.
    """
    result = InvokerValidationResult()

    matches = YAML_UNSAFE_PATTERN.findall(text)
    if matches:
        unique_chars = sorted(set(matches))
        result.add_error(
            f"{context} contains YAML-unsafe characters: {unique_chars}. "
            f"These will break config.yaml parsing."
        )

    return result


def validate_param_type(
    type_obj: typing.Any,
    param_name: str,
) -> InvokerValidationResult:
    """
    Validate that a parameter type is supported by the framework.

    Parameters
    ----------
    type_obj : Any
        The type annotation of the parameter.
    param_name : str
        Name of the parameter (for error context).

    Returns
    -------
    InvokerValidationResult
        Validation result.
    """
    result = InvokerValidationResult()

    if type_obj is None:
        return result.add_error(f"Parameter '{param_name}' has no type annotation.")

    # Unwrap Optional/Union
    actual_type = type_obj
    origin = typing.get_origin(type_obj)
    if origin in (typing.Union,):
        args = typing.get_args(type_obj)
        non_none = [a for a in args if a is not type(None)]
        if non_none:
            actual_type = non_none[0]

    # Check if it's a recognized type
    type_name = getattr(actual_type, "__name__", str(actual_type))

    if type_name not in SUPPORTED_PARAM_TYPES:
        # Check pathlib.Path variants
        if hasattr(actual_type, "__mro__"):
            mro_names = {cls.__name__ for cls in actual_type.__mro__}
            if "Path" in mro_names or "PurePath" in mro_names:
                return result  # It's a Path subclass, valid
            if "Image" in mro_names:
                return result  # It's an Image subclass, valid

        result.add_warning(
            f"Parameter '{param_name}' has type '{type_name}' which may not be "
            f"fully supported. Supported types: {sorted(SUPPORTED_PARAM_TYPES)}"
        )

    return result


def validate_protocol(protocol: str) -> InvokerValidationResult:
    """
    Validate that a protocol version string is recognized.

    Parameters
    ----------
    protocol : str
        Protocol version string (e.g. "V1", "V2").

    Returns
    -------
    InvokerValidationResult
        Validation result.
    """
    result = InvokerValidationResult()

    if protocol not in VALID_PROTOCOLS:
        result.add_error(
            f"Protocol '{protocol}' is not recognized. Must be one of: {sorted(VALID_PROTOCOLS)}"
        )

    return result


def validate_invoker_name(name: str) -> InvokerValidationResult:
    """
    Validate an invoker script name.

    Parameters
    ----------
    name : str
        The invoker name to validate.

    Returns
    -------
    InvokerValidationResult
        Validation result.
    """
    result = InvokerValidationResult()

    if not name or not name.strip():
        return result.add_error("Invoker name must not be empty.")

    if not _PYTHON_IDENT.match(name):
        result.add_error(
            f"Invoker name '{name}' is not a valid Python identifier. "
            "Use lowercase letters, numbers, and underscores."
        )

    yaml_check = validate_yaml_safe(name, context="Invoker name")
    result.merge(yaml_check)

    if name.startswith("_"):
        result.add_warning(
            f"Invoker name '{name}' starts with underscore (private convention). "
            "Consider removing the leading underscore."
        )

    return result


def validate_param_name(name: str, invoker_name: str = "") -> InvokerValidationResult:
    """
    Validate a parameter name.

    Parameters
    ----------
    name : str
        The parameter name to validate.
    invoker_name : str
        Parent invoker name for context.

    Returns
    -------
    InvokerValidationResult
        Validation result.
    """
    result = InvokerValidationResult()
    context = f"{invoker_name}.{name}" if invoker_name else name

    if not name or not name.strip():
        return result.add_error(f"Parameter name in '{invoker_name}' must not be empty.")

    if not _PYTHON_IDENT.match(name):
        result.add_error(f"Parameter name '{context}' is not a valid Python identifier.")

    if name.lower() in RESERVED_PARAM_NAMES:
        result.add_warning(
            f"Parameter name '{context}' conflicts with reserved name '{name}'. "
            "Consider a more specific name."
        )

    yaml_check = validate_yaml_safe(name, context=f"Parameter name '{context}'")
    result.merge(yaml_check)

    return result


def sanitize_description(text: str) -> str:
    """
    Sanitize a description string for safe YAML embedding.

    Replaces YAML-unsafe characters with safe alternatives.

    Parameters
    ----------
    text : str
        The raw description text.

    Returns
    -------
    str
        Sanitized description safe for unquoted YAML values.
    """
    replacements: dict[str, str] = {
        ":": " -",
        "{": "(",
        "}": ")",
        "[": "(",
        "]": ")",
        "#": "",
        "&": "and",
        "*": "",
        "!": "",
        "|": " or ",
        ">": "",
        "'": "",
        '"': "",
        "%": " percent",
        "@": " at ",
        "`": "",
    }

    result = text
    for char, replacement in replacements.items():
        result = result.replace(char, replacement)

    # Collapse multiple spaces
    result = re.sub(r"\s+", " ", result).strip()
    return result
