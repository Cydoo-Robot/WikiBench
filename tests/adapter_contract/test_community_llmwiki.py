"""``LLMWikiCompilerAdapter`` — optional integration (real ``llmwiki`` + API).

CI does not install Node; default suite skips this test. To run locally::

    set WIKIBENCH_RUN_LLMWIKI_INTEGRATION=1
    set WIKIBENCH_LLM_MOCK=
    uv run pytest tests/adapter_contract/test_community_llmwiki.py -v
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from wikibench.cli.verify import run_adapter_verify

REPO_ROOT = Path(__file__).resolve().parents[2]
TINY = REPO_ROOT / "corpora" / "synthetic" / "tiny"


@pytest.mark.skipif(
    os.environ.get("WIKIBENCH_RUN_LLMWIKI_INTEGRATION", "").strip() not in ("1", "true", "True"),
    reason="Set WIKIBENCH_RUN_LLMWIKI_INTEGRATION=1 and install llmwiki (npm i -g llm-wiki-compiler)",
)
def test_llm_wiki_compiler_contract() -> None:
    run_adapter_verify(
        "wikibench.adapters.community.llm_wiki_compiler:LLMWikiCompilerAdapter",
        TINY,
        config={},
        mock_llm=False,
    )
