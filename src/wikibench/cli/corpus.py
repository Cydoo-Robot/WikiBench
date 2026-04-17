"""wikibench corpus — manage corpora (generate / verify)."""

from __future__ import annotations

from typing import Annotated

import typer
from rich.console import Console

app = typer.Typer(help="Manage WikiBench corpora.")
console = Console()


@app.command("generate")
def generate(
    domain: Annotated[
        str,
        typer.Option("--domain", "-d", help="Domain id or alias (e.g. saas, saas_engineering)."),
    ],
    n_docs: Annotated[int, typer.Option("--n-docs", help="Number of documents to generate.")] = 50,
    out: Annotated[str, typer.Option("--out", "-o", help="Output directory.")] = "./corpus-out",
    seed: Annotated[int, typer.Option(help="Random seed (noise / filler injection).")] = 42,
    qa_per_doc: Annotated[int, typer.Option(help="1 or 2 QA pairs per document.")] = 2,
    noise: Annotated[
        float,
        typer.Option("--noise", help="Probability [0,1] of adding a filler paragraph."),
    ] = 0.0,
) -> None:
    """Generate a deterministic synthetic corpus from a domain template."""
    from wikibench.corpora.synthetic.generator import SyntheticGenerator

    try:
        gen = SyntheticGenerator(
            domain=domain,
            seed=seed,
            qa_per_doc=qa_per_doc,
            noise_probability=noise,
        )
        path = gen.generate(out, n_docs)
    except KeyError as exc:
        console.print(f"[red]ERROR[/red] {exc}")
        raise typer.Exit(code=1) from exc
    except (ValueError, NotImplementedError) as exc:
        console.print(f"[red]ERROR[/red] {exc}")
        raise typer.Exit(code=1) from exc
    except RuntimeError as exc:
        console.print(f"[red]VERIFY FAILED[/red] {exc}")
        raise typer.Exit(code=1) from exc

    console.print(f"[green]OK[/green] Synthetic corpus written to [bold]{path}[/bold]")


@app.command("verify")
def verify(
    path: Annotated[str, typer.Argument(help="Path to corpus directory.")],
    quiet: Annotated[bool, typer.Option("--quiet", "-q", help="Only print errors.")] = False,
) -> None:
    """Validate a corpus directory against the manifest schema."""
    from wikibench.corpora.manifest import verify_corpus_dir

    result = verify_corpus_dir(path)

    if not quiet:
        for w in result.warnings:
            console.print(f"[yellow]WARNING[/yellow] {w}")

    for e in result.errors:
        console.print(f"[red]ERROR[/red]   {e}")

    if result.ok:
        console.print(f"[green]PASS[/green] Corpus at [bold]{path}[/bold] passed all checks.")
    else:
        console.print(
            f"[red]FAIL[/red] Corpus at [bold]{path}[/bold] has {len(result.errors)} error(s)."
        )
        raise typer.Exit(code=1)


@app.command("info")
def info(
    path: Annotated[str, typer.Argument(help="Path to corpus directory.")],
) -> None:
    """Show a summary of a corpus (documents, ground truth counts, metadata)."""

    from wikibench.corpora.__main__ import main

    raise typer.Exit(code=main(path))
