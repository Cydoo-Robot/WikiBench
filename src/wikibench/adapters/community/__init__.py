"""Third-party LLM Wiki implementations (sandboxes + subprocess / orchestration)."""

from __future__ import annotations

from wikibench.adapters.community.llm_wiki_compiler import LLMWikiCompilerAdapter
from wikibench.adapters.community.obsidian_wiki import ObsidianWikiAdapter

__all__ = [
    "LLMWikiCompilerAdapter",
    "ObsidianWikiAdapter",
]
