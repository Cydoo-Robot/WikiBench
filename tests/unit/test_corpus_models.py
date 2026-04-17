"""Unit tests for Corpus data models."""

from __future__ import annotations

from wikibench.models.corpus import (
    ContradictionPair,
    Corpus,
    CorpusMetadata,
    FidelityClaim,
    GroundTruth,
    QAPair,
)
from wikibench.models.document import Document


def _make_metadata(**overrides: object) -> CorpusMetadata:
    defaults: dict = {
        "id": "test-corpus@1.0.0",
        "version": "1.0.0",
        "tier": "synthetic",
        "doc_count": 2,
    }
    defaults.update(overrides)
    return CorpusMetadata(**defaults)


def _make_doc(idx: int = 1) -> Document:
    return Document(id=f"doc-{idx:03d}", path=f"docs/doc{idx}.md", content=f"# Doc {idx}")


class TestCorpusMetadata:
    def test_defaults(self) -> None:
        meta = _make_metadata()
        assert meta.language == "en"
        assert meta.domain == ""
        assert meta.wikibench_min_version == "0.1.0"

    def test_id_property(self) -> None:
        meta = _make_metadata(id="my-corpus@2.0.0")
        assert meta.id == "my-corpus@2.0.0"

    def test_extra_fields_stored(self) -> None:
        meta = _make_metadata(extra={"custom_key": "custom_value"})
        assert meta.extra["custom_key"] == "custom_value"


class TestGroundTruth:
    def test_empty_ground_truth(self) -> None:
        gt = GroundTruth()
        assert gt.qa_pairs == []
        assert gt.fidelity_claims == []
        assert gt.contradictions == []

    def test_qa_pair(self) -> None:
        qa = QAPair(
            id="qa-1",
            query_id="q-1",
            document_ids=["doc-001"],
            question="What is X?",
            answer="X is Y.",
        )
        assert qa.difficulty == "medium"

    def test_fidelity_claim_verdicts(self) -> None:
        for verdict in ("supported", "not_supported", "unknown"):
            claim = FidelityClaim(
                id=f"fc-{verdict}",
                document_id="doc-001",
                claim="Some claim.",
                verdict=verdict,
            )
            assert claim.verdict == verdict

    def test_contradiction_pair(self) -> None:
        pair = ContradictionPair(
            id="ct-1",
            doc_id_a="doc-001",
            doc_id_b="doc-002",
            description="Doc A says X, Doc B says not X.",
        )
        assert pair.doc_id_a != pair.doc_id_b


class TestCorpus:
    def test_id_delegates_to_metadata(self) -> None:
        corpus = Corpus(
            metadata=_make_metadata(id="my-corpus@1.0.0"),
            documents=[_make_doc()],
            ground_truth=GroundTruth(),
        )
        assert corpus.id == "my-corpus@1.0.0"

    def test_empty_corpus(self) -> None:
        corpus = Corpus(
            metadata=_make_metadata(doc_count=0),
            documents=[],
            ground_truth=GroundTruth(),
        )
        assert len(corpus.documents) == 0

    def test_corpus_with_ground_truth(self) -> None:
        gt = GroundTruth(
            qa_pairs=[
                QAPair(id="q1", query_id="q1", document_ids=["d1"], question="Q?", answer="A.")
            ]
        )
        corpus = Corpus(
            metadata=_make_metadata(),
            documents=[_make_doc()],
            ground_truth=gt,
        )
        assert len(corpus.ground_truth.qa_pairs) == 1
