"""wikibench report — render a saved BenchmarkResult."""

from __future__ import annotations

from typing import Annotated

import typer

app = typer.Typer(help="Render a saved benchmark result.")


@app.callback(invoke_without_command=True)
def report(
    path: Annotated[str, typer.Argument(help="Path to result directory or .json file.")],
    format: Annotated[  # noqa: A002
        str,
        typer.Option("--format", "-f", help="Output format: console|json|markdown|html."),
    ] = "console",
    out: Annotated[str | None, typer.Option("--out", "-o", help="Write to file.")] = None,
) -> None:
    """Render a previously saved benchmark result."""
    typer.echo("[wikibench report] Not yet implemented — coming in Phase 1 Week 4.")
    raise typer.Exit(code=1)
