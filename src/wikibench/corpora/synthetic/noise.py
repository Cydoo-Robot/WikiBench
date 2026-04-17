"""Optional noise injection to make synthetic docs less templated."""

from __future__ import annotations

import random


def inject_filler_paragraph(body: str, rng: random.Random, probability: float = 0.25) -> str:
    """With *probability*, append a generic filler paragraph (harmless boilerplate)."""
    if rng.random() >= probability:
        return body
    filler = (
        "\n\n## Administrative note\n"
        "This page is auto-generated for evaluation purposes. "
        "Ignore scheduling metadata in this section.\n"
    )
    return body + filler
