"""Unit / smoke tests for NaiveAdapter.

All LLM calls are intercepted by mock mode (WIKIBENCH_LLM_MOCK=1).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from wikibench.adapters.builtin.naive import NaiveAdapter, _build_messages, _extract_json
from wikibench.models.document import Document
from wikibench.models.query import Query
from wikibench.runtime.cache import ResponseCache, reset_default_cache


@pytest.fixture(autouse=True)
def _setup(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("WIKIBENCH_LLM_MOCK", "1")
    reset_default_cache()
    from wikibench.runtime import cache as _c

    _c._default_cache = ResponseCache(cache_dir=tmp_path / "naive-cache")
    yield  # type: ignore[misc]
    reset_default_cache()


@pytest.fixture()
def adapter() -> NaiveAdapter:
    return NaiveAdapter({"model": "gpt-4o-mini"})


@pytest.fixture()
def docs() -> list[Document]:
    return [
        Document(id="d1", path="arch/overview.md", content="# Overview\n\nWe use gRPC."),
        Document(id="d2", path="decisions/db.md", content="# DB Choice\n\nWe chose PostgreSQL."),
    ]


# ── ingest ────────────────────────────────────────────────────────────────────


class TestIngest:
    def test_returns_ingest_result(self, adapter: NaiveAdapter, docs: list[Document]) -> None:
        result = adapter.ingest(docs)
        assert result.wiki_id.startswith("naive-")
        assert result.stats.llm_calls == 0

    def test_wiki_tokens_positive(self, adapter: NaiveAdapter, docs: list[Document]) -> None:
        result = adapter.ingest(docs)
        assert result.stats.wiki_tokens > 0

    def test_context_contains_all_docs(self, adapter: NaiveAdapter, docs: list[Document]) -> None:
        adapter.ingest(docs)
        assert "arch/overview.md" in adapter._context
        assert "decisions/db.md" in adapter._context

    def test_ingest_zero_docs(self, adapter: NaiveAdapter) -> None:
        result = adapter.ingest([])
        assert result.stats.wiki_tokens == 0

    def test_export_wiki_after_ingest(self, adapter: NaiveAdapter, docs: list[Document]) -> None:
        adapter.ingest(docs)
        wiki = adapter.export_wiki()
        assert isinstance(wiki, str)
        assert len(wiki) > 0


# ── query ─────────────────────────────────────────────────────────────────────


class TestQuery:
    def test_qa_query(self, adapter: NaiveAdapter, docs: list[Document]) -> None:
        adapter.ingest(docs)
        q = Query(id="q1", text="What database do we use?", intent="qa")
        resp = adapter.query(q)
        assert resp.answer

    def test_fidelity_check_query(self, adapter: NaiveAdapter, docs: list[Document]) -> None:
        adapter.ingest(docs)
        q = Query(
            id="q2",
            text="Is this claim correct?",
            intent="fidelity_check",
            params={"claim": "We use PostgreSQL."},
        )
        resp = adapter.query(q)
        assert resp.answer

    def test_query_without_ingest_raises(self, adapter: NaiveAdapter) -> None:
        q = Query(id="q3", text="Anything", intent="qa")
        with pytest.raises(RuntimeError, match="ingest"):
            adapter.query(q)

    def test_describe(self, adapter: NaiveAdapter) -> None:
        desc = adapter.describe()
        assert desc["name"] == "naive"
        assert "adapter_backend" in desc["llm_models"]


# ── _build_messages ───────────────────────────────────────────────────────────


class TestBuildMessages:
    def test_qa_has_system_and_user(self) -> None:
        q = Query(id="q", text="What is X?", intent="qa")
        msgs = _build_messages(q, "context text")
        roles = [m["role"] for m in msgs]
        assert roles == ["system", "user"]

    def test_system_contains_context(self) -> None:
        q = Query(id="q", text="?", intent="qa")
        msgs = _build_messages(q, "MY_CONTEXT_MARKER")
        assert "MY_CONTEXT_MARKER" in msgs[0]["content"]

    def test_fidelity_user_contains_claim(self) -> None:
        q = Query(id="q", text="x", intent="fidelity_check", params={"claim": "WE_USE_GRPC"})
        msgs = _build_messages(q, "ctx")
        assert "WE_USE_GRPC" in msgs[1]["content"]


# ── _extract_json ─────────────────────────────────────────────────────────────


class TestExtractJson:
    def test_plain_json(self) -> None:
        result = _extract_json('{"verdict": "supported"}')
        assert result == {"verdict": "supported"}

    def test_json_with_markdown_fence(self) -> None:
        text = '```json\n{"verdict": "not_supported"}\n```'
        result = _extract_json(text)
        assert result["verdict"] == "not_supported"

    def test_json_embedded_in_text(self) -> None:
        text = 'Here is the answer: {"has_contradiction": false, "pairs": []} - done.'
        result = _extract_json(text)
        assert result["has_contradiction"] is False

    def test_invalid_returns_empty(self) -> None:
        result = _extract_json("This is plain text, no JSON here.")
        assert result == {}

    def test_nested_json(self) -> None:
        payload = {"a": {"b": [1, 2, 3]}}
        result = _extract_json(json.dumps(payload))
        assert result == payload
