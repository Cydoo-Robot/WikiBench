"""Text normalisation helpers."""

from __future__ import annotations

import re


def normalise_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def truncate(text: str, max_chars: int, suffix: str = "…") -> str:
    if len(text) <= max_chars:
        return text
    return text[: max_chars - len(suffix)] + suffix
