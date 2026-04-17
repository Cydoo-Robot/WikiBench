"""Unified LLM call wrapper (Phase 1 Week 2).

All LLM calls — from adapters, tasks, and the judge — must go through
``llm_call`` so that token counting and cost tracking are accurate.
"""

from __future__ import annotations

from typing import Any


def llm_call(
    model: str,
    messages: list[dict[str, str]],
    purpose: str = "unknown",
    **kwargs: Any,
) -> str:
    """Make a chat-completion call via litellm and track cost.

    Parameters
    ----------
    model:
        Model slug understood by litellm, e.g. ``"gpt-4o-mini"``.
    messages:
        OpenAI-format message list.
    purpose:
        Cost-tracking bucket, e.g. ``"adapter.query"`` or ``"task.judge"``.
    """
    raise NotImplementedError("llm_call — Phase 1 Week 2.")
