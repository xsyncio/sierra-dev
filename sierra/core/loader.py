import pathlib
import typing

import sierra.core.base as sierra_core_base
import sierra.internal.errors as sierra_internal_errors

if typing.TYPE_CHECKING:
    import sierra.client as sierra_client


class SierraSideloader(sierra_core_base.SierraCoreObject):
    """
    A sideloader that mimics APT-like behavior for fetching and managing Python invoker scripts
    from GitHub sources. Handles downloading, caching, and installing .py files only.

    Parameters
    ----------
    client : sierra_client.SierraDevelopmentClient
        A reference to the Sierra development client.
    """

    def __init__(
        self, client: "sierra_client.SierraDevelopmentClient"
    ) -> None:
        self.client = client
        self.cache = self.client.cache
        self.path: pathlib.Path = self.client.environment.config_path

        self.client.logger.log("Initializing SierraSideloader...", "info")

        if not self.path.exists():
            self.client.logger.log(
                f"Missing config path: {self.path}", "error"
            )
            raise sierra_internal_errors.SierraPathError(
                f"Path {self.path} does not exist."
            )

        source_path = self.path / "source"
        if not source_path.exists():
            self.client.logger.log(
                f"Missing source file: {source_path}", "error"
            )
            raise sierra_internal_errors.SierraPathError(
                f"File {source_path} does not exist."
            )

        if source_path.stat().st_size == 0:
            self.client.logger.log(
                f"Source file is empty: {source_path}", "warning"
            )
            raise sierra_internal_errors.SierraPathError(
                f"File {source_path} is empty."
            )

        with open(source_path, "r", encoding="utf-8") as f:
            self.sources: typing.List[str] = [
                line.strip() for line in f if line.strip()
            ]

        self.client.logger.log(
            f"Loaded {len(self.sources)} sources from {source_path}", "debug"
        )
        super().__init__(client)

    def _get_github_data(self, url: str) -> typing.Dict[str, typing.Any]:
        """Fetch GitHub API data with proper error handling."""
        self.client.logger.log(f"Fetching GitHub data: {url}", "debug")
        response = self.client.http_client.get(url)
        if response.status_code != 200:
            self.client.logger.log(
                f"GitHub fetch failed [{response.status_code}]: {url}", "error"
            )
            raise sierra_internal_errors.SierraHTTPError(
                f"Failed to fetch data from {url}: {response.status_code}"
            )

        return typing.cast("typing.Dict[str, typing.Any]", response.json())

    def _download_and_cache(self, name: str, url: str) -> None:
        """Download a Python file and cache it using the new CacheManager."""
        self.client.logger.log(
            f"Downloading .py file: {name} from {url}", "debug"
        )
        response = self.client.http_client.get(url)
        if response.status_code != 200:
            self.client.logger.log(
                f"Failed to download {url} [{response.status_code}]", "error"
            )
            raise sierra_internal_errors.SierraHTTPError(
                f"Failed to download {url}: {response.status_code}"
            )

        # Use new CacheManager interface with proper typing
        cache_data: typing.Dict[str, typing.Any] = {
            "content": response.text,
            "type": "file",
            "source": url,
        }

        # Store with compression and persistence enabled, using TTL of 7 days
        self.cache.set(
            key=name,
            value=cache_data,
            ttl=7 * 24 * 3600,  # 7 days in seconds
            persist=True,
            compress=True,
        )

        self.client.logger.log(f"Cached '{name}' successfully", "info")

    def populate(self) -> None:
        """Pulls new files from all sources and caches all valid `.py` scripts."""
        self.client.logger.log("Starting population from sources...", "info")
        total_cached = 0
        total_skipped = 0

        for source in self.sources:
            if not source.startswith("http"):
                source = f"https://{source}"

            self.client.logger.log(f"Processing source: {source}", "debug")

            try:
                data = self._get_github_data(source)
            except sierra_internal_errors.SierraHTTPError as e:
                self.client.logger.log(
                    f"Skipping source due to error: {e}", "warning"
                )
                continue

            # Handle both direct file lists and nested file structures
            files = data if isinstance(data, list) else data.get("files", [])
            files = typing.cast("typing.List[typing.Any]", files)

            for file_item in files:
                # Check if file is a dictionary (expected format)
                if not isinstance(file_item, dict):
                    self.client.logger.log(
                        f"Unexpected file format, skipping: {file_item}",
                        "warning",
                    )
                    continue

                file_dict = typing.cast(
                    "typing.Dict[str, typing.Any]", file_item
                )

                if file_dict.get("type") == "file":
                    file_path_str = file_dict.get("path")
                    if not file_path_str:
                        self.client.logger.log(
                            f"Missing path in file object: {file_dict}",
                            "warning",
                        )
                        continue

                    # Convert to pathlib.Path for proper path handling
                    file_path = pathlib.Path(typing.cast("str", file_path_str))

                    if file_path.suffix == ".py":
                        name = file_path.stem

                        # Check if already cached using the new CacheManager exists method
                        if self.cache.exists(name):
                            self.client.logger.log(
                                f"'{name}' already cached, skipping", "debug"
                            )
                            total_skipped += 1
                            continue

                        # Try to get download URL with fallback to raw_url
                        url_raw = file_dict.get(
                            "download_url"
                        ) or file_dict.get("raw_url")
                        if not url_raw:
                            self.client.logger.log(
                                f"Missing raw/download URL for: {file_dict}",
                                "warning",
                            )
                            continue

                        url = typing.cast("str", url_raw)

                        try:
                            self._download_and_cache(name=name, url=url)
                            total_cached += 1
                        except sierra_internal_errors.SierraHTTPError as e:
                            self.client.logger.log(
                                f"Failed to cache {name}: {e}", "error"
                            )

        self.client.logger.log(
            f"Population complete: {total_cached} .py files cached, {total_skipped} skipped (already cached)",
            "info",
        )

    def update(self) -> None:
        """Refreshes the sideloader by pulling from all sources again."""
        self.client.logger.log("Updating sideloader sources...", "info")
        self.populate()

    def install(self, name: str) -> None:
        """
        Installs a cached .py script into the Sierra environment's script directory.

        Parameters
        ----------
        name : str
            The name of the file to install (without `.py`).

        Raises
        ------
        SierraCacheError
            If the file is not found in the cache.
        """
        self.client.logger.log(f"Attempting to install '{name}'", "info")
        entry_raw = self.cache.get(name)

        if not entry_raw:
            self.client.logger.log(
                f"Script '{name}' not found in cache.", "error"
            )
            raise sierra_internal_errors.SierraCacheError(
                f"No cached package named '{name}' found."
            )

        # Type cast the cache entry to expected format
        entry = typing.cast("typing.Dict[str, typing.Any]", entry_raw)

        # Validate that it's a file entry
        if entry.get("type") != "file":
            self.client.logger.log(
                f"Cache entry for '{name}' is not a file type.", "error"
            )
            raise sierra_internal_errors.SierraCacheError(
                f"Cached item '{name}' is not a file."
            )

        content = entry.get("content")
        if not content:
            self.client.logger.log(
                f"Cache entry for '{name}' has no content.", "error"
            )
            raise sierra_internal_errors.SierraCacheError(
                f"Cached file '{name}' has no content."
            )

        content_str = typing.cast("str", content)

        script_dir = self.client.environment.scripts_path
        if not script_dir.exists():
            self.client.logger.log(
                f"Script path missing: {script_dir}, creating it.", "debug"
            )
            script_dir.mkdir(parents=True, exist_ok=True)

        script_path = script_dir / f"{name}.py"
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(content_str)

        self.client.logger.log(f"Installed '{name}' to {script_path}", "info")

    def search(self, query: str) -> typing.List[str]:
        """
        Searches for scripts in the cache by partial name match.

        Parameters
        ----------
        query : str
            The search keyword.

        Returns
        -------
        List[str]
            Matching script names.
        """
        results: typing.List[str] = []

        # Use the new CacheManager's keys() method
        cache_keys = self.cache.keys(include_expired=False)

        for key in cache_keys:
            key_str = key
            if query.lower() in key_str.lower():
                # Verify it's a file entry by checking the cache
                entry_raw = self.cache.get(key_str)
                if entry_raw:
                    entry = typing.cast(
                        "typing.Dict[str, typing.Any]", entry_raw
                    )
                    if entry.get("type") == "file":
                        results.append(key_str)

        self.client.logger.log(
            f"Search for '{query}' returned: {results}", "debug"
        )
        return results

    def list_available(self) -> typing.List[str]:
        """
        Lists all `.py` script packages currently cached (including from disk).

        Returns
        -------
        List[str]
            Cached script names.
        """
        available: typing.List[str] = []

        # Use the new CacheManager's keys() method which handles both memory and disk
        cache_keys = self.cache.keys(include_expired=False)

        for key in cache_keys:
            key_str = key
            entry_raw = self.cache.get(key_str)
            if entry_raw:
                entry = typing.cast("typing.Dict[str, typing.Any]", entry_raw)
                if entry.get("type") == "file":
                    available.append(key_str)

        self.client.logger.log(f"Cached .py scripts: {available}", "debug")
        return available

    def info(self, name: str) -> typing.Dict[str, typing.Any]:
        """
        Returns metadata about a cached script.

        Parameters
        ----------
        name : str
            Name of the cached script.

        Returns
        -------
        Dict[str, Any]
            Metadata of the script including cache entry details.

        Raises
        ------
        SierraCacheError
            If script not found in cache.
        """
        entry_raw = self.cache.get(name)
        if not entry_raw:
            self.client.logger.log(f"No info found for '{name}'", "error")
            raise sierra_internal_errors.SierraCacheError(
                f"Package '{name}' not found in cache."
            )

        entry = typing.cast("typing.Dict[str, typing.Any]", entry_raw)

        # Get detailed cache information using the new CacheManager's get_entry_info method
        cache_info_raw = self.cache.get_entry_info(name)
        if cache_info_raw:
            cache_info = cache_info_raw

            # Combine entry data with cache metadata
            info_dict: typing.Dict[str, typing.Any] = {
                "name": name,
                "type": entry.get("type"),
                "source": entry.get("source"),
                "content_length": len(entry.get("content", "")),
                "cache_info": {
                    "created_at": cache_info.get("created_at"),
                    "expires_at": cache_info.get("expires_at"),
                    "compression": cache_info.get("compression"),
                    "size_bytes": cache_info.get("size_bytes"),
                    "access_count": cache_info.get("access_count"),
                    "last_accessed": cache_info.get("last_accessed"),
                    "in_memory": cache_info.get("in_memory"),
                },
            }
        else:
            # Fallback to basic info if detailed cache info is not available
            info_dict = {
                "name": name,
                "type": entry.get("type"),
                "source": entry.get("source"),
                "content_length": len(entry.get("content", "")),
            }

        self.client.logger.log(f"Info for '{name}': {info_dict}", "debug")
        return info_dict

    def cleanup_expired(self) -> int:
        """
        Manually clean up expired cache entries.

        Returns
        -------
        int
            Number of entries removed.
        """
        self.client.logger.log("Cleaning up expired cache entries...", "info")
        removed_count = self.cache.cleanup()
        self.client.logger.log(
            f"Removed {removed_count} expired cache entries", "info"
        )
        return removed_count

    def get_cache_stats(self) -> typing.Dict[str, typing.Any]:
        """
        Get comprehensive cache statistics.

        Returns
        -------
        Dict[str, Any]
            Cache statistics including file counts and sizes.
        """
        stats_raw = self.cache.stats()
        stats = stats_raw

        # Add sideloader-specific stats
        file_count = 0
        for key in self.cache.keys(include_expired=False):
            entry_raw = self.cache.get(key)
            if entry_raw:
                entry = typing.cast("typing.Dict[str, typing.Any]", entry_raw)
                if entry.get("type") == "file":
                    file_count += 1

        enhanced_stats: typing.Dict[str, typing.Any] = {
            **stats,
            "python_files_cached": file_count,
            "sources_configured": len(self.sources),
        }

        return enhanced_stats
