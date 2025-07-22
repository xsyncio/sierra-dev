# Loader

The `sierra.core.loader` module is responsible for loading compiled Sierra invoker scripts.

??? example "Loading an invoker"
    ```python
    import sierra

    # Create an instance of SierraSideloader with the Sierra client
    loader = sierra.SierraSideloader(client=...)

    # Populate the sideloader by pulling new files from all sources
    # This will cache all valid `.py` scripts from the configured sources
    loader.populate()
    ```

:::sierra.core.loader
