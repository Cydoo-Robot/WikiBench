"""ReferenceWikiAdapter — hierarchical reference wiki (summaries + global index).

Ingest pipeline
---------------
1. One LLM call per document → short summary (same goal as :class:`SimpleSummaryAdapter`).
2. One LLM call over all summaries → a Markdown **index** (topic → document paths).
3. Compiled wiki text = index + per-document summary sections.

Queries use the same message shape as :class:`~wikibench.adapters.builtin.naive.NaiveAdapter`
via shared helpers :func:`~wikibench.adapters.builtin.naive._build_messages` /
:func:`~wikibench.adapters.builtin.naive._parse_response`.
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

_INDEX_SYSTEM = """\
You maintain a navigable index for a small internal wiki.
Output Markdown only (headings, bullet lists). No JSON, no code fences.
Map themes and facts to document paths so a reader knows where to look."""


class ReferenceWikiAdapter(WikiAdapter):
    """Reference: per-doc summaries plus one global index pass (Karpathy-style sketch)."""

    name = "reference_wiki"
    version = "0.1.0"

    def __init__(self, config: dict[str, Any]) -> None:
        self.model: str = config.get("model", "gemini/gemini-2.5-flash")
        self.max_tokens: int | None = config.get("max_tokens")
        self.temperature: float = float(config.get("temperature", 0.0))
        self.timeout_s: float = float(config.get("timeout_s", 120.0))
        self._summaries: dict[str, str] = {}
        self._index_md: str = ""
        self._context: str = ""
        self._wiki_tokens: int = 0

    def describe(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "llm_models": {"adapter_backend": self.model},
            "strategy": "summaries_plus_index",
        }

    def _gemini_extra(self) -> dict[str, Any]:
        extra: dict[str, Any] = {}
        if "gemini-2.5" in self.model or "gemini-3" in self.model:
            extra["thinking"] = {"type": "disabled"}
        return extra

    def ingest(self, docs: list[Document]) -> IngestResult:
        from wikibench.runtime.llm import llm_call

        t0 = time.perf_counter()
        self._summaries.clear()
        self._index_md = ""
        llm_calls = 0
        sections: list[str] = []
        extra = self._gemini_extra()

        for doc in docs:
            user_msg = (
                f"Document path: {doc.path}\nModality: {doc.modality}\n\n---\n\n{doc.content}"
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

        if self._summaries:
            index_user_parts = [
                f"## {path}\n{txt}\n" for path, txt in sorted(self._summaries.items())
            ]
            index_user = (
                "Here are per-document summaries. Build a compact wiki INDEX "
                "(topics, decisions, entities) and reference document paths.\n\n"
                + "\n".join(index_user_parts)
            )
            self._index_md = llm_call(
                model=self.model,
                messages=[
                    {"role": "system", "content": _INDEX_SYSTEM},
                    {"role": "user", "content": index_user},
                ],
                purpose="adapter.ingest",
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                timeout_s=self.timeout_s,
                **extra,
            ).strip()
            llm_calls += 1

        body = "\n\n---\n\n".join(sections) if sections else ""
        if self._index_md and body:
            self._context = f"## Wiki index\n\n{self._index_md}\n\n---\n\n## Summaries\n\n{body}"
        elif body:
            self._context = f"## Summaries\n\n{body}"
        else:
            self._context = ""

        self._wiki_tokens = count_tokens(self._context, self.model) if self._context else 0
        duration = time.perf_counter() - t0

        log.info(
            "ReferenceWikiAdapter ingested %d docs, %d LLM calls, %d wiki tokens in %.3fs",
            len(docs),
            llm_calls,
            self._wiki_tokens,
            duration,
        )

        return IngestResult(
            wiki_id=f"reference_wiki-{id(self):x}",
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
            raise RuntimeError("ReferenceWikiAdapter.ingest() must be called before query().")

        from wikibench.runtime.llm import llm_call

        messages = _build_messages(query, self._context)
        extra_q: dict[str, Any] = self._gemini_extra()

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
