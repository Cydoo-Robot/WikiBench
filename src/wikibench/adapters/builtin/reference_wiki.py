"""ReferenceWikiAdapter — Karpathy-style reference implementation (Phase 1 Week 5)."""

from __future__ import annotations

from typing import Any

from wikibench.adapters._base import WikiAdapter
from wikibench.models.document import Document
from wikibench.models.query import Query, QueryResponse
from wikibench.models.result import IngestResult


class ReferenceWikiAdapter(WikiAdapter):
    """Reference: hierarchical LLM wiki with per-document summaries + index."""

    name = "reference_wiki"
    version = "0.1.0"

    def __init__(self, config: dict[str, Any]) -> None:
        self.model: str = config.get("model", "gpt-4o-mini")

    def describe(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "llm_models": {"adapter_backend": self.model},
        }

    def ingest(self, docs: list[Document]) -> IngestResult:
        raise NotImplementedError("ReferenceWikiAdapter.ingest — coming in Phase 1 Week 5.")

    def query(self, query: Query) -> QueryResponse:
        raise NotImplementedError("ReferenceWikiAdapter.query — coming in Phase 1 Week 5.")
