# Base Classes

The `sierra.abc.base` module provides foundational abstract classes for Sierra core objects, ensuring consistent initialization, configuration loading, and error handling.

??? example "Extending SierraCoreObject"
    ```python
    from sierra.abc.base import SierraCoreObject
    from sierra.internal.logger import UniversalLogger, LogLevel
    from sierra.client import SierraDevelopmentClient

    # Initialize a dummy client for demonstration
    client = SierraDevelopmentClient(logger=UniversalLogger(level=LogLevel.DEBUG))

    class MyCoreComponent(SierraCoreObject):
        """
        Example component that leverages SierraCoreObject for standardized behavior.
        """
        def __init__(self, client, name: str):
            super().__init__(client)
            self.name = name
            self.client.logger.log(f"MyCoreComponent '{self.name}' initialized", "info")

        def perform_action(self):
            self.client.logger.log(f"Performing action in {self.name}", "debug")

    # Usage
    component = MyCoreComponent(client, name="Example")
    component.perform_action()
    ```

::: sierra.abc.base
