"""JSON reporter — serialises a BenchmarkResult to JSON."""

from __future__ import annotations

import json
from pathlib import Path

from wikibench.models.result import BenchmarkResult


def render(result: BenchmarkResult, indent: int = 2) -> str:
    """Return the result as a pretty-printed JSON string."""
    return result.model_dump_json(indent=indent)


def save(result: BenchmarkResult, path: str | Path, indent: int = 2) -> Path:
    """Write result JSON to *path*.

    If *path* is a directory the file is named ``<run_id>.json``.
    The file's parent directories are created automatically.

    Returns the resolved file path.
    """
    p = Path(path)
    if p.is_dir() or str(path).endswith("/") or str(path).endswith("\\"):
        p = p / f"{result.run_id}.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(render(result, indent=indent), encoding="utf-8")
    return p.resolve()


def load(path: str | Path) -> BenchmarkResult:
    """Load a :class:`BenchmarkResult` from a JSON file."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Result file not found: {p}")
    raw = json.loads(p.read_text(encoding="utf-8"))
    return BenchmarkResult.model_validate(raw)
