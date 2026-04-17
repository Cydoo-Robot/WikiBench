# Quick Start

!!! note "Phase 0"
    The full pipeline is under active development (Phase 1).
    This page will be updated as features land.

## Run against the built-in tiny corpus

```bash
wikibench run \
  --impl naive \
  --corpus synthetic-tiny \
  --task retrieval_accuracy \
  --task knowledge_fidelity
```

## Generate a synthetic corpus

```bash
wikibench corpus generate \
  --domain saas \
  --n-docs 50 \
  --out ./my-corpus
```

## View a saved result

```bash
wikibench report ./runs/my-run/ --format html --out report.html
```

## Verify your adapter

```bash
wikibench verify-adapter myimpl
```
