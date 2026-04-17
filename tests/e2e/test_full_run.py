"""End-to-end test: full CLI pipeline on synthetic-tiny corpus.

``WIKIBENCH_LLM_MOCK=1`` (see :mod:`wikibench.runtime.llm`) stub all LLM calls so
this test needs no credentials and hits no network. It still exercises
``wikibench run`` → :class:`~wikibench.storage.result_store.ResultStore` +
:class:`~wikibench.storage.sqlite.BenchmarkSqliteStore`, and ``wikibench report``.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pathlib import Path
from typer.testing import CliRunner

from wikibench.cli.main import app


@pytest.fixture
def cli_runner() -> CliRunner:
    return CliRunner()


@pytest.mark.e2e
def test_wikibench_run_full_pipeline_mock_llm(
    tiny_corpus_path: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    cli_runner: CliRunner,
) -> None:
    """``wikibench run`` writes artifacts + SQLite; ``report list/show`` work."""
    monkeypatch.setenv("WIKIBENCH_LLM_MOCK", "1")

    store_root = tmp_path / "results"
    db_path = tmp_path / "bench.db"
    cache_dir = tmp_path / "cache"

    invoke = cli_runner.invoke(
        app,
        [
            "run",
            "--impl",
            "naive",
            "--corpus",
            str(tiny_corpus_path),
            "--output",
            str(store_root),
            "--sqlite",
            str(db_path),
            "--cache-dir",
            str(cache_dir),
            "--quiet",
            "--format",
            "json",
        ],
    )
    assert invoke.exit_code == 0, f"stdout={invoke.stdout!r} stderr={invoke.stderr!r}"

    run_dirs = [p for p in store_root.iterdir() if p.is_dir()]
    assert len(run_dirs) == 1
    run_dir = run_dirs[0]
    run_id = run_dir.name

    for name in ("result.json", "report.md", "report.html"):
        assert (run_dir / name).is_file(), f"missing {name}"

    payload = json.loads((run_dir / "result.json").read_text(encoding="utf-8"))
    assert payload["corpus_id"] == "synthetic-tiny@0.1.0"
    assert payload["impl"] == "naive@0.1.0"
    for task_id in ("retrieval_accuracy", "knowledge_fidelity", "contradiction_detection"):
        assert task_id in payload["per_task"]

    from wikibench.storage.sqlite import BenchmarkSqliteStore

    assert BenchmarkSqliteStore(db_path).list_run_ids() == [run_id]

    show_dir = cli_runner.invoke(
        app,
        ["report", "show", str(run_dir), "--format", "json"],
    )
    assert show_dir.exit_code == 0, f"{show_dir.stdout!r} {show_dir.stderr!r}"

    show_db = cli_runner.invoke(
        app,
        ["report", "show", str(db_path), "--run-id", run_id, "--format", "markdown"],
    )
    assert show_db.exit_code == 0, f"{show_db.stdout!r} {show_db.stderr!r}"

    listed = cli_runner.invoke(app, ["report", "list", str(store_root)])
    assert listed.exit_code == 0
    assert run_id in listed.stdout
