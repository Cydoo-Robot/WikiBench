"""Unified LLM call wrapper.

Every LLM call — adapters, tasks, judge — **must** go through :func:`llm_call`
so that token counting, cost tracking, caching, and timeout enforcement are
consistent across the framework.

Quick reference::

    from wikibench.runtime import llm_call

    reply = llm_call(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Hello"}],
        purpose="adapter.query",
    )

Environment variables
---------------------
``WIKIBENCH_LLM_MOCK``
    When set to ``"1"`` or ``"true"``, all calls return a canned stub
    response without hitting any API.  Useful in tests and CI.
"""

from __future__ import annotations

import logging
import os
import time
from typing import Any

from wikibench.runtime.cache import ResponseCache, get_default_cache
from wikibench.runtime.cost import CostTracker
from wikibench.runtime.timeout import timeout as _timeout
from wikibench.runtime.token_counter import count_messages_tokens, count_tokens

log = logging.getLogger(__name__)

# ── Mock mode ─────────────────────────────────────────────────────────────────
_MOCK_ENV_VARS = {"WIKIBENCH_LLM_MOCK", "WIKIBENCH_TEST_MODE"}

_MOCK_REPLY = '{"verdict": "supported", "explanation": "Mock response for testing."}'


def _is_mock_mode() -> bool:
    return any(os.getenv(v, "").lower() in ("1", "true", "yes") for v in _MOCK_ENV_VARS)


# ── Public API ────────────────────────────────────────────────────────────────


def llm_call(
    model: str,
    messages: list[dict[str, str]],
    purpose: str = "unknown",
    *,
    cache: ResponseCache | None = None,
    use_cache: bool = True,
    timeout_s: float = 120.0,
    temperature: float = 0.0,
    max_tokens: int | None = None,
    **litellm_kwargs: Any,
) -> str:
    """Make a chat-completion call and return the assistant message content.

    Pipeline (in order):
    1. Check cache → return early on hit.
    2. Check mock mode → return stub without API call.
    3. Call litellm with timeout.
    4. Record tokens + cost in the active :class:`~wikibench.runtime.cost.CostTracker`.
    5. Store response in cache.
    6. Return response string.

    Args:
        model: litellm model slug, e.g. ``"gpt-4o-mini"`` or
               ``"anthropic/claude-3-haiku-20240307"``.
        messages: OpenAI-format message list.
        purpose: Cost-tracking bucket — ``"adapter.ingest"`` / ``"adapter.query"`` /
                 ``"task.judge"`` / ``"corpus.generate"``.
        cache: Explicit cache instance.  Defaults to the process-wide cache.
        use_cache: Set to ``False`` to bypass caching for this call.
        timeout_s: Per-call timeout in seconds.
        temperature: Sampling temperature (0 = deterministic).
        max_tokens: Maximum completion tokens (``None`` = model default).
        **litellm_kwargs: Extra keyword arguments forwarded to ``litellm.completion``.

    Returns:
        Assistant message content as a plain string.

    Raises:
        :class:`~wikibench.runtime.cost.CostLimitExceededError`: If the active
            tracker's hard limit is exceeded.
        :class:`~wikibench.runtime.timeout.TimeoutError`: If the call exceeds
            ``timeout_s``.
        ``litellm.exceptions.AuthenticationError`` and similar: propagated as-is.
    """
    effective_cache = cache if cache is not None else get_default_cache()

    # ── 1. Cache lookup ───────────────────────────────────────────────────────
    if use_cache:
        cached = effective_cache.get(model, messages)
        if cached is not None:
            CostTracker.current().record(
                model=model,
                purpose=purpose,
                tokens_in=count_messages_tokens(messages, model),
                tokens_out=count_tokens(cached, model),
                cached=True,
            )
            return cached

    # ── 2. Mock mode ──────────────────────────────────────────────────────────
    if _is_mock_mode():
        log.debug("Mock mode active — returning stub for purpose=%r", purpose)
        tokens_in = count_messages_tokens(messages, model)
        tokens_out = count_tokens(_MOCK_REPLY, model)
        CostTracker.current().record(
            model=model,
            purpose=purpose,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            cached=False,
        )
        if use_cache:
            effective_cache.set(model, messages, _MOCK_REPLY)
        return _MOCK_REPLY

    # ── 3. Actual LLM call ────────────────────────────────────────────────────
    import litellm

    call_kwargs: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        **litellm_kwargs,
    }
    if max_tokens is not None:
        call_kwargs["max_tokens"] = max_tokens

    t0 = time.perf_counter()
    try:
        with _timeout(timeout_s):
            response = litellm.completion(**call_kwargs)
    except Exception as exc:
        log.error("llm_call failed (model=%r purpose=%r): %s", model, purpose, exc)
        raise

    elapsed = time.perf_counter() - t0
    log.debug("llm_call ok model=%r purpose=%r elapsed=%.2fs", model, purpose, elapsed)

    content: str = response.choices[0].message.content or ""

    # ── 4. Track cost ─────────────────────────────────────────────────────────
    usage = getattr(response, "usage", None)
    tokens_in = int(getattr(usage, "prompt_tokens", 0)) or count_messages_tokens(messages, model)
    tokens_out = int(getattr(usage, "completion_tokens", 0)) or count_tokens(content, model)

    CostTracker.current().record(
        model=model,
        purpose=purpose,
        tokens_in=tokens_in,
        tokens_out=tokens_out,
        cached=False,
    )

    # ── 5. Store in cache ─────────────────────────────────────────────────────
    if use_cache and content:
        effective_cache.set(model, messages, content)

    return content
