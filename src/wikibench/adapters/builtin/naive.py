"""NaiveAdapter — full-context baseline.

Strategy
--------
Concatenate every document into a single Markdown blob during ``ingest``
(O(1) LLM calls, cost ≈ 0).  On each ``query``, prepend the blob as a
system prompt and let the LLM answer directly.

This is the *simplest possible* LLM Wiki strategy and serves as the
lower-bound quality baseline.  No compression, no indexing, no summarisation.

Supported intents
-----------------
* ``qa``                → free-text answer
* ``fidelity_check``    → ``{"verdict": "supported|not_supported|unknown"}``
* ``contradiction_check`` → ``{"has_contradiction": bool, "pairs": [...]}``
* ``grounding``         → ``{"sources": [...]}``  (best-effort)
"""

from __future__ import annotations

import json
import logging
import time
from typing import Any

from wikibench.adapters._base import WikiAdapter
from wikibench.models.document import Document
from wikibench.models.query import Query, QueryResponse
from wikibench.models.result import IngestResult, IngestStats
from wikibench.runtime.token_counter import count_tokens

log = logging.getLogger(__name__)

# System prompt shown to the model on every query
_SYSTEM_PROMPT = """\
You are a knowledge-base assistant.
Answer questions using ONLY the information in the knowledge base below.
If the answer cannot be found in the knowledge base, say so explicitly.
Do not invent facts.
"""

# Intent-specific instruction appended before the user question
_INTENT_INSTRUCTIONS: dict[str, str] = {
    "fidelity_check": (
        "Evaluate the following claim against the knowledge base.\n"
        "Reply with ONLY valid JSON (no markdown fences):\n"
        '{"verdict": "supported|not_supported|unknown", "explanation": "<one sentence>"}'
    ),
    "contradiction_check": (
        "Identify any factual contradictions BETWEEN documents in the knowledge base.\n"
        "Reply with ONLY valid JSON (no markdown fences):\n"
        '{"has_contradiction": true|false, "pairs": [{"doc_a": "<path>", "doc_b": "<path>", "description": "<brief>"}]}'
    ),
    "grounding": (
        "Answer the question and cite the specific document paths that support your answer.\n"
        "Reply with ONLY valid JSON (no markdown fences):\n"
        '{"answer": "<your answer>", "sources": ["<doc-path>", ...]}'
    ),
}


class NaiveAdapter(WikiAdapter):
    """Baseline: full document context on every query."""

    name = "naive"
    version = "0.1.0"

    def __init__(self, config: dict[str, Any]) -> None:
        self.model: str = config.get("model", "gemini/gemini-2.5-flash")
        self.max_tokens: int | None = config.get("max_tokens", None)
        self.temperature: float = float(config.get("temperature", 0.0))
        self.timeout_s: float = float(config.get("timeout_s", 120.0))

        self._context: str = ""
        self._wiki_tokens: int = 0
        self._ingest_doc_count: int = 0

    def describe(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "llm_models": {"adapter_backend": self.model},
            "strategy": "full_context",
        }

    # ── ingest ────────────────────────────────────────────────────────────────

    def ingest(self, docs: list[Document]) -> IngestResult:
        """Concatenate all documents into a single context string.

        No LLM calls are made during ingest; the cost is purely local CPU.
        """
        t0 = time.perf_counter()

        sections = []
        for doc in docs:
            header = f"### [{doc.modality}] {doc.path}"
            sections.append(f"{header}\n\n{doc.content}")

        self._context = "\n\n---\n\n".join(sections)
        self._ingest_doc_count = len(docs)
        self._wiki_tokens = count_tokens(self._context, self.model)

        duration = time.perf_counter() - t0
        log.info(
            "NaiveAdapter ingested %d docs, %d wiki tokens in %.3fs",
            self._ingest_doc_count,
            self._wiki_tokens,
            duration,
        )

        return IngestResult(
            wiki_id=f"naive-{id(self):x}",
            stats=IngestStats(
                tokens_in=0,
                tokens_out=0,
                llm_calls=0,
                duration_s=duration,
                wiki_tokens=self._wiki_tokens,
            ),
        )

    # ── query ─────────────────────────────────────────────────────────────────

    def query(self, query: Query) -> QueryResponse:
        """Answer a query using the full document context."""
        if not self._context:
            raise RuntimeError("NaiveAdapter.ingest() must be called before query().")

        from wikibench.runtime.llm import llm_call

        messages = _build_messages(query, self._context)

        # Gemini 2.5+ enables thinking by default; disable for deterministic,
        # lower-latency evaluation queries.
        extra: dict[str, Any] = {}
        if "gemini-2.5" in self.model or "gemini-3" in self.model:
            extra["thinking"] = {"type": "disabled"}

        raw = llm_call(
            model=self.model,
            messages=messages,
            purpose="adapter.query",
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            timeout_s=self.timeout_s,
            **extra,
        )
        return _parse_response(query, raw)

    # ── optional ──────────────────────────────────────────────────────────────

    def export_wiki(self) -> str:
        return self._context


# ── Prompt construction ───────────────────────────────────────────────────────

def _build_messages(query: Query, context: str) -> list[dict[str, str]]:
    """Build the OpenAI-format messages list for a query."""
    system_content = f"{_SYSTEM_PROMPT}\n\n## Knowledge Base\n\n{context}"

    intent_instruction = _INTENT_INSTRUCTIONS.get(query.intent, "")

    if query.intent == "fidelity_check":
        claim = query.params.get("claim", query.text)
        user_content = f"{intent_instruction}\n\nClaim to evaluate:\n{claim}"
    elif query.intent == "contradiction_check":
        user_content = intent_instruction
    elif query.intent == "grounding":
        user_content = f"{intent_instruction}\n\nQuestion:\n{query.text}"
    else:
        user_content = query.text

    return [
        {"role": "system", "content": system_content},
        {"role": "user", "content": user_content},
    ]


# ── Response parsing ──────────────────────────────────────────────────────────

def _parse_response(query: Query, raw: str) -> QueryResponse:
    """Parse the raw LLM output into a structured QueryResponse."""
    structured: dict[str, Any] = {}

    if query.intent in ("fidelity_check", "contradiction_check", "grounding"):
        structured = _extract_json(raw)

    # Normalise fidelity verdict casing
    if query.intent == "fidelity_check" and "verdict" in structured:
        structured["verdict"] = structured["verdict"].lower().strip()

    # For grounding, move answer up if present
    answer = raw
    if query.intent == "grounding" and "answer" in structured:
        answer = structured.pop("answer")

    return QueryResponse(
        answer=answer,
        structured=structured,
        sources=structured.get("sources", []),
        raw={"raw_text": raw},
    )


def _extract_json(text: str) -> dict[str, Any]:
    """Extract the first JSON object from a string, ignoring markdown fences."""
    # Strip ```json ... ``` fences if present
    stripped = text.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        inner = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
        stripped = inner.strip()

    try:
        return json.loads(stripped)  # type: ignore[return-value]
    except json.JSONDecodeError:
        pass

    # Find first {...} block
    start = stripped.find("{")
    if start != -1:
        depth = 0
        for i, ch in enumerate(stripped[start:], start):
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(stripped[start : i + 1])  # type: ignore[return-value]
                    except json.JSONDecodeError:
                        break

    log.debug("Could not parse JSON from LLM response: %r", text[:200])
    return {}
