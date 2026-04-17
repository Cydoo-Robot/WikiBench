"""diskcache-backed LLM response cache.

Keys are derived from a stable SHA-256 hash of the full call parameters so
that identical calls to the same model with the same messages always hit the
cache regardless of wall-clock time.

Cache layout on disk::

    .wikibench-cache/
    └── <sha256-prefix>/  (diskcache shards automatically)

Usage::

    cache = ResponseCache(".wikibench-cache")
    result = cache.get(model, messages)   # → str | None
    cache.set(model, messages, reply)
"""

from __future__ import annotations

import hashlib
import json
import logging
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)


def _make_key(model: str, messages: list[dict[str, str]], extra: dict[str, Any] | None = None) -> str:
    """Derive a stable cache key from call parameters."""
    payload: dict[str, Any] = {"model": model, "messages": messages}
    if extra:
        payload["extra"] = extra
    serialised = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(serialised.encode()).hexdigest()


class ResponseCache:
    """Persistent LLM response cache backed by diskcache.

    Args:
        cache_dir: Path to the on-disk cache directory.
        ttl_seconds: Time-to-live in seconds (default 30 days).
        enabled: Set to ``False`` to disable the cache entirely.
    """

    _TTL_30_DAYS = 60 * 60 * 24 * 30

    def __init__(
        self,
        cache_dir: str | Path = ".wikibench-cache",
        ttl_seconds: int = _TTL_30_DAYS,
        enabled: bool = True,
    ) -> None:
        self._enabled = enabled
        self._ttl = ttl_seconds
        self._cache: Any = None  # lazy-init to avoid import at module level

        if enabled:
            self._cache_dir = Path(cache_dir)
            self._cache_dir.mkdir(parents=True, exist_ok=True)
            self._init_cache()

    def _init_cache(self) -> None:
        try:
            import diskcache

            self._cache = diskcache.Cache(str(self._cache_dir))
            log.debug("ResponseCache opened at %s", self._cache_dir)
        except ImportError:
            log.warning("diskcache not installed; response cache disabled")
            self._enabled = False

    # ── Public API ────────────────────────────────────────────────────────────

    def get(
        self,
        model: str,
        messages: list[dict[str, str]],
        extra: dict[str, Any] | None = None,
    ) -> str | None:
        """Return cached response string, or ``None`` on miss."""
        if not self._enabled or self._cache is None:
            return None
        key = _make_key(model, messages, extra)
        value = self._cache.get(key)
        if value is not None:
            log.debug("Cache HIT  key=%s…", key[:12])
            return str(value)
        log.debug("Cache MISS key=%s…", key[:12])
        return None

    def set(
        self,
        model: str,
        messages: list[dict[str, str]],
        response: str,
        extra: dict[str, Any] | None = None,
    ) -> None:
        """Store a response in the cache."""
        if not self._enabled or self._cache is None:
            return
        key = _make_key(model, messages, extra)
        self._cache.set(key, response, expire=self._ttl)
        log.debug("Cache SET  key=%s…", key[:12])

    def invalidate(
        self,
        model: str,
        messages: list[dict[str, str]],
        extra: dict[str, Any] | None = None,
    ) -> bool:
        """Remove a specific entry.  Returns ``True`` if it existed."""
        if not self._enabled or self._cache is None:
            return False
        key = _make_key(model, messages, extra)
        return bool(self._cache.delete(key))

    def clear(self) -> None:
        """Evict all cached entries."""
        if self._cache is not None:
            self._cache.clear()

    def close(self) -> None:
        """Release the cache file handle."""
        if self._cache is not None:
            self._cache.close()

    def __len__(self) -> int:
        if self._cache is None:
            return 0
        return len(self._cache)

    # ── Module-level singleton ────────────────────────────────────────────────


_default_cache: ResponseCache | None = None


def get_default_cache(cache_dir: str = ".wikibench-cache", enabled: bool = True) -> ResponseCache:
    """Return (or lazily create) the process-wide default cache."""
    global _default_cache
    if _default_cache is None:
        _default_cache = ResponseCache(cache_dir=cache_dir, enabled=enabled)
    return _default_cache


def reset_default_cache() -> None:
    """Discard the process-wide default cache (useful in tests)."""
    global _default_cache
    if _default_cache is not None:
        _default_cache.close()
    _default_cache = None
