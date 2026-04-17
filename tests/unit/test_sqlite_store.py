"""Tests for BenchmarkSqliteStore."""

from __future__ import annotations

from pathlib import Path

import pytest

from wikibench.models.result import (
    BenchmarkResult,
    IngestStats,
    RunEnvironment,
    Score,
    TaskResult,
)
from wikibench.storage.sqlite import BenchmarkSqliteStore


def _minimal_result() -> BenchmarkResult:
    env = RunEnvironment(
        python_version="3.12.0",
        os="Windows",
        wikibench_version="0.1.0-alpha",
        impl_version="0.1.0",
        llm_models={"adapter_backend": "mock"},
        seed=42,
    )
    ingest = IngestStats(
        tokens_in=100,
        tokens_out=0,
        llm_calls=0,
        duration_s=0.1,
        wiki_tokens=50,
        cost_usd=0.0,
    )
    tr = TaskResult(
        task_id="knowledge_fidelity",
        task_version="1.0.0",
        scores=[Score(metric="knowledge_fidelity", value=1.0, details={})],
        slices={"mean": 0.5},
    )
    return BenchmarkResult(
        impl="naive@0.1.0",
        corpus_id="synthetic-tiny@0.1.0",
        environment=env,
        ingest=ingest,
        per_task={"knowledge_fidelity": tr},
        metrics={"knowledge_fidelity.mean": 0.5},
        warnings=[],
    )


def test_save_load_roundtrip(tmp_path: Path) -> None:
    minimal_result = _minimal_result()
    db = tmp_path / "runs.db"
    store = BenchmarkSqliteStore(db)
    store.save(minimal_result)
    loaded = store.load(minimal_result.run_id)
    assert loaded.run_id == minimal_result.run_id
    assert loaded.impl == minimal_result.impl
    assert loaded.metrics == minimal_result.metrics


def test_list_run_ids_order(tmp_path: Path) -> None:
    minimal_result = _minimal_result()
    db = tmp_path / "runs.db"
    store = BenchmarkSqliteStore(db)
    store.save(minimal_result)
    ids = store.list_run_ids()
    assert ids == [minimal_result.run_id]


def test_load_missing_raises(tmp_path: Path) -> None:
    db = tmp_path / "empty.db"
    store = BenchmarkSqliteStore(db)
    with pytest.raises(FileNotFoundError):
        store.load("nope")
