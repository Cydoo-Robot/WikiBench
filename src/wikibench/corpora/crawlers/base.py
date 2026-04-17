"""BaseCrawler ABC (Phase 1.5)."""

from __future__ import annotations

from abc import ABC, abstractmethod

from wikibench.models.document import ForumThread


class BaseCrawler(ABC):
    @abstractmethod
    def fetch(self, query: str, max_results: int = 100) -> list[ForumThread]:
        """Fetch threads matching ``query``."""
