"""Built-in metric registrations — single source of truth for all metric IDs."""

from wikibench.metrics import register_metric
from wikibench.models.result import TaskResult


@register_metric(id="retrieval_accuracy", higher_is_better=True, range=(0.0, 1.0))
def retrieval_accuracy(task_results: dict[str, TaskResult]) -> float:
    raise NotImplementedError("Phase 1 Week 3.")


@register_metric(id="fidelity_score", higher_is_better=True, range=(0.0, 1.0))
def fidelity_score(task_results: dict[str, TaskResult]) -> float:
    raise NotImplementedError("Phase 1 Week 3.")


@register_metric(id="contradiction_recall", higher_is_better=True, range=(0.0, 1.0))
def contradiction_recall(task_results: dict[str, TaskResult]) -> float:
    raise NotImplementedError("Phase 1 Week 3.")


@register_metric(id="hallucination_rate", higher_is_better=False, range=(0.0, 1.0))
def hallucination_rate(task_results: dict[str, TaskResult]) -> float:
    raise NotImplementedError("Phase 1 Week 3.")


@register_metric(id="token_ratio", higher_is_better=True, range=(0.0, float("inf")))
def token_ratio(task_results: dict[str, TaskResult]) -> float:
    raise NotImplementedError("Phase 1 Week 4.")
