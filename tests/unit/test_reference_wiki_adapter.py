"""Tests for ReferenceWikiAdapter (LLM mocked)."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pathlib import Path

from wikibench.adapters.builtin.reference_wiki import ReferenceWikiAdapter
from wikibench.models.document import Document
from wikibench.models.query import Query
from wikibench.runtime.cache import ResponseCache, reset_default_cache


@pytest.fixture(autouse=True)
def _setup(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("WIKIBENCH_LLM_MOCK", "1")
    reset_default_cache()
    from wikibench.runtime import cache as _c

    _c._default_cache = ResponseCache(cache_dir=tmp_path / "ref-cache")
    yield  # type: ignore[misc]
    reset_default_cache()


@pytest.fixture()
def adapter() -> ReferenceWikiAdapter:
    return ReferenceWikiAdapter({"model": "gpt-4o-mini"})


@pytest.fixture()
def docs() -> list[Document]:
    return [
        Document(id="d1", path="a.md", content="# A\n\nAlpha fact."),
        Document(id="d2", path="b.md", content="# B\n\nBeta fact."),
    ]


class TestIngest:
    def test_llm_calls_docs_plus_index(
        self, adapter: ReferenceWikiAdapter, docs: list[Document]
    ) -> None:
        result = adapter.ingest(docs)
        assert result.stats.llm_calls == len(docs) + 1
        assert result.stats.wiki_tokens > 0

    def test_context_has_index_and_summaries(
        self, adapter: ReferenceWikiAdapter, docs: list[Document]
    ) -> None:
        adapter.ingest(docs)
        w = adapter.export_wiki()
        assert "Wiki index" in w or "Summaries" in w
        assert "a.md" in w and "b.md" in w

    def test_empty_docs(self, adapter: ReferenceWikiAdapter) -> None:
        result = adapter.ingest([])
        assert result.stats.llm_calls == 0
        assert result.stats.wiki_tokens == 0


class TestQuery:
    def test_qa(self, adapter: ReferenceWikiAdapter, docs: list[Document]) -> None:
        adapter.ingest(docs)
        resp = adapter.query(Query(id="q1", text="What is Alpha?", intent="qa"))
        assert resp.answer
