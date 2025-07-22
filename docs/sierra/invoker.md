# Invoker

Define and manage invoker scripts in the Sierra Dev. Invoker scripts are used to execute specific actions in a controlled environment.

??? example "Invoker Example"
    ```python
    import sierra

    # Define an InvokerScript with dependencies and an entry point
    invoker = sierra.InvokerScript(
        name="example",
        description="An example invoker script."
    )

    @invoker.dependency
    def helper_function(param: int) -> int:
        return param + 1

    @invoker.entry_point
    def run(param: sierra.Param[int, sierra.SierraOption(description="An integer parameter.")]) -> None:
        result = helper_function(param)
        print(f"Result: {result}")

    # Register the invoker
    sierra.register_invoker(invoker)
    ```

::: sierra.invoker
