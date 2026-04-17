"""wikibench verify — smoke-test an adapter against a corpus (contract-lite)."""

from __future__ import annotations

import importlib
import os
from pathlib import Path
from typing import TYPE_CHECKING, Annotated, Any

import typer
from rich.console import Console

if TYPE_CHECKING:
    from wikibench.adapters._base import WikiAdapter

app = typer.Typer(help="Verify an adapter passes WikiBench adapter smoke checks.")

_con = Console(stderr=True)


def _load_yaml_config(path: str | None) -> dict[str, Any]:
    if not path:
        return {}
    import yaml

    p = Path(path)
    raw = yaml.safe_load(p.read_text(encoding="utf-8"))
    if raw is None:
        return {}
    if not isinstance(raw, dict):
        raise ValueError(f"Config YAML must be a mapping, got {type(raw).__name__}")
    return raw


def _resolve_adapter_spec(spec: str) -> Any:
    """Same rules as ``wikibench run --impl``: entry-point name or ``module:Class``."""
    if ":" in spec:
        module_path, cls_name = spec.rsplit(":", 1)
        try:
            mod = importlib.import_module(module_path)
        except ImportError as exc:
            raise ValueError(f"Cannot import module {module_path!r}: {exc}") from exc
        cls = getattr(mod, cls_name, None)
        if cls is None:
            raise ValueError(f"Class {cls_name!r} not found in {module_path!r}")
        return cls
    return spec


def _instantiate_adapter(spec: Any, cfg: dict[str, Any]) -> WikiAdapter:
    from wikibench.adapters._base import WikiAdapter
    from wikibench.adapters.registry import get_adapter

    if isinstance(spec, type) and issubclass(spec, WikiAdapter):
        return spec(cfg)
    if isinstance(spec, str):
        cls = get_adapter(spec)
        return cls(cfg)
    raise TypeError(f"Cannot instantiate adapter from {type(spec).__name__!r}")


def _ensure_tasks_registered() -> None:
    import importlib

    for mod in (
        "wikibench.tasks.retrieval_accuracy",
        "wikibench.tasks.knowledge_fidelity",
        "wikibench.tasks.contradiction_detection",
    ):
        importlib.import_module(mod)


def run_adapter_verify(
    adapter_spec: str,
    corpus_path: str | Path,
    *,
    config: dict[str, Any] | None = None,
    mock_llm: bool = True,
) -> None:
    """Load *corpus*, instantiate adapter, run ingest + one query per task intent.

    Raises on failure. Intended for CI and :func:`verify_cmd`.

    When *mock_llm* is True, sets ``WIKIBENCH_LLM_MOCK=1`` if not already set.
    """
    if mock_llm:
        os.environ.setdefault("WIKIBENCH_LLM_MOCK", "1")

    _ensure_tasks_registered()

    cfg = dict(config or {})
    spec = _resolve_adapter_spec(adapter_spec)
    adapter = _instantiate_adapter(spec, cfg)

    from wikibench.corpora.loader import load_corpus
    from wikibench.tasks import get_task

    corpus = load_corpus(corpus_path)

    desc = adapter.describe()
    if not desc.get("name") or not desc.get("version"):
        raise ValueError("adapter.describe() must include 'name' and 'version'")
    if "llm_models" not in desc:
        raise ValueError("adapter.describe() must include 'llm_models'")

    ingest = adapter.ingest(corpus.documents)

    _con.print(
        f"[green]ingest OK[/green] — wiki_tokens={ingest.stats.wiki_tokens} "
        f"llm_calls={ingest.stats.llm_calls}"
    )

    task_ids = ("retrieval_accuracy", "knowledge_fidelity", "contradiction_detection")
    for task_id in task_ids:
        task = get_task(task_id)()
        queries = task.prepare(corpus)
        if not queries:
            _con.print(f"[yellow]skip[/yellow] {task_id}: no queries")
            continue
        q = queries[0]
        resp = adapter.query(q)
        if not isinstance(resp.answer, str):
            raise TypeError(f"{task_id}: QueryResponse.answer must be str")
        _con.print(f"[green]query OK[/green] {task_id} intent={q.intent!r}")

    try:
        adapter.teardown()
    except Exception as exc:
        _con.print(f"[yellow]teardown raised[/yellow] {exc!r}")


@app.callback(invoke_without_command=True)
def verify_cmd(
    adapter: Annotated[
        str,
        typer.Option(
            "--adapter",
            "-a",
            help="Adapter entry-point name or 'module.path:Class'.",
            metavar="SPEC",
        ),
    ],
    config_path: Annotated[
        str | None,
        typer.Option("--config", help="Path to adapter config YAML."),
    ] = None,
    corpus: Annotated[
        str,
        typer.Option("--corpus", "-c", help="Corpus directory path."),
    ] = "corpora/synthetic/tiny",
    no_mock: Annotated[
        bool,
        typer.Option("--no-mock", help="Allow real LLM calls (unset mock mode)."),
    ] = False,
) -> None:
    """Run ingest + one sample query per default task (T1/T2/T3) on *corpus*."""
    try:
        cfg = _load_yaml_config(config_path)
        run_adapter_verify(
            adapter,
            corpus,
            config=cfg,
            mock_llm=not no_mock,
        )
    except Exception as exc:
        _con.print(f"[bold red]VERIFY FAILED:[/bold red] {exc}")
        raise typer.Exit(code=1) from exc
    _con.print("[bold green]Adapter verify passed.[/bold green]")
