"""Write :class:`DocSpec` trees to ``docs/**/*.md``."""

from __future__ import annotations

import random
from pathlib import Path

from wikibench.corpora.synthetic.fact_sampler import DocSpec
from wikibench.corpora.synthetic.noise import inject_filler_paragraph


def write_documents(
    corpus_root: Path,
    specs: list[DocSpec],
    rng: random.Random | None = None,
    noise_probability: float = 0.0,
) -> None:
    """Write markdown files under ``corpus_root/docs/``."""
    docs_dir = corpus_root / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)

    rng = rng or random.Random(0)
    for spec in specs:
        text = spec.body
        if noise_probability > 0:
            text = inject_filler_paragraph(text, rng, probability=noise_probability)
        out = docs_dir / spec.rel_path
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
