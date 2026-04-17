"""Resolve how to invoke ``llmwiki`` from a local clone of atomicmemory/llm-wiki-compiler."""

from __future__ import annotations

import os
from pathlib import Path


def resolve_llmwiki_invocation(sandbox_root: Path) -> list[str] | None:
    """Return argv prefix to run the CLI from a sandbox checkout.

    Preference order:

    1. ``node_modules/.bin/llmwiki`` (Unix), ``llmwiki.cmd`` / ``llmwiki.ps1`` (Windows)
    2. ``node dist/cli.js`` if ``dist/cli.js`` exists (after ``npm run build``)
    """
    root = sandbox_root.expanduser().resolve()
    if not root.is_dir():
        return None

    bin_dir = root / "node_modules" / ".bin"
    if bin_dir.is_dir():
        for name in ("llmwiki.cmd", "llmwiki.ps1", "llmwiki"):
            candidate = bin_dir / name
            if candidate.is_file():
                return [str(candidate.resolve())]

    cli_js = root / "dist" / "cli.js"
    if cli_js.is_file():
        node = shutil_which("node")
        if node:
            return [node, str(cli_js.resolve())]
    return None


def shutil_which(cmd: str) -> str | None:
    """Thin wrapper for tests."""
    from shutil import which

    return which(cmd)


def default_sandbox_from_env_or_cwd() -> Path | None:
    """``WIKIBENCH_LLM_WIKI_ROOT`` or ``.wikibench-sandboxes/llm-wiki-compiler`` under cwd."""
    raw = os.environ.get("WIKIBENCH_LLM_WIKI_ROOT", "").strip()
    if raw:
        return Path(raw).expanduser().resolve()
    candidate = Path.cwd() / ".wikibench-sandboxes" / "llm-wiki-compiler"
    if candidate.is_dir():
        return candidate.resolve()
    return None
