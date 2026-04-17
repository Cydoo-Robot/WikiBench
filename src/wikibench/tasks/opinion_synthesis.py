"""T5 — Opinion Synthesis task (Phase 1.5, requires Forum corpus)."""

from __future__ import annotations

from wikibench.models.corpus import Corpus
from wikibench.models.query import Query, QueryResponse
from wikibench.models.result import Score
from wikibench.tasks import Task


class OpinionSynthesisTask(Task):
    """Evaluate adapter ability to synthesise multiple community stances on a topic."""

    id = "opinion_synthesis"
    version = "1.0.0"

    def prepare(self, corpus: Corpus) -> list[Query]:
        raise NotImplementedError("OpinionSynthesisTask — Phase 1.5.")

    def score(self, query: Query, response: QueryResponse, corpus: Corpus) -> Score:
        raise NotImplementedError("OpinionSynthesisTask — Phase 1.5.")
