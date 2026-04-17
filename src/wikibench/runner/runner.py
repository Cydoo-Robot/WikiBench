"""Main Runner — orchestrates adapter + corpus + tasks into a BenchmarkResult."""

from __future__ import annotations

import contextlib
import logging
import time
from typing import Any

from wikibench.models.corpus import Corpus
from wikibench.models.result import BenchmarkResult, TaskResult
from wikibench.runtime.cache import ResponseCache
from wikibench.runtime.cost import CostTracker

log = logging.getLogger(__name__)

# Default MVP task set
_DEFAULT_TASKS = ["retrieval_accuracy", "knowledge_fidelity", "contradiction_detection"]


def _ensure_tasks_registered() -> None:
    """Import built-in task modules so their @register_task decorators fire."""
    import importlib

    _BUILTIN_TASKS = [
        "wikibench.tasks.retrieval_accuracy",
        "wikibench.tasks.knowledge_fidelity",
        "wikibench.tasks.contradiction_detection",
    ]
    for mod_name in _BUILTIN_TASKS:
        importlib.import_module(mod_name)


class Runner:
    """Orchestrate a WikiBench evaluation run.

    Parameters
    ----------
    adapter_spec:
        * A registered adapter name (str), e.g. ``"naive"`` — loaded from
          entry_points.
        * A ``WikiAdapter`` **class** — instantiated with ``adapter_config``.
        * A pre-instantiated ``WikiAdapter`` **instance** — used directly.
    adapter_config:
        Configuration dict forwarded to ``WikiAdapter.__init__``.
    corpus:
        A corpus directory path (str/Path) or a loaded :class:`Corpus`.
    tasks:
        Task IDs to run.  Defaults to T1+T2+T3.
    seed:
        Random seed for reproducibility.
    cache_dir:
        Directory for response caching.  Pass ``None`` to disable.
    hard_limit_usd:
        Abort the run if cumulative LLM cost exceeds this value.
    """

    def __init__(
        self,
        adapter_spec: Any,
        adapter_config: dict[str, Any] | None = None,
        corpus: str | Corpus | None = None,
        tasks: list[str] | None = None,
        seed: int = 42,
        cache_dir: str | None = ".wikibench-cache",
        hard_limit_usd: float = float("inf"),
    ) -> None:
        self.adapter_spec = adapter_spec
        self.adapter_config = adapter_config or {}
        self._corpus_spec = corpus
        self._task_ids = tasks or _DEFAULT_TASKS
        self.seed = seed
        self.cache_dir = cache_dir
        self.hard_limit_usd = hard_limit_usd

    # ── Public API ────────────────────────────────────────────────────────────

    def run(self) -> BenchmarkResult:
        """Execute the full evaluation pipeline.

        Steps
        -----
        1. Load corpus.
        2. Resolve and instantiate adapter.
        3. Install a fresh CostTracker.
        4. Configure response cache.
        5. ``adapter.ingest(docs)`` — compile the wiki.
        6. For each task: ``prepare`` → ``query`` each adapter → ``score`` → ``aggregate``.
        7. Flatten metrics into BenchmarkResult.
        8. Teardown adapter.
        """
        t_run_start = time.perf_counter()

        _ensure_tasks_registered()

        # ── 1. Load corpus ────────────────────────────────────────────────────
        corpus = self._load_corpus()
        log.info("Runner: corpus %s (%d docs)", corpus.id, len(corpus.documents))

        # ── 2. Resolve adapter ────────────────────────────────────────────────
        adapter = self._resolve_adapter()
        log.info("Runner: adapter %s v%s", adapter.name, adapter.version)

        # ── 3. Cost tracker ───────────────────────────────────────────────────
        tracker = CostTracker(hard_limit_usd=self.hard_limit_usd)
        CostTracker.install(tracker)

        # ── 4. Cache ──────────────────────────────────────────────────────────
        if self.cache_dir:
            cache = ResponseCache(cache_dir=self.cache_dir)
            from wikibench.runtime import cache as _cache_mod

            _cache_mod._default_cache = cache

        try:
            # ── 5. Ingest ─────────────────────────────────────────────────────
            log.info("Runner: ingesting %d documents…", len(corpus.documents))
            t_ingest = time.perf_counter()
            ingest_result = adapter.ingest(corpus.documents)
            log.info(
                "Runner: ingest done in %.2fs, wiki_tokens=%d",
                time.perf_counter() - t_ingest,
                ingest_result.stats.wiki_tokens,
            )

            # ── 6. Tasks ──────────────────────────────────────────────────────
            per_task: dict[str, TaskResult] = {}
            for task_id in self._task_ids:
                task_result = self._run_task(task_id, adapter, corpus)
                if task_result is not None:
                    per_task[task_id] = task_result

        finally:
            # ── 8. Teardown ───────────────────────────────────────────────────
            with contextlib.suppress(Exception):
                adapter.teardown()
            CostTracker.uninstall()

        # ── 7. Assemble result ────────────────────────────────────────────────
        from wikibench.runner.env import collect_environment

        desc = adapter.describe()
        env = collect_environment(
            impl_version=getattr(adapter, "version", "unknown"),
            llm_models=desc.get("llm_models", {}),
            seed=self.seed,
            impl_commit=desc.get("commit"),
        )

        metrics = _flatten_metrics(per_task)
        elapsed = time.perf_counter() - t_run_start

        result = BenchmarkResult(
            impl=f"{adapter.name}@{getattr(adapter, 'version', 'unknown')}",
            corpus_id=corpus.id,
            environment=env,
            ingest=ingest_result.stats,
            per_task=per_task,
            metrics=metrics,
            warnings=_collect_warnings(per_task, tracker, elapsed),
        )

        log.info(
            "Runner: run complete in %.2fs | cost $%.4f | %d tasks",
            elapsed,
            tracker.total_usd,
            len(per_task),
        )
        return result

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _load_corpus(self) -> Corpus:
        if isinstance(self._corpus_spec, Corpus):
            return self._corpus_spec
        if self._corpus_spec is None:
            raise ValueError("Runner: corpus must be provided.")
        from wikibench.corpora.loader import load_corpus

        return load_corpus(self._corpus_spec)

    def _resolve_adapter(self) -> Any:
        """Return a ready-to-use WikiAdapter instance."""
        from wikibench.adapters._base import WikiAdapter

        spec = self.adapter_spec

        # Already an instance
        if isinstance(spec, WikiAdapter):
            return spec

        # A class — instantiate it
        if isinstance(spec, type) and issubclass(spec, WikiAdapter):
            return spec(self.adapter_config)

        # A string: ``"entry_point_name"`` or ``"module.path:ClassName"`` (same as CLI).
        if isinstance(spec, str):
            if ":" in spec:
                module_path, cls_name = spec.rsplit(":", 1)
                if module_path and cls_name:
                    import importlib

                    mod = importlib.import_module(module_path)
                    cls = getattr(mod, cls_name, None)
                    if isinstance(cls, type) and issubclass(cls, WikiAdapter):
                        return cls(self.adapter_config)
                    raise TypeError(
                        f"Adapter spec {spec!r} must name a WikiAdapter subclass; got {cls!r}"
                    )
            from wikibench.adapters.registry import get_adapter

            cls = get_adapter(spec)
            return cls(self.adapter_config)

        raise TypeError(f"Cannot resolve adapter from {type(spec).__name__!r}: {spec!r}")

    def _run_task(self, task_id: str, adapter: Any, corpus: Corpus) -> TaskResult | None:
        """Prepare queries, run adapter, score, aggregate for one task."""
        from wikibench.tasks import get_task

        try:
            task_cls = get_task(task_id)
        except KeyError:
            log.warning("Runner: unknown task %r — skipping", task_id)
            return None

        task = task_cls()

        log.info("Runner: running task %s", task_id)
        t0 = time.perf_counter()

        queries = task.prepare(corpus)
        if not queries:
            log.warning("Runner: task %s produced no queries — skipping", task_id)
            return None

        scores = []
        for query in queries:
            try:
                response = adapter.query(query)
                score = task.score(query, response, corpus)
                scores.append(score)
            except Exception as exc:
                from wikibench.runtime.cost import CostLimitExceededError

                if isinstance(exc, CostLimitExceededError):
                    raise  # propagate immediately — abort the whole run
                log.error("Runner: error on query %s (%s): %s", query.id, task_id, exc)
                from wikibench.models.result import Score

                scores.append(
                    Score(
                        metric=task_id,
                        value=0.0,
                        details={"error": str(exc)},
                    )
                )

        result = task.aggregate(scores)
        log.info(
            "Runner: task %s done in %.2fs — mean=%.3f",
            task_id,
            time.perf_counter() - t0,
            result.slices.get("mean", 0.0),
        )
        return result


# ── Helpers ───────────────────────────────────────────────────────────────────


def _flatten_metrics(per_task: dict[str, TaskResult]) -> dict[str, float]:
    """Produce a flat ``{metric_name: value}`` dict from all task results."""
    metrics: dict[str, float] = {}
    for task_id, result in per_task.items():
        for key, val in result.slices.items():
            if isinstance(val, (int, float)):
                metrics[f"{task_id}.{key}"] = float(val)
    return metrics


def _collect_warnings(
    per_task: dict[str, TaskResult],
    tracker: CostTracker,
    elapsed_s: float,
) -> list[str]:
    warnings: list[str] = []
    for result in per_task.values():
        warnings.extend(result.warnings)
    if tracker.total_usd > 5.0:
        warnings.append(f"High cost: ${tracker.total_usd:.3f} for this run")
    if elapsed_s > 1800:
        warnings.append(f"Long run: {elapsed_s:.0f}s")
    return warnings
