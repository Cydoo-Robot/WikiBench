"""T3 — Contradiction Detection task (Phase 1 Week 3)."""

from __future__ import annotations

from wikibench.models.corpus import Corpus
from wikibench.models.query import Query, QueryResponse
from wikibench.models.result import Score
from wikibench.tasks import Task, register_task


@register_task
class ContradictionDetectionTask(Task):
    """Measure whether the adapter detects deliberate contradictions across documents."""

    id = "contradiction_detection"
    version = "1.0.0"

    def prepare(self, corpus: Corpus) -> list[Query]:
        raise NotImplementedError("ContradictionDetectionTask.prepare — Phase 1 Week 3.")

    def score(self, query: Query, response: QueryResponse, corpus: Corpus) -> Score:
        raise NotImplementedError("ContradictionDetectionTask.score — Phase 1 Week 3.")
