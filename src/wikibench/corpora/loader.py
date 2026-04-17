"""Corpus loader — reads a manifest.yaml directory into a Corpus object (Phase 1 Week 1)."""

from __future__ import annotations

from pathlib import Path

from wikibench.models.corpus import Corpus


def load_corpus(path: str | Path) -> Corpus:
    """Load a WikiBench corpus from a directory containing ``manifest.yaml``.

    Args:
        path: Path to the corpus root directory.

    Returns:
        A fully populated :class:`~wikibench.models.corpus.Corpus` instance.
    """
    raise NotImplementedError("load_corpus — Phase 1 Week 1.")
