"""Unit tests for reporters (console / json / markdown) and ResultStore."""

from __future__ import annotations

import json
from io import StringIO
from pathlib import Path

import pytest
from rich.console import Console

from wikibench.models.result import (
    BenchmarkResult,
    IngestStats,
    RunEnvironment,
    Score,
    TaskResult,
)


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture()
def minimal_result() -> BenchmarkResult:
    """A BenchmarkResult with minimal populated fields."""
    env = RunEnvironment(
        python_version="3.12.0",
        os="Windows",
        wikibench_version="0.1.0-alpha",
        impl_version="0.1.0",
        llm_models={"adapter_backend": "mock", "judge": "mock"},
        seed=42,
    )
    ingest = IngestStats(
        tokens_in=500,
        tokens_out=0,
        llm_calls=0,
        duration_s=0.1,
        wiki_tokens=450,
        cost_usd=0.0,
    )
    scores = [
        Score(metric="knowledge_fidelity", value=1.0, details={"correct": True}),
        Score(metric="knowledge_fidelity", value=0.0, details={"correct": False}),
    ]
    task_result = TaskResult(
        task_id="knowledge_fidelity",
        task_version="1.0.0",
        scores=scores,
        slices={"mean": 0.5, "hallucination_rate": 0.0, "precision": 1.0, "recall": 0.5},
    )
    return BenchmarkResult(
        impl="naive@0.1.0",
        corpus_id="synthetic-tiny@0.1.0",
        environment=env,
        ingest=ingest,
        per_task={"knowledge_fidelity": task_result},
        metrics={"knowledge_fidelity.mean": 0.5, "knowledge_fidelity.precision": 1.0},
        composite={"wikibench_v1": 0.5},
        warnings=["Test warning"],
    )


# ── JSON reporter ─────────────────────────────────────────────────────────────

class TestJsonReporter:
    def test_render_is_valid_json(self, minimal_result: BenchmarkResult) -> None:
        from wikibench.reporters.json import render
        text = render(minimal_result)
        data = json.loads(text)
        assert data["run_id"] == minimal_result.run_id
        assert data["impl"] == "naive@0.1.0"

    def test_render_contains_metrics(self, minimal_result: BenchmarkResult) -> None:
        from wikibench.reporters.json import render
        text = render(minimal_result)
        data = json.loads(text)
        assert "knowledge_fidelity.mean" in data["metrics"]

    def test_save_creates_file(self, minimal_result: BenchmarkResult, tmp_path: Path) -> None:
        from wikibench.reporters.json import save, load
        saved = save(minimal_result, tmp_path)
        assert saved.exists()
        assert saved.suffix == ".json"

    def test_save_to_dir_uses_run_id(self, minimal_result: BenchmarkResult, tmp_path: Path) -> None:
        from wikibench.reporters.json import save
        saved = save(minimal_result, tmp_path)
        assert minimal_result.run_id in saved.name

    def test_load_roundtrip(self, minimal_result: BenchmarkResult, tmp_path: Path) -> None:
        from wikibench.reporters.json import save, load
        path = save(minimal_result, tmp_path)
        loaded = load(path)
        assert loaded.run_id == minimal_result.run_id
        assert loaded.impl == minimal_result.impl
        assert abs(loaded.metrics["knowledge_fidelity.mean"] - 0.5) < 1e-9

    def test_load_missing_file_raises(self, tmp_path: Path) -> None:
        from wikibench.reporters.json import load
        with pytest.raises(FileNotFoundError):
            load(tmp_path / "nonexistent.json")


# ── Markdown reporter ─────────────────────────────────────────────────────────

class TestMarkdownReporter:
    def test_render_is_string(self, minimal_result: BenchmarkResult) -> None:
        from wikibench.reporters.markdown import render
        text = render(minimal_result)
        assert isinstance(text, str)
        assert len(text) > 50

    def test_render_contains_run_id(self, minimal_result: BenchmarkResult) -> None:
        from wikibench.reporters.markdown import render
        text = render(minimal_result)
        assert minimal_result.run_id in text

    def test_render_contains_task_section(self, minimal_result: BenchmarkResult) -> None:
        from wikibench.reporters.markdown import render
        text = render(minimal_result)
        assert "knowledge_fidelity" in text

    def test_render_contains_metrics(self, minimal_result: BenchmarkResult) -> None:
        from wikibench.reporters.markdown import render
        text = render(minimal_result)
        assert "0.5000" in text  # mean slice

    def test_save_creates_md_file(self, minimal_result: BenchmarkResult, tmp_path: Path) -> None:
        from wikibench.reporters.markdown import save
        path = save(minimal_result, tmp_path)
        assert path.exists()
        assert path.suffix == ".md"

    def test_render_includes_warnings(self, minimal_result: BenchmarkResult) -> None:
        from wikibench.reporters.markdown import render
        text = render(minimal_result)
        assert "Test warning" in text


# ── Console reporter ──────────────────────────────────────────────────────────

class TestConsoleReporter:
    def _capture(self, result: BenchmarkResult) -> str:
        from wikibench.reporters.console import render
        buf = StringIO()
        con = Console(file=buf, no_color=True, width=100)
        render(result, console=con)
        return buf.getvalue()

    def test_render_includes_run_id(self, minimal_result: BenchmarkResult) -> None:
        text = self._capture(minimal_result)
        assert minimal_result.run_id in text

    def test_render_includes_impl(self, minimal_result: BenchmarkResult) -> None:
        text = self._capture(minimal_result)
        assert "naive@0.1.0" in text

    def test_render_includes_task_scores(self, minimal_result: BenchmarkResult) -> None:
        text = self._capture(minimal_result)
        assert "knowledge_fidelity" in text
        assert "0.500" in text

    def test_render_includes_warnings(self, minimal_result: BenchmarkResult) -> None:
        text = self._capture(minimal_result)
        assert "Test warning" in text

    def test_render_no_crash_on_empty_tasks(self, minimal_result: BenchmarkResult) -> None:
        from wikibench.reporters.console import render
        minimal_result.per_task = {}
        minimal_result.metrics = {}
        buf = StringIO()
        con = Console(file=buf, no_color=True, width=100)
        render(minimal_result, console=con)
        assert len(buf.getvalue()) > 0


# ── ResultStore ───────────────────────────────────────────────────────────────

class TestResultStore:
    def test_save_creates_directory(self, minimal_result: BenchmarkResult, tmp_path: Path) -> None:
        from wikibench.storage.result_store import ResultStore
        store = ResultStore(root=tmp_path)
        run_dir = store.save(minimal_result)
        assert run_dir.is_dir()
        assert (run_dir / "result.json").exists()

    def test_save_creates_markdown(self, minimal_result: BenchmarkResult, tmp_path: Path) -> None:
        from wikibench.storage.result_store import ResultStore
        store = ResultStore(root=tmp_path, write_markdown=True)
        run_dir = store.save(minimal_result)
        assert (run_dir / "report.md").exists()

    def test_load_by_run_id(self, minimal_result: BenchmarkResult, tmp_path: Path) -> None:
        from wikibench.storage.result_store import ResultStore
        store = ResultStore(root=tmp_path)
        store.save(minimal_result)
        loaded = store.load(minimal_result.run_id)
        assert loaded.run_id == minimal_result.run_id

    def test_list_runs(self, minimal_result: BenchmarkResult, tmp_path: Path) -> None:
        from wikibench.storage.result_store import ResultStore
        store = ResultStore(root=tmp_path)
        store.save(minimal_result)
        runs = store.list_runs()
        assert minimal_result.run_id in runs

    def test_list_runs_empty_on_missing_root(self, tmp_path: Path) -> None:
        from wikibench.storage.result_store import ResultStore
        store = ResultStore(root=tmp_path / "nonexistent")
        assert store.list_runs() == []

    def test_exists(self, minimal_result: BenchmarkResult, tmp_path: Path) -> None:
        from wikibench.storage.result_store import ResultStore
        store = ResultStore(root=tmp_path)
        assert not store.exists(minimal_result.run_id)
        store.save(minimal_result)
        assert store.exists(minimal_result.run_id)

    def test_load_missing_run_raises(self, tmp_path: Path) -> None:
        from wikibench.storage.result_store import ResultStore
        store = ResultStore(root=tmp_path)
        with pytest.raises(FileNotFoundError):
            store.load("nonexistent-run-id")

    def test_load_from_path_file(self, minimal_result: BenchmarkResult, tmp_path: Path) -> None:
        from wikibench.storage.result_store import ResultStore
        store = ResultStore(root=tmp_path)
        run_dir = store.save(minimal_result)
        loaded = store.load_from_path(run_dir / "result.json")
        assert loaded.run_id == minimal_result.run_id

    def test_load_from_path_dir(self, minimal_result: BenchmarkResult, tmp_path: Path) -> None:
        from wikibench.storage.result_store import ResultStore
        store = ResultStore(root=tmp_path)
        run_dir = store.save(minimal_result)
        loaded = store.load_from_path(run_dir)
        assert loaded.run_id == minimal_result.run_id


# ── reporters.__init__.render dispatch ───────────────────────────────────────

class TestReportersDispatch:
    def test_json_dispatch_returns_string(self, minimal_result: BenchmarkResult) -> None:
        from wikibench.reporters import render
        text = render(minimal_result, format="json")
        assert text is not None
        json.loads(text)

    def test_markdown_dispatch_returns_string(self, minimal_result: BenchmarkResult) -> None:
        from wikibench.reporters import render
        text = render(minimal_result, format="markdown")
        assert text is not None
        assert "WikiBench" in text

    def test_unknown_format_raises(self, minimal_result: BenchmarkResult) -> None:
        from wikibench.reporters import render
        with pytest.raises(ValueError, match="Unknown format"):
            render(minimal_result, format="pdf")
