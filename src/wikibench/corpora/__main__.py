"""python -m wikibench.corpora.loader <corpus-path>

Loads a corpus and prints a summary table to stdout.  Useful for quickly
verifying a corpus directory during development.

Usage::

    python -m wikibench.corpora.loader corpora/synthetic/tiny
    uv run python -m wikibench.corpora.loader corpora/synthetic/tiny
"""

from __future__ import annotations

import sys

from rich.console import Console
from rich.table import Table

from wikibench.corpora.loader import load_corpus
from wikibench.corpora.manifest import verify_corpus_dir

console = Console()


def main(path: str) -> int:
    # Integrity check first
    result = verify_corpus_dir(path)
    if result.warnings:
        for w in result.warnings:
            console.print(f"[yellow]WARNING[/yellow] {w}")
    if not result.ok:
        for e in result.errors:
            console.print(f"[red]ERROR[/red]   {e}")
        return 1

    corpus = load_corpus(path)
    meta = corpus.metadata
    gt = corpus.ground_truth

    # ── Summary table ─────────────────────────────────────────────────────────
    table = Table(
        title=f"Corpus: [bold]{meta.id}[/bold]", show_header=True, header_style="bold cyan"
    )
    table.add_column("Field", style="dim", min_width=20)
    table.add_column("Value")

    table.add_row("ID", meta.id)
    table.add_row("Version", meta.version)
    table.add_row("Tier", meta.tier)
    table.add_row("Domain", meta.domain or "—")
    table.add_row("Language", meta.language)
    table.add_row("Documents loaded", str(len(corpus.documents)))
    table.add_row("  doc_count (manifest)", str(meta.doc_count))
    table.add_row("QA pairs", str(len(gt.qa_pairs)))
    table.add_row("Fidelity claims", str(len(gt.fidelity_claims)))
    table.add_row("Contradiction pairs", str(len(gt.contradictions)))
    if meta.description:
        table.add_row("Description", meta.description.strip())

    console.print(table)

    # ── Document list ─────────────────────────────────────────────────────────
    if corpus.documents:
        doc_table = Table(title="Documents", show_header=True, header_style="bold")
        doc_table.add_column("#", style="dim", width=4)
        doc_table.add_column("Path")
        doc_table.add_column("Modality")
        doc_table.add_column("Chars", justify="right")

        for i, doc in enumerate(corpus.documents, 1):
            doc_table.add_row(str(i), doc.path, doc.modality, str(len(doc.content)))

        console.print(doc_table)

    console.print(f"\n[green]OK[/green] Corpus [bold]{meta.id}[/bold] loaded successfully.")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        console.print("[red]Usage:[/red] python -m wikibench.corpora.loader <corpus-path>")
        sys.exit(1)
    sys.exit(main(sys.argv[1]))
