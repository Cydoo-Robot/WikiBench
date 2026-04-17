# Contributing to WikiBench

Thank you for your interest in contributing!  WikiBench is an open evaluation
infrastructure for LLM-maintained knowledge bases, and community contributions
are essential to making it the standard.

---

## Table of Contents

1. [Ways to Contribute](#ways-to-contribute)
2. [Development Setup](#development-setup)
3. [Project Structure](#project-structure)
4. [Submitting a PR](#submitting-a-pr)
5. [Submitting an Adapter](#submitting-an-adapter)
6. [Corpus Contributions](#corpus-contributions)
7. [Code Style](#code-style)
8. [Testing](#testing)

---

## Ways to Contribute

| Type | Description |
|------|-------------|
| **Bug fix** | Fix a broken behaviour; include a regression test |
| **Task implementation** | Implement a Phase-tagged TODO (see roadmap) |
| **Adapter** | Wrap an existing LLM Wiki implementation as a `WikiAdapter` |
| **Corpus** | Add or improve a corpus in `corpora/` |
| **Documentation** | Improve `Doc/` or the MkDocs site |
| **Discussion** | Open a GitHub Discussion or issue to propose ideas |

---

## Development Setup

We use [`uv`](https://github.com/astral-sh/uv) for dependency management.

```bash
# 1. Fork & clone
git clone https://github.com/your-org/WikiBench.git
cd WikiBench

# 2. Create a virtual env and install all dependencies
uv sync --extra dev

# 3. Install pre-commit hooks
pre-commit install

# 4. Verify your setup
pytest tests/unit/ -v
wikibench --version
```

---

## Project Structure

```
src/wikibench/    # Main package
tests/            # pytest test suite
corpora/          # Corpus data (markdown + ground truth)
Doc/              # Planning & specification documents
```

See `Doc/06-技术栈与工程规范.md` for the full annotated directory tree.

---

## Submitting a PR

1. Create a branch: `git checkout -b feat/my-feature`
2. Make your changes with tests
3. Run the full local check:
   ```bash
   ruff check src/ tests/
   ruff format src/ tests/
   mypy src/wikibench/ --ignore-missing-imports
   pytest tests/unit/ tests/integration/
   ```
4. Open a PR using the PR template

---

## Submitting an Adapter

An **adapter** wraps an existing LLM Wiki implementation so WikiBench can
evaluate it.

1. Create a package named `wikibench-adapter-<name>`
2. Subclass `WikiAdapter` from `wikibench.adapters`
3. Declare the entry point in your `pyproject.toml`:
   ```toml
   [project.entry-points."wikibench.adapters"]
   myimpl = "wikibench_adapter_myimpl:MyImplAdapter"
   ```
4. Pass the contract tests:
   ```bash
   pip install wikibench wikibench-adapter-myimpl
   wikibench verify-adapter myimpl
   ```
5. Open a GitHub Issue using the **New adapter submission** template

Full specification: `Doc/05-评测接口与适配器规范.md`

---

## Corpus Contributions

- All documents must be stored as `.md` files
- Each corpus needs a `manifest.yaml` validated against `CorpusMetadata`
- Ground truth files: `qa_pairs.jsonl`, `fidelity_claims.jsonl`, `contradictions.jsonl`
- Run `wikibench corpus verify <path>` before submitting

Full specification: `Doc/03-数据集与语料库设计.md`

---

## Code Style

- **Python 3.11+**, type hints everywhere
- **ruff** for lint + format (runs in pre-commit)
- **mypy --strict** for core modules
- No commented-out code; no obvious redundant comments
- Line length: 100 characters

---

## Testing

| Suite | Command | When to run |
|-------|---------|-------------|
| Unit | `pytest tests/unit/` | Always — fast, no I/O |
| Integration | `pytest tests/integration/` | Before PR |
| E2E | `pytest tests/e2e/ -m e2e` | Requires LLM credentials |

Aim for **≥70% coverage** on `src/wikibench/` core modules.

---

## Questions?

Open a [GitHub Discussion](https://github.com/your-org/WikiBench/discussions)
or drop into `#wikibench` on Discord.
