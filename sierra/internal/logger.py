import dataclasses
import datetime
import enum
import os
import pathlib
import sys
import typing

import colorama

# Initialize colorama for cross-platform ANSI coloring
colorama.init(autoreset=True)

LogTypeLiteral = typing.Literal["info", "warning", "debug", "error"]


class LogLevel(str, enum.Enum):
    """
    Logging verbosity levels.

    Attributes
    ----------
    NO_ERROR : str
        Suppress all messages.
    BASIC : str
        Log "info" and "warning".
    STANDARD : str
        Log "info", "warning", and "error".
    DEBUG : str
        Log all levels including "debug".
    """

    NO_ERROR = "no-error"
    BASIC = "basic"
    STANDARD = "standard"
    DEBUG = "debug"


class LogType(str, enum.Enum):
    """
    Types of log messages.

    Attributes
    ----------
    INFO : str
        Informational messages.
    WARNING : str
        Warning messages.
    DEBUG : str
        Debug messages.
    ERROR : str
        Error messages.
    """

    INFO = "info"
    WARNING = "warning"
    DEBUG = "debug"
    ERROR = "error"


class LoggerConfig(typing.TypedDict, total=False):
    """
    Configuration for UniversalLogger.

    Keys
    ----
    name : str
        Prefix for each log message. (required)
    level : LogLevel
        Minimum log level to emit. (default LogLevel.BASIC)
    log_file : pathlib.Path | str | None
        File path for persistent logging. (default None)
    clean_logs : bool
        If True, uses stdout.write for performance. (default True)
    enable_colors : bool
        If True, ANSI colors are applied. (default True)
    timestamp_format : str
        Format specifier for datetime. (default "%Y-%m-%d %H:%M:%S")
    buffer_size : int
        Max messages retained in buffer. (default 1000)
    auto_flush : bool
        Flush buffer when full. (default True)
    """

    name: str
    level: LogLevel
    log_file: typing.Union[str, pathlib.Path, None]
    clean_logs: bool
    enable_colors: bool
    timestamp_format: str
    buffer_size: int
    auto_flush: bool


@dataclasses.dataclass(frozen=True)
class LogColor:
    """ANSI color codes and emoji icons for log message components."""

    INFO: str = colorama.Fore.GREEN
    WARNING: str = colorama.Fore.YELLOW
    DEBUG: str = colorama.Fore.LIGHTBLACK_EX
    ERROR: str = colorama.Fore.RED
    TIMESTAMP: str = colorama.Fore.CYAN
    RESET: str = colorama.Fore.RESET
    
    # Emoji icons for visual enhancement
    ICON_INFO: str = "✅"
    ICON_WARNING: str = "⚠️"
    ICON_DEBUG: str = "🔍"
    ICON_ERROR: str = "❌"


class LogBuffer:
    """
    In-memory FIFO buffer for log entries.

    Parameters
    ----------
    max_size : int
        Maximum entries to retain.
    """

    def __init__(self, max_size: int = 1000) -> None:
        self.messages: list[str] = []
        self.max_size: int = max_size

    def add(self, message: str) -> None:
        """
        Add a log entry to the buffer.

        Parameters
        ----------
        message : str
            Formatted log message.
        """
        self.messages.append(message)
        if len(self.messages) > self.max_size:
            self.messages.pop(0)

    def flush(self) -> list[str]:
        """
        Clear buffer and return all entries.

        Returns
        -------
        list[str]
            All buffered messages before clearing.
        """
        entries: list[str] = self.messages[:]
        self.messages.clear()
        return entries

    def get_all(self) -> list[str]:
        """
        Retrieve buffer contents without clearing.

        Returns
        -------
        list[str]
            Current buffered messages.
        """
        return self.messages[:]


class UniversalLogger:
    """
    Main logger class integrating console, file, and buffer outputs.

    Attributes
    ----------
    name : str
        Logger name (required in __init__ kwargs).
    level : LogLevel
        Minimum log level to display.
    clean_logs : bool
        Whether to use emoji-free output.

    Raises
    ------
    ValueError
        If 'name' is missing or empty.
    OSError
        If log file directory or file cannot be created.
    """

    _LEVEL_MAP: typing.ClassVar[dict[LogLevel, set[LogTypeLiteral]]] = {
        LogLevel.NO_ERROR: set(),
        LogLevel.BASIC: {"info", "warning"},
        LogLevel.STANDARD: {"info", "warning", "error"},
        LogLevel.DEBUG: {"info", "warning", "debug", "error"},
    }

    def __init__(self, **kwargs: typing.Unpack[LoggerConfig]) -> None:
        name: str = kwargs.get("name", "Sierra")
        self.name: str = name
        # Apply defaults
        self.level: LogLevel = kwargs.get("level", LogLevel.BASIC)  # type: ignore[arg-type]
        raw_log_file: typing.Union[str, pathlib.Path, None] = kwargs.get(
            "log_file"
        )  # type: ignore[assignment]
        self.log_file_path: typing.Optional[pathlib.Path] = (
            pathlib.Path(raw_log_file) if raw_log_file else None
        )
        self.clean_logs: bool = kwargs.get("clean_logs", True)  # type: ignore[arg-type]
        self.enable_colors: bool = kwargs.get("enable_colors", True)  # type: ignore[arg-type]
        self.timestamp_format: str = kwargs.get(
            "timestamp_format", "%Y-%m-%d %H:%M:%S"
        )  # type: ignore[arg-type]
        self.buffer_size: int = kwargs.get("buffer_size", 1000)  # type: ignore[arg-type]
        self.auto_flush: bool = kwargs.get("auto_flush", True)  # type: ignore[arg-type]

        self.colors: LogColor = LogColor()
        self.buffer: LogBuffer = LogBuffer(self.buffer_size)

        self._validate_config()
        self.log("Logger initialized", "debug")

    def _validate_config(self) -> None:
        """
        Validate configuration and prepare log file.

        Raises
        ------
        OSError
            If file or directory creation fails.
        """
        if self.log_file_path:
            os.makedirs(self.log_file_path.parent, exist_ok=True)
            self.log_file_path.touch(exist_ok=True)

    def _timestamp(self) -> str:
        """
        Generate formatted timestamp.

        Returns
        -------
        str
            Timestamp, colored if enabled.
        """
        now: str = (
            datetime.datetime.now()
            .astimezone()
            .strftime(self.timestamp_format)
        )
        if self.enable_colors:
            return f"{self.colors.TIMESTAMP}{now}{self.colors.RESET}"
        return now

    def _format(self, msg: str, typ: LogTypeLiteral) -> str:
        """
        Build the final log string.

        Parameters
        ----------
        msg : str
            Core message.
        typ : Literal["info","warning","debug","error"]
            Severity indicator.

        Returns
        -------
        str
            Fully formatted and optionally colored log line.
        """
        level_cap: str = typ.capitalize()
        ts: str = self._timestamp()
        icon: str = getattr(self.colors, f"ICON_{typ.upper()}", "")
        
        if self.enable_colors:
            color_code: str = getattr(self.colors, typ.upper())
            return f"{self.name}: {ts} - {icon} {level_cap} - {color_code}{msg}{self.colors.RESET}"
        return f"{self.name}: {ts} - {icon} {level_cap} - {msg}"

    def _should_log(self, typ: LogTypeLiteral) -> bool:
        """
        Decide if message passes current level filter.

        Parameters
        ----------
        typ : Literal["info","warning","debug","error"]
            Message type.

        Returns
        -------
        bool
            True if allowed by level.
        """
        allowed: set[LogTypeLiteral] = UniversalLogger._LEVEL_MAP[self.level]
        return typ in allowed

    def _write_file(self, line: str) -> None:
        """
        Append a line to the log file, if configured.

        Parameters
        ----------
        line : str
            Full formatted log line.
        """
        if not self.log_file_path:
            return
        try:
            with self.log_file_path.open("a", encoding="utf-8") as handle:
                handle.write(line + "\n")
        except Exception as err:
            sys.stderr.write(f"File log error: {err}\n")

    def log(self, message: str, log_type: LogTypeLiteral) -> None:
        """
        Emit a log entry.

        Parameters
        ----------
        message : str
            Content of the log.
        log_type : Literal["info","warning","debug","error"]
            Severity level.
        """
        if not self._should_log(log_type):
            return

        line: str = self._format(message, log_type)
        self.buffer.add(line)

        if self.clean_logs:
            sys.stdout.write(line + "\n")
            sys.stdout.flush()
        else:
            print(line)

        self._write_file(line)

        if self.auto_flush and len(self.buffer.messages) >= self.buffer_size:
            self.flush_buffer()

    def flush_buffer(self) -> list[str]:
        """
        Flush and retrieve buffered messages.

        Returns
        -------
        list[str]
            All buffered lines before flush.
        """
        return self.buffer.flush()

    def get_logs(self) -> list[str]:
        """
        Get buffered messages without flushing.

        Returns
        -------
        list[str]
            Current buffer contents.
        """
        return self.buffer.get_all()

    @staticmethod
    def clear_console() -> None:
        """Clear the terminal screen."""
        sys.stdout.write("\033[H\033[J")
        sys.stdout.flush()
