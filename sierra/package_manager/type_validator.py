"""
Type-safe script validator for Sierra invokers.

Enforces type safety when converting scripts to invokers.
"""

import ast
import typing
from pathlib import Path
from dataclasses import dataclass

from sierra.internal.logger import UniversalLogger


@dataclass
class ValidationError:
    """Represents a type safety validation error."""
    
    line: int
    column: int
    message: str
    severity: str = "error"
    
    def __str__(self) -> str:
        """Format error for display."""
        icon = {"error": "❌", "warning": "⚠️"}.get(self.severity, "•")
        return f"{icon} Line {self.line}:{self.column} - {self.message}"


class TypeSafetyValidator:
    """
    Validates invoker scripts for type safety.
    
    Ensures:
    - All function parameters have type annotations
    - Entry point has proper type hints
    - No unsafe type usage
    - Proper return type annotations
    """
    
    def __init__(self, logger: UniversalLogger | None = None):
        """Initialize validator."""
        self.logger = logger or UniversalLogger(name="TypeSafetyValidator")
        self.errors: list[ValidationError] = []
    
    def validate_script(self, script_path: Path) -> list[ValidationError]:
        """
        Validate a script for type safety.
        
        Parameters
        ----------
        script_path : Path
            Path to script file
        
        Returns
        -------
        list[ValidationError]
            List of validation errors found
        """
        self.logger.log(f"Validating script for type safety: {script_path.name}", "debug")
        self.errors = []
        
        try:
            with open(script_path, 'r') as f:
                source = f.read()
            
            tree = ast.parse(source, filename=str(script_path))
            self._validate_ast(tree)
            
            error_count = sum(1 for e in self.errors if e.severity == "error")
            warning_count = sum(1 for e in self.errors if e.severity == "warning")
            self.logger.log(f"Validation complete: {error_count} errors, {warning_count} warnings", "debug")
            
        except SyntaxError as e:
            self.logger.log(f"Syntax error in {script_path.name}: {e.msg}", "error")
            self.errors.append(
                ValidationError(
                    line=e.lineno or 0,
                    column=e.offset or 0,
                    message=f"Syntax error: {e.msg}",
                    severity="error"
                )
            )
        
        return self.errors
    
    def _validate_ast(self, tree: ast.AST) -> None:
        """Validate AST for type safety."""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                self._validate_function(node)
    
    def _validate_function(self, node: ast.FunctionDef) -> None:
        """
        Validate a function definition.
        
        Checks:
        - Return type annotation exists
        - All parameters have type annotations
        - No use of 'Any' type (enforces specificity)
        """
        # Check return annotation
        if node.returns is None:
            self.errors.append(
                ValidationError(
                    line=node.lineno,
                    column=node.col_offset,
                    message=f"Function '{node.name}' missing return type annotation",
                    severity="error"
                )
            )
        
        # Check parameter annotations
        for arg in node.args.args:
            if arg.arg == 'self':  # Skip self parameter
                continue
            
            if arg.annotation is None:
                self.errors.append(
                    ValidationError(
                        line=arg.lineno,
                        column=arg.col_offset,
                        message=f"Parameter '{arg.arg}' in '{node.name}' missing type annotation",
                        severity="error"
                    )
                )
            else:
                # Check for 'Any' type usage
                if self._is_any_type(arg.annotation):
                    self.errors.append(
                        ValidationError(
                            line=arg.lineno,
                            column=arg.col_offset,
                            message=f"Parameter '{arg.arg}' uses 'Any' type - please use specific type",
                            severity="warning"
                        )
                    )
    
    def _is_any_type(self, annotation: ast.AST) -> bool:
        """Check if annotation is typing.Any."""
        if isinstance(annotation, ast.Name):
            return annotation.id == 'Any'
        elif isinstance(annotation, ast.Attribute):
            return annotation.attr == 'Any'
        return False
    
    def has_errors(self) -> bool:
        """Check if any errors were found."""
        return any(e.severity == "error" for e in self.errors)
    
    def format_report(self) -> str:
        """
        Format validation report.
        
        Returns
        -------
        str
            Formatted report of all errors/warnings
        """
        if not self.errors:
            return "✅ Type safety validation passed"
        
        lines = ["\n🔍 Type Safety Validation Report:\n"]
        
        errors = [e for e in self.errors if e.severity == "error"]
        warnings = [e for e in self.errors if e.severity == "warning"]
        
        if errors:
            lines.append("ERRORS:")
            for error in errors:
                lines.append(f"  {error}")
            lines.append("")
        
        if warnings:
            lines.append("WARNINGS:")
            for warning in warnings:
                lines.append(f"  {warning}")
            lines.append("")
        
        lines.append(f"Summary: {len(errors)} errors, {len(warnings)} warnings\n")
        
        return "\n".join(lines)


def validate_invoker_script(script_path: Path) -> tuple[bool, str]:
    """
    Validate an invoker script for type safety.
    
    Parameters
    ----------
    script_path : Path
        Path to script file
    
    Returns
    -------
    tuple[bool, str]
        (is_valid, report) - True if valid, formatted report
    """
    validator = TypeSafetyValidator()
    validator.validate_script(script_path)
    
    report = validator.format_report()
    is_valid = not validator.has_errors()
    
    return is_valid, report
