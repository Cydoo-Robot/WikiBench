# WikiBench

The first benchmark suite for evaluating LLM-maintained knowledge bases. LLM Wiki, pioneered by Karpathy, is becoming core infrastructure for AI workflows — letting LLMs "compile" raw documents into structured knowledge bases, replacing the stateless retrieve-on-every-query pattern of RAG.

## Install

```bash
uv sync --extra dev
uv run wikibench --version
```

PyPI install (when published): `pip install wikibench` (see `pyproject.toml` for Python version).

## Quick start

Step-by-step CLI walkthroughs (corpus verify → synthetic generation → `wikibench run` → saved results + SQLite + `report`) live under **[examples/](examples/README.md)**.

## Docs

- [README_cn.md](README_cn.md) — project vision and design (Chinese).
- [Doc/](Doc/README.md) — full planning documents.
- [CHANGELOG.md](CHANGELOG.md) — release notes.
- [Doc/10-测试说明书.md](Doc/10-测试说明书.md) — how to run tests.

## License

Apache 2.0 — see [LICENSE](LICENSE).
