"""Synthetic corpus generation (deterministic templates + ground truth)."""

from wikibench.corpora.synthetic.generator import SyntheticGenerator
from wikibench.corpora.synthetic.pipeline import run_pipeline

__all__ = ["SyntheticGenerator", "run_pipeline"]
