# Compiler

The `sierra.core.compiler` module is responsible for taking registered invoker scripts and producing standalone Python scripts along with the corresponding YAML configuration.

??? example "Compiling invoker scripts"
    ```python
    import pathlib
    import sierra

    # Initialize your SierraDevelopmentClient
    client = sierra.SierraDevelopmentClient(
        environment_path=pathlib.Path("default_env"),
        environment_name="default_env",
        logger=sierra.UniversalLogger(name="Sierra", level=sierra.sierra_internal_logger.LogLevel.DEBUG),
    )

    # Discover and register all invokers
    client.load_invokers_from_scripts()

    # Compile into standalone scripts and config.yaml
    client.compiler.compile()
    ```

::: sierra.core.compiler
