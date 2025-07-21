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
        """
        Initialize the SierraSideloader.

        Parameters
        ----------
        client : SierraDevelopmentClient
            A reference to the Sierra development client.

        Raises
        ------
        SierraPathError
            If the configuration path or source file does not exist.
        """
        self.client = client
        self.cache = self.client.cache
        self.path: pathlib.Path = self.client.environment.config_path

        self.client.logger.log("Initializing SierraSideloader...", "info")

        if not self.path.exists():
            self.client.logger.log("Missing config path.", "error")
            raise sierra_internal_errors.SierraPathError(
                f"Path {self.path} does not exist."
            )

        source_path = self.path / "source"
        if not source_path.exists():
            self.client.logger.log("Missing source file.", "error")
            raise sierra_internal_errors.SierraPathError(
                f"File {source_path} does not exist."
            )

        if source_path.stat().st_size == 0:
            self.client.logger.log("Source file is empty.", "warning")

        with open(source_path, "r", encoding="utf-8") as f:
            self.sources: list[str] = [
                line.strip() for line in f if line.strip()
            ]

        self.client.logger.log(
            f"Loaded {len(self.sources)} sources from {source_path}.", "debug"
        )
        super().__init__(client)

    def _get_github_data(self, url: str) -> dict[str, typing.Any]:
        """
        Fetch data from the GitHub API.

        Parameters
        ----------
        url : str
            The URL to fetch data from.

        Returns
        -------
        dict[str, typing.Any]
            The JSON response from the GitHub API.

        Raises
        ------
        SierraHTTPError
            If the request to the GitHub API fails.

        Notes
        -----
        This function logs each step of the data-fetching process.
        """
        self.client.logger.log(
            f"Fetching data from GitHub API: {url}", "debug"
        )
        response = self.client.http_client.get(url)
        if response.status_code != 200:
            self.client.logger.log(
                f"Failed to fetch data from GitHub: {url}, Status Code: {response.status_code}",
                "error",
            )
            raise sierra_internal_errors.SierraHTTPError(
                f"Failed to fetch data from {url}: {response.status_code}"
            )

        self.client.logger.log("GitHub data fetched successfully", "info")
        return typing.cast("dict[str, typing.Any]", response.json())

    def _download_and_cache(self, name: str, url: str) -> None:
        """
        Download a Python file and cache it using the new CacheManager.

        Parameters
        ----------
        name : str
            The name of the file to cache.
        url : str
            The URL to download the file from.

        Raises
        ------
        SierraHTTPError
            If the request to `url` fails.
        """
        self.client.logger.log(
            f"Downloading .py file: {name} from {url}", "info"
        )
        response = self.client.http_client.get(url)
        if response.status_code != 200:
            self.client.logger.log(
                f"Failed to download {url}: {response.status_code}", "error"
            )
            raise sierra_internal_errors.SierraHTTPError(
                f"Failed to download {url}: {response.status_code}"
            )

        # Use new CacheManager interface with proper typing
        cache_data: dict[str, typing.Any] = {
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

        # Check if sources list is empty and handle gracefully
        if not self.sources:
            self.client.logger.log(
                "No sources configured. Nothing to populate.", "warning"
            )
            return

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
            files = typing.cast("list[typing.Any]", files)

            for file_item in files:
                # Check if file is a dictionary (expected format)
                if not isinstance(file_item, dict):
                    self.client.logger.log(
                        f"Skipping unexpected file format: {file_item}",
                        "warning",
                    )
                    continue

                file_dict = typing.cast("dict[str, typing.Any]", file_item)

                if file_dict.get("type") == "file":
                    file_path_str = file_dict.get("path")
                    if not file_path_str:
                        self.client.logger.log(
                            f"Skipping file without path: {file_dict}",
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
                                f"Skipping '{name}' as it is already cached",
                                "debug",
                            )
                            total_skipped += 1
                            continue

                        # Try to get download URL with fallback to raw_url
                        url_raw = file_dict.get(
                            "download_url"
                        ) or file_dict.get("raw_url")
                        if not url_raw:
                            self.client.logger.log(
                                f"Skipping file without raw/download URL: {file_dict}",
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
        self.client.logger.log("Clearing cache for update...", "debug")
        self.cache.clear()
        self.client.logger.log("Populating sideloader sources...", "info")
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
                f"Script '{name}' not found in cache. Raising SierraCacheError.",
                "error",
            )
            raise sierra_internal_errors.SierraCacheError(
                f"No cached package named '{name}' found."
            )

        # Type cast the cache entry to expected format
        entry = typing.cast("dict[str, typing.Any]", entry_raw)

        # Validate that it's a file entry
        if entry.get("type") != "file":
            self.client.logger.log(
                f"Cache entry for '{name}' is not a file type. Raising SierraCacheError.",
                "error",
            )
            raise sierra_internal_errors.SierraCacheError(
                f"Cached item '{name}' is not a file."
            )

        content = entry.get("content")
        if not content:
            self.client.logger.log(
                f"Cache entry for '{name}' has no content. Raising SierraCacheError.",
                "error",
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

    def search(self, query: str) -> list[str]:
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
        results: list[str] = []

        # Use the new CacheManager's keys() method
        cache_keys = self.cache.keys(include_expired=False)

        for key in cache_keys:
            key_str = key
            if query.lower() in key_str.lower():
                # Verify it's a file entry by checking the cache
                self.client.logger.log(
                    f"Checking if {key_str} is a file entry", "debug"
                )
                entry_raw = self.cache.get(key_str)
                if entry_raw:
                    entry = typing.cast("dict[str, typing.Any]", entry_raw)
                    if entry.get("type") == "file":
                        self.client.logger.log(
                            f"{key_str} is a file entry, adding to results",
                            "debug",
                        )
                        results.append(key_str)

        self.client.logger.log(
            f"Search for '{query}' returned: {results}", "debug"
        )
        return results

    def list_available(self) -> list[str]:
        """
        Lists all `.py` script packages currently cached (including from disk).

        Returns
        -------
        List[str]
            Cached script names.
        """
        available: list[str] = []

        # Use the new CacheManager's keys() method which handles both memory and disk
        cache_keys = self.cache.keys(include_expired=False)

        for key in cache_keys:
            key_str = key
            self.client.logger.log(
                f"Searching for '{key_str}' in cache.", "debug"
            )
            entry_raw = self.cache.get(key_str)
            if entry_raw:
                entry = typing.cast("dict[str, typing.Any]", entry_raw)
                if entry.get("type") == "file":
                    self.client.logger.log(
                        f"Found '{key_str}' in cache, adding to results.",
                        "debug",
                    )
                    available.append(key_str)

        self.client.logger.log(f"Cached .py scripts: {available}", "debug")
        return available

    def info(self, name: str) -> dict[str, typing.Any]:
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
        self.client.logger.log(f"Retrieving info for '{name}'...", "debug")
        entry_raw = self.cache.get(name)
        if not entry_raw:
            self.client.logger.log(f"No info found for '{name}'", "error")
            raise sierra_internal_errors.SierraCacheError(
                f"Package '{name}' not found in cache."
            )

        entry = typing.cast("dict[str, typing.Any]", entry_raw)

        # Get detailed cache information using the new CacheManager's get_entry_info method
        cache_info_raw = self.cache.get_entry_info(name)
        if cache_info_raw:
            cache_info = cache_info_raw

            # Combine entry data with cache metadata
            info_dict: dict[str, typing.Any] = {
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
        removed_count = self.cache.cleanup()
        self.client.logger.log(
            f"Removed {removed_count} expired cache entries", "info"
        )
        return removed_count

    def get_cache_stats(self) -> dict[str, typing.Any]:
        """
        Get comprehensive cache statistics.

        Returns
        -------
        Dict[str, Any]
            Cache statistics including file counts and sizes.
        """
        stats_raw = self.cache.stats()
        self.client.logger.log(
            f"Retrieved cache statistics: {stats_raw}", "debug"
        )
        stats = stats_raw

        # Add sideloader-specific stats
        self.client.logger.log("Counting cached Python files", "debug")
        file_count = 0
        for key in self.cache.keys(include_expired=False):
            self.client.logger.log(
                f"Checking if '{key}' is a file entry", "debug"
            )
            entry_raw = self.cache.get(key)
            if entry_raw:
                self.client.logger.log(f"Checking type of '{key}'", "debug")
                entry = typing.cast("dict[str, typing.Any]", entry_raw)
                if entry.get("type") == "file":
                    self.client.logger.log(
                        f"Found '{key}' to be a file entry, incrementing count",
                        "debug",
                    )
                    file_count += 1

        self.client.logger.log(
            f"Counted {file_count} cached Python files", "debug"
        )
        enhanced_stats: dict[str, typing.Any] = {
            **stats,
            "python_files_cached": file_count,
            "sources_configured": len(self.sources),
        }

        self.client.logger.log(
            f"Returning enhanced cache statistics: {enhanced_stats}", "debug"
        )
        return enhanced_stats
