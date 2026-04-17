"""M2 — Staleness Detection task (Phase 1.5)."""

from __future__ import annotations

from wikibench.models.corpus import Corpus
from wikibench.models.query import Query, QueryResponse
from wikibench.models.result import Score
from wikibench.tasks import Task


class StalenessDetectionTask(Task):
    id = "staleness_detection"
    version = "1.0.0"

    def prepare(self, corpus: Corpus) -> list[Query]:
        raise NotImplementedError("StalenessDetectionTask — Phase 1.5.")

    def score(self, query: Query, response: QueryResponse, corpus: Corpus) -> Score:
        raise NotImplementedError("StalenessDetectionTask — Phase 1.5.")
