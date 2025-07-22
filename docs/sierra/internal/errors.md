# Error Definitions

The `sierra.internal.errors` module defines all custom exception types used throughout sierra-dev, enabling precise error handling and logging.

??? example "Common Sierra errors"
    ```python
    import sierra.internal.errors as errors

    try:
        # Simulate a missing scripts directory
        raise errors.SierraClientPathError("Invalid path: ./scripts")
    except errors.SierraClientPathError as e:
        print(f"Caught client path error: {e}")

    try:
        # Simulate a module load failure
        raise errors.SierraClientLoadError("No invoker found in module")
    except errors.SierraClientLoadError as e:
        print(f"Caught load error: {e}")

    try:
        # Simulate a runtime failure in an invoker
        raise errors.SierraExecutionError("Script runtime exception")
    except errors.SierraExecutionError as e:
        print(f"Caught execution error: {e}")
    ```

::: sierra.internal.errors
