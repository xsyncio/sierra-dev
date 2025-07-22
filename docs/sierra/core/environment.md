# Environment

The `sierra.core.environment` module handles creation, initialization, and teardown of the on‑disk Sierra development environment—setting up config directories, the virtualenv, scripts folder, and more.

??? example "Initializing your Sierra environment"
    ```python
    import pathlib
    import sierra.core.environment as environment

    # Given a SierraDevelopmentClient instance `client`...
    project_root = pathlib.Path("/path/to/project")
    env = environment.SierraDevelopmentEnvironment(
        client=client,
        name="default_env",            # logical environment name
        path=project_root      # base path for all Sierra files
    )

    # Create config/, scripts/, venv/, invokers/ directories
    env.init()
    ```

:::sierra.core.environment
