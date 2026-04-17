"""Tests for SyntheticGenerator and synthetic corpus pipeline."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from wikibench.corpora.loader import load_corpus
from wikibench.corpora.synthetic.domains import get_domain, list_domains
from wikibench.corpora.synthetic.generator import SyntheticGenerator
from wikibench.corpora.synthetic.knowledge_graph import KnowledgeGraph
from wikibench.corpora.synthetic.pipeline import run_pipeline
from wikibench.corpora.synthetic.verifier import verify_generated_corpus

if TYPE_CHECKING:
    from pathlib import Path


def test_list_domains() -> None:
    d = list_domains()
    assert "saas_engineering" in d
    assert "clinical_trials" in d


def test_get_domain_alias() -> None:
    assert get_domain("saas").id == "saas_engineering"


def test_unknown_domain_raises() -> None:
    with pytest.raises(KeyError, match="Unknown domain"):
        get_domain("no-such-domain-xyz")


def test_generator_produces_valid_corpus(tmp_path: Path) -> None:
    out = tmp_path / "corp"
    gen = SyntheticGenerator(domain="saas", seed=7, qa_per_doc=2)
    path = gen.generate(out, n_docs=4)
    assert path == out.resolve()

    vr = verify_generated_corpus(path)
    assert vr.ok, vr

    corpus = load_corpus(path)
    assert len(corpus.documents) == 4
    assert corpus.metadata.doc_count == 4
    assert "synthetic-gen-saas_engineering-s7@" in corpus.metadata.id
    assert len(corpus.ground_truth.qa_pairs) == 8  # 2 per doc
    assert len(corpus.ground_truth.fidelity_claims) == 4
    assert len(corpus.ground_truth.contradictions) == 2  # pairs (0,1) and (2,3)


def test_generator_single_doc_no_contradictions(tmp_path: Path) -> None:
    gen = SyntheticGenerator(domain="clinical_trials", seed=1)
    gen.generate(tmp_path / "one", n_docs=1)
    corpus = load_corpus(tmp_path / "one")
    assert len(corpus.ground_truth.contradictions) == 0


def test_deterministic_reproducible(tmp_path: Path) -> None:
    a = tmp_path / "a"
    b = tmp_path / "b"
    SyntheticGenerator(domain="saas", seed=99).generate(a, n_docs=3)
    SyntheticGenerator(domain="saas", seed=99).generate(b, n_docs=3)
    t1 = (a / "docs" / "topics" / "000-microservices-architecture.md").read_text(encoding="utf-8")
    t2 = (b / "docs" / "topics" / "000-microservices-architecture.md").read_text(encoding="utf-8")
    assert t1 == t2


def test_pipeline_matches_generator(tmp_path: Path) -> None:
    p1 = SyntheticGenerator(domain="saas", seed=3).generate(tmp_path / "g", 5)
    p2 = run_pipeline(tmp_path / "p", domain="saas", n_docs=5, seed=3)
    m1 = (p1 / "manifest.yaml").read_text(encoding="utf-8")
    m2 = (p2 / "manifest.yaml").read_text(encoding="utf-8")
    assert m1 == m2


def test_qa_per_doc_one(tmp_path: Path) -> None:
    gen = SyntheticGenerator(domain="saas", seed=0, qa_per_doc=1)
    gen.generate(tmp_path / "q", n_docs=2)
    corpus = load_corpus(tmp_path / "q")
    assert len(corpus.ground_truth.qa_pairs) == 2


def test_knowledge_graph_pairs() -> None:
    g = KnowledgeGraph.build(get_domain("saas"), n_docs=5)
    assert len(g.contradiction_pair_indices) == 2
    assert g.contradiction_pair_indices[0] == (0, 1)


def test_use_llm_raises() -> None:
    with pytest.raises(NotImplementedError):
        SyntheticGenerator(domain="saas", use_llm=True)
