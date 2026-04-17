"""Metrics registry and helpers."""

from __future__ import annotations

from typing import Any, Callable

_METRIC_REGISTRY: dict[str, dict[str, Any]] = {}


def register_metric(
    id: str,  # noqa: A002
    higher_is_better: bool = True,
    range: tuple[float, float] = (0.0, 1.0),  # noqa: A002
) -> Callable[[Callable[..., float]], Callable[..., float]]:
    """Decorator to register a metric computation function."""

    def decorator(fn: Callable[..., float]) -> Callable[..., float]:
        _METRIC_REGISTRY[id] = {
            "fn": fn,
            "higher_is_better": higher_is_better,
            "range": range,
        }
        return fn

    return decorator


def list_metrics() -> list[str]:
    return list(_METRIC_REGISTRY)
