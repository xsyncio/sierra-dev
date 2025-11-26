"""
Tests for TypeSafetyValidator.
"""
import pytest
from pathlib import Path

from sierra.package_manager.type_validator import TypeSafetyValidator, ValidationError, validate_invoker_script


class TestValidationError:
    """Test ValidationError dataclass."""
    
    def test_validation_error_creation(self):
        """Test creating a validation error."""
        error = ValidationError(
            line=10,
            column=5,
            message="Missing type annotation",
            severity="error"
        )
        assert error.line == 10
        assert error.column == 5
        assert error.severity == "error"
    
    def test_validation_error_str(self):
        """Test validation error string representation."""
        error = ValidationError(line=1, column=0, message="Test error", severity="error")
        error_str = str(error)
        assert "Line 1:0" in error_str
        assert "Test error" in error_str
        assert "❌" in error_str
    
    def test_validation_warning_str(self):
        """Test validation warning string representation."""
        warning = ValidationError(line=5, column=2, message="Test warning", severity="warning")
        warning_str = str(warning)
        assert "⚠️" in warning_str


class TestTypeSafetyValidator:
    """Test TypeSafetyValidator class."""
    
    def test_validator_initialization(self, mock_logger):
        """Test initializing validator."""
        validator = TypeSafetyValidator(logger=mock_logger)
        assert validator.errors == []
    
    def test_validate_script_with_types(self, temp_dir, mock_logger):
        """Test validating script with proper types."""
        script_path = temp_dir / "test.py"
        script_path.write_text('''
def test_function(param: str) -> None:
    """Test function."""
    print(param)
''')
        
        validator = TypeSafetyValidator(logger=mock_logger)
        errors = validator.validate_script(script_path)
        
        # Should have no errors for properly typed function
        error_count = sum(1 for e in errors if e.severity == "error")
        assert error_count == 0
    
    def test_validate_script_missing_return_type(self, temp_dir, mock_logger):
        """Test validating script with missing return type."""
        script_path = temp_dir / "test.py"
        script_path.write_text('''
def test_function(param: str):  # Missing return type
    """Test function."""
    print(param)
''')
        
        validator = TypeSafetyValidator(logger=mock_logger)
        errors = validator.validate_script(script_path)
        
        # Should have error for missing return type
        error_messages = [e.message for e in errors]
        assert any("return type" in msg.lower() for msg in error_messages)
    
    def test_validate_script_missing_param_type(self, temp_dir, mock_logger):
        """Test validating script with missing parameter type."""
        script_path = temp_dir / "test.py"
        script_path.write_text('''
def test_function(param) -> None:  # Missing parameter type
    """Test function."""
    print(param)
''')
        
        validator = TypeSafetyValidator(logger=mock_logger)
        errors = validator.validate_script(script_path)
        
        # Should have error for missing parameter type
        error_count = sum(1 for e in errors if e.severity == "error")
        assert error_count > 0
    
    def test_validate_script_with_any_type(self, temp_dir, mock_logger):
        """Test validating script with Any type (should warn)."""
        script_path = temp_dir / "test.py"
        script_path.write_text('''
import typing

def test_function(param: typing.Any) -> None:
    """Test function."""
    print(param)
''')
        
        validator = TypeSafetyValidator(logger=mock_logger)
        errors = validator.validate_script(script_path)
        
        # Should have warning for Any type
        warning_count = sum(1 for e in errors if e.severity == "warning")
        assert warning_count > 0
    
    def test_validate_script_syntax_error(self, temp_dir, mock_logger):
        """Test validating script with syntax error."""
        script_path = temp_dir / "test.py"
        script_path.write_text('''
def test_function(param: str) -> None
    print(param)  # Missing colon
''')
        
        validator = TypeSafetyValidator(logger=mock_logger)
        errors = validator.validate_script(script_path)
        
        # Should have syntax error
        assert any("syntax" in e.message.lower() for e in errors)
    
    def test_validate_multiple_functions(self, temp_dir, mock_logger):
        """Test validating script with multiple functions."""
        script_path = temp_dir / "test.py"
        script_path.write_text('''
def func1(x: int) -> int:
    return x * 2

def func2(y):  # Missing types
    return y

def func3(z: str) -> str:
    return z.upper()
''')
        
        validator = TypeSafetyValidator(logger=mock_logger)
        errors = validator.validate_script(script_path)
        
        # Should have errors from func2 only
        error_count = sum(1 for e in errors if e.severity == "error")
        assert error_count > 0


@pytest.mark.unit
class TestValidateInvokerScriptFunction:
    """Test the validate_invoker_script helper function."""
    
    def test_validate_valid_script(self, temp_dir):
        """Test validating a valid script."""
        script_path = temp_dir / "valid.py"
        script_path.write_text('''
def run(target: str) -> None:
    """Entry point."""
    print(target)
''')
        
        is_valid, report = validate_invoker_script(script_path)
        assert is_valid is True
    
    def test_validate_invalid_script(self, temp_dir):
        """Test validating an invalid script."""
        script_path = temp_dir / "invalid.py"
        script_path.write_text('''
def run(target):  # Missing types
    print(target)
''')
        
        is_valid, report = validate_invoker_script(script_path)
        assert is_valid is False
        assert len(report) > 0
    
    def test_validate_script_with_warnings_only(self, temp_dir):
        """Test script with only warnings passes."""
        script_path = temp_dir / "warnings.py"
        script_path.write_text('''
import typing

def run(data: typing.Any) -> None:  # Any type warning
    """Entry point."""
    print(data)
''')
        
        is_valid, report = validate_invoker_script(script_path)
        # Should be valid (warnings don't fail)
        assert is_valid is True
