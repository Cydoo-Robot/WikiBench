"""Unit tests for pydantic data models."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from wikibench.models.document import Document, ForumThread
from wikibench.models.query import Query, QueryResponse
from wikibench.models.corpus import CorpusMetadata, GroundTruth
from wikibench.models.result import IngestStats, BenchmarkResult, RunEnvironment


class TestDocument:
    def test_minimal_document(self) -> None:
        doc = Document(id="d1", path="foo/bar.md", content="# Hello")
        assert doc.modality == "markdown"
        assert doc.metadata == {}

    def test_modality_validation(self) -> None:
        doc = Document(id="d2", path="a.md", content="x", modality="forum_thread")
        assert doc.modality == "forum_thread"

    def test_invalid_modality(self) -> None:
        with pytest.raises(ValidationError):
            Document(id="d3", path="a.md", content="x", modality="invalid_type")  # type: ignore[arg-type]


class TestQuery:
    def test_qa_query(self) -> None:
        q = Query(id="q1", text="What is X?", intent="qa")
        assert q.params == {}

    def test_fidelity_query(self) -> None:
        q = Query(
            id="q2",
            text="Is this claim correct?",
            intent="fidelity_check",
            params={"claim": "PostgreSQL is used", "decision_space": ["supported", "not_supported"]},
        )
        assert q.params["claim"] == "PostgreSQL is used"

    def test_invalid_intent(self) -> None:
        with pytest.raises(ValidationError):
            Query(id="q3", text="x", intent="unknown_intent")  # type: ignore[arg-type]


class TestQueryResponse:
    def test_minimal_response(self) -> None:
        r = QueryResponse(answer="42")
        assert r.structured == {}
        assert r.sources == []
        assert r.confidence is None


class TestIngestStats:
    def test_required_fields(self) -> None:
        stats = IngestStats(
            tokens_in=100,
            tokens_out=50,
            llm_calls=1,
            duration_s=1.5,
            wiki_tokens=200,
        )
        assert stats.cost_usd is None


class TestCorpusMetadata:
    def test_from_dict(self) -> None:
        meta = CorpusMetadata(
            id="synthetic-tiny@0.1.0",
            version="0.1.0",
            tier="synthetic",
            doc_count=5,
        )
        assert meta.language == "en"


class TestBenchmarkResult:
    def test_auto_run_id(self) -> None:
        env = RunEnvironment(
            python_version="3.11.0",
            os="Linux",
            wikibench_version="0.1.0-alpha",
            impl_version="0.1.0",
            llm_models={"adapter_backend": "gpt-4o-mini"},
            seed=42,
        )
        stats = IngestStats(
            tokens_in=0, tokens_out=0, llm_calls=0, duration_s=0.01, wiki_tokens=100
        )
        result = BenchmarkResult(
            impl="naive@0.1.0",
            corpus_id="synthetic-tiny@0.1.0",
            environment=env,
            ingest=stats,
        )
        assert result.run_id  # auto-generated UUID
        assert result.metrics == {}
