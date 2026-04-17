"""Unit tests for cost tracker."""

from __future__ import annotations

import pytest

from wikibench.runtime.cost import (
    CostLimitExceededError,
    CostTracker,
    estimate_cost,
)


class TestEstimateCost:
    def test_known_model_nonzero(self) -> None:
        cost = estimate_cost("gpt-4o-mini", tokens_in=1000, tokens_out=100)
        assert cost > 0

    def test_unknown_model_returns_zero(self) -> None:
        cost = estimate_cost("totally-unknown-model-xyz", tokens_in=1000, tokens_out=100)
        assert cost == 0.0

    def test_proportional_to_tokens(self) -> None:
        c1 = estimate_cost("gpt-4o-mini", tokens_in=100, tokens_out=10)
        c2 = estimate_cost("gpt-4o-mini", tokens_in=1000, tokens_out=100)
        assert c2 > c1

    def test_output_more_expensive_than_input(self) -> None:
        input_only = estimate_cost("gpt-4o", tokens_in=1000, tokens_out=0)
        output_only = estimate_cost("gpt-4o", tokens_in=0, tokens_out=1000)
        assert output_only > input_only


class TestCostTracker:
    def test_initial_state(self) -> None:
        t = CostTracker()
        assert t.total_usd == 0.0
        assert t.total_llm_calls == 0

    def test_record_accumulates(self) -> None:
        t = CostTracker()
        t.record("gpt-4o-mini", "adapter.query", tokens_in=500, tokens_out=50)
        t.record("gpt-4o-mini", "adapter.query", tokens_in=500, tokens_out=50)
        assert t.total_llm_calls == 2
        assert t.total_usd > 0

    def test_cached_calls_not_counted(self) -> None:
        t = CostTracker()
        t.record("gpt-4o-mini", "adapter.query", tokens_in=100, tokens_out=10, cached=True)
        assert t.total_llm_calls == 0

    def test_hard_limit_raises(self) -> None:
        t = CostTracker(hard_limit_usd=0.000001)
        with pytest.raises(CostLimitExceededError) as exc_info:
            t.record("gpt-4o-mini", "adapter.query", tokens_in=10000, tokens_out=1000)
        assert exc_info.value.limit == 0.000001

    def test_breakdown_by_purpose(self) -> None:
        t = CostTracker()
        t.record("gpt-4o-mini", "adapter.query", tokens_in=100, tokens_out=10)
        t.record("gpt-4o-mini", "task.judge", tokens_in=200, tokens_out=20)
        breakdown = t.breakdown_by_purpose()
        assert "adapter.query" in breakdown
        assert "task.judge" in breakdown
        assert breakdown["adapter.query"]["calls"] == 1

    def test_reset_clears_state(self) -> None:
        t = CostTracker()
        t.record("gpt-4o-mini", "adapter.query", tokens_in=100, tokens_out=10)
        t.reset()
        assert t.total_usd == 0.0
        assert t.total_llm_calls == 0

    def test_thread_local_current(self) -> None:
        t = CostTracker()
        CostTracker.install(t)
        assert CostTracker.current() is t
        CostTracker.uninstall()
