"""wikibench corpus — manage corpora (generate / crawl / verify)."""

from __future__ import annotations

from typing import Annotated

import typer

app = typer.Typer(help="Manage WikiBench corpora.")


@app.command("generate")
def generate(
    domain: Annotated[str, typer.Option("--domain", "-d", help="Domain template name.")],
    n_docs: Annotated[int, typer.Option("--n-docs", help="Number of documents to generate.")] = 50,
    out: Annotated[str, typer.Option("--out", "-o", help="Output directory.")] = "./corpus-out",
    seed: Annotated[int, typer.Option(help="Random seed.")] = 42,
) -> None:
    """Generate a synthetic corpus from a domain template."""
    typer.echo("[wikibench corpus generate] Not yet implemented — coming in Phase 1 Week 5.")
    raise typer.Exit(code=1)


@app.command("verify")
def verify(
    path: Annotated[str, typer.Argument(help="Path to corpus directory.")],
) -> None:
    """Validate a corpus directory against the manifest schema."""
    typer.echo("[wikibench corpus verify] Not yet implemented — coming in Phase 1 Week 1.")
    raise typer.Exit(code=1)
