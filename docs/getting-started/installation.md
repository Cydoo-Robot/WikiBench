# Installation

## Requirements

- Python 3.11 or 3.12
- pip or [uv](https://github.com/astral-sh/uv) (recommended)

## Install from PyPI

```bash
pip install wikibench
```

Or with uv:

```bash
uv add wikibench
```

## Verify installation

```bash
wikibench --version
```

## Install an adapter

Adapters are distributed as separate packages:

```bash
pip install wikibench-adapter-naive   # built-in baseline (included)
pip install wikibench-adapter-ussumant  # community adapter (Phase 1.5+)
```

## Development install

```bash
git clone https://github.com/your-org/WikiBench.git
cd WikiBench
uv sync --extra dev
pre-commit install
```
