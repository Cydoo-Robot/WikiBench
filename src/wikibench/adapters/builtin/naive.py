"""NaiveAdapter — full-context baseline.

Concatenates every document into a single large prompt and sends it with
every query.  No compression, no summarisation.  This is the simplest
possible LLM Wiki strategy and serves as the lower-bound baseline.
"""

from __future__ import annotations

import time
from typing import Any

from wikibench.adapters._base import WikiAdapter
from wikibench.models.document import Document
from wikibench.models.query import Query, QueryResponse
from wikibench.models.result import IngestResult, IngestStats


class NaiveAdapter(WikiAdapter):
    """Baseline: send all documents as context on every query."""

    name = "naive"
    version = "0.1.0"

    def __init__(self, config: dict[str, Any]) -> None:
        self.model: str = config.get("model", "gpt-4o-mini")
        self._context: str = ""
        self._wiki_tokens: int = 0

    def describe(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "llm_models": {"adapter_backend": self.model},
        }

    def ingest(self, docs: list[Document]) -> IngestResult:
        t0 = time.perf_counter()
        self._context = "\n\n---\n\n".join(
            f"## {d.path}\n\n{d.content}" for d in docs
        )
        try:
            import tiktoken

            enc = tiktoken.encoding_for_model(self.model)
            self._wiki_tokens = len(enc.encode(self._context))
        except Exception:
            self._wiki_tokens = len(self._context) // 4  # rough fallback

        return IngestResult(
            wiki_id=f"naive-{id(self)}",
            stats=IngestStats(
                tokens_in=0,
                tokens_out=0,
                llm_calls=0,
                duration_s=time.perf_counter() - t0,
                wiki_tokens=self._wiki_tokens,
            ),
        )

    def query(self, query: Query) -> QueryResponse:
        from wikibench.runtime.llm import llm_call

        prompt = _build_prompt(query, self._context)
        reply = llm_call(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            purpose="adapter.query",
        )
        return _parse_response(query, reply)

    def export_wiki(self) -> str:
        return self._context


def _build_prompt(query: Query, context: str) -> str:
    if query.intent == "fidelity_check":
        claim = query.params.get("claim", "")
        return (
            f"Given the following knowledge base:\n\n{context}\n\n"
            f"Evaluate this claim: {claim}\n"
            "Reply with JSON: {\"verdict\": \"supported|not_supported|unknown\", "
            "\"explanation\": \"...\"}"
        )
    if query.intent == "contradiction_check":
        return (
            f"Given the following knowledge base:\n\n{context}\n\n"
            "Identify any contradictions between documents.\n"
            "Reply with JSON: {\"has_contradiction\": bool, \"pairs\": ["
            "{\"doc_a\": \"...\", \"doc_b\": \"...\", \"description\": \"...\"}]}"
        )
    return (
        f"Given the following knowledge base:\n\n{context}\n\n"
        f"Answer this question: {query.text}"
    )


def _parse_response(query: Query, raw: str) -> QueryResponse:
    import json

    structured: dict[str, Any] = {}
    if query.intent in ("fidelity_check", "contradiction_check"):
        try:
            structured = json.loads(raw)
        except json.JSONDecodeError:
            pass
    return QueryResponse(answer=raw, structured=structured, raw={"raw_text": raw})
