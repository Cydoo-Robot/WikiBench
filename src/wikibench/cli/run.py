"""wikibench run — execute a benchmark run."""

from __future__ import annotations

from typing import Annotated

import typer

app = typer.Typer(help="Run a WikiBench evaluation.")


@app.callback(invoke_without_command=True)
def run(
    impl: Annotated[str, typer.Option("--impl", "-i", help="Adapter name or 'package:Class'.")],
    corpus: Annotated[str, typer.Option("--corpus", "-c", help="Corpus ID or path.")],
    tasks: Annotated[
        list[str] | None,
        typer.Option("--task", "-t", help="Task IDs to run (repeatable). Default: all."),
    ] = None,
    seed: Annotated[int, typer.Option(help="Random seed.")] = 42,
    cache_dir: Annotated[str, typer.Option(help="Cache directory.")] = ".wikibench-cache",
    no_cache: Annotated[bool, typer.Option("--no-cache", help="Disable caching.")] = False,
    output: Annotated[str | None, typer.Option("--output", "-o", help="Output directory.")] = None,
    format: Annotated[  # noqa: A002
        str,
        typer.Option("--format", "-f", help="Report format: console|json|markdown|html."),
    ] = "console",
) -> None:
    """Run a WikiBench evaluation against a specified adapter and corpus."""
    typer.echo("[wikibench run] Not yet implemented — coming in Phase 1 Week 3.")
    raise typer.Exit(code=1)
