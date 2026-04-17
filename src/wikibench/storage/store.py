"""Abstract storage interface (Phase 1 Week 6)."""

from __future__ import annotations

from abc import ABC, abstractmethod

from wikibench.models.result import BenchmarkResult


class ResultStore(ABC):
    @abstractmethod
    def save(self, result: BenchmarkResult) -> str:
        """Persist a result; return its storage key."""

    @abstractmethod
    def load(self, run_id: str) -> BenchmarkResult:
        """Load a result by run_id."""

    @abstractmethod
    def list_runs(self) -> list[str]:
        """Return all stored run_ids."""
