"""T4 — Grounding task (Phase 1.5)."""

from __future__ import annotations

from wikibench.models.corpus import Corpus
from wikibench.models.query import Query, QueryResponse
from wikibench.models.result import Score
from wikibench.tasks import Task


class GroundingTask(Task):
    """Measure whether adapter responses are grounded in actual source documents."""

    id = "grounding"
    version = "1.0.0"

    def prepare(self, corpus: Corpus) -> list[Query]:
        raise NotImplementedError("GroundingTask — Phase 1.5.")

    def score(self, query: Query, response: QueryResponse, corpus: Corpus) -> Score:
        raise NotImplementedError("GroundingTask — Phase 1.5.")
