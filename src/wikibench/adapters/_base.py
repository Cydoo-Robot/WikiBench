"""WikiAdapter — abstract base class for all LLM Wiki implementations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from wikibench.models.document import Document
from wikibench.models.query import Query, QueryResponse
from wikibench.models.result import IngestResult


class WikiAdapter(ABC):
    """Interface between WikiBench runner and a third-party LLM Wiki implementation.

    Implementors must subclass this and provide concrete ``ingest`` and ``query``
    methods.  All other methods are optional.

    Class attributes (set on the subclass)
    ---------------------------------------
    name : str
        Unique adapter ID, e.g. ``"ussumant"``.
    version : str
        SemVer string, e.g. ``"0.3.2"``.
    supports_update : bool
        Whether the adapter implements incremental ``update()``.
    supports_staleness : bool
        Whether the adapter can signal document staleness.
    supports_coverage : bool
        Whether the adapter implements coverage self-assessment.
    """

    name: str
    version: str
    supports_update: bool = False
    supports_staleness: bool = False
    supports_coverage: bool = False

    def __init__(self, config: dict[str, Any]) -> None:
        """Initialise from a configuration dictionary.

        Config schema is adapter-defined; document it in your adapter's README.
        """

    def describe(self) -> dict[str, Any]:
        """Return adapter metadata written into ``RunEnvironment``.

        Must include ``llm_models`` key mapping role → model name.
        """
        return {
            "name": self.name,
            "version": self.version,
            "llm_models": {},
        }

    # ── Required ─────────────────────────────────────────────────────────────

    @abstractmethod
    def ingest(self, docs: list[Document]) -> IngestResult:
        """Compile raw documents into a wiki; return compilation statistics."""

    @abstractmethod
    def query(self, query: Query) -> QueryResponse:
        """Answer a query against the compiled wiki.

        The ``structured`` field of the response must be populated according
        to ``query.intent`` — see ``QueryResponse`` docstring for required keys.
        """

    # ── Optional ─────────────────────────────────────────────────────────────

    def update(
        self,
        added: list[Document],
        removed: list[str],
        modified: list[Document],
    ) -> IngestResult:
        """Incrementally update the wiki (Phase 1.5+)."""
        raise NotImplementedError

    def export_wiki(self) -> str:
        """Export the compiled wiki artefact as a string.

        Used to measure ``wiki_tokens`` precisely.  When not implemented the
        runner estimates from ``IngestStats.wiki_tokens``.
        """
        raise NotImplementedError

    def teardown(self) -> None:
        """Release resources (close processes, clear caches, etc.)."""
