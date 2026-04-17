"""M1 — Incremental Update task (Phase 1.5)."""

from __future__ import annotations

from wikibench.models.corpus import Corpus
from wikibench.models.query import Query, QueryResponse
from wikibench.models.result import Score
from wikibench.tasks import Task


class IncrementalUpdateTask(Task):
    id = "incremental_update"
    version = "1.0.0"

    def prepare(self, corpus: Corpus) -> list[Query]:
        raise NotImplementedError("IncrementalUpdateTask — Phase 1.5.")

    def score(self, query: Query, response: QueryResponse, corpus: Corpus) -> Score:
        raise NotImplementedError("IncrementalUpdateTask — Phase 1.5.")
