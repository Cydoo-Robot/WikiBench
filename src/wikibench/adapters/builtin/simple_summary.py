"""SimpleSummaryAdapter — LLM-summarisation baseline (Phase 1 Week 5)."""

from __future__ import annotations

from typing import Any

from wikibench.adapters._base import WikiAdapter
from wikibench.models.document import Document
from wikibench.models.query import Query, QueryResponse
from wikibench.models.result import IngestResult, IngestStats


class SimpleSummaryAdapter(WikiAdapter):
    """Baseline: compress each document to an LLM-generated summary during ingest."""

    name = "simple_summary"
    version = "0.1.0"

    def __init__(self, config: dict[str, Any]) -> None:
        self.model: str = config.get("model", "gpt-4o-mini")
        self._summaries: dict[str, str] = {}

    def describe(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "llm_models": {"adapter_backend": self.model},
        }

    def ingest(self, docs: list[Document]) -> IngestResult:
        raise NotImplementedError("SimpleSummaryAdapter.ingest — coming in Phase 1 Week 5.")

    def query(self, query: Query) -> QueryResponse:
        raise NotImplementedError("SimpleSummaryAdapter.query — coming in Phase 1 Week 5.")
