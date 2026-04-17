"""ObsidianWikiAdapter contract — uses minimal `.skills/` fixture + LLM mock."""

from __future__ import annotations

from pathlib import Path

from wikibench.cli.verify import run_adapter_verify

REPO_ROOT = Path(__file__).resolve().parents[2]
TINY = REPO_ROOT / "corpora" / "synthetic" / "tiny"
OBS_FIXTURE = REPO_ROOT / "tests" / "fixtures" / "obsidian_wiki_minimal"


def test_obsidian_wiki_adapter_contract() -> None:
    run_adapter_verify(
        "wikibench.adapters.community.obsidian_wiki:ObsidianWikiAdapter",
        TINY,
        config={"obsidian_wiki_repo": str(OBS_FIXTURE)},
        mock_llm=True,
    )
