"""BenchmarkResult and related output models."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class IngestStats(BaseModel):
    tokens_in: int
    tokens_out: int
    llm_calls: int
    duration_s: float
    wiki_tokens: int
    """Token count of the compiled wiki artefact — must be reported."""
    cost_usd: float | None = None
    extra: dict[str, Any] = Field(default_factory=dict)


class IngestResult(BaseModel):
    wiki_id: str
    """Adapter-internal identifier for the compiled wiki."""
    stats: IngestStats


class RunEnvironment(BaseModel):
    python_version: str
    os: str
    wikibench_version: str
    impl_version: str
    impl_commit: str | None = None
    llm_models: dict[str, str]
    """e.g. ``{"adapter_backend": "gpt-4o-mini", "judge": "gpt-4o"}``"""
    seed: int


class Score(BaseModel):
    metric: str
    value: float
    details: dict[str, Any] = Field(default_factory=dict)


class TaskResult(BaseModel):
    task_id: str
    task_version: str
    scores: list[Score]
    slices: dict[str, Any] = Field(default_factory=dict)
    """Per-slice breakdown, e.g. by difficulty or document type."""
    warnings: list[str] = Field(default_factory=list)


class BenchmarkResult(BaseModel):
    run_id: str = Field(default_factory=lambda: str(uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    impl: str
    """e.g. ``ussumant@0.3.2``"""
    corpus_id: str
    environment: RunEnvironment
    ingest: IngestStats
    per_task: dict[str, TaskResult] = Field(default_factory=dict)
    metrics: dict[str, float] = Field(default_factory=dict)
    """Flat metric dictionary."""
    composite: dict[str, float] = Field(default_factory=dict)
    """Multiple composite scores, e.g. ``{"wikibench_v1": 0.73}``."""
    warnings: list[str] = Field(default_factory=list)
