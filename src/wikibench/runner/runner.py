"""Main Runner class (Phase 1 Week 3)."""

from __future__ import annotations

from typing import Any

from wikibench.models.corpus import Corpus
from wikibench.models.result import BenchmarkResult


class Runner:
    """Orchestrate a WikiBench evaluation run.

    Parameters
    ----------
    adapter_spec:
        Adapter name (looked up from entry_points) or a pre-instantiated
        ``WikiAdapter`` instance.
    adapter_config:
        Configuration dict forwarded to ``WikiAdapter.__init__``.
    corpus:
        A corpus ID string or a loaded ``Corpus`` instance.
    tasks:
        List of task IDs to run.  Defaults to all registered tasks.
    seed:
        Random seed for reproducibility.
    cache_dir:
        Directory for diskcache response caching.
    """

    def __init__(
        self,
        adapter_spec: Any,
        adapter_config: dict[str, Any] | None = None,
        corpus: str | Corpus | None = None,
        tasks: list[str] | None = None,
        seed: int = 42,
        cache_dir: str = ".wikibench-cache",
    ) -> None:
        self.adapter_spec = adapter_spec
        self.adapter_config = adapter_config or {}
        self.corpus = corpus
        self.tasks = tasks
        self.seed = seed
        self.cache_dir = cache_dir

    def run(self) -> BenchmarkResult:
        raise NotImplementedError("Runner.run — Phase 1 Week 3.")
