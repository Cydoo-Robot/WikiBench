"""Query and QueryResponse models."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

QueryIntent = Literal["qa", "fidelity_check", "contradiction_check", "grounding"]


class Query(BaseModel):
    """A single question posed to a WikiAdapter."""

    id: str
    text: str
    intent: QueryIntent
    params: dict[str, Any] = Field(default_factory=dict)
    """Intent-specific parameters.

    * ``fidelity_check`` — ``{"claim": "...", "decision_space": [...]}``
    * ``contradiction_check`` — ``{}``
    * ``grounding`` — ``{}``
    """


class QueryResponse(BaseModel):
    """The answer returned by a WikiAdapter for a single Query."""

    answer: str
    """Free-text main answer."""
    structured: dict[str, Any] = Field(default_factory=dict)
    """Intent-specific structured fields.

    * ``qa``                 → ``{}`` (optional ``"candidates"``)
    * ``fidelity_check``     → ``{"verdict": "supported|not_supported|unknown"}``
    * ``contradiction_check`` → ``{"has_contradiction": bool, "pairs": [...]}``
    * ``grounding``          → ``{"sources": ["doc1#L10", ...]}``
    """
    sources: list[str] = Field(default_factory=list)
    confidence: float | None = None
    raw: dict[str, Any] | None = None
    """Adapter-private raw return value for debugging."""
