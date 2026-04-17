"""wikibench run — execute a benchmark evaluation run."""

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated, Any

import typer
from rich.console import Console

if TYPE_CHECKING:
    from wikibench.models.result import BenchmarkResult

app = typer.Typer(help="Run a WikiBench evaluation.")

_con = Console(stderr=True)


@app.callback(invoke_without_command=True)
def run(
    impl: Annotated[
        str,
        typer.Option("--impl", "-i", help="Adapter name (registered entry-point) or 'package:ClassName'."),
    ],
    corpus: Annotated[
        str,
        typer.Option("--corpus", "-c", help="Corpus directory path."),
    ],
    tasks: Annotated[
        list[str] | None,
        typer.Option("--task", "-t", help="Task IDs to run (repeatable). Default: T1+T2+T3."),
    ] = None,
    seed: Annotated[int, typer.Option(help="Random seed.")] = 42,
    cache_dir: Annotated[
        str,
        typer.Option(help="Directory used for LLM response caching."),
    ] = ".wikibench-cache",
    no_cache: Annotated[
        bool,
        typer.Option("--no-cache", help="Disable response caching."),
    ] = False,
    output: Annotated[
        str | None,
        typer.Option("--output", "-o", help="Directory to save results (JSON + Markdown + HTML)."),
    ] = None,
    sqlite: Annotated[
        str | None,
        typer.Option("--sqlite", help="Also append this run to a SQLite file (benchmark_runs table)."),
    ] = None,
    format: Annotated[
        str,
        typer.Option(
            "--format", "-f",
            help="Report format printed to stdout: console | json | markdown | html.",
        ),
    ] = "console",
    hard_limit: Annotated[
        float,
        typer.Option(
            "--hard-limit",
            help="Abort run if cumulative LLM cost (USD) exceeds this value.",
        ),
    ] = float("inf"),
    quiet: Annotated[
        bool,
        typer.Option("--quiet", "-q", help="Suppress progress messages."),
    ] = False,
) -> None:
    """Run a WikiBench evaluation and print (or save) the results."""
    # ── Resolve adapter ───────────────────────────────────────────────────────
    adapter_spec = _resolve_adapter_spec(impl)

    # ── Build Runner ──────────────────────────────────────────────────────────
    from wikibench.runner.runner import Runner

    runner = Runner(
        adapter_spec=adapter_spec,
        corpus=corpus,
        tasks=tasks or None,
        seed=seed,
        cache_dir=None if no_cache else cache_dir,
        hard_limit_usd=hard_limit,
    )

    if not quiet:
        _con.print(f"[bold blue]WikiBench[/bold blue] running [green]{impl}[/green] "
                   f"on corpus [green]{corpus}[/green] …")

    # ── Execute ───────────────────────────────────────────────────────────────
    try:
        result = runner.run()
    except Exception as exc:
        _con.print(f"[bold red]ERROR:[/bold red] {exc}")
        raise typer.Exit(code=1) from exc

    if not quiet:
        _con.print(f"[bold green]Done.[/bold green] Run ID: {result.run_id}")

    # ── Save result ───────────────────────────────────────────────────────────
    if output:
        from wikibench.storage.result_store import ResultStore
        store = ResultStore(root=output)
        run_dir = store.save(result)
        if not quiet:
            _con.print(f"Results saved to: {run_dir}")

    if sqlite:
        from wikibench.storage.sqlite import BenchmarkSqliteStore
        BenchmarkSqliteStore(sqlite).save(result)
        if not quiet:
            _con.print(f"Run appended to SQLite: {sqlite}")

    # ── Print report ──────────────────────────────────────────────────────────
    _print_report(result, report_format=format, output=output)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _resolve_adapter_spec(spec: str) -> Any:
    """Resolve an adapter spec string to a class or name.

    Supported formats:
    * ``"naive"``            — registered entry-point name
    * ``"mypackage:MyClass"`` — dotted module + class name
    """
    if ":" in spec:
        module_path, cls_name = spec.rsplit(":", 1)
        import importlib
        try:
            mod = importlib.import_module(module_path)
        except ImportError as exc:
            _con.print(f"[red]Cannot import module '{module_path}': {exc}[/red]")
            raise typer.Exit(code=1) from exc
        cls = getattr(mod, cls_name, None)
        if cls is None:
            _con.print(f"[red]Class '{cls_name}' not found in module '{module_path}'.[/red]")
            raise typer.Exit(code=1)
        return cls
    # Plain name — let the Runner resolve via entry_points
    return spec


def _print_report(
    result: BenchmarkResult,
    *,
    report_format: str,
    output: str | None = None,
) -> None:
    """Print the report in the requested format to stdout."""
    con_out = Console()  # stdout

    if report_format == "console":
        from wikibench.reporters.console import render
        render(result, console=con_out)
    elif report_format == "json":
        from wikibench.reporters.json import render
        con_out.print(render(result))
    elif report_format in ("markdown", "md"):
        from wikibench.reporters.markdown import render
        con_out.print(render(result))
    elif report_format == "html":
        from wikibench.reporters.html.renderer import render as html_render
        if output:
            _con.print("[dim]HTML report also written as report.html under --output directory.[/dim]")
        else:
            con_out.print(html_render(result))
    else:
        _con.print(f"[red]Unknown format '{report_format}'. Use: console | json | markdown | html.[/red]")
        raise typer.Exit(code=1)
