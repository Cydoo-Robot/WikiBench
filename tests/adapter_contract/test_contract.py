"""Adapter contract tests — built-in adapters must pass :func:`run_adapter_verify`."""

from __future__ import annotations

from pathlib import Path

import pytest

from wikibench.cli.verify import run_adapter_verify

REPO_ROOT = Path(__file__).resolve().parents[2]
TINY = REPO_ROOT / "corpora" / "synthetic" / "tiny"


@pytest.mark.parametrize(
    "adapter_spec",
    [
        "wikibench.adapters.builtin.naive:NaiveAdapter",
        "wikibench.adapters.builtin.simple_summary:SimpleSummaryAdapter",
        "wikibench.adapters.builtin.reference_wiki:ReferenceWikiAdapter",
    ],
)
def test_builtin_adapter_contract(adapter_spec: str) -> None:
    run_adapter_verify(adapter_spec, TINY, mock_llm=True)
