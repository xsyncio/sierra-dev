import importlib.util
import pathlib
import typing

import httpx

import sierra.core.builder as sierra_core_builder
import sierra.core.environment as sierra_core_environment
import sierra.core.loader as sierra_core_loader
import sierra.internal.cache as sierra_internal_cache
import sierra.internal.errors as sierra_internal_errors
import sierra.internal.logger as sierra_internal_logger
import sierra.invoker as sierra_invoker


class InvokerWithLoad(typing.Protocol):
    def load(self, client: "SierraDevelopmentClient") -> None: ...


class ClientParams(typing.TypedDict, total=False):
    logger: sierra_internal_logger.UniversalLogger
    cache: sierra_internal_cache.CacheManager


class SierraDevelopmentClient:
    def __init__(
        self,
        environment_path: pathlib.Path = pathlib.Path.cwd(),
        environment_name: str = "default_env",
        **kwargs: typing.Unpack[ClientParams],
    ) -> None:
        """
        Initialize the Sierra Development Client.

        Parameters
        ----------
        environment_path : pathlib.Path
            Path to the root of the Sierra environment.
        environment_name : str
            Name of the environment configuration to load.
        **kwargs : ClientParams
            Optional: logger and cache manager.
        """
        # Logger setup
        self.logger: sierra_internal_logger.UniversalLogger = kwargs.get(
            "logger", sierra_internal_logger.UniversalLogger()
        )
        self.logger.log("Logger initialized", "debug")
        self.logger.log(
            "Sierra Development Client initialization started", "info"
        )

        # Environment setup
        self.environment: sierra_core_environment.SierraDevelopmentEnvironment = sierra_core_environment.SierraDevelopmentEnvironment(
            client=self,
            name=environment_name,
            path=environment_path,
        )
        self.logger.log(
            f"Environment created: name={self.environment.name}, path={self.environment.path}",
            "debug",
        )
        self.environment.init()
        self.logger.log("Environment initialized successfully", "debug")

        # Cache manager setup
        self.cache: sierra_internal_cache.CacheManager = kwargs.get(
            "cache",
            sierra_internal_cache.CacheManager(
                cache_dir=self.environment.config_path / "cache"
            ),
        )
        self.logger.log("Cache manager initialized", "debug")

        # HTTP client setup
        self.http_client: httpx.Client = httpx.Client(
            headers={"User-Agent": "Sierra-SDK/1.0"}
        )
        self.logger.log("HTTP client initialized", "debug")

        # Sideloader setup
        self.loader: sierra_core_loader.SierraSideloader = (
            sierra_core_loader.SierraSideloader(client=self)
        )
        self.logger.log("Sideloader initialized", "debug")
        self.loader.populate()
        self.logger.log(
            f"Sideloader populated with sources {len(self.loader.sources)}",
            "debug",
        )

        # Invokers list
        self.invokers: list[sierra_invoker.InvokerScript] = []
        self.logger.log("Client ready to load invokers", "info")
        self.builder = sierra_core_builder.SierraInvokerBuilder(client=self)

    def load_invoker(self, invoker: "sierra_invoker.InvokerScript") -> None:
        """
        Register a single invoker instance with the client.

        Parameters
        ----------
        invoker : InvokerScript
            An instance of an InvokerScript.
        """
        if invoker not in self.invokers:
            self.invokers.append(invoker)
            self.logger.log(f"Invoker registered: {invoker.name}", "debug")
        else:
            self.logger.log(
                f"Invoker already registered: {invoker.name}", "warning"
            )

    def unload_invoker(self, invoker: "sierra_invoker.InvokerScript") -> None:
        """Unregister a single invoker instance from the client."""
        if invoker in self.invokers:
            self.invokers.remove(invoker)
            self.logger.log(f"Invoker unregistered: {invoker.name}", "debug")
        else:
            self.logger.log(f"Invoker not found: {invoker.name}", "warning")

    def load_invokers_from_scripts(self) -> None:
        """
        Automatically discover and load all InvokerScript subclasses
        from .py files in the environment's scripts directory.
        """
        script_dir: pathlib.Path = self.environment.scripts_path.resolve()
        self.logger.log(
            f"Loading invokers from directory: {script_dir}", "info"
        )

        if not script_dir.is_dir():
            raise sierra_internal_errors.SierraClientPathError(
                f"Invalid scripts directory: {script_dir}"
            )

        for file_path in script_dir.iterdir():
            if not file_path.is_file() or file_path.suffix != ".py":
                continue
            self.logger.log(f"Processing file: {file_path.name}", "debug")
            try:
                self._load_invoker_file(file_path)
            except Exception as e:
                self.logger.log(
                    f"Failed to load invoker from {file_path.name}: {e}",
                    "error",
                )

    def _load_invoker_file(
        self, path_to_invoker: typing.Union[str, pathlib.Path]
    ) -> None:
        """
        Import a module, automatically register its InvokerScript instances,
        then invoke each's load() method for setup.
        """
        path_obj: pathlib.Path = pathlib.Path(path_to_invoker).resolve()
        self.logger.log(f"Importing module from: {path_obj}", "debug")

        if not path_obj.is_file() or path_obj.suffix != ".py":
            raise sierra_internal_errors.SierraClientPathError(
                f"Invalid invoker file: {path_obj}"
            )

        spec = importlib.util.spec_from_file_location(path_obj.stem, path_obj)
        if not spec or not spec.loader:
            raise sierra_internal_errors.SierraClientPathError(
                f"Cannot create spec for module: {path_obj}"
            )

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)  # type: ignore
        self.logger.log(f"Module imported: {path_obj.name}", "debug")

        # Discover all InvokerScript instances in module
        found: list[sierra_invoker.InvokerScript] = []
        for obj in vars(module).values():
            if isinstance(obj, sierra_invoker.InvokerScript):
                found.append(obj)

        if not found:
            raise sierra_internal_errors.SierraClientLoadError(
                f"No InvokerScript instance found in {path_obj.name}"
            )

        # Register and load each invoker
        for inv in found:
            self.logger.log(f"Registering invoker: {inv.name}", "debug")
            self.load_invoker(inv)
            loader = typing.cast("InvokerWithLoad", inv)
            if hasattr(inv, "load") and callable(loader.load):
                self.logger.log(f"Executing load() for: {inv.name}", "debug")
                try:
                    loader.load(self)
                    self.logger.log(f"Loaded invoker: {inv.name}", "info")
                except Exception as err:
                    self.logger.log(
                        f"Error during load() of {inv.name}: {err}",
                        "error",
                    )

        self.logger.log(
            f"Finished processing {path_obj.name}, total invokers found: {len(found)}",
            "debug",
        )
