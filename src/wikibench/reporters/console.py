"""Rich console reporter — pretty-prints a BenchmarkResult to the terminal."""

from __future__ import annotations

from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from wikibench.models.result import BenchmarkResult

_SCORE_COLORS = [
    (0.8, "bright_green"),
    (0.6, "green"),
    (0.4, "yellow"),
    (0.2, "red"),
    (0.0, "bright_red"),
]


def _score_color(val: float) -> str:
    for threshold, color in _SCORE_COLORS:
        if val >= threshold:
            return color
    return "bright_red"


def _fmt(val: float) -> str:
    return f"{val:.3f}"


def render(result: BenchmarkResult, console: Console | None = None) -> None:
    """Print a full benchmark result to *console* (defaults to stdout)."""
    con = console or Console()

    # ── Header panel ─────────────────────────────────────────────────────────
    env = result.environment
    header_lines = [
        f"[bold]Run ID:[/bold]      {result.run_id}",
        f"[bold]Timestamp:[/bold]   {result.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}",
        f"[bold]Impl:[/bold]        {result.impl}",
        f"[bold]Corpus:[/bold]      {result.corpus_id}",
        f"[bold]WikiBench:[/bold]   v{env.wikibench_version}",
        f"[bold]Python:[/bold]      {env.python_version.split()[0]}",
        f"[bold]Seed:[/bold]        {env.seed}",
    ]
    if env.llm_models:
        models_str = ", ".join(f"{k}={v}" for k, v in env.llm_models.items())
        header_lines.append(f"[bold]LLM models:[/bold]  {models_str}")
    con.print(Panel("\n".join(header_lines), title="WikiBench Report", border_style="blue"))

    # ── Ingest stats ──────────────────────────────────────────────────────────
    ingest = result.ingest
    con.print()
    ig_table = Table("Metric", "Value", title="Ingest Stats", box=box.SIMPLE_HEAVY, show_header=True)
    ig_table.add_row("Wiki tokens", str(ingest.wiki_tokens))
    ig_table.add_row("Tokens in", str(ingest.tokens_in))
    ig_table.add_row("Tokens out", str(ingest.tokens_out))
    ig_table.add_row("LLM calls", str(ingest.llm_calls))
    ig_table.add_row("Duration", f"{ingest.duration_s:.2f}s")
    if ingest.cost_usd is not None:
        ig_table.add_row("Cost (USD)", f"${ingest.cost_usd:.6f}")
    con.print(ig_table)

    # ── Per-task results ──────────────────────────────────────────────────────
    for task_id, task_result in result.per_task.items():
        con.print()
        t = Table(
            "Metric", "Value",
            title=f"Task: [bold]{task_id}[/bold] v{task_result.task_version}",
            box=box.SIMPLE_HEAVY,
        )
        for key, val in task_result.slices.items():
            if isinstance(val, float):
                color = _score_color(val)
                t.add_row(key, f"[{color}]{_fmt(val)}[/{color}]")
            elif isinstance(val, dict):
                t.add_row(key, str(val))
            else:
                t.add_row(key, str(val))
        if task_result.warnings:
            for w in task_result.warnings:
                t.add_row("[yellow]warning[/yellow]", w)
        con.print(t)

    # ── Top-level metrics table ───────────────────────────────────────────────
    if result.metrics:
        con.print()
        m_table = Table(
            "Metric", "Score",
            title="Flat Metrics Summary",
            box=box.SIMPLE_HEAVY,
        )
        for key in sorted(result.metrics):
            val = result.metrics[key]
            color = _score_color(val)
            m_table.add_row(key, f"[{color}]{_fmt(val)}[/{color}]")
        con.print(m_table)

    # ── Composite scores ──────────────────────────────────────────────────────
    if result.composite:
        con.print()
        c_table = Table("Score", "Value", title="Composite Scores", box=box.SIMPLE_HEAVY)
        for key, val in sorted(result.composite.items()):
            color = _score_color(val)
            c_table.add_row(f"[bold]{key}[/bold]", f"[{color}]{_fmt(val)}[/{color}]")
        con.print(c_table)

    # ── Warnings ─────────────────────────────────────────────────────────────
    if result.warnings:
        con.print()
        for w in result.warnings:
            con.print(f"[yellow]WARNING:[/yellow] {w}")

    con.print()
