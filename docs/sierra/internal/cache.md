# Cache Manager

The `sierra.internal.cache` module provides a simple file‑based cache for speeding up repeated operations (e.g., sideloader scans, compilation outputs).

??? example "Using the CacheManager"
    ```python
    from pathlib import Path
    from sierra.internal.cache import CacheManager

    # Create a cache directory inside your environment
    cache_dir = Path("default_env") / "cache"
    cache = CacheManager(cache_dir=cache_dir)

    # Store a value in the cache
    cache.set("last_run_scripts", ["greet.py", "scan.py"])

    # Retrieve a cached value (or None if missing)
    scripts = cache.get("last_run_scripts")
    print(scripts)  # ["greet.py", "scan.py"]
    ```

::: sierra.internal.cache
