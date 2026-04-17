"""wikibench report — render a previously saved BenchmarkResult."""

from __future__ import annotations

from typing import Annotated

import typer
from rich.console import Console

app = typer.Typer(help="Render a saved benchmark result.")

_con = Console(stderr=True)


@app.command("show")
def show(
    path: Annotated[
        str,
        typer.Argument(
            help=(
                "Path to a run directory (contains result.json), "
                "a result.json file, or a results store root with --run-id."
            )
        ),
    ],
    format: Annotated[  # noqa: A002
        str,
        typer.Option("--format", "-f", help="Output format: console | json | markdown."),
    ] = "console",
    out: Annotated[
        str | None,
        typer.Option("--out", "-o", help="Write rendered output to this file."),
    ] = None,
    run_id: Annotated[
        str | None,
        typer.Option("--run-id", help="Specific run ID to load from a store root."),
    ] = None,
) -> None:
    """Render a previously saved benchmark result."""
    _do_report(path=path, format=format, out=out, run_id=run_id)


@app.command("list")
def list_runs(
    path: Annotated[
        str,
        typer.Argument(help="Results store root directory."),
    ],
) -> None:
    """List all run IDs saved in a results store directory."""
    from wikibench.storage.result_store import ResultStore

    store = ResultStore(root=path, write_markdown=False)
    ids = store.list_runs()
    if not ids:
        _con.print("[yellow]No saved runs found.[/yellow]")
        raise typer.Exit()
    con_out = Console()
    for rid in ids:
        con_out.print(rid)


# ── Shared implementation ──────────────────────────────────────────────────────

def _do_report(path: str, format: str, out: str | None, run_id: str | None) -> None:
    from pathlib import Path
    from wikibench.storage.result_store import ResultStore

    p = Path(path)

    try:
        if run_id:
            store = ResultStore(root=p, write_markdown=False)
            result = store.load(run_id)
        elif p.is_file() or (p.is_dir() and (p / "result.json").exists()):
            store = ResultStore(root=p.parent, write_markdown=False)
            result = store.load_from_path(p)
        else:
            _con.print(f"[red]Path not found or unrecognised: {p}[/red]")
            raise typer.Exit(code=1)
    except FileNotFoundError as exc:
        _con.print(f"[red]File not found: {exc}[/red]")
        raise typer.Exit(code=1) from exc

    con_out = Console()

    if format == "console":
        from wikibench.reporters.console import render
        if out:
            from io import StringIO
            buf = StringIO()
            con_buf = Console(file=buf, no_color=True, width=120)
            render(result, console=con_buf)
            _write_out(out, buf.getvalue())
        else:
            render(result, console=con_out)
    elif format == "json":
        from wikibench.reporters.json import render
        text = render(result)
        if out:
            _write_out(out, text)
        else:
            con_out.print(text)
    elif format in ("markdown", "md"):
        from wikibench.reporters.markdown import render
        text = render(result)
        if out:
            _write_out(out, text)
        else:
            con_out.print(text)
    else:
        _con.print(f"[red]Unknown format '{format}'. Use: console | json | markdown.[/red]")
        raise typer.Exit(code=1)


def _write_out(path: str, content: str) -> None:
    from pathlib import Path
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    _con.print(f"Written to: {p.resolve()}")
