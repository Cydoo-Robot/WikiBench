"""WikiBench reporters — render BenchmarkResult in various formats."""

from __future__ import annotations

from wikibench.models.result import BenchmarkResult


def render(result: BenchmarkResult, format: str = "console", **kwargs) -> str | None:  # noqa: A002
    """Render *result* in the requested format.

    Args:
        result: The benchmark result to render.
        format: One of ``"console"``, ``"json"``, ``"markdown"``, ``"html"``.
        **kwargs: Passed through to the format-specific renderer.

    Returns:
        String output for ``"json"``, ``"markdown"``, and ``"html"``; ``None`` for
        ``"console"`` (output goes directly to stdout via Rich).
    """
    if format == "console":
        from wikibench.reporters.console import render as _render
        _render(result, **kwargs)
        return None
    if format == "json":
        from wikibench.reporters.json import render as _render
        return _render(result, **kwargs)
    if format in ("markdown", "md"):
        from wikibench.reporters.markdown import render as _render
        return _render(result)
    if format == "html":
        from wikibench.reporters.html.renderer import render as _render
        return _render(result)
    raise ValueError(f"Unknown format {format!r}. Choices: console, json, markdown, html.")
