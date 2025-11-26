"""
Tests for UniversalLogger.
"""
import pytest
from sierra.internal.logger import UniversalLogger, LogLevel, LogType


class TestUniversalLogger:
    """Test UniversalLogger functionality."""
    
    def test_logger_initialization(self):
        """Test logger can be initialized."""
        logger = UniversalLogger(name="TestLogger", enable_colors=False)
        assert logger.name == "TestLogger"
        assert logger.level == LogLevel.BASIC
    
    def test_logger_with_debug_level(self):
        """Test logger with debug level."""
        logger = UniversalLogger(name="Debug", level=LogLevel.DEBUG, enable_colors=False)
        assert logger.level == LogLevel.DEBUG
    
    def test_log_info_message(self, capsys):
        """Test logging info message."""
        logger = UniversalLogger(name="Test", enable_colors=False)
        logger.log("Test message", LogType.INFO)
        
        captured = capsys.readouterr()
        assert "Test message" in captured.out
        assert "Info" in captured.out
    
    def test_log_error_message(self, capsys):
        """Test logging error message."""
        # Error requires STANDARD level or higher
        logger = UniversalLogger(name="Test", level=LogLevel.STANDARD, enable_colors=False)
        logger.log("Error occurred", LogType.ERROR)
        
        captured = capsys.readouterr()
        assert "Error occurred" in captured.out
        assert "Error" in captured.out
    
    def test_log_warning_message(self, capsys):
        """Test logging warning message."""
        logger = UniversalLogger(name="Test", level=LogLevel.STANDARD, enable_colors=False)
        logger.log("Warning message", LogType.WARNING)
        
        captured = capsys.readouterr()
        assert "Warning message" in captured.out
    
    def test_log_debug_message_with_debug_level(self, capsys):
        """Test debug messages appear with DEBUG level."""
        logger = UniversalLogger(name="Test", level=LogLevel.DEBUG, enable_colors=False)
        logger.log("Debug info", LogType.DEBUG)
        
        captured = capsys.readouterr()
        assert "Debug info" in captured.out
    
    def test_log_debug_message_without_debug_level(self, capsys):
        """Test debug messages hidden without DEBUG level."""
        logger = UniversalLogger(name="Test", level=LogLevel.STANDARD, enable_colors=False)
        logger.log("Debug info", LogType.DEBUG)
        
        captured = capsys.readouterr()
        assert "Debug info" not in captured.out
    
    def test_emoji_icons_in_output(self, capsys):
        """Test that emoji icons appear in output."""
        logger = UniversalLogger(name="Test", enable_colors=False)
        logger.log("Success", LogType.INFO)
        
        captured = capsys.readouterr()
        # Should contain emoji (✅, ⚠️, ❌, or 🔍)
        assert any(emoji in captured.out for emoji in ["✅", "⚠️", "❌", "🔍"])


@pytest.mark.unit
class TestLogLevel:
    """Test LogLevel enum."""
    
    def test_log_levels_exist(self):
        """Test all log levels are defined."""
        assert LogLevel.NO_ERROR == "no-error"
        assert LogLevel.BASIC == "basic"
        assert LogLevel.STANDARD == "standard"
        assert LogLevel.DEBUG == "debug"


@pytest.mark.unit
class TestLogType:
    """Test LogType enum."""
    
    def test_log_types_exist(self):
        """Test all log types are defined."""
        assert LogType.INFO == "info"
        assert LogType.WARNING == "warning"
        assert LogType.DEBUG == "debug"
        assert LogType.ERROR == "error"
