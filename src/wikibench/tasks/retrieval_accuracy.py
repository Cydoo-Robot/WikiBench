"""T1 — Retrieval Accuracy task (Phase 1 Week 3)."""

from __future__ import annotations

from wikibench.models.corpus import Corpus
from wikibench.models.query import Query, QueryResponse
from wikibench.models.result import Score, TaskResult
from wikibench.tasks import Task, register_task


@register_task
class RetrievalAccuracyTask(Task):
    """Measure whether the adapter can retrieve the correct answer to factual QA queries."""

    id = "retrieval_accuracy"
    version = "1.0.0"

    def prepare(self, corpus: Corpus) -> list[Query]:
        raise NotImplementedError("RetrievalAccuracyTask.prepare — Phase 1 Week 3.")

    def score(self, query: Query, response: QueryResponse, corpus: Corpus) -> Score:
        raise NotImplementedError("RetrievalAccuracyTask.score — Phase 1 Week 3.")
