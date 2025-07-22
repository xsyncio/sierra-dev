# Logger

The `sierra.internal.logger` module provides the `UniversalLogger` class for structured, leveled logging throughout Sierra‑SDK.

??? example "Using UniversalLogger"
    ```python
    from sierra.internal.logger import UniversalLogger, LogLevel

    # Create a logger that writes DEBUG+ messages
    logger = UniversalLogger(name="Sierra", level=LogLevel.DEBUG)

    # Log messages at various levels
    logger.log("Starting application", "info")
    logger.log("Detailed debug info", "debug")
    logger.log("A warning occurred", "warning")
    logger.log("An error occurred", "error")
    ```

::: sierra.internal.logger
