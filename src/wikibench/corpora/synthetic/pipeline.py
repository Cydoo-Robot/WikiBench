"""Thin facade over :class:`~wikibench.corpora.synthetic.generator.SyntheticGenerator`."""

from __future__ import annotations

from pathlib import Path

from wikibench.corpora.synthetic.generator import SyntheticGenerator


def run_pipeline(
    out: str | Path,
    domain: str,
    n_docs: int,
    seed: int = 42,
    qa_per_doc: int = 2,
    noise_probability: float = 0.0,
    use_llm: bool = False,
) -> Path:
    """Generate a corpus at *out*; same semantics as :meth:`SyntheticGenerator.generate`."""
    gen = SyntheticGenerator(
        domain=domain,
        seed=seed,
        qa_per_doc=qa_per_doc,
        noise_probability=noise_probability,
        use_llm=use_llm,
    )
    return gen.generate(out, n_docs)
