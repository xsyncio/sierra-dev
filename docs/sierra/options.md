# Options

In Sierra‑SDK, every Invoker entry‑point parameter must be wrapped with `Param[...]`, supplying a `SierraOption` to describe its behavior and validation rules.

??? example "Options Example"
    ```python
    import sierra

    def example(foo: sierra.Param[str, sierra.SierraOption(description="Foo is a foo")])->None:
    """
    Foo is a string, the options add a metadata called description.
    """
    result = sierra.create_tree_result([f"{foo}"])
    print(result)
    ```

::: sierra.options
