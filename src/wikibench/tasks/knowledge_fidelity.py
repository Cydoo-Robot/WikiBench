"""T2 — Knowledge Fidelity task (Phase 1 Week 3)."""

from __future__ import annotations

from wikibench.models.corpus import Corpus
from wikibench.models.query import Query, QueryResponse
from wikibench.models.result import Score
from wikibench.tasks import Task, register_task


@register_task
class KnowledgeFidelityTask(Task):
    """Measure whether the adapter correctly judges factual claims as supported / not / unknown."""

    id = "knowledge_fidelity"
    version = "1.0.0"

    def prepare(self, corpus: Corpus) -> list[Query]:
        raise NotImplementedError("KnowledgeFidelityTask.prepare — Phase 1 Week 3.")

    def score(self, query: Query, response: QueryResponse, corpus: Corpus) -> Score:
        raise NotImplementedError("KnowledgeFidelityTask.score — Phase 1 Week 3.")
