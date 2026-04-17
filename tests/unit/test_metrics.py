"""Unit tests for metrics registry."""

from __future__ import annotations

import pytest

from wikibench.metrics import list_metrics, register_metric


def test_built_in_metrics_registered() -> None:
    import wikibench.metrics._registry  # noqa: F401 — triggers registrations

    metrics = list_metrics()
    assert "retrieval_accuracy" in metrics
    assert "fidelity_score" in metrics
    assert "hallucination_rate" in metrics


def test_custom_metric_registration() -> None:
    @register_metric(id="test_custom_metric", higher_is_better=True, range=(0.0, 1.0))
    def _custom(task_results: dict) -> float:  # type: ignore[type-arg]
        return 1.0

    assert "test_custom_metric" in list_metrics()
