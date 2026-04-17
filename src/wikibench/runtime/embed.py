"""Unified embedding call (Phase 1.5 — used by stance clustering)."""

from __future__ import annotations


def embed(texts: list[str], model: str = "text-embedding-3-small") -> list[list[float]]:
    raise NotImplementedError("embed — Phase 1.5.")
