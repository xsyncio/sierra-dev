# Sierra Client

The `sierra.client` module exposes the `SierraDevelopmentClient` class, which orchestrates environment setup, script loading, caching, and compilation.

??? example "Initializing SierraDevelopmentClient"
    ```python
    import pathlib
    from sierra.client import SierraDevelopmentClient
    from sierra.internal.logger import UniversalLogger, LogLevel

    client = SierraDevelopmentClient(
        environment_path=pathlib.Path("default_env"),
        environment_name="default_env",
        logger=UniversalLogger(name="Sierra", level=LogLevel.DEBUG),
    )

    client.load_invokers_from_scripts()
    client.compiler.compile()
    ```

::: sierra.client
