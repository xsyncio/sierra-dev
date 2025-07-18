import contextlib
import gzip
import hashlib
import json
import os
import pathlib
import sqlite3
import sys
import threading
import time
import typing
from dataclasses import dataclass
from enum import Enum


class CompressionType(Enum):
    """Compression types for cache entries."""

    NONE = "none"
    GZIP = "gzip"


@dataclass
class CacheEntry:
    """Represents a cache entry with metadata."""

    key: str
    value: typing.Any
    created_at: float
    expires_at: typing.Optional[float] = None
    compression: CompressionType = CompressionType.NONE
    size_bytes: int = 0
    access_count: int = 0
    last_accessed: float = 0.0


class CacheManager:
    """
    A full-featured cache manager with SQLite-backed persistence, TTL expiration,
    auto-cleanup, compression, and efficient key enumeration.

    Features:
    - SQLite-backed metadata storage for fast key enumeration
    - Separate file storage for large values
    - Memory cache for frequently accessed items
    - TTL support with automatic cleanup
    - Compression support (gzip)
    - Thread-safe operations
    - Access statistics tracking
    - Atomic operations
    """

    def __init__(
        self,
        cache_dir: typing.Optional[pathlib.Path] = None,
        max_memory_entries: int = 1000,
        cleanup_interval: float = 3600,  # 1 hour
        auto_cleanup: bool = True,
    ) -> None:
        """
        Initialize the CacheManager.

        Parameters
        ----------
        cache_dir : pathlib.Path, optional
            Directory for cache storage. If None, uses OS-appropriate location.
        max_memory_entries : int
            Maximum number of entries to keep in memory cache.
        cleanup_interval : float
            Interval in seconds between automatic cleanup runs.
        auto_cleanup : bool
            Whether to automatically clean up expired entries.
        """
        self._memory_cache: typing.Dict[str, CacheEntry] = {}
        self._lock = threading.RLock()
        self._max_memory_entries = max_memory_entries
        self._cleanup_interval = cleanup_interval
        self._auto_cleanup = auto_cleanup
        self._last_cleanup = time.time()

        # Setup directories
        self._base_dir = cache_dir or self._default_cache_dir()
        self._base_dir.mkdir(parents=True, exist_ok=True)
        self._data_dir = self._base_dir / "data"
        self._data_dir.mkdir(exist_ok=True)

        # Setup SQLite database
        self._db_path = self._base_dir / "cache.db"
        self._init_database()

    def _default_cache_dir(self) -> pathlib.Path:
        """Returns a platform-appropriate cache directory."""
        if sys.platform.startswith("darwin"):
            return pathlib.Path.home() / "Library" / "Caches" / "sierra"
        elif sys.platform.startswith("win"):
            return (
                pathlib.Path(os.environ.get("LOCALAPPDATA", "."))
                / "sierra"
                / "Cache"
            )
        else:
            return pathlib.Path.home() / ".cache" / "sierra"

    def _init_database(self) -> None:
        """Initialize the SQLite database."""
        with sqlite3.connect(self._db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cache_entries (
                    key TEXT PRIMARY KEY,
                    created_at REAL NOT NULL,
                    expires_at REAL,
                    compression TEXT NOT NULL,
                    size_bytes INTEGER NOT NULL,
                    access_count INTEGER NOT NULL DEFAULT 0,
                    last_accessed REAL NOT NULL
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_expires_at ON cache_entries(expires_at)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_last_accessed ON cache_entries(last_accessed)
            """)
            conn.commit()

    def _key_to_filename(self, key: str) -> pathlib.Path:
        """Convert a cache key to a filename."""
        digest = hashlib.sha256(key.encode()).hexdigest()
        return self._data_dir / f"{digest}.cache"

    def _now(self) -> float:
        """Get current timestamp."""
        return time.time()

    def _should_cleanup(self) -> bool:
        """Check if cleanup should be performed."""
        if not self._auto_cleanup:
            return False
        return (self._now() - self._last_cleanup) > self._cleanup_interval

    def _cleanup_if_needed(self) -> None:
        """Perform cleanup if needed."""
        if self._should_cleanup():
            self._cleanup_expired()

    def _serialize_value(
        self, value: typing.Any, compression: CompressionType
    ) -> bytes:
        """Serialize and optionally compress a value."""
        json_data = json.dumps(value, default=str).encode("utf-8")

        if compression == CompressionType.GZIP:
            return gzip.compress(json_data)
        else:
            return json_data

    def _deserialize_value(
        self, data: bytes, compression: CompressionType
    ) -> typing.Any:
        """Deserialize and decompress a value."""
        if compression == CompressionType.GZIP:
            json_data = gzip.decompress(data)
        else:
            json_data = data

        return json.loads(json_data.decode("utf-8"))

    def _evict_lru_memory(self) -> None:
        """Evict least recently used items from memory cache."""
        if len(self._memory_cache) <= self._max_memory_entries:
            return

        # Sort by last_accessed and remove oldest entries
        sorted_entries = sorted(
            self._memory_cache.items(), key=lambda x: x[1].last_accessed
        )

        # Remove oldest entries to get back to max size
        excess_count = len(self._memory_cache) - self._max_memory_entries
        for i in range(excess_count):
            key = sorted_entries[i][0]
            del self._memory_cache[key]

    def _load_from_disk(self, key: str) -> typing.Optional[CacheEntry]:
        """Load a cache entry from disk."""
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.execute(
                "SELECT created_at, expires_at, compression, size_bytes, access_count, last_accessed "
                "FROM cache_entries WHERE key = ?",
                (key,),
            )
            row = cursor.fetchone()
            if not row:
                return None

            (
                created_at,
                expires_at,
                compression_str,
                size_bytes,
                access_count,
                last_accessed,
            ) = row
            compression = CompressionType(compression_str)

            # Check if expired
            if expires_at and self._now() > expires_at:
                self.delete(key)
                return None

            # Load the actual value
            filename = self._key_to_filename(key)
            if not filename.exists():
                # Inconsistent state - remove from database
                conn.execute("DELETE FROM cache_entries WHERE key = ?", (key,))
                conn.commit()
                return None

            try:
                with open(filename, "rb") as f:
                    data = f.read()
                value = self._deserialize_value(data, compression)

                return CacheEntry(
                    key=key,
                    value=value,
                    created_at=created_at,
                    expires_at=expires_at,
                    compression=compression,
                    size_bytes=size_bytes,
                    access_count=access_count,
                    last_accessed=last_accessed,
                )
            except Exception:
                # Corrupted file - remove both file and database entry
                self.delete(key)
                return None

    def set(
        self,
        key: str,
        value: typing.Any,
        ttl: typing.Optional[float] = None,
        persist: bool = True,
        compress: bool = False,
    ) -> None:
        """
        Store a value in the cache.

        Parameters
        ----------
        key : str
            Cache key.
        value : Any
            Value to cache.
        ttl : float, optional
            Time to live in seconds.
        persist : bool
            Whether to persist to disk (default: True).
        compress : bool
            Whether to compress the value.
        """
        with self._lock:
            self._cleanup_if_needed()

            now = self._now()
            expires_at = now + ttl if ttl else None
            compression = (
                CompressionType.GZIP if compress else CompressionType.NONE
            )

            # Serialize the value
            serialized_data = self._serialize_value(value, compression)
            size_bytes = len(serialized_data)

            entry = CacheEntry(
                key=key,
                value=value,
                created_at=now,
                expires_at=expires_at,
                compression=compression,
                size_bytes=size_bytes,
                access_count=0,
                last_accessed=now,
            )

            # Store in memory cache
            self._memory_cache[key] = entry
            self._evict_lru_memory()

            if persist:
                # Save to disk
                filename = self._key_to_filename(key)
                with open(filename, "wb") as f:
                    f.write(serialized_data)

                # Update database
                with sqlite3.connect(self._db_path) as conn:
                    conn.execute(
                        """
                        INSERT OR REPLACE INTO cache_entries 
                        (key, created_at, expires_at, compression, size_bytes, access_count, last_accessed)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            key,
                            now,
                            expires_at,
                            compression.value,
                            size_bytes,
                            0,
                            now,
                        ),
                    )
                    conn.commit()

    def get(self, key: str) -> typing.Optional[typing.Any]:
        """
        Retrieve a value from the cache.

        Parameters
        ----------
        key : str
            Cache key.

        Returns
        -------
        Any or None
            The cached value or None if not found/expired.
        """
        with self._lock:
            self._cleanup_if_needed()

            # Check memory cache first
            if key in self._memory_cache:
                entry = self._memory_cache[key]
                if entry.expires_at and self._now() > entry.expires_at:
                    self.delete(key)
                    return None

                # Update access statistics
                entry.access_count += 1
                entry.last_accessed = self._now()

                return entry.value

            # Load from disk
            entry = self._load_from_disk(key)
            if entry is None:
                return None

            # Update access statistics
            entry.access_count += 1
            entry.last_accessed = self._now()

            # Store in memory cache
            self._memory_cache[key] = entry
            self._evict_lru_memory()

            # Update database statistics
            with sqlite3.connect(self._db_path) as conn:
                conn.execute(
                    "UPDATE cache_entries SET access_count = ?, last_accessed = ? WHERE key = ?",
                    (entry.access_count, entry.last_accessed, key),
                )
                conn.commit()

            return entry.value

    def exists(self, key: str) -> bool:
        """
        Check if a key exists and is not expired.

        Parameters
        ----------
        key : str
            Cache key.

        Returns
        -------
        bool
            True if the key exists and is valid.
        """
        with self._lock:
            # Check memory first
            if key in self._memory_cache:
                entry = self._memory_cache[key]
                if entry.expires_at and self._now() > entry.expires_at:
                    self.delete(key)
                    return False
                return True

            # Check database
            with sqlite3.connect(self._db_path) as conn:
                cursor = conn.execute(
                    "SELECT expires_at FROM cache_entries WHERE key = ?",
                    (key,),
                )
                row = cursor.fetchone()
                if not row:
                    return False

                expires_at = row[0]
                if expires_at and self._now() > expires_at:
                    self.delete(key)
                    return False

                return True

    def delete(self, key: str) -> None:
        """
        Delete a cache entry.

        Parameters
        ----------
        key : str
            Cache key.
        """
        with self._lock:
            # Remove from memory
            self._memory_cache.pop(key, None)

            # Remove from disk
            filename = self._key_to_filename(key)
            with contextlib.suppress(FileNotFoundError):
                filename.unlink()

            # Remove from database
            with sqlite3.connect(self._db_path) as conn:
                conn.execute("DELETE FROM cache_entries WHERE key = ?", (key,))
                conn.commit()

    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            # Clear memory
            self._memory_cache.clear()

            # Clear disk files
            for file in self._data_dir.glob("*.cache"):
                with contextlib.suppress(Exception):
                    file.unlink()

            # Clear database
            with sqlite3.connect(self._db_path) as conn:
                conn.execute("DELETE FROM cache_entries")
                conn.commit()

    def keys(self, include_expired: bool = False) -> typing.List[str]:
        """
        Get all cache keys.

        Parameters
        ----------
        include_expired : bool
            Whether to include expired keys.

        Returns
        -------
        List[str]
            List of cache keys.
        """
        with self._lock:
            if include_expired:
                with sqlite3.connect(self._db_path) as conn:
                    cursor = conn.execute("SELECT key FROM cache_entries")
                    return [row[0] for row in cursor.fetchall()]
            else:
                now = self._now()
                with sqlite3.connect(self._db_path) as conn:
                    cursor = conn.execute(
                        "SELECT key FROM cache_entries WHERE expires_at IS NULL OR expires_at > ?",
                        (now,),
                    )
                    return [row[0] for row in cursor.fetchall()]

    def _cleanup_expired(self) -> int:
        """Clean up expired entries and return count of removed entries."""
        with self._lock:
            now = self._now()
            removed_count = 0

            # Clean up memory cache
            expired_keys = [
                key
                for key, entry in self._memory_cache.items()
                if entry.expires_at and now > entry.expires_at
            ]
            for key in expired_keys:
                del self._memory_cache[key]
                removed_count += 1

            # Clean up persistent storage
            with sqlite3.connect(self._db_path) as conn:
                # Get expired entries
                cursor = conn.execute(
                    "SELECT key FROM cache_entries WHERE expires_at IS NOT NULL AND expires_at <= ?",
                    (now,),
                )
                expired_persistent = [row[0] for row in cursor.fetchall()]

                # Remove files
                for key in expired_persistent:
                    filename = self._key_to_filename(key)
                    with contextlib.suppress(FileNotFoundError):
                        filename.unlink()

                # Remove from database
                conn.execute(
                    "DELETE FROM cache_entries WHERE expires_at IS NOT NULL AND expires_at <= ?",
                    (now,),
                )
                conn.commit()

                removed_count += len(expired_persistent)

            self._last_cleanup = now
            return removed_count

    def cleanup(self) -> int:
        """
        Manually clean up expired entries.

        Returns
        -------
        int
            Number of entries removed.
        """
        return self._cleanup_expired()

    def stats(self) -> typing.Dict[str, typing.Any]:
        """
        Get cache statistics.

        Returns
        -------
        Dict[str, Any]
            Statistics dictionary.
        """
        with self._lock and sqlite3.connect(self._db_path) as conn:
            # Total entries
            cursor = conn.execute("SELECT COUNT(*) FROM cache_entries")
            total_entries = cursor.fetchone()[0]

            # Total size
            cursor = conn.execute("SELECT SUM(size_bytes) FROM cache_entries")
            total_size = cursor.fetchone()[0] or 0

            # Expired entries
            now = self._now()
            cursor = conn.execute(
                "SELECT COUNT(*) FROM cache_entries WHERE expires_at IS NOT NULL AND expires_at <= ?",
                (now,),
            )
            expired_entries = cursor.fetchone()[0]

            return {
                "total_entries": total_entries,
                "memory_entries": len(self._memory_cache),
                "expired_entries": expired_entries,
                "total_size_bytes": total_size,
                "cache_directory": str(self._base_dir),
                "last_cleanup": self._last_cleanup,
                "database_path": str(self._db_path),
            }

    def get_entry_info(
        self, key: str
    ) -> typing.Optional[typing.Dict[str, typing.Any]]:
        """
        Get detailed information about a cache entry.

        Parameters
        ----------
        key : str
            Cache key.

        Returns
        -------
        Dict[str, Any] or None
            Entry information or None if not found.
        """
        with self._lock:
            # Check memory first
            if key in self._memory_cache:
                entry = self._memory_cache[key]
                return {
                    "key": entry.key,
                    "created_at": entry.created_at,
                    "expires_at": entry.expires_at,
                    "compression": entry.compression.value,
                    "size_bytes": entry.size_bytes,
                    "access_count": entry.access_count,
                    "last_accessed": entry.last_accessed,
                    "in_memory": True,
                }

            # Check database
            with sqlite3.connect(self._db_path) as conn:
                cursor = conn.execute(
                    "SELECT created_at, expires_at, compression, size_bytes, access_count, last_accessed "
                    "FROM cache_entries WHERE key = ?",
                    (key,),
                )
                row = cursor.fetchone()
                if not row:
                    return None

                (
                    created_at,
                    expires_at,
                    compression,
                    size_bytes,
                    access_count,
                    last_accessed,
                ) = row
                return {
                    "key": key,
                    "created_at": created_at,
                    "expires_at": expires_at,
                    "compression": compression,
                    "size_bytes": size_bytes,
                    "access_count": access_count,
                    "last_accessed": last_accessed,
                    "in_memory": False,
                }

    def close(self) -> None:
        """Close the cache manager and perform final cleanup."""
        with self._lock:
            self._cleanup_expired()
            self._memory_cache.clear()
