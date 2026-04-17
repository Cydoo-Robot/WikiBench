"""WikiBench CLI entry point."""

import typer
from rich import print as rprint

from wikibench.__version__ import __version__

app = typer.Typer(
    name="wikibench",
    help="WikiBench — evaluation infrastructure for LLM-maintained knowledge bases.",
    add_completion=True,
    no_args_is_help=True,
)


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(False, "--version", "-v", help="Show version and exit."),
) -> None:
    if version:
        rprint(f"[bold]wikibench[/bold] {__version__}")
        raise typer.Exit()
    if ctx.invoked_subcommand is None:
        rprint(ctx.get_help())


# Sub-commands are registered in their own modules and imported here.
# Deferred import avoids circular deps at import time.
def _register_subcommands() -> None:
    from wikibench.cli import corpus, report, run, verify

    app.add_typer(run.app, name="run")
    app.add_typer(corpus.app, name="corpus")
    app.add_typer(verify.app, name="verify")
    app.add_typer(report.app, name="report")


_register_subcommands()
