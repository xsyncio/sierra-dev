# Builder

The `sierra.core.builder` module is responsible for building invoker scripts in the Sierra Dev. It provides functionality to assemble standalone scripts from invoker definitions, handling imports, dependencies, and entry points.

??? example "Creating a builder?"
    ```python
    import sierra

    # Define an InvokerScript
    invoker = sierra.InvokerScript(
        name="example",
        description="An example invoker script."
    )

    # Define the entry point
    @invoker.entry_point
    def run(param: sierra.Param[int, sierra.SierraOption(description="An integer parameter.")]) -> None:
        print(f"Running with parameter: {param}")

    # Use SierraInvokerBuilder to build the script
    builder = sierra.core.builder.SierraInvokerBuilder(client=sierra_client)
    script = builder.build(invoker)

    # Output the generated script
    print(script)
    ```

::: sierra.core.builder
