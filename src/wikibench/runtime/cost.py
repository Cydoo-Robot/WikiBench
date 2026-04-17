"""Cost tracking and hard-limit enforcement.

All LLM calls routed through ``llm_call`` accumulate into a thread-local
``CostTracker``.  The tracker can be reset per-run and will raise
``CostLimitExceededError`` when a configured hard limit is exceeded.
"""

from __future__ import annotations

import logging
import threading
from collections import defaultdict
from dataclasses import dataclass, field
from typing import ClassVar

log = logging.getLogger(__name__)

# USD per 1 000 tokens — updated 2026-04.  litellm's cost API is preferred
# when available; this table is the offline fallback.
_PRICE_TABLE: dict[str, dict[str, float]] = {
    "gpt-4o": {"input": 0.005, "output": 0.015},
    "gpt-4o-mini": {"input": 0.000150, "output": 0.000600},
    "gpt-4-turbo": {"input": 0.010, "output": 0.030},
    "gpt-4": {"input": 0.030, "output": 0.060},
    "gpt-3.5-turbo": {"input": 0.000500, "output": 0.001500},
    "claude-3-5-sonnet-20241022": {"input": 0.003, "output": 0.015},
    "claude-3-haiku-20240307": {"input": 0.00025, "output": 0.00125},
    "gemini/gemini-1.5-flash": {"input": 0.000075, "output": 0.000300},
    "gemini/gemini-2.0-flash": {"input": 0.000100, "output": 0.000400},
    "gemini/gemini-2.5-flash": {"input": 0.000150, "output": 0.000600},
    "gemini/gemini-2.5-pro-preview-04-17": {"input": 0.00125, "output": 0.010},
}


class CostLimitExceededError(RuntimeError):
    """Raised when a run exceeds its configured cost hard-limit."""

    def __init__(self, spent: float, limit: float) -> None:
        self.spent = spent
        self.limit = limit
        super().__init__(
            f"Cost hard-limit exceeded: spent ${spent:.4f} >= limit ${limit:.4f}. "
            "Aborting run to avoid runaway charges."
        )


@dataclass
class CallRecord:
    """One tracked LLM call."""

    model: str
    purpose: str
    tokens_in: int
    tokens_out: int
    cost_usd: float
    cached: bool = False


@dataclass
class CostTracker:
    """Accumulates cost across all LLM calls for a single run.

    Usage::

        tracker = CostTracker(hard_limit_usd=5.0)
        tracker.record("gpt-4o-mini", "adapter.query", tokens_in=200, tokens_out=50)
        print(tracker.total_usd)   # → ~0.000105
    """

    hard_limit_usd: float = float("inf")
    warn_threshold_usd: float = float("inf")

    _records: list[CallRecord] = field(default_factory=list, repr=False)
    _warned: bool = field(default=False, repr=False)

    # Thread-local singleton used by llm_call
    _local: ClassVar[threading.local] = threading.local()

    # ── Public API ────────────────────────────────────────────────────────────

    def record(
        self,
        model: str,
        purpose: str,
        tokens_in: int,
        tokens_out: int,
        cached: bool = False,
    ) -> float:
        """Record a completed call and return its estimated cost in USD."""
        cost = estimate_cost(model, tokens_in, tokens_out)
        self._records.append(
            CallRecord(
                model=model,
                purpose=purpose,
                tokens_in=tokens_in,
                tokens_out=tokens_out,
                cost_usd=cost,
                cached=cached,
            )
        )

        total = self.total_usd
        if not self._warned and total >= self.warn_threshold_usd:
            log.warning(
                "Cost warning: $%.4f spent (threshold $%.4f)", total, self.warn_threshold_usd
            )
            self._warned = True

        if total >= self.hard_limit_usd:
            raise CostLimitExceededError(total, self.hard_limit_usd)

        return cost

    @property
    def total_usd(self) -> float:
        return sum(r.cost_usd for r in self._records)

    @property
    def total_tokens_in(self) -> int:
        return sum(r.tokens_in for r in self._records)

    @property
    def total_tokens_out(self) -> int:
        return sum(r.tokens_out for r in self._records)

    @property
    def total_llm_calls(self) -> int:
        return sum(1 for r in self._records if not r.cached)

    def breakdown_by_purpose(self) -> dict[str, dict[str, float]]:
        """Return cost and token totals grouped by ``purpose`` bucket."""
        result: dict[str, dict[str, float]] = defaultdict(
            lambda: {"cost_usd": 0.0, "tokens_in": 0, "tokens_out": 0, "calls": 0}
        )
        for r in self._records:
            g = result[r.purpose]
            g["cost_usd"] += r.cost_usd
            g["tokens_in"] += r.tokens_in
            g["tokens_out"] += r.tokens_out
            g["calls"] += 0 if r.cached else 1
        return dict(result)

    def reset(self) -> None:
        self._records.clear()
        self._warned = False

    # ── Thread-local singleton helpers ────────────────────────────────────────

    @classmethod
    def current(cls) -> CostTracker:
        """Return the tracker installed for the current thread, or a no-op one."""
        return getattr(cls._local, "tracker", _NOOP_TRACKER)

    @classmethod
    def install(cls, tracker: CostTracker) -> None:
        """Install ``tracker`` as the active tracker for the current thread."""
        cls._local.tracker = tracker

    @classmethod
    def uninstall(cls) -> None:
        cls._local.tracker = _NOOP_TRACKER


# ── Standalone helpers ────────────────────────────────────────────────────────


def estimate_cost(model: str, tokens_in: int, tokens_out: int) -> float:
    """Estimate cost in USD for a single LLM call.

    Uses litellm's cost API when available; falls back to the built-in price
    table, then to zero (with a debug log) when the model is unknown.

    Args:
        model: Model slug.
        tokens_in: Prompt token count.
        tokens_out: Completion token count.

    Returns:
        Estimated cost in USD.
    """
    try:
        from litellm import completion_cost

        return float(
            completion_cost(
                model=model,
                prompt_tokens=tokens_in,
                completion_tokens=tokens_out,
            )
        )
    except Exception:
        pass

    # Offline fallback
    bare = model.split("/")[-1]
    prices = _PRICE_TABLE.get(model) or _PRICE_TABLE.get(bare)
    if prices:
        return (tokens_in * prices["input"] + tokens_out * prices["output"]) / 1_000
    log.debug("No pricing info for model %r; cost reported as 0.0", model)
    return 0.0


# Sentinel used when no tracker is installed (avoids None checks everywhere)
_NOOP_TRACKER = CostTracker(hard_limit_usd=float("inf"), warn_threshold_usd=float("inf"))
