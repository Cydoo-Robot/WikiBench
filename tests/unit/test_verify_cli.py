"""Tests for wikibench verify CLI and run_adapter_verify."""

from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from wikibench.cli.main import app
from wikibench.cli.verify import run_adapter_verify

REPO_ROOT = Path(__file__).resolve().parents[2]
TINY = REPO_ROOT / "corpora" / "synthetic" / "tiny"


@pytest.fixture
def cli_runner() -> CliRunner:
    return CliRunner(mix_stderr=False)


@pytest.mark.parametrize(
    "spec",
    [
        "wikibench.adapters.builtin.naive:NaiveAdapter",
        "wikibench.adapters.builtin.simple_summary:SimpleSummaryAdapter",
        "wikibench.adapters.builtin.reference_wiki:ReferenceWikiAdapter",
    ],
)
def test_run_adapter_verify_smoke(spec: str) -> None:
    run_adapter_verify(spec, TINY, mock_llm=True)


def test_verify_cli_module_class(cli_runner: CliRunner, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("WIKIBENCH_LLM_MOCK", "1")
    result = cli_runner.invoke(
        app,
        [
            "verify",
            "--adapter",
            "wikibench.adapters.builtin.naive:NaiveAdapter",
            "--corpus",
            str(TINY),
        ],
    )
    assert result.exit_code == 0, result.stdout + result.stderr
