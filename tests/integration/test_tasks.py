"""Integration tests for T1 / T2 / T3 tasks (mock LLM mode)."""

from __future__ import annotations

from pathlib import Path

import pytest

from wikibench.corpora.loader import load_corpus
from wikibench.models.corpus import Corpus
from wikibench.models.query import Query, QueryResponse
from wikibench.models.result import Score
from wikibench.runtime.cache import ResponseCache, reset_default_cache
from wikibench.tasks.contradiction_detection import ContradictionDetectionTask
from wikibench.tasks.knowledge_fidelity import KnowledgeFidelityTask
from wikibench.tasks.retrieval_accuracy import RetrievalAccuracyTask


@pytest.fixture(autouse=True)
def _mock(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("WIKIBENCH_LLM_MOCK", "1")
    reset_default_cache()
    from wikibench.runtime import cache as _c

    _c._default_cache = ResponseCache(cache_dir=tmp_path / "task-cache")
    yield  # type: ignore[misc]
    reset_default_cache()


@pytest.fixture(scope="module")
def tiny_corpus(tmp_path_factory: pytest.TempPathFactory) -> Corpus:
    repo = Path(__file__).parent.parent.parent
    return load_corpus(repo / "corpora" / "synthetic" / "tiny")


# ── T1 RetrievalAccuracy ──────────────────────────────────────────────────────


class TestRetrievalAccuracyTask:
    def test_prepare_returns_queries(self, tiny_corpus: Corpus) -> None:
        task = RetrievalAccuracyTask()
        queries = task.prepare(tiny_corpus)
        assert len(queries) == len(tiny_corpus.ground_truth.qa_pairs)

    def test_query_intent_is_qa(self, tiny_corpus: Corpus) -> None:
        task = RetrievalAccuracyTask()
        queries = task.prepare(tiny_corpus)
        assert all(q.intent == "qa" for q in queries)

    def test_score_returns_score_object(self, tiny_corpus: Corpus) -> None:
        task = RetrievalAccuracyTask()
        queries = task.prepare(tiny_corpus)
        q = queries[0]
        resp = QueryResponse(answer="gRPC over mTLS")
        score = task.score(q, resp, tiny_corpus)
        assert isinstance(score, Score)
        assert 0.0 <= score.value <= 1.0

    def test_score_unknown_query_returns_zero(self, tiny_corpus: Corpus) -> None:
        task = RetrievalAccuracyTask()
        task.prepare(tiny_corpus)
        q = Query(id="nonexistent", text="?", intent="qa")
        resp = QueryResponse(answer="something")
        score = task.score(q, resp, tiny_corpus)
        assert score.value == 0.0

    def test_aggregate_contains_mean(self, tiny_corpus: Corpus) -> None:
        task = RetrievalAccuracyTask()
        queries = task.prepare(tiny_corpus)
        scores = [task.score(q, QueryResponse(answer="test"), tiny_corpus) for q in queries]
        result = task.aggregate(scores)
        assert "mean" in result.slices
        assert 0.0 <= result.slices["mean"] <= 1.0

    def test_aggregate_difficulty_slices(self, tiny_corpus: Corpus) -> None:
        task = RetrievalAccuracyTask()
        queries = task.prepare(tiny_corpus)
        scores = [task.score(q, QueryResponse(answer="test"), tiny_corpus) for q in queries]
        result = task.aggregate(scores)
        # Should have at least one difficulty slice (easy/medium/hard)
        difficulty_keys = [k for k in result.slices if k.endswith("_mean")]
        assert len(difficulty_keys) > 0

    def test_aggregate_empty_scores(self, tiny_corpus: Corpus) -> None:
        task = RetrievalAccuracyTask()
        result = task.aggregate([])
        assert result.scores == []


# ── T2 KnowledgeFidelity ──────────────────────────────────────────────────────


class TestKnowledgeFidelityTask:
    def test_prepare_returns_fidelity_queries(self, tiny_corpus: Corpus) -> None:
        task = KnowledgeFidelityTask()
        queries = task.prepare(tiny_corpus)
        assert len(queries) == len(tiny_corpus.ground_truth.fidelity_claims)
        assert all(q.intent == "fidelity_check" for q in queries)

    def test_correct_verdict_scores_one(self, tiny_corpus: Corpus) -> None:
        task = KnowledgeFidelityTask()
        queries = task.prepare(tiny_corpus)
        # First claim: reference verdict is "not_supported"
        q = queries[0]
        claim = tiny_corpus.ground_truth.fidelity_claims[0]
        resp = QueryResponse(
            answer="This claim is not supported.",
            structured={"verdict": claim.verdict},
        )
        score = task.score(q, resp, tiny_corpus)
        assert score.value == 1.0

    def test_wrong_verdict_scores_zero(self, tiny_corpus: Corpus) -> None:
        task = KnowledgeFidelityTask()
        queries = task.prepare(tiny_corpus)
        q = queries[0]
        claim = tiny_corpus.ground_truth.fidelity_claims[0]
        wrong = "supported" if claim.verdict != "supported" else "not_supported"
        resp = QueryResponse(answer="...", structured={"verdict": wrong})
        score = task.score(q, resp, tiny_corpus)
        assert score.value == 0.0

    def test_aggregate_has_hallucination_rate(self, tiny_corpus: Corpus) -> None:
        task = KnowledgeFidelityTask()
        queries = task.prepare(tiny_corpus)
        scores = [
            task.score(
                q, QueryResponse(answer="x", structured={"verdict": "not_supported"}), tiny_corpus
            )
            for q in queries
        ]
        result = task.aggregate(scores)
        assert "hallucination_rate" in result.slices
        assert "precision" in result.slices
        assert "recall" in result.slices

    def test_verdict_alias_normalisation(self, tiny_corpus: Corpus) -> None:
        """Aliases like 'false', 'unsupported' should map to 'not_supported'."""
        task = KnowledgeFidelityTask()
        queries = task.prepare(tiny_corpus)
        claim = tiny_corpus.ground_truth.fidelity_claims[0]
        assert claim.verdict == "not_supported"
        q = queries[0]
        resp = QueryResponse(answer="...", structured={"verdict": "false"})
        score = task.score(q, resp, tiny_corpus)
        assert score.details["adapter_verdict"] == "not_supported"


# ── T3 ContradictionDetection ─────────────────────────────────────────────────


class TestContradictionDetectionTask:
    def test_prepare_returns_queries(self, tiny_corpus: Corpus) -> None:
        task = ContradictionDetectionTask()
        queries = task.prepare(tiny_corpus)
        assert len(queries) == len(tiny_corpus.ground_truth.contradictions)
        assert all(q.intent == "contradiction_check" for q in queries)

    def test_correct_flag_scores_one(self, tiny_corpus: Corpus) -> None:
        task = ContradictionDetectionTask()
        queries = task.prepare(tiny_corpus)
        q = queries[0]
        resp = QueryResponse(
            answer="Yes there is a contradiction.",
            structured={"has_contradiction": True, "pairs": []},
        )
        score = task.score(q, resp, tiny_corpus)
        assert score.value == 1.0

    def test_missed_contradiction_scores_zero(self, tiny_corpus: Corpus) -> None:
        task = ContradictionDetectionTask()
        queries = task.prepare(tiny_corpus)
        q = queries[0]
        resp = QueryResponse(
            answer="No contradiction found.",
            structured={"has_contradiction": False, "pairs": []},
        )
        score = task.score(q, resp, tiny_corpus)
        assert score.value == 0.0

    def test_text_inference_when_no_structured(self, tiny_corpus: Corpus) -> None:
        """If structured is empty, infer from free text."""
        task = ContradictionDetectionTask()
        queries = task.prepare(tiny_corpus)
        q = queries[0]
        resp = QueryResponse(answer="These two documents clearly contradict each other.")
        score = task.score(q, resp, tiny_corpus)
        assert score.value == 1.0

    def test_aggregate_recall(self, tiny_corpus: Corpus) -> None:
        task = ContradictionDetectionTask()
        queries = task.prepare(tiny_corpus)
        scores = [
            task.score(
                q,
                QueryResponse(answer="x", structured={"has_contradiction": True}),
                tiny_corpus,
            )
            for q in queries
        ]
        result = task.aggregate(scores)
        assert "recall" in result.slices
        assert result.slices["recall"] == 1.0
