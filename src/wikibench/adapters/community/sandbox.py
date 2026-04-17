"""Sandbox path helpers for community adapters (upstream clones live outside Git)."""

from __future__ import annotations

import os
from pathlib import Path

# Default root for per-machine clones; already ignored by repo `.gitignore` (`.*`).
DEFAULT_SANDBOX_ROOT = Path(
    os.environ.get("WIKIBENCH_SANDBOX_ROOT", ".wikibench-sandboxes")
).expanduser()


def sandbox_root(config: dict[str, object] | None) -> Path:
    """Return base directory for optional upstream checkouts."""
    if not config:
        return DEFAULT_SANDBOX_ROOT
    raw = config.get("sandbox_root")
    if isinstance(raw, str) and raw.strip():
        return Path(raw).expanduser().resolve()
    if isinstance(raw, Path):
        return raw.expanduser().resolve()
    return DEFAULT_SANDBOX_ROOT


def suggested_clone_path(config: dict[str, object] | None, repo_dirname: str) -> Path:
    """e.g. ``.wikibench-sandboxes/llm-wiki-compiler``."""
    return sandbox_root(config) / repo_dirname
