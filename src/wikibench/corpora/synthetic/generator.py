"""SyntheticGenerator — deterministic synthetic corpus generation (Phase 1 Week 5)."""

from __future__ import annotations

import random
from datetime import date
from pathlib import Path

import yaml

from wikibench.corpora.synthetic.doc_writer import write_documents
from wikibench.corpora.synthetic.domains import get_domain
from wikibench.corpora.synthetic.fact_sampler import build_ground_truth, sample_documents
from wikibench.corpora.synthetic.knowledge_graph import KnowledgeGraph
from wikibench.corpora.synthetic.verifier import verify_generated_corpus


class SyntheticGenerator:
    """Generate a WikiBench corpus directory (manifest + docs + ground truth).

    Generation is **fully deterministic** given ``domain``, ``seed``, and ``n_docs``.
    Optional LLM enrichment is reserved for a future release (``use_llm=True`` raises).
    """

    def __init__(
        self,
        domain: str,
        seed: int = 42,
        qa_per_doc: int = 2,
        noise_probability: float = 0.0,
        use_llm: bool = False,
    ) -> None:
        if use_llm:
            raise NotImplementedError(
                "LLM-enriched synthetic generation is not implemented yet; "
                "omit use_llm or set it to False for deterministic generation."
            )
        self._domain = get_domain(domain)
        self.seed = seed
        self.qa_per_doc = min(2, max(1, qa_per_doc))
        self.noise_probability = noise_probability

    def generate(self, out: str | Path, n_docs: int) -> Path:
        """Write a corpus tree to *out* and return the resolved directory path.

        Raises:
            ValueError: ``n_docs < 1`` or domain has no concepts.
            RuntimeError: verification failed after write.
        """
        if n_docs < 1:
            raise ValueError("n_docs must be >= 1")

        out_path = Path(out).resolve()
        rng = random.Random(self.seed)

        graph = KnowledgeGraph.build(self._domain, n_docs)
        specs = sample_documents(graph, n_docs, rng)
        qa_rows, fid_rows, contr_rows = build_ground_truth(
            graph, specs, qa_per_doc=self.qa_per_doc
        )

        out_path.mkdir(parents=True, exist_ok=True)
        (out_path / "ground_truth").mkdir(parents=True, exist_ok=True)

        write_documents(out_path, specs, rng=rng, noise_probability=self.noise_probability)

        corpus_id = f"synthetic-gen-{graph.domain_id}-s{self.seed}@0.1.0"
        manifest: dict = {
            "id": corpus_id,
            "version": "0.1.0",
            "description": (
                f"Deterministic synthetic corpus ({graph.domain_id}, "
                f"seed={self.seed}, n_docs={n_docs})."
            ),
            "tier": "synthetic",
            "domain": graph.domain_id,
            "language": "en",
            "doc_count": n_docs,
            "created_at": date.today().isoformat(),
            "wikibench_min_version": "0.1.0",
        }
        (out_path / "manifest.yaml").write_text(
            yaml.safe_dump(manifest, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )

        _write_jsonl(out_path / "ground_truth" / "qa_pairs.jsonl", qa_rows)
        _write_jsonl(out_path / "ground_truth" / "fidelity_claims.jsonl", fid_rows)
        _write_jsonl(out_path / "ground_truth" / "contradictions.jsonl", contr_rows)

        vr = verify_generated_corpus(out_path)
        if not vr.ok:
            raise RuntimeError(f"Generated corpus failed verification:\n{vr}")

        return out_path


def _write_jsonl(path: Path, rows: list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(row.model_dump_json() + "\n")
