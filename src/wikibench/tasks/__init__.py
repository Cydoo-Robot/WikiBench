"""Task ABC and registry."""

from __future__ import annotations

from abc import ABC, abstractmethod

from wikibench.models.corpus import Corpus
from wikibench.models.query import Query, QueryResponse
from wikibench.models.result import Score, TaskResult

_TASK_REGISTRY: dict[str, type[Task]] = {}


def register_task(cls: type[Task]) -> type[Task]:
    """Class decorator to register a Task implementation."""
    _TASK_REGISTRY[cls.id] = cls
    return cls


def get_task(task_id: str) -> type[Task]:
    if task_id not in _TASK_REGISTRY:
        raise KeyError(f"Unknown task: '{task_id}'. Available: {list(_TASK_REGISTRY)}")
    return _TASK_REGISTRY[task_id]


def list_tasks() -> list[str]:
    return list(_TASK_REGISTRY)


class Task(ABC):
    """Abstract base class for all WikiBench evaluation tasks."""

    id: str
    version: str

    @abstractmethod
    def prepare(self, corpus: Corpus) -> list[Query]:
        """Generate queries from corpus ground truth."""

    @abstractmethod
    def score(self, query: Query, response: QueryResponse, corpus: Corpus) -> Score:
        """Score a single adapter response."""

    def aggregate(self, scores: list[Score]) -> TaskResult:
        """Default aggregation: arithmetic mean + collect scores."""
        if not scores:
            return TaskResult(task_id=self.id, task_version=self.version, scores=[])
        mean = sum(s.value for s in scores) / len(scores)
        return TaskResult(
            task_id=self.id,
            task_version=self.version,
            scores=scores,
            slices={"mean": mean},
        )
