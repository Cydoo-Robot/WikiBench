"""LLM-as-judge base class (Phase 1 Week 3)."""

from __future__ import annotations

from abc import ABC, abstractmethod

from wikibench.models.query import Query, QueryResponse
from wikibench.models.result import Score


class BaseJudge(ABC):
    @abstractmethod
    def judge(self, query: Query, response: QueryResponse, reference: str) -> Score:
        """Evaluate a response against a reference answer."""
