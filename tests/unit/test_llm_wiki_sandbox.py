"""Unit tests for :mod:`wikibench.adapters.community.llm_wiki_sandbox`."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest  # noqa: TC002

from wikibench.adapters.community import llm_wiki_sandbox as sandbox_mod
from wikibench.adapters.community.llm_wiki_sandbox import resolve_llmwiki_invocation


def test_resolve_prefers_node_modules_bin(tmp_path: Path) -> None:
    bin_dir = tmp_path / "node_modules" / ".bin"
    bin_dir.mkdir(parents=True)
    name = "llmwiki.cmd" if sys.platform == "win32" else "llmwiki"
    fake = bin_dir / name
    fake.write_text("", encoding="utf-8")
    got = resolve_llmwiki_invocation(tmp_path)
    assert got == [str(fake.resolve())]


def test_resolve_node_dist_fallback(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "cli.js").write_text("// cli", encoding="utf-8")
    monkeypatch.setattr(
        sandbox_mod, "shutil_which", lambda cmd: "/fake/node" if cmd == "node" else None
    )
    got = resolve_llmwiki_invocation(tmp_path)
    assert got == ["/fake/node", str((dist / "cli.js").resolve())]


def test_resolve_missing_returns_none(tmp_path: Path) -> None:
    assert resolve_llmwiki_invocation(tmp_path) is None
