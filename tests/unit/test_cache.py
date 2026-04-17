"""Unit tests for response cache."""

from __future__ import annotations

from pathlib import Path

import pytest

from wikibench.runtime.cache import ResponseCache, _make_key, reset_default_cache


@pytest.fixture(autouse=True)
def _reset_global_cache() -> None:
    """Ensure the global cache singleton is reset between tests."""
    reset_default_cache()
    yield  # type: ignore[misc]
    reset_default_cache()


class TestMakeKey:
    def test_deterministic(self) -> None:
        msgs = [{"role": "user", "content": "Hello"}]
        assert _make_key("gpt-4o-mini", msgs) == _make_key("gpt-4o-mini", msgs)

    def test_different_model(self) -> None:
        msgs = [{"role": "user", "content": "Hello"}]
        assert _make_key("gpt-4o-mini", msgs) != _make_key("gpt-4o", msgs)

    def test_different_content(self) -> None:
        m1 = [{"role": "user", "content": "A"}]
        m2 = [{"role": "user", "content": "B"}]
        assert _make_key("m", m1) != _make_key("m", m2)

    def test_extra_affects_key(self) -> None:
        msgs = [{"role": "user", "content": "x"}]
        k1 = _make_key("m", msgs, extra={"seed": 1})
        k2 = _make_key("m", msgs, extra={"seed": 2})
        assert k1 != k2


class TestResponseCache:
    def test_miss_returns_none(self, tmp_path: Path) -> None:
        cache = ResponseCache(cache_dir=tmp_path)
        assert cache.get("m", [{"role": "user", "content": "q"}]) is None
        cache.close()

    def test_set_then_get(self, tmp_path: Path) -> None:
        cache = ResponseCache(cache_dir=tmp_path)
        msgs = [{"role": "user", "content": "What is 2+2?"}]
        cache.set("gpt-4o-mini", msgs, "4")
        assert cache.get("gpt-4o-mini", msgs) == "4"
        cache.close()

    def test_different_messages_miss(self, tmp_path: Path) -> None:
        cache = ResponseCache(cache_dir=tmp_path)
        msgs_a = [{"role": "user", "content": "A"}]
        msgs_b = [{"role": "user", "content": "B"}]
        cache.set("m", msgs_a, "reply_a")
        assert cache.get("m", msgs_b) is None
        cache.close()

    def test_disabled_cache_always_miss(self, tmp_path: Path) -> None:
        cache = ResponseCache(cache_dir=tmp_path, enabled=False)
        msgs = [{"role": "user", "content": "x"}]
        cache.set("m", msgs, "reply")
        assert cache.get("m", msgs) is None

    def test_invalidate(self, tmp_path: Path) -> None:
        cache = ResponseCache(cache_dir=tmp_path)
        msgs = [{"role": "user", "content": "q"}]
        cache.set("m", msgs, "reply")
        assert cache.invalidate("m", msgs) is True
        assert cache.get("m", msgs) is None
        cache.close()

    def test_clear_empties_cache(self, tmp_path: Path) -> None:
        cache = ResponseCache(cache_dir=tmp_path)
        msgs = [{"role": "user", "content": "q"}]
        cache.set("m", msgs, "reply")
        cache.clear()
        assert len(cache) == 0
        cache.close()
