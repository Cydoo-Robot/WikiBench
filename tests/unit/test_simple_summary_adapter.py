"""Tests for SimpleSummaryAdapter (LLM calls mocked)."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pathlib import Path

from wikibench.adapters.builtin.simple_summary import SimpleSummaryAdapter
from wikibench.models.document import Document
from wikibench.models.query import Query
from wikibench.runtime.cache import ResponseCache, reset_default_cache


@pytest.fixture(autouse=True)
def _setup(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("WIKIBENCH_LLM_MOCK", "1")
    reset_default_cache()
    from wikibench.runtime import cache as _c

    _c._default_cache = ResponseCache(cache_dir=tmp_path / "ss-cache")
    yield  # type: ignore[misc]
    reset_default_cache()


@pytest.fixture()
def adapter() -> SimpleSummaryAdapter:
    return SimpleSummaryAdapter({"model": "gpt-4o-mini"})


@pytest.fixture()
def docs() -> list[Document]:
    return [
        Document(id="d1", path="arch/overview.md", content="# Overview\n\nWe use gRPC."),
        Document(id="d2", path="decisions/db.md", content="# DB Choice\n\nWe chose PostgreSQL."),
    ]


class TestIngest:
    def test_llm_calls_per_doc(self, adapter: SimpleSummaryAdapter, docs: list[Document]) -> None:
        result = adapter.ingest(docs)
        assert result.stats.llm_calls == len(docs)
        assert result.stats.wiki_tokens > 0

    def test_export_wiki_contains_paths(
        self, adapter: SimpleSummaryAdapter, docs: list[Document]
    ) -> None:
        adapter.ingest(docs)
        wiki = adapter.export_wiki()
        assert "arch/overview.md" in wiki
        assert "decisions/db.md" in wiki

    def test_empty_docs(self, adapter: SimpleSummaryAdapter) -> None:
        result = adapter.ingest([])
        assert result.stats.llm_calls == 0
        assert result.stats.wiki_tokens == 0


class TestQuery:
    def test_qa_after_ingest(self, adapter: SimpleSummaryAdapter, docs: list[Document]) -> None:
        adapter.ingest(docs)
        q = Query(id="q1", text="What database do we use?", intent="qa")
        resp = adapter.query(q)
        assert resp.answer
