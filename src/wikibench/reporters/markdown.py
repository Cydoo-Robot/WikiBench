"""Markdown reporter — renders a BenchmarkResult as a GitHub-flavoured Markdown document."""

from __future__ import annotations

from io import StringIO
from pathlib import Path

from wikibench.models.result import BenchmarkResult


def render(result: BenchmarkResult) -> str:
    """Return the result as a Markdown string."""
    buf = StringIO()
    w = buf.write

    env = result.environment

    w(f"# WikiBench Report\n\n")
    w(f"| Field | Value |\n|---|---|\n")
    w(f"| Run ID | `{result.run_id}` |\n")
    w(f"| Timestamp | {result.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')} |\n")
    w(f"| Impl | `{result.impl}` |\n")
    w(f"| Corpus | `{result.corpus_id}` |\n")
    w(f"| WikiBench | v{env.wikibench_version} |\n")
    w(f"| Python | {env.python_version.split()[0]} |\n")
    w(f"| Seed | {env.seed} |\n")
    if env.llm_models:
        for role, model in env.llm_models.items():
            w(f"| LLM ({role}) | `{model}` |\n")
    w("\n")

    # ── Ingest ────────────────────────────────────────────────────────────────
    ingest = result.ingest
    w("## Ingest Stats\n\n")
    w("| Metric | Value |\n|---|---|\n")
    w(f"| Wiki tokens | {ingest.wiki_tokens} |\n")
    w(f"| Tokens in | {ingest.tokens_in} |\n")
    w(f"| Tokens out | {ingest.tokens_out} |\n")
    w(f"| LLM calls | {ingest.llm_calls} |\n")
    w(f"| Duration | {ingest.duration_s:.2f}s |\n")
    if ingest.cost_usd is not None:
        w(f"| Cost (USD) | ${ingest.cost_usd:.6f} |\n")
    w("\n")

    # ── Per-task ──────────────────────────────────────────────────────────────
    for task_id, task_result in result.per_task.items():
        w(f"## Task: {task_id} (v{task_result.task_version})\n\n")
        if task_result.slices:
            w("| Metric | Value |\n|---|---|\n")
            for key, val in task_result.slices.items():
                if isinstance(val, float):
                    w(f"| {key} | {val:.4f} |\n")
                else:
                    w(f"| {key} | {val} |\n")
        if task_result.warnings:
            w("\n**Warnings:**\n\n")
            for warning in task_result.warnings:
                w(f"- {warning}\n")
        w("\n")

    # ── Flat metrics ─────────────────────────────────────────────────────────
    if result.metrics:
        w("## Flat Metrics\n\n")
        w("| Metric | Score |\n|---|---|\n")
        for key in sorted(result.metrics):
            w(f"| {key} | {result.metrics[key]:.4f} |\n")
        w("\n")

    # ── Composite ────────────────────────────────────────────────────────────
    if result.composite:
        w("## Composite Scores\n\n")
        w("| Score | Value |\n|---|---|\n")
        for key in sorted(result.composite):
            w(f"| {key} | {result.composite[key]:.4f} |\n")
        w("\n")

    # ── Warnings ─────────────────────────────────────────────────────────────
    if result.warnings:
        w("## Warnings\n\n")
        for warning in result.warnings:
            w(f"- {warning}\n")
        w("\n")

    return buf.getvalue()


def save(result: BenchmarkResult, path: str | Path) -> Path:
    """Write Markdown to *path*.

    If *path* is a directory the file is named ``<run_id>.md``.
    """
    p = Path(path)
    if p.is_dir() or str(path).endswith("/") or str(path).endswith("\\"):
        p = p / f"{result.run_id}.md"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(render(result), encoding="utf-8")
    return p.resolve()
