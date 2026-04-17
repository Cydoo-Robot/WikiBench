"""``LLMWikiCompilerAdapter`` — optional integration (real ``llmwiki`` + API).

Requires a prepared sandbox (``scripts/setup_llmwiki_sandbox.ps1`` or ``.sh``),
``npm install`` + ``npm run build`` inside the clone, and provider credentials.

CI does not install Node; the test is skipped unless both the env flag and a
working CLI under ``.wikibench-sandboxes/llm-wiki-compiler`` are present.

Example (PowerShell)::

    .\\scripts\\setup_llmwiki_sandbox.ps1
    $env:WIKIBENCH_LLM_WIKI_ROOT = (Resolve-Path .\\.wikibench-sandboxes\\llm-wiki-compiler)
    $env:WIKIBENCH_RUN_LLMWIKI_INTEGRATION = \"1\"
    Remove-Item Env:WIKIBENCH_LLM_MOCK -ErrorAction SilentlyContinue
    uv run pytest tests/adapter_contract/test_community_llmwiki.py -v
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from wikibench.adapters.community.llm_wiki_sandbox import resolve_llmwiki_invocation
from wikibench.cli.verify import run_adapter_verify

REPO_ROOT = Path(__file__).resolve().parents[2]
TINY = REPO_ROOT / "corpora" / "synthetic" / "tiny"
SANDBOX = REPO_ROOT / ".wikibench-sandboxes" / "llm-wiki-compiler"


def _llmwiki_sandbox_ready() -> bool:
    return SANDBOX.is_dir() and resolve_llmwiki_invocation(SANDBOX) is not None


@pytest.mark.skipif(
    os.environ.get("WIKIBENCH_RUN_LLMWIKI_INTEGRATION", "").strip() not in ("1", "true", "True"),
    reason="Set WIKIBENCH_RUN_LLMWIKI_INTEGRATION=1 for real llmwiki integration",
)
@pytest.mark.skipif(
    not _llmwiki_sandbox_ready(),
    reason="Run scripts/setup_llmwiki_sandbox.ps1|.sh (git clone + npm install + npm run build)",
)
def test_llm_wiki_compiler_contract() -> None:
    run_adapter_verify(
        "wikibench.adapters.community.llm_wiki_compiler:LLMWikiCompilerAdapter",
        TINY,
        config={"llm_wiki_compiler_root": str(SANDBOX)},
        mock_llm=False,
    )
