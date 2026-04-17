"""ResultStore — persist and retrieve BenchmarkResult objects on disk.

Directory layout
----------------
``<store_root>/
    <run_id>/
        result.json      — full serialised BenchmarkResult
        report.md        — Markdown human-readable report (optional)
        report.html      — single-page HTML report (optional)
``

Usage
-----
>>> store = ResultStore("./results")
>>> path = store.save(result)
>>> loaded = store.load(result.run_id)
>>> all_ids = store.list_runs()
"""

from __future__ import annotations

from pathlib import Path

from wikibench.models.result import BenchmarkResult
from wikibench.reporters import json as json_reporter
from wikibench.reporters import markdown as md_reporter
from wikibench.reporters.html import renderer as html_reporter


class ResultStore:
    """Persistent key-value store for :class:`BenchmarkResult` objects.

    Args:
        root: Root directory for storing results.
        write_markdown: Also write a ``report.md`` alongside ``result.json``.
        write_html: Also write a ``report.html`` alongside ``result.json``.
    """

    def __init__(
        self,
        root: str | Path = "./results",
        write_markdown: bool = True,
        write_html: bool = True,
    ) -> None:
        self.root = Path(root)
        self.write_markdown = write_markdown
        self.write_html = write_html

    # ── Write ─────────────────────────────────────────────────────────────────

    def save(self, result: BenchmarkResult) -> Path:
        """Persist *result* and return the directory path.

        Creates ``<root>/<run_id>/result.json`` (and optionally ``report.md`` / ``report.html``).
        """
        run_dir = self.root / result.run_id
        run_dir.mkdir(parents=True, exist_ok=True)

        json_path = run_dir / "result.json"
        json_reporter.save(result, json_path)

        if self.write_markdown:
            md_path = run_dir / "report.md"
            md_reporter.save(result, md_path)

        if self.write_html:
            html_path = run_dir / "report.html"
            html_reporter.save(result, html_path)

        return run_dir.resolve()

    # ── Read ──────────────────────────────────────────────────────────────────

    def load(self, run_id: str) -> BenchmarkResult:
        """Load a result by run_id.

        Raises :class:`FileNotFoundError` if the run does not exist.
        """
        json_path = self.root / run_id / "result.json"
        return json_reporter.load(json_path)

    def load_from_path(self, path: str | Path) -> BenchmarkResult:
        """Load a result from an explicit file or directory path.

        * If *path* is a ``result.json`` file, load it directly.
        * If *path* is a run directory, load ``<path>/result.json``.
        """
        p = Path(path)
        if p.is_dir():
            p = p / "result.json"
        return json_reporter.load(p)

    # ── Enumerate ─────────────────────────────────────────────────────────────

    def list_runs(self) -> list[str]:
        """Return a sorted list of run IDs present in the store."""
        if not self.root.exists():
            return []
        return sorted(
            d.name for d in self.root.iterdir() if d.is_dir() and (d / "result.json").exists()
        )

    def exists(self, run_id: str) -> bool:
        return (self.root / run_id / "result.json").exists()
