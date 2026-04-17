"""Integration tests for Runner (mock LLM mode)."""

from __future__ import annotations

from pathlib import Path

import pytest

from wikibench.corpora.loader import load_corpus
from wikibench.models.corpus import Corpus
from wikibench.models.result import BenchmarkResult
from wikibench.runner.runner import Runner
from wikibench.runtime.cache import ResponseCache, reset_default_cache


TINY_CORPUS_PATH = Path(__file__).parent.parent.parent / "corpora" / "synthetic" / "tiny"


@pytest.fixture(autouse=True)
def _mock(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("WIKIBENCH_LLM_MOCK", "1")
    reset_default_cache()
    from wikibench.runtime import cache as _c
    _c._default_cache = ResponseCache(cache_dir=tmp_path / "runner-cache")
    yield  # type: ignore[misc]
    reset_default_cache()


@pytest.fixture()
def tiny_corpus() -> Corpus:
    return load_corpus(TINY_CORPUS_PATH)


# ── Runner instantiation ──────────────────────────────────────────────────────

class TestRunnerInstantiation:
    def test_from_adapter_instance(self, tiny_corpus: Corpus) -> None:
        from wikibench.adapters.builtin.naive import NaiveAdapter
        adapter = NaiveAdapter({})
        runner = Runner(adapter_spec=adapter, corpus=tiny_corpus)
        assert runner is not None

    def test_from_adapter_class(self, tiny_corpus: Corpus) -> None:
        from wikibench.adapters.builtin.naive import NaiveAdapter
        runner = Runner(adapter_spec=NaiveAdapter, corpus=tiny_corpus)
        assert runner is not None

    def test_from_corpus_path(self) -> None:
        from wikibench.adapters.builtin.naive import NaiveAdapter
        runner = Runner(
            adapter_spec=NaiveAdapter,
            corpus=str(TINY_CORPUS_PATH),
        )
        assert runner is not None

    def test_missing_corpus_raises(self) -> None:
        from wikibench.adapters.builtin.naive import NaiveAdapter
        runner = Runner(adapter_spec=NaiveAdapter, corpus=None)
        with pytest.raises(ValueError, match="corpus"):
            runner.run()


# ── Runner.run() ──────────────────────────────────────────────────────────────

class TestRunnerRun:
    def test_returns_benchmark_result(self, tiny_corpus: Corpus) -> None:
        from wikibench.adapters.builtin.naive import NaiveAdapter
        result = Runner(
            adapter_spec=NaiveAdapter,
            corpus=tiny_corpus,
            tasks=["knowledge_fidelity", "contradiction_detection"],
        ).run()
        assert isinstance(result, BenchmarkResult)

    def test_result_has_impl_name(self, tiny_corpus: Corpus) -> None:
        from wikibench.adapters.builtin.naive import NaiveAdapter
        result = Runner(adapter_spec=NaiveAdapter, corpus=tiny_corpus,
                        tasks=["knowledge_fidelity"]).run()
        assert "naive" in result.impl

    def test_result_has_corpus_id(self, tiny_corpus: Corpus) -> None:
        from wikibench.adapters.builtin.naive import NaiveAdapter
        result = Runner(adapter_spec=NaiveAdapter, corpus=tiny_corpus,
                        tasks=["knowledge_fidelity"]).run()
        assert result.corpus_id == "synthetic-tiny@0.1.0"

    def test_result_has_ingest_stats(self, tiny_corpus: Corpus) -> None:
        from wikibench.adapters.builtin.naive import NaiveAdapter
        result = Runner(adapter_spec=NaiveAdapter, corpus=tiny_corpus,
                        tasks=["knowledge_fidelity"]).run()
        assert result.ingest.wiki_tokens > 0
        assert result.ingest.llm_calls == 0  # NaiveAdapter ingest has no LLM calls

    def test_per_task_populated(self, tiny_corpus: Corpus) -> None:
        from wikibench.adapters.builtin.naive import NaiveAdapter
        result = Runner(
            adapter_spec=NaiveAdapter,
            corpus=tiny_corpus,
            tasks=["knowledge_fidelity", "contradiction_detection"],
        ).run()
        assert "knowledge_fidelity" in result.per_task
        assert "contradiction_detection" in result.per_task

    def test_metrics_are_flat_floats(self, tiny_corpus: Corpus) -> None:
        from wikibench.adapters.builtin.naive import NaiveAdapter
        result = Runner(
            adapter_spec=NaiveAdapter,
            corpus=tiny_corpus,
            tasks=["contradiction_detection"],
        ).run()
        for key, val in result.metrics.items():
            assert isinstance(key, str)
            assert isinstance(val, float), f"{key}={val!r} is not float"

    def test_environment_populated(self, tiny_corpus: Corpus) -> None:
        from wikibench.adapters.builtin.naive import NaiveAdapter
        result = Runner(adapter_spec=NaiveAdapter, corpus=tiny_corpus,
                        tasks=["knowledge_fidelity"]).run()
        env = result.environment
        assert env.wikibench_version
        assert env.python_version
        assert env.seed == 42

    def test_run_id_is_uuid(self, tiny_corpus: Corpus) -> None:
        from wikibench.adapters.builtin.naive import NaiveAdapter
        import uuid
        result = Runner(adapter_spec=NaiveAdapter, corpus=tiny_corpus,
                        tasks=["knowledge_fidelity"]).run()
        uuid.UUID(result.run_id)  # raises if invalid

    def test_unknown_task_skipped_gracefully(self, tiny_corpus: Corpus) -> None:
        from wikibench.adapters.builtin.naive import NaiveAdapter
        result = Runner(
            adapter_spec=NaiveAdapter,
            corpus=tiny_corpus,
            tasks=["knowledge_fidelity", "nonexistent_task_xyz"],
        ).run()
        assert "knowledge_fidelity" in result.per_task
        assert "nonexistent_task_xyz" not in result.per_task

    def test_hard_limit_aborts_run(self, tiny_corpus: Corpus) -> None:
        from wikibench.adapters.builtin.naive import NaiveAdapter
        from wikibench.runtime.cost import CostLimitExceededError
        with pytest.raises(CostLimitExceededError):
            Runner(
                adapter_spec=NaiveAdapter,
                corpus=tiny_corpus,
                tasks=["retrieval_accuracy"],  # uses LLM judge → incurs cost
                hard_limit_usd=0.000001,
            ).run()

    def test_all_three_tasks(self, tiny_corpus: Corpus) -> None:
        from wikibench.adapters.builtin.naive import NaiveAdapter
        result = Runner(
            adapter_spec=NaiveAdapter,
            corpus=tiny_corpus,
            tasks=["retrieval_accuracy", "knowledge_fidelity", "contradiction_detection"],
        ).run()
        assert len(result.per_task) == 3
        assert result.metrics  # at least some metrics populated
