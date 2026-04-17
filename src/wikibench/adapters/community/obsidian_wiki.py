"""Community adapter: Ar9av/obsidian-wiki — prompt orchestration via upstream ``.skills/``.

This does **not** embed Obsidian or a custom vault compiler. It loads Markdown skill
files from a checkout of `obsidian-wiki` (or a test fixture with the same layout)
and uses WikiBench :func:`wikibench.runtime.llm.llm_call` for queries, with corpus
content as the knowledge base (same coverage pattern as :class:`NaiveAdapter`).

See ``Doc/07`` §4.2 B.
"""

from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Any

from wikibench.adapters._base import WikiAdapter
from wikibench.adapters.builtin.naive import _parse_response
from wikibench.adapters.community.query_prompt import KB_SYSTEM_PROMPT, build_user_query_text
from wikibench.adapters.community.sandbox import suggested_clone_path
from wikibench.models.document import Document
from wikibench.models.query import Query, QueryResponse
from wikibench.models.result import IngestResult, IngestStats
from wikibench.runtime.token_counter import count_tokens

log = logging.getLogger(__name__)

_SYSTEM_PREFIX = """You are a knowledge-base assistant.
The following blocks are upstream skill instructions (from obsidian-wiki `.skills/`).
Apply them when answering. Then use ONLY the knowledge base section — do not invent facts.
"""


class ObsidianWikiAdapter(WikiAdapter):
    """Skills-augmented full-context queries (compatible with ``WIKIBENCH_LLM_MOCK``)."""

    name = "obsidian_wiki"
    version = "0.1.0"

    def __init__(self, config: dict[str, Any]) -> None:
        super().__init__(config)
        raw = config.get("obsidian_wiki_repo")
        if not raw:
            raise ValueError(
                "ObsidianWikiAdapter requires config key 'obsidian_wiki_repo' "
                "(path to a clone of Ar9av/obsidian-wiki or a test fixture with `.skills/`)."
            )
        self._repo = Path(str(raw)).expanduser().resolve()
        self.model: str = config.get("model", "gemini/gemini-2.5-flash")
        self.max_tokens: int | None = config.get("max_tokens")
        self.temperature: float = float(config.get("temperature", 0.0))
        self.timeout_s: float = float(config.get("timeout_s", 120.0))

        self._skills_text: str = ""
        self._context: str = ""
        self._wiki_tokens: int = 0

    def describe(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "llm_models": {"adapter_backend": self.model},
            "strategy": "obsidian_skills_llm",
            "upstream_hint": str(suggested_clone_path({}, "obsidian-wiki")),
        }

    def _load_skills(self) -> str:
        skills_dir = self._repo / ".skills"
        if not skills_dir.is_dir():
            log.warning("No .skills directory under %s — continuing with empty skills", self._repo)
            return ""
        parts: list[str] = []
        for md in sorted(skills_dir.rglob("*.md")):
            rel = md.relative_to(skills_dir)
            parts.append(f"### {rel.as_posix()}\n{md.read_text(encoding='utf-8')}")
        return "\n\n".join(parts)

    def ingest(self, docs: list[Document]) -> IngestResult:
        t0 = time.perf_counter()
        self._skills_text = self._load_skills()

        sections: list[str] = []
        for doc in docs:
            header = f"### [{doc.modality}] {doc.path}"
            sections.append(f"{header}\n\n{doc.content}")
        self._context = "\n\n---\n\n".join(sections)
        self._wiki_tokens = count_tokens(self._context, self.model)

        duration = time.perf_counter() - t0
        return IngestResult(
            wiki_id=f"obsidian-wiki-{id(self):x}",
            stats=IngestStats(
                tokens_in=0,
                tokens_out=0,
                llm_calls=0,
                duration_s=duration,
                wiki_tokens=self._wiki_tokens,
                extra={"obsidian_wiki_repo": str(self._repo)},
            ),
        )

    def query(self, query: Query) -> QueryResponse:
        if not self._context:
            raise RuntimeError("ObsidianWikiAdapter.ingest() must be called before query().")

        from wikibench.runtime.llm import llm_call

        skills_block = self._skills_text or "(no skill files loaded)"
        system_content = (
            f"{_SYSTEM_PREFIX}\n\n## Upstream skills\n\n{skills_block}\n\n"
            f"{KB_SYSTEM_PROMPT}\n\n## Knowledge Base\n\n{self._context}"
        )
        user_content = build_user_query_text(query)
        messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content},
        ]

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

    def export_wiki(self) -> str:
        return self._context
