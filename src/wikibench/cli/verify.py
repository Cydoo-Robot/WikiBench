"""wikibench verify — contract-test an adapter."""

from __future__ import annotations

from typing import Annotated

import typer

app = typer.Typer(help="Verify an adapter passes the WikiBench contract tests.")


@app.callback(invoke_without_command=True)
def verify_adapter(
    adapter: Annotated[str, typer.Argument(help="Adapter name or 'package:Class'.")],
    config: Annotated[
        str | None, typer.Option("--config", help="Path to adapter config YAML.")
    ] = None,
) -> None:
    """Run the adapter contract test suite against a tiny synthetic corpus."""
    typer.echo("[wikibench verify-adapter] Not yet implemented — coming in Phase 1.5.")
    raise typer.Exit(code=1)
