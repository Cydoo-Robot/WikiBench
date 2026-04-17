"""Unit tests for the unified llm_call wrapper.

All tests run with WIKIBENCH_LLM_MOCK=1 — no real API calls.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from wikibench.runtime.cache import ResponseCache, reset_default_cache
from wikibench.runtime.cost import CostTracker
from wikibench.runtime.llm import _MOCK_REPLY, llm_call


@pytest.fixture(autouse=True)
def _mock_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("WIKIBENCH_LLM_MOCK", "1")
    reset_default_cache()
    # Point default cache to a temp dir so tests don't pollute the project cache
    from wikibench.runtime import cache as _cache_mod

    _cache_mod._default_cache = ResponseCache(cache_dir=tmp_path / "test-cache")
    yield  # type: ignore[misc]
    reset_default_cache()


class TestLLMCallMockMode:
    def test_returns_mock_reply(self) -> None:
        reply = llm_call(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Hello"}],
            purpose="test",
        )
        assert reply == _MOCK_REPLY

    def test_records_cost(self) -> None:
        tracker = CostTracker()
        CostTracker.install(tracker)
        try:
            llm_call(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "Hello"}],
                purpose="test",
            )
            assert tracker.total_llm_calls == 1
        finally:
            CostTracker.uninstall()

    def test_cache_hit_on_second_call(self, tmp_path: Path) -> None:
        cache = ResponseCache(cache_dir=tmp_path / "cache2")
        msgs = [{"role": "user", "content": "cached question"}]
        # First call populates cache
        llm_call("gpt-4o-mini", msgs, purpose="test", cache=cache)
        # Second call should be a cache hit (still returns same mock reply)
        reply2 = llm_call("gpt-4o-mini", msgs, purpose="test", cache=cache)
        assert reply2 == _MOCK_REPLY
        cache.close()

    def test_no_cache_skips_cache(self, tmp_path: Path) -> None:
        cache = ResponseCache(cache_dir=tmp_path / "cache3")
        msgs = [{"role": "user", "content": "skip cache"}]
        llm_call("gpt-4o-mini", msgs, purpose="test", cache=cache, use_cache=False)
        # Nothing should be in cache
        assert cache.get("gpt-4o-mini", msgs) is None
        cache.close()


class TestLLMCallMockDisabled:
    """Tests that verify the real call path (still mocked at litellm level)."""

    def test_propagates_litellm_error(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        monkeypatch.delenv("WIKIBENCH_LLM_MOCK", raising=False)
        from wikibench.runtime import cache as _cache_mod

        _cache_mod._default_cache = ResponseCache(cache_dir=tmp_path / "cache-err", enabled=False)

        import litellm

        with (
            patch.object(litellm, "completion", side_effect=RuntimeError("API error")),
            pytest.raises(RuntimeError, match="API error"),
        ):
            llm_call(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "fail"}],
                purpose="test",
                use_cache=False,
            )
