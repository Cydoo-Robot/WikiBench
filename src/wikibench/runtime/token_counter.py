"""Token counting utilities.

Provides a single entry-point ``count_tokens`` that works for any model
supported by litellm.  Falls back to a rough character-based estimate when
the model's tokeniser is not available locally.
"""

from __future__ import annotations

import logging

log = logging.getLogger(__name__)

# Models whose tiktoken encoding name differs from the model slug.
_TIKTOKEN_ALIASES: dict[str, str] = {
    "gpt-4o": "o200k_base",
    "gpt-4o-mini": "o200k_base",
    "gpt-4": "cl100k_base",
    "gpt-4-turbo": "cl100k_base",
    "gpt-3.5-turbo": "cl100k_base",
    "text-embedding-3-small": "cl100k_base",
    "text-embedding-3-large": "cl100k_base",
}

# Models that use Google's SentencePiece tokenizer — tiktoken cannot count
# these accurately; we fall through to the character-based estimate.
_GOOGLE_MODEL_PREFIXES = ("gemini/", "google/", "gemini-")


def _is_google_model(model: str) -> bool:
    bare = model.split("/")[-1].lower()
    return any(model.lower().startswith(p) for p in _GOOGLE_MODEL_PREFIXES) or bare.startswith(
        "gemini"
    )


# Rough chars-per-token ratios used when tiktoken is unavailable.
_CHARS_PER_TOKEN = 4.0


def count_tokens(text: str, model: str = "gpt-4o-mini") -> int:
    """Return the number of tokens in ``text`` for the given model.

    Uses tiktoken when available; falls back to ``len(text) / 4`` otherwise.

    Args:
        text: The string to count tokens for.
        model: Model slug (e.g. ``"gpt-4o-mini"``).

    Returns:
        Estimated token count (always >= 1 for non-empty text).
    """
    if not text:
        return 0

    # Google Gemini models use SentencePiece — skip tiktoken entirely
    if _is_google_model(model):
        return max(1, int(len(text) / _CHARS_PER_TOKEN))

    try:
        import tiktoken

        encoding_name = _resolve_encoding(model)
        enc = tiktoken.get_encoding(encoding_name)
        return len(enc.encode(text))
    except Exception as exc:
        log.debug("tiktoken unavailable for model %r (%s); using char estimate", model, exc)
        return max(1, int(len(text) / _CHARS_PER_TOKEN))


def count_messages_tokens(messages: list[dict[str, str]], model: str = "gpt-4o-mini") -> int:
    """Estimate total tokens for an OpenAI-format message list.

    Includes per-message overhead (~4 tokens each) as per OpenAI's cookbook.

    Args:
        messages: List of ``{"role": ..., "content": ...}`` dicts.
        model: Model slug.

    Returns:
        Estimated total token count including message overhead.
    """
    total = 3  # reply priming tokens
    for msg in messages:
        total += 4  # per-message overhead
        total += count_tokens(msg.get("content", ""), model)
        total += count_tokens(msg.get("role", ""), model)
    return total


def _resolve_encoding(model: str) -> str:
    """Map a model slug to a tiktoken encoding name."""
    if model in _TIKTOKEN_ALIASES:
        return _TIKTOKEN_ALIASES[model]

    # Strip provider prefix (e.g. "openai/gpt-4o" → "gpt-4o")
    bare = model.split("/")[-1]
    if bare in _TIKTOKEN_ALIASES:
        return _TIKTOKEN_ALIASES[bare]

    # Try tiktoken's own resolution
    try:
        import tiktoken

        tiktoken.encoding_for_model(bare)
        return bare
    except Exception:
        pass

    # Default fallback
    return "cl100k_base"
