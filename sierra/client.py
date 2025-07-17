import pathlib
import typing

import httpx

import sierra.core.environment as sierra_core_environment
import sierra.core.loader as sierra_core_loader
import sierra.internal.cache as sierra_internal_cache
import sierra.internal.logger as sierra_internal_logger


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
        pass
        self.logger: sierra_internal_logger.UniversalLogger = kwargs.get(
            "logger", sierra_internal_logger.UniversalLogger()
        )
        self.logger.log("Sierra Development Client initialized.", "info")
        self.environment: sierra_core_environment.SierraDevelopmentEnvironment = sierra_core_environment.SierraDevelopmentEnvironment(
            client=self, name=environment_name, path=environment_path
        )
        self.logger.log(
            f"Environment initialized with name: {self.environment.name} at path: {self.environment.path}",
            "debug",
        )
        self.environment.init()
        self.logger.log("Environment initialized successfully.", "debug")
        self.cache: sierra_internal_cache.CacheManager = kwargs.get(
            "cache",
            sierra_internal_cache.CacheManager(
                cache_dir=self.environment.config_path / "cache"
            ),
        )
        self.logger.log("Cache manager initialized.", "debug")
        self.http_client: httpx.Client = httpx.Client(
            headers={"User-Agent": "Sierra-SDK/1.0"}
        )
        self.logger.log("HTTP client initialized.", "debug")
        self.loader: sierra_core_loader.SierraSideloader = (
            sierra_core_loader.SierraSideloader(client=self)
        )
        self.logger.log("Sierra sideloader initialized.", "debug")
        self.loader.populate()
        self.logger.log("Sierra sideloader populated with sources.", "debug")
