"""
Sierra Validation and Safety Checker Module.

This module provides comprehensive validation for:
- Type safety of invoker parameters
- YAML safety (detects problematic characters)
- Parameter constraints and ranges
- Configuration file validation
- Invoker health diagnostics

Usage:
    from sierra.core.checker import SierraChecker
    
    checker = SierraChecker(client)
    issues = checker.validate_all()
    if issues:
        for issue in issues:
            print(issue)
"""

import re
import typing
from dataclasses import dataclass
from pathlib import Path

import sierra.abc.sierra as sierra_abc_sierra
import sierra.core.base as sierra_core_base
import sierra.invoker as sierra_invoker

if typing.TYPE_CHECKING:
    import pathlib


@dataclass
class ValidationIssue:
    """Represents a validation issue found during checking."""
    
    severity: str  # "error", "warning", "info"
    component: str  # "invoker", "parameter", "yaml", "config"
    name: str  # Name of the invoker/parameter/file
    message: str  # Description of the issue
    suggestion: str = ""  # Optional suggestion to fix
    
    def __str__(self) -> str:
        """Format issue for display."""
        icon = {"error": "❌", "warning": "⚠️", "info": "ℹ️"}.get(self.severity, "•")
        msg = f"{icon} [{self.severity.upper()}] {self.component}: {self.name}"
        msg += f"\n  {self.message}"
        if self.suggestion:
            msg += f"\n  💡 Suggestion: {self.suggestion}"
        return msg


class SierraChecker(sierra_core_base.SierraCoreObject):
    """
    Comprehensive validation and safety checker for Sierra SDK.
    
    Validates:
    - Type safety of parameters
    - YAML-unsafe characters in strings
    - Parameter naming conventions
    - Configuration file structure
    - Invoker health and completeness
    
    Parameters
    ----------
    client : SierraClient
        The Sierra client instance.
    
    Attributes
    ----------
    client : SierraClient
        The client instance.
    issues : list[ValidationIssue]
        Collected validation issues.
    """
    
    # YAML-unsafe characters that can break parsing
    YAML_UNSAFE_CHARS = {
        ":": "colon (breaks key-value parsing)",
        "{": "opening brace (template syntax)",
        "}": "closing brace (template syntax)",
        "[": "opening bracket (array syntax)",
        "]": "closing bracket (array syntax)",
        ",": "comma (list separator)",
        "&": "ampersand (anchor syntax)",
        "*": "asterisk (alias syntax)",
        "#": "hash (comment syntax)",
        "!": "exclamation (tag syntax)",
        "|": "pipe (literal block)",
        ">": "greater-than (folded block)",
        "'": "single quote (needs escaping)",
        '"': "double quote (needs escaping)",
        "%": "percent (directive syntax)",
        "@": "at-sign (reserved)",
        "`": "backtick (reserved)",
    }
    
    # Reserved parameter names that could conflict
    RESERVED_NAMES = {
        "self", "client", "args", "kwargs", "config", "environment",
        "logger", "result", "output", "input", "type", "name"
    }
    
    # Valid Python identifier pattern
    PYTHON_IDENTIFIER = re.compile(r'^[a-z_][a-z0-9_]*$', re.IGNORECASE)
    
    def __init__(self, client: typing.Any) -> None:
        """Initialize the checker with a Sierra client."""
        super().__init__(client)
        self.issues: list[ValidationIssue] = []
    
    def clear_issues(self) -> None:
        """Clear all collected issues."""
        self.issues = []
    
    def add_issue(
        self,
        severity: str,
        component: str,
        name: str,
        message: str,
        suggestion: str = ""
    ) -> None:
        """Add a validation issue to the collection."""
        self.issues.append(
            ValidationIssue(severity, component, name, message, suggestion)
        )
        self.client.logger.log(
            f"Validation {severity}: {component}.{name} - {message}",
            "debug" if severity == "info" else severity
        )
    
    def check_yaml_safety(self, text: str, context: str = "") -> list[str]:
        """
        Check if text contains YAML-unsafe characters.
        
        Parameters
        ----------
        text : str
            The text to check.
        context : str
            Context information for error messages.
        
        Returns
        -------
        list[str]
            List of unsafe characters found with descriptions.
        """
        unsafe = []
        for char, description in self.YAML_UNSAFE_CHARS.items():
            if char in text:
                unsafe.append(f"'{char}' ({description})")
        return unsafe
    
    def sanitize_yaml_text(self, text: str) -> str:
        """
        Sanitize text for safe YAML usage.
        
        Parameters
        ----------
        text : str
            The text to sanitize.
        
        Returns
        -------
        str
            Sanitized text with problematic characters handled.
        """
        # Replace problematic characters with safe alternatives
        replacements = {
            ":": " -",
            "{": "(",
            "}": ")",
            "[": "(",
            "]": ")",
        }
        
        result = text
        for char, replacement in replacements.items():
            result = result.replace(char, replacement)
        
        return result
    
    def validate_parameter_name(self, name: str, invoker_name: str) -> bool:
        """
        Validate that a parameter name follows best practices.
        
        Parameters
        ----------
        name : str
            Parameter name to validate.
        invoker_name : str
            Name of the invoker (for context).
        
        Returns
        -------
        bool
            True if valid, False otherwise.
        """
        is_valid = True
        
        # Check if it's a valid Python identifier
        if not self.PYTHON_IDENTIFIER.match(name):
            self.add_issue(
                "error",
                "parameter",
                f"{invoker_name}.{name}",
                f"Invalid parameter name '{name}' - must be a valid Python identifier",
                "Use lowercase letters, numbers, and underscores only"
            )
            is_valid = False
        
        # Check if it's reserved
        if name.lower() in self.RESERVED_NAMES:
            self.add_issue(
                "warning",
                "parameter",
                f"{invoker_name}.{name}",
                f"Parameter name '{name}' is reserved/commonly used",
                "Consider using a more specific name to avoid conflicts"
            )
        
        # Check naming conventions
        if name.startswith("_"):
            self.add_issue(
                "warning",
                "parameter",
                f"{invoker_name}.{name}",
                f"Parameter name '{name}' starts with underscore (private convention)",
                "Remove leading underscore for public parameters"
            )
        
        if name.isupper():
            self.add_issue(
                "warning",
                "parameter",
                f"{invoker_name}.{name}",
                f"Parameter name '{name}' is all uppercase (constant convention)",
                "Use lowercase or snake_case for parameters"
            )
        
        return is_valid
    
    def validate_parameter_description(
        self,
        description: str,
        param_name: str,
        invoker_name: str
    ) -> bool:
        """
        Validate parameter description for YAML safety.
        
        Parameters
        ----------
        description : str
            The parameter description.
        param_name : str
            Name of the parameter.
        invoker_name : str
            Name of the invoker.
        
        Returns
        -------
        bool
            True if safe, False if issues found.
        """
        if not description or description.strip() == "":
            self.add_issue(
                "warning",
                "parameter",
                f"{invoker_name}.{param_name}",
                "Missing parameter description",
                "Add a description in the docstring"
            )
            return False
        
        unsafe_chars = self.check_yaml_safety(description)
        if unsafe_chars:
            sanitized = self.sanitize_yaml_text(description)
            self.add_issue(
                "error",
                "parameter",
                f"{invoker_name}.{param_name}",
                f"Description contains YAML-unsafe characters: {', '.join(unsafe_chars)}",
                f"Use: '{sanitized}' instead"
            )
            return False
        
        return True
    
    def validate_type_safety(
        self,
        param: sierra_abc_sierra.SierraInvokerParam,
        invoker_name: str
    ) -> bool:
        """
        Validate type annotations for parameters.
        
        Parameters
        ----------
        param : SierraInvokerParam
            The parameter to validate.
        invoker_name : str
            Name of the invoker.
        
        Returns
        -------
        bool
            True if type is valid and safe.
        """
        param_name = param.get("Name")
        param_type = param.get("Type")
        
        # Check if type is specified
        if param_type is None:
            self.add_issue(
                "error",
                "parameter",
                f"{invoker_name}.{param_name}",
                "Missing type annotation",
                "Add type hint to parameter"
            )
            return False
        
        # Check for supported types
        supported_types = {int, str, float, bool, Path, type(None)}
        
        # Get the actual type (unwrap Optional if needed)
        actual_type = param_type
        if hasattr(param_type, "__args__"):  # Union/Optional type
            args = typing.get_args(param_type)
            actual_type = args[0] if args else param_type
        
        # Validate type is supported
        if actual_type not in supported_types and not (
            hasattr(actual_type, "__name__") and actual_type.__name__ == "Path"
        ):
            type_name = getattr(actual_type, "__name__", str(actual_type))
            self.add_issue(
                "warning",
                "parameter",
                f"{invoker_name}.{param_name}",
                f"Type '{type_name}' may not be fully supported",
                "Use: str, int, float, bool, or pathlib.Path"
            )
        
        return True
    
    def validate_invoker(self, invoker: "sierra_invoker.InvokerScript") -> bool:
        """
        Validate a complete invoker script.
        
        Parameters
        ----------
        invoker : InvokerScript
            The invoker to validate.
        
        Returns
        -------
        bool
            True if all validations pass.
        """
        all_valid = True
        invoker_name = invoker.name
        
        self.client.logger.log(f"🔍 Validating invoker: {invoker_name}", "debug")
        
        # Validate invoker name
        if not self.PYTHON_IDENTIFIER.match(invoker_name):
            self.add_issue(
                "error",
                "invoker",
                invoker_name,
                f"Invalid invoker name '{invoker_name}'",
                "Use only lowercase letters, numbers, and underscores"
            )
            all_valid = False
        
        # Validate description
        if not invoker.description or invoker.description.strip() == "":
            self.add_issue(
                "warning",
                "invoker",
                invoker_name,
                "Missing invoker description",
                "Add a description when creating InvokerScript"
            )
        else:
            unsafe_chars = self.check_yaml_safety(invoker.description)
            if unsafe_chars:
                sanitized = self.sanitize_yaml_text(invoker.description)
                self.add_issue(
                    "error",
                    "invoker",
                    invoker_name,
                    f"Description has YAML-unsafe characters: {', '.join(unsafe_chars)}",
                    f"Use: '{sanitized}'"
                )
                all_valid = False
        
        # Validate parameters
        if not invoker.params:
            self.add_issue(
                "warning",
                "invoker",
                invoker_name,
                "No parameters defined",
                "Add at least one parameter to the entry_point function"
            )
        
        for param in invoker.params:
            param_name = param.get("Name")
            param_desc = param.get("Description", "")
            
            # Validate parameter name
            if not self.validate_parameter_name(param_name, invoker_name):
                all_valid = False
            
            # Validate parameter description
            if not self.validate_parameter_description(
                param_desc, param_name, invoker_name
            ):
                all_valid = False
            
            # Validate type safety
            if not self.validate_type_safety(param, invoker_name):
                all_valid = False
        
        # Check for entry point
        if not hasattr(invoker, '_entry_point') or invoker._entry_point is None:
            self.add_issue(
                "error",
                "invoker",
                invoker_name,
                "No entry point defined",
                "Add @invoker.entry_point decorator to a function"
            )
            all_valid = False
        
        return all_valid
    
    def validate_config_yaml(self, config_path: Path) -> bool:
        """
        Validate the generated config.yaml file.
        
        Parameters
        ----------
        config_path : Path
            Path to config.yaml file.
        
        Returns
        -------
        bool
            True if config is valid.
        """
        if not config_path.exists():
            self.add_issue(
                "error",
                "config",
                str(config_path),
                "Config file does not exist",
                "Run 'python -m sierra build' to generate"
            )
            return False
        
        try:
            import yaml
            with open(config_path, 'r') as f:
                config_data = yaml.safe_load(f)
            
            if config_data is None:
                self.add_issue(
                    "error",
                    "config",
                    str(config_path),
                    "Config file is empty",
                    "Regenerate config with build command"
                )
                return False

            # Validate structure
            if "PATHS" not in config_data:
                self.add_issue(
                    "error",
                    "config",
                    str(config_path),
                    "Missing PATHS section",
                    "Regenerate config with build command"
                )
                return False
            
            if "SCRIPTS" not in config_data:
                self.add_issue(
                    "error",
                    "config",
                    str(config_path),
                    "Missing SCRIPTS section",
                    "Regenerate config with build command"
                )
                return False
            
            self.client.logger.log(
                f"✅ Config YAML validated successfully: {config_path}",
                "info"
            )
            return True
            
        except Exception as e:
            self.add_issue(
                "error",
                "config",
                str(config_path),
                f"YAML parsing error: {str(e)}",
                "Check for syntax errors, especially colons in descriptions"
            )
            return False
    
    def validate_all(self) -> list[ValidationIssue]:
        """
        Run all validations on registered invokers.
        
        Returns
        -------
        list[ValidationIssue]
            All issues found during validation.
        """
        self.clear_issues()
        
        self.client.logger.log("🔍 Starting comprehensive validation", "info")
        
        # Validate all invokers
        for invoker in self.client.invokers:
            self.validate_invoker(invoker)
        
        # Validate config if it exists
        config_path = self.client.environment.config_path / "config.yaml"
        if config_path.exists():
            self.validate_config_yaml(config_path)
        
        # Summary
        error_count = sum(1 for issue in self.issues if issue.severity == "error")
        warning_count = sum(1 for issue in self.issues if issue.severity == "warning")
        
        if error_count > 0:
            self.client.logger.log(
                f"❌ Validation failed: {error_count} errors, {warning_count} warnings",
                "error"
            )
        elif warning_count > 0:
            self.client.logger.log(
                f"⚠️ Validation passed with warnings: {warning_count} warnings",
                "warning"
            )
        else:
            self.client.logger.log(
                "✅ All validations passed successfully",
                "info"
            )
        
        return self.issues
    
    def health_check(self) -> dict[str, typing.Any]:
        """
        Perform a health check on the Sierra environment.
        
        Returns
        -------
        dict
            Health check results with status and details.
        """
        health = {
            "status": "healthy",
            "invokers_count": len(self.client.invokers),
            "issues": {
                "errors": 0,
                "warnings": 0,
                "info": 0
            },
            "checks": {}
        }
        
        issues = self.validate_all()
        
        # Count issues by severity
        for issue in issues:
            health["issues"][issue.severity + "s"] = (
                health["issues"].get(issue.severity + "s", 0) + 1
            )
        
        # Determine overall status
        if health["issues"]["errors"] > 0:
            health["status"] = "unhealthy"
        elif health["issues"]["warnings"] > 0:
            health["status"] = "degraded"
        
        # Add specific checks
        health["checks"]["config_exists"] = (
            self.client.environment.config_path / "config.yaml"
        ).exists()
        health["checks"]["invokers_path_exists"] = (
            self.client.environment.invokers_path.exists()
        )
        health["checks"]["venv_exists"] = (
            self.client.environment.venv_path.exists()
        )
        
        return health
