"""SimpleSummaryAdapter — LLM-summarisation baseline.

During ``ingest``, each document is compressed to an LLM-generated summary.
During ``query``, the model sees only those summaries (not full raw text),
reducing context size versus :class:`~wikibench.adapters.builtin.naive.NaiveAdapter`.
"""

from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING, Any

from wikibench.adapters._base import WikiAdapter
from wikibench.adapters.builtin.naive import _build_messages, _parse_response
from wikibench.models.result import IngestResult, IngestStats
from wikibench.runtime.token_counter import count_tokens

if TYPE_CHECKING:
    from wikibench.models.document import Document
    from wikibench.models.query import Query, QueryResponse

log = logging.getLogger(__name__)

_SUMMARY_SYSTEM = """\
You summarize documents for a compiled knowledge base.
Output plain prose only (no JSON, no markdown code fences).
Preserve factual claims, names, numbers, and technical terms.
Be concise: for typical docs, a few short paragraphs suffice."""


class SimpleSummaryAdapter(WikiAdapter):
    """Baseline: per-document LLM summaries at ingest; queries use summary bundle."""

    name = "simple_summary"
    version = "0.1.0"

    def __init__(self, config: dict[str, Any]) -> None:
        self.model: str = config.get("model", "gemini/gemini-2.5-flash")
        self.max_tokens: int | None = config.get("max_tokens")
        self.temperature: float = float(config.get("temperature", 0.0))
        self.timeout_s: float = float(config.get("timeout_s", 120.0))
        self._summaries: dict[str, str] = {}
        self._context: str = ""
        self._wiki_tokens: int = 0

    def describe(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "llm_models": {"adapter_backend": self.model},
            "strategy": "per_doc_summary",
        }

    def ingest(self, docs: list[Document]) -> IngestResult:
        """One LLM call per document to produce a summary; then concatenate summaries."""
        from wikibench.runtime.llm import llm_call

        t0 = time.perf_counter()
        self._summaries.clear()

        llm_calls = 0
        sections: list[str] = []

        extra: dict[str, Any] = {}
        if "gemini-2.5" in self.model or "gemini-3" in self.model:
            extra["thinking"] = {"type": "disabled"}

        for doc in docs:
            user_msg = (
                f"Document path: {doc.path}\n"
                f"Modality: {doc.modality}\n\n---\n\n{doc.content}"
            )
            raw = llm_call(
                model=self.model,
                messages=[
                    {"role": "system", "content": _SUMMARY_SYSTEM},
                    {"role": "user", "content": user_msg},
                ],
                purpose="adapter.ingest",
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                timeout_s=self.timeout_s,
                **extra,
            )
            llm_calls += 1
            self._summaries[doc.path] = raw.strip()
            header = f"### [{doc.modality}] {doc.path} (summary)"
            sections.append(f"{header}\n\n{raw.strip()}")

        self._context = "\n\n---\n\n".join(sections) if sections else ""
        self._wiki_tokens = count_tokens(self._context, self.model) if self._context else 0
        duration = time.perf_counter() - t0

        log.info(
            "SimpleSummaryAdapter ingested %d docs, %d LLM calls, %d wiki tokens in %.3fs",
            len(docs),
            llm_calls,
            self._wiki_tokens,
            duration,
        )

        return IngestResult(
            wiki_id=f"simple_summary-{id(self):x}",
            stats=IngestStats(
                tokens_in=0,
                tokens_out=0,
                llm_calls=llm_calls,
                duration_s=duration,
                wiki_tokens=self._wiki_tokens,
            ),
        )

    def query(self, query: Query) -> QueryResponse:
        if not self._context:
            raise RuntimeError("SimpleSummaryAdapter.ingest() must be called before query().")

        from wikibench.runtime.llm import llm_call

        messages = _build_messages(query, self._context)
        extra_q: dict[str, Any] = {}
        if "gemini-2.5" in self.model or "gemini-3" in self.model:
            extra_q["thinking"] = {"type": "disabled"}

        raw = llm_call(
            model=self.model,
            messages=messages,
            purpose="adapter.query",
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            timeout_s=self.timeout_s,
            **extra_q,
        )
        return _parse_response(query, raw)

    def export_wiki(self) -> str:
        return self._context
