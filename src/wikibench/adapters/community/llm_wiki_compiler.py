"""Community adapter: atomicmemory/llm-wiki-compiler via ``llmwiki`` CLI (subprocess).

Requires Node.js + globally or PATH-resolvable ``llmwiki``, provider credentials for
``compile`` / ``query``, and **must not** run under ``WIKIBENCH_LLM_MOCK=1`` (the
upstream tool performs real LLM calls).

See ``Doc/07`` §4.2 A and ``sandbox.py`` for clone layout.
"""

from __future__ import annotations

import logging
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any

from wikibench.adapters._base import WikiAdapter
from wikibench.adapters.builtin.naive import _parse_response
from wikibench.adapters.community.query_prompt import build_user_query_text
from wikibench.adapters.community.sandbox import suggested_clone_path
from wikibench.models.document import Document
from wikibench.models.query import Query, QueryResponse
from wikibench.models.result import IngestResult, IngestStats
from wikibench.runtime.token_counter import count_tokens

log = logging.getLogger(__name__)

_DEFAULT_MODEL_LABEL = "llmwiki-cli"


class LLMWikiCompilerAdapter(WikiAdapter):
    """Orchestrate ``llmwiki ingest`` / ``compile`` / ``query`` in a project directory."""

    name = "llm_wiki_compiler"
    version = "0.1.0"

    def __init__(self, config: dict[str, Any]) -> None:
        super().__init__(config)
        self._llmwiki_bin: str = str(config.get("llmwiki_bin", "llmwiki"))
        self._timeout_ingest_s: float = float(config.get("timeout_ingest_s", 600.0))
        self._timeout_query_s: float = float(config.get("timeout_query_s", 180.0))
        raw_project = config.get("project_dir")
        self._project_dir: Path | None = Path(raw_project).resolve() if raw_project else None
        self._own_project_dir = False
        self._model_label = str(config.get("model", _DEFAULT_MODEL_LABEL))

    def describe(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "llm_models": {"adapter_backend": self._model_label},
            "strategy": "llmwiki_cli",
            "upstream_hint": str(suggested_clone_path({}, "llm-wiki-compiler")),
        }

    def _reject_mock(self) -> None:
        if os.environ.get("WIKIBENCH_LLM_MOCK", "").strip() in ("1", "true", "True", "yes"):
            msg = (
                "LLMWikiCompilerAdapter runs the real llmwiki CLI (compile/query need API access). "
                "Unset WIKIBENCH_LLM_MOCK or use a built-in adapter for mock mode."
            )
            raise RuntimeError(msg)

    def _run(self, args: list[str], *, cwd: Path, timeout: float) -> str:
        log.debug("Running %s in %s", args, cwd)
        proc = subprocess.run(
            args,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        if proc.returncode != 0:
            err = (proc.stderr or proc.stdout or "").strip()
            raise RuntimeError(f"Command failed ({args!r}): {err[:2000]}")
        return (proc.stdout or "").strip()

    def _ensure_project_dir(self) -> Path:
        if self._project_dir is not None:
            self._project_dir.mkdir(parents=True, exist_ok=True)
            return self._project_dir
        self._project_dir = Path(
            tempfile.mkdtemp(prefix="wikibench-llmwiki-", dir=tempfile.gettempdir())
        )
        self._own_project_dir = True
        return self._project_dir

    def ingest(self, docs: list[Document]) -> IngestResult:
        self._reject_mock()
        exe = shutil.which(self._llmwiki_bin)
        if not exe and Path(self._llmwiki_bin).exists():
            exe = str(Path(self._llmwiki_bin).resolve())
        if not exe:
            raise RuntimeError(
                f"Cannot find llmwiki executable ({self._llmwiki_bin!r}). "
                "Install with: npm install -g llm-wiki-compiler"
            )
        self._llmwiki_bin = exe

        t0 = time.perf_counter()
        root = self._ensure_project_dir()

        for doc in docs:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                suffix=".md",
                delete=False,
            ) as fh:
                fh.write(doc.content)
                tmp_path = fh.name
            try:
                self._run(
                    [self._llmwiki_bin, "ingest", tmp_path],
                    cwd=root,
                    timeout=self._timeout_ingest_s,
                )
            finally:
                Path(tmp_path).unlink(missing_ok=True)

        self._run([self._llmwiki_bin, "compile"], cwd=root, timeout=self._timeout_ingest_s)

        wiki_dir = root / "wiki"
        wiki_tokens = 0
        if wiki_dir.is_dir():
            for md in wiki_dir.rglob("*.md"):
                wiki_tokens += count_tokens(md.read_text(encoding="utf-8"), self._model_label)
        else:
            wiki_tokens = count_tokens("", self._model_label)

        duration = time.perf_counter() - t0
        return IngestResult(
            wiki_id=f"llmwiki-{root.name}",
            stats=IngestStats(
                tokens_in=0,
                tokens_out=0,
                llm_calls=0,
                duration_s=duration,
                wiki_tokens=wiki_tokens,
                extra={"project_dir": str(root), "llmwiki_bin": self._llmwiki_bin},
            ),
        )

    def query(self, query: Query) -> QueryResponse:
        self._reject_mock()
        if self._project_dir is None:
            raise RuntimeError("ingest() must run before query().")
        text = build_user_query_text(query)
        raw = self._run(
            [self._llmwiki_bin, "query", text],
            cwd=self._project_dir,
            timeout=self._timeout_query_s,
        )
        return _parse_response(query, raw)

    def teardown(self) -> None:
        if self._own_project_dir and self._project_dir is not None:
            shutil.rmtree(self._project_dir, ignore_errors=True)
        self._project_dir = None
        self._own_project_dir = False
        return
