# Abstract Base Classes

The `sierra.abc.sierra` module defines base protocols and classes for building custom Sierra components, such as invoker parameters and plugin interfaces.

??? example "Working with SierraInvokerParam"
    ```python
    from sierra.abc.sierra import SierraInvokerParam, SierraCoreObject

    # Create a parameter definition
    param = SierraInvokerParam(
        Name="domain",
        Type=str,
        Description="The domain to query",
        Options="MANDATORY"
    )

    # SierraCoreObject provides common initialization for core components
    class MyComponent(SierraCoreObject):
        def __init__(self, client):
            super().__init__(client)
            client.logger.log("MyComponent initialized", "info")
    ```

::: sierra.abc.sierra
